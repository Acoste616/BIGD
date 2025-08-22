from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.domain import Interaction, Session as SessionModel, Client
from app.schemas.interaction import InteractionCreateNested
from app.services.ai_service import generate_sales_analysis

class InteractionRepository:
    """
    Repozytorium do zarządzania operacjami na danych interakcji.
    """
    async def get_interaction(self, db: AsyncSession, interaction_id: int):
        query = select(Interaction).where(Interaction.id == interaction_id)
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
            
            try:
                # Spróbuj wygenerować analizę AI
                if client:
                    client_profile = {
                        "alias": client.alias,
                        "archetype": client.archetype,
                        "notes": client.notes
                    }
                    
                    # Historia sesji (pusta na razie)
                    session_history = []
                    session_context = {"session_type": "consultation"}
                    
                    ai_response = await generate_sales_analysis(
                        user_input=interaction_data.user_input,
                        client_profile=client_profile,
                        session_history=session_history,
                        session_context=session_context
                    )
                    
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
            return db_interaction
            
        except Exception as e:
            raise ValueError(f"Błąd podczas tworzenia interakcji: {e}")

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