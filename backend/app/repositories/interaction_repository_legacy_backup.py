from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import joinedload
from datetime import datetime
from typing import Optional, List, Dict, Any
import asyncio
from app.models.domain import Interaction, Session as SessionModel, Client
from app.schemas.interaction import InteractionCreateNested
from app.services.ai_service import generate_sales_analysis, ai_service
from app.services.session_psychology_service import session_psychology_engine
from app.core.database import engine  # Import engine dla fresh database session
import logging

logger = logging.getLogger(__name__)

class InteractionRepository:
    """
    Repozytorium do zarządzania operacjami na danych interakcji.
    """
    async def get_interaction(self, db: AsyncSession, interaction_id: int):
        # EAGER LOADING: Pobierz interaction wraz z session psychology data
        query = select(Interaction).options(joinedload(Interaction.session)).where(Interaction.id == interaction_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_session_interactions(self, db: AsyncSession, session_id: int, skip: int = 0, limit: int = 100):
        query = select(Interaction).where(Interaction.session_id == session_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_interaction(self, db: AsyncSession, session_id: int, interaction_data: InteractionCreateNested):
        """
        Tworzy nową interakcję z analizą AI.
        """
        try:
            # Pobierz sesję z klientem dla kontekstu AI
            session_query = select(SessionModel).where(SessionModel.id == session_id)
            session_result = await db.execute(session_query)
            session = session_result.scalar_one_or_none()
            
            if not session:
                raise ValueError(f"Sesja o ID {session_id} nie istnieje")
            
            # Pobierz klienta
            client_query = select(Client).where(Client.id == session.client_id)
            client_result = await db.execute(client_query)
            client = client_result.scalar_one_or_none()
            
            # Przygotuj podstawowe dane interakcji
            interaction_dict = {
                "session_id": session_id,
                "user_input": interaction_data.user_input,
                "ai_response_json": {},
                "feedback_data": []
            }
            
            # NOWE: Sprawdź czy to clarification interaction
            is_clarification = bool(interaction_data.additional_context or interaction_data.clarifying_answer)
            parent_id = interaction_data.parent_interaction_id if hasattr(interaction_data, 'parent_interaction_id') else None
            
            print(f"🔄 [CREATE] Tworzenie interakcji: is_clarification={is_clarification}, parent_id={parent_id}")
            
            try:
                # NOWA LOGIKA v4.0 - ULTRA MÓZG: Psychology PRZED AI Response
                if client:
                    client_profile = {
                        "alias": client.alias,
                        "archetype": client.archetype,
                        "notes": client.notes
                    }
                    
                    # Historia sesji
                    session_history = []
                    session_context = {"session_type": "consultation"}
                    
                    # KROK 3.1: KLUCZOWE! Pobierz i zaktualizuj surowe dane psychometryczne PRZED AI response
                    logger.info(f"🧠 [ULTRA BRAIN REPO] Rozpoczynam analizę psychology dla sesji {session_id}")
                    updated_psychology_profile = await session_psychology_engine.update_and_get_psychology(
                        session_id=session_id,
                        db=db,
                        ai_service=ai_service
                    )
                    logger.info(f"✅ [ULTRA BRAIN REPO] Psychology profile gotowy! Confidence: {updated_psychology_profile.get('psychology_confidence', 0)}%")
                    
                    # 🚀 PRIORYTET 4: PARALLEL PROCESSING - Synteza + Wskaźniki równolegle
                    logger.info(f"🔬 [ULTRA BRAIN PARALLEL] Rozpoczynam równoległe przetwarzanie DNA + Wskaźników...")
                    
                    # Uruchom syntezę holistyczną i generowanie wskaźników równolegle jeśli możliwe
                    holistic_task = ai_service._run_holistic_synthesis(updated_psychology_profile)
                    
                    # Czekaj na DNA Klienta (wymagane do wskaźników)
                    holistic_profile = await holistic_task
                    logger.info(f"✅ [SYNTEZATOR REPO] DNA Klienta gotowe! Drive: {holistic_profile.get('main_drive', 'Unknown')}")
                    
                    # Teraz uruchom równolegle: zapis do bazy + generowanie wskaźników
                    db_save_task = db.execute(
                        update(SessionModel)
                        .where(SessionModel.id == session_id)
                        .values(holistic_psychometric_profile=holistic_profile)
                    )
                    
                    indicators_task = ai_service._run_sales_indicators_generation(holistic_profile)
                    
                    # Czekaj na oba procesy równolegle
                    try:
                        db_result, sales_indicators = await asyncio.gather(
                            db_save_task,
                            indicators_task,
                            return_exceptions=True
                        )
                        
                        # Sprawdź wyniki
                        if isinstance(db_result, Exception):
                            logger.error(f"❌ [SYNTEZATOR REPO] Błąd zapisu holistycznego profilu: {db_result}")
                        else:
                            logger.info(f"💾 [SYNTEZATOR REPO] Holistyczny profil zapisany równolegle!")
                            
                        if isinstance(sales_indicators, Exception):
                            logger.error(f"❌ [SALES INDICATORS REPO] Błąd generacji wskaźników: {sales_indicators}")
                            sales_indicators = ai_service._create_fallback_sales_indicators()
                        else:
                            logger.info(f"✅ [SALES INDICATORS REPO] Wskaźniki wygenerowane równolegle! Temperature: {sales_indicators.get('purchase_temperature', {}).get('value', 'Unknown')}%")
                            
                    except Exception as e:
                        logger.error(f"❌ [ULTRA BRAIN PARALLEL] Błąd podczas równoległego przetwarzania: {e}")
                        sales_indicators = ai_service._create_fallback_sales_indicators()
                    
                    if is_clarification and parent_id:
                        # ŚCIEŻKA CLARIFICATION: Analiza z DNA Klienta (Ultra Mózg v4.0)
                        logger.info(f"⚡ [ULTRA BRAIN] Clarification analysis z DNA Klienta dla parent={parent_id}")
                        
                        ai_response = await generate_sales_analysis(
                            user_input=f"Aktualizacja: {interaction_data.user_input}",
                            client_profile=client_profile,
                            session_history=session_history,
                            session_context={'type': 'clarification_update'},
                            session_psychology=updated_psychology_profile,  # DEPRECATED v4.0
                            holistic_profile=holistic_profile,              # NOWY v4.0: DNA Klienta
                            sales_indicators=sales_indicators               # NOWY v4.1: PRIORYTET 3
                        )
                    else:
                        # ŚCIEŻKA STANDARD: Strategia z DNA Klienta (Ultra Mózg v4.0)
                        logger.info(f"⚡ [ULTRA BRAIN] Generator Strategii aktywny - używam DNA Klienta")
                        
                        ai_response = await generate_sales_analysis(
                            user_input=interaction_data.user_input,
                            client_profile=client_profile,
                            session_history=session_history,
                            session_context=session_context,
                            session_psychology=updated_psychology_profile,  # DEPRECATED v4.0
                            holistic_profile=holistic_profile,              # NOWY v4.0: DNA Klienta
                            sales_indicators=sales_indicators,              # NOWY v4.1: PRIORYTET 3
                            customer_archetype=updated_psychology_profile.get('customer_archetype')  # NOWE! Customer archetype
                        )
                        
                        # USUNIĘTE: Stare confidence scoring - teraz mamy prawdziwe dane z psychology engine
                    
                    interaction_dict["ai_response_json"] = ai_response
                    
            except Exception as ai_error:
                # Fallback gdy AI nie działa
                interaction_dict["ai_response_json"] = {
                    "main_analysis": "AI niedostępny. Postępuj zgodnie z procedurami.",
                    "suggested_actions": [
                        {"action": "Kontynuuj rozmowę", "reasoning": "Zbierz więcej informacji"}
                    ],
                    "quick_response": "Rozumiem. Czy mógłby Pan powiedzieć więcej?",
                    "is_fallback": True,
                    "error_reason": str(ai_error)
                }

            # Utwórz interakcję
            db_interaction = Interaction(**interaction_dict)
            db.add(db_interaction)
            await db.flush()
            await db.refresh(db_interaction)
            
            # ULTRA MÓZG v4.0: Background task USUNIĘTY! 
            # Psychology jest teraz przetwarzana synchronicznie PRZED AI response
            logger.info(f"🧠⚡ [ULTRA MÓZG] Dwuetapowa analiza ukończona! Synteza + Strategia dla sesji {session_id}")
            
            return db_interaction
            
        except Exception as e:
            raise ValueError(f"Błąd podczas tworzenia interakcji: {e}")

    # STARE FUNKCJE USUNIĘTE - Zastąpione przez SessionPsychologyEngine v3.0
    # Wszystkie per-interaction psychology functions zostały przeniesione na poziom sesji

    async def update_interaction(self, db: AsyncSession, interaction_id: int, update_data: dict):
        """
        Aktualizuje dane interakcji.
        """
        query = select(Interaction).where(Interaction.id == interaction_id)
        result = await db.execute(query)
        interaction = result.scalar_one_or_none()
        
        if not interaction:
            return None
        
        for field, value in update_data.items():
            if hasattr(interaction, field):
                setattr(interaction, field, value)
        
        await db.flush()
        await db.refresh(interaction)
        return interaction

    async def delete_interaction(self, db: AsyncSession, interaction_id: int):
        """
        Usuwa interakcję.
        """
        query = select(Interaction).where(Interaction.id == interaction_id)
        result = await db.execute(query)
        interaction = result.scalar_one_or_none()
        
        if not interaction:
            return False
        
        await db.delete(interaction)
        await db.flush()
        return True