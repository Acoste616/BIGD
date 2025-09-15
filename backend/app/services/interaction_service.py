"""
InteractionService - Warstwa biznesowa dla operacji na interakcjach

REFAKTORYZACJA: Przejmuje całą logikę AI (150+ linii) z InteractionRepository
- Psychology analysis
- Holistic synthesis (DNA Klienta)  
- Sales indicators generation
- AI strategy generation
- Parallel processing optimization

Repository zostaje czysty - tylko operacje DB
"""
import logging
import asyncio
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.models.domain import Session as SessionModel, Client
from app.schemas.interaction import InteractionCreateNested
from app.repositories.interaction_repository import InteractionRepository
from app.services.session_psychology_service import session_psychology_engine

# Import nowych wyspecjalizowanych serwisów AI
from app.services.ai import (
    get_psychology_service,
    get_sales_strategy_service,
    get_holistic_synthesis_service,
    check_ai_services_health
)
from app.services.ai.semantic_validator_service import SemanticValidatorService
from app.services.redis_cache_service import RedisCacheService

# Import ConnectionManager from stream module for WebSocket notifications
from app.routers.stream import connection_manager

# Fallback - import starego ai_service jeśli potrzebny
from app.services.ai_service import generate_sales_analysis, ai_service

logger = logging.getLogger(__name__)


class InteractionService:
    """
    Warstwa biznesowa dla interakcji - orchestruje wszystkie operacje AI i DB
    
    Funkcjonalności:
    - Tworzenie interakcji z pełną analizą AI
    - Psychology analysis z session_psychology_engine
    - Holistic synthesis (DNA Klienta) 
    - Sales indicators generation
    - Parallel processing dla performance
    - Clean separation od Repository layer
    """
    
    def __init__(self):
        """Inicjalizacja serwisu interakcji"""
        # Repository dla operacji DB
        self.interaction_repo = InteractionRepository()
        
        # Serwisy AI będą inicjalizowane z sesją DB gdy będą potrzebne
        self.psychology_service = None
        self.sales_strategy_service = None
        self.holistic_service = None
        
        # Serwis walidacji semantycznej (bezstanowy)
        self.semantic_validator = SemanticValidatorService()
        
        # Serwis cache'owania Redis
        self.cache_service = RedisCacheService()
        
        logger.info("✅ InteractionService initialized with semantic validator + Redis cache")
    
    def _initialize_ai_services(self, db_session: AsyncSession):
        """Inicjalizuje serwisy AI z sesją bazy danych"""
        if not self.psychology_service:
            self.psychology_service = get_psychology_service(db_session)
        if not self.sales_strategy_service:
            self.sales_strategy_service = get_sales_strategy_service(db_session)
        if not self.holistic_service:
            self.holistic_service = get_holistic_synthesis_service(db_session)
    
    # === MAIN BUSINESS METHODS ===
    
    async def create_interaction_with_ai_analysis(
        self,
        db: AsyncSession,
        session_id: int,
        interaction_data: InteractionCreateNested
    ):
        """
        MAIN METHOD: Tworzy interakcję z pełną analizą AI
        
        Przejmuje całą logikę (150+ linii) z InteractionRepository.create_interaction
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            interaction_data: Dane interakcji
            
        Returns:
            Dict: Utworzona interakcja z AI analysis
        """
        try:
            logger.info(f"🚀 [INTERACTION SERVICE] Tworzenie interakcji dla sesji {session_id}")
            
            # KROK 0: Inicjalizuj serwisy AI z sesją DB
            self._initialize_ai_services(db)
            
            # KROK 1: Pobierz kontekst (session + client)
            session_context = await self._get_session_context(db, session_id)
            if not session_context:
                raise ValueError(f"Sesja o ID {session_id} nie istnieje")
            
            # KROK 2: Przygotuj dane interakcji (bez AI jeszcze)
            base_interaction_data = self._prepare_base_interaction_data(
                session_id, interaction_data
            )
            
            # KROK 3: Sprawdź typ interakcji
            is_clarification = self._is_clarification_interaction(interaction_data)
            parent_id = getattr(interaction_data, 'parent_interaction_id', None)
            
            logger.info(f"🔍 [INTERACTION SERVICE] Type: {'clarification' if is_clarification else 'standard'}, Parent: {parent_id}")
            
            # KROK 4: GŁÓWNA LOGIKA AI - Ultra Mózg Pipeline
            ai_response = await self._run_ultra_brain_pipeline(
                db=db,
                session_id=session_id,
                session_context=session_context,
                interaction_data=interaction_data,
                is_clarification=is_clarification,
                parent_id=parent_id
            )
            
            # KROK 5: Dodaj AI response do danych interakcji
            base_interaction_data["ai_response_json"] = ai_response
            
            # KROK 6: Zapisz interakcję przez Repository (czyste DB operations)
            # TYMCZASOWO: Używamy starej metody, później stworzymy czystą
            from app.models.domain import Interaction
            db_interaction = Interaction(**base_interaction_data)
            db.add(db_interaction)
            await db.flush()
            await db.refresh(db_interaction)
            created_interaction = db_interaction
            
            # KROK 7: Inwalidacja cache'a - nowa interakcja wymaga przeliczenia profili
            cache_pattern = f"*session:{session_id}*"
            invalidated_keys = await self.cache_service.invalidate_pattern(cache_pattern)
            if invalidated_keys > 0:
                logger.info(f"🗑️ [CACHE INVALIDATION] Unieważniono {invalidated_keys} kluczy cache dla sesji {session_id}")
            
            # KROK 8: Notify WebSocket clients about the new analysis
            await self._notify_websocket_clients(session_id, created_interaction)
            
            logger.info(f"✅ [INTERACTION SERVICE] Interakcja {created_interaction.id} utworzona z AI analysis")
            return created_interaction
            
        except Exception as e:
            logger.error(f"❌ [INTERACTION SERVICE] Błąd podczas tworzenia interakcji: {e}")
            # Fallback - utwórz interakcję bez AI
            return await self._create_fallback_interaction(db, session_id, interaction_data, str(e))
    
    async def get_interaction(self, db: AsyncSession, interaction_id: int):
        """Pobiera interakcję - deleguje do Repository"""
        return await self.interaction_repo.get_interaction(db, interaction_id)
    
    async def get_session_interactions(
        self, 
        db: AsyncSession, 
        session_id: int, 
        skip: int = 0, 
        limit: int = 100
    ):
        """Pobiera interakcje sesji - deleguje do Repository"""
        return await self.interaction_repo.get_session_interactions(db, session_id, skip, limit)
    
    async def update_interaction(self, db: AsyncSession, interaction_id: int, update_data: dict):
        """Aktualizuje interakcję - deleguje do Repository"""
        return await self.interaction_repo.update_interaction(db, interaction_id, update_data)
    
    async def delete_interaction(self, db: AsyncSession, interaction_id: int):
        """Usuwa interakcję - deleguje do Repository"""
        return await self.interaction_repo.delete_interaction(db, interaction_id)
    
    # === ULTRA BRAIN PIPELINE (CORE AI LOGIC) ===
    
    async def _run_ultra_brain_pipeline(
        self,
        db: AsyncSession,
        session_id: int,
        session_context: Dict[str, Any],
        interaction_data: InteractionCreateNested,
        is_clarification: bool = False,
        parent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        ULTRA MÓZG v4.0 Pipeline - główna logika AI
        
        Przeprowadza pełny cykl:
        1. Psychology Analysis
        2. Holistic Synthesis (DNA Klienta)
        3. Sales Indicators Generation  
        4. Sales Strategy Generation
        5. Parallel Processing Optimization
        """
        try:
            logger.info(f"🧠⚡ [ULTRA BRAIN PIPELINE] Rozpoczynam dla sesji {session_id}")
            
            client = session_context['client']
            session = session_context['session']
            
            if not client:
                logger.warning("⚠️ [ULTRA BRAIN] Brak klienta - używam fallback")
                return self._create_ai_fallback()
            
            # Przygotuj profil klienta
            client_profile = {
                "alias": client.alias,
                "archetype": client.archetype,
                "notes": client.notes
            }
            
            # Historia sesji (placeholder - można rozbudować)
            session_history = []
            session_context_data = {"session_type": "consultation"}
            
            # === KROK 1: PSYCHOLOGY ANALYSIS ===
            logger.info(f"🧠 [STEP 1] Psychology Analysis dla sesji {session_id}")
            updated_psychology_profile = await session_psychology_engine.update_and_get_psychology(
                session_id=session_id,
                db=db,
                ai_service=ai_service  # Używamy starego ai_service jako fallback
            )
            psychology_confidence = updated_psychology_profile.get('psychology_confidence', 0)
            logger.info(f"✅ [STEP 1] Psychology gotowe! Confidence: {psychology_confidence}%")
            
            # === KROK 1.5: SEMANTIC VALIDATION - PSYCHOLOGY PROFILE ===
            logger.info(f"🔍 [STEP 1.5] Semantic Validation - Psychology Profile")
            is_psychology_valid, psychology_error = self.semantic_validator.validate_psychology_profile(updated_psychology_profile)
            
            if not is_psychology_valid:
                logger.warning(f"⚠️ [STEP 1.5] Psychology validation warning: {psychology_error}")
                # Dla profilu psychometrycznego używamy ostrzeżenia zamiast błędu krytycznego
                # Pozwalamy kontynuować, ale logujemy problem
            else:
                logger.info(f"✅ [STEP 1.5] Psychology validation passed!")
            
            # === KROK 2: HOLISTIC SYNTHESIS (DNA Klienta) ===
            logger.info(f"🧬 [STEP 2] Holistic Synthesis - DNA Klienta")
            holistic_profile = await self.holistic_service.run_holistic_synthesis(
                raw_psychology_profile=updated_psychology_profile,
                additional_context={
                    'client_profile': client_profile,
                    'session_context': session_context_data
                }
            )
            main_drive = holistic_profile.get('main_drive', 'Unknown')
            logger.info(f"✅ [STEP 2] DNA Klienta gotowe! Drive: {main_drive}")
            
            # === KROK 2.5: SEMANTIC VALIDATION ===
            logger.info(f"🔍 [STEP 2.5] Semantic Validation - DNA Klienta")
            is_valid, error_message = self.semantic_validator.validate_holistic_synthesis(holistic_profile)
            
            if not is_valid:
                # Jeśli walidacja zawiedzie, logujemy błąd i przerywamy operację,
                # aby nie zapisać "halucynacji" do bazy.
                error_msg = f"AI response failed semantic validation: {error_message}"
                logger.error(f"❌ [STEP 2.5] Semantic validation failed: {error_message}")
                
                # W przyszłości można tu zaimplementować ponowienie zapytania do AI
                # Na razie rzucamy wyjątek, aby zatrzymać dalsze przetwarzanie
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=500,
                    detail=error_msg
                )
            
            logger.info(f"✅ [STEP 2.5] Semantic validation passed!")
            
            # === KROK 3: PARALLEL PROCESSING - DB Save + Sales Indicators ===
            logger.info(f"🔬 [STEP 3] Parallel: DB Save + Sales Indicators")
            
            # Task 1: Zapisz holistyczny profil do sesji
            db_save_task = db.execute(
                update(SessionModel)
                .where(SessionModel.id == session_id)
                .values(holistic_psychometric_profile=holistic_profile)
            )
            
            # Task 2: Wygeneruj wskaźniki sprzedażowe
            indicators_task = self.holistic_service.run_sales_indicators_generation(
                holistic_profile=holistic_profile,
                session_context=session_context_data
            )
            
            # Wykonaj równolegle
            try:
                db_result, sales_indicators = await asyncio.gather(
                    db_save_task,
                    indicators_task,
                    return_exceptions=True
                )
                
                # Sprawdź wyniki
                if isinstance(db_result, Exception):
                    logger.error(f"❌ [STEP 3] DB save error: {db_result}")
                else:
                    logger.info(f"💾 [STEP 3] Holistic profile saved!")
                
                if isinstance(sales_indicators, Exception):
                    logger.error(f"❌ [STEP 3] Sales indicators error: {sales_indicators}")
                    sales_indicators = self.holistic_service._create_indicators_fallback()
                
                # Po naprawie sales_indicators zawsze jest dict, ale sprawdźmy typ żeby uspokoić linter
                if isinstance(sales_indicators, dict):
                    temperature = sales_indicators.get('purchase_temperature', {}).get('value', 0)
                    logger.info(f"✅ [STEP 3] Sales indicators ready! Temperature: {temperature}%")
                else:
                    logger.warning("⚠️ [STEP 3] Sales indicators type issue - using fallback")
                    sales_indicators = self.holistic_service._create_indicators_fallback()
                    
            except Exception as e:
                logger.error(f"❌ [STEP 3] Parallel processing error: {e}")
                sales_indicators = self.holistic_service._create_indicators_fallback()
            
            # === KROK 4: SALES STRATEGY GENERATION ===
            logger.info(f"🎯 [STEP 4] Sales Strategy Generation")
            
            if is_clarification and parent_id:
                # Ścieżka clarification
                logger.info(f"⚡ [STEP 4] Clarification strategy for parent={parent_id}")
                ai_response = await self.sales_strategy_service.generate_sales_strategy(
                    user_input=f"Aktualizacja: {interaction_data.user_input}",
                    client_profile=client_profile,
                    session_history=session_history,
                    psychology_profile=updated_psychology_profile,
                    holistic_profile=holistic_profile,
                    customer_archetype=updated_psychology_profile.get('customer_archetype')
                )
            else:
                # Ścieżka standardowa
                logger.info(f"⚡ [STEP 4] Standard strategy generation")
                ai_response = await self.sales_strategy_service.generate_sales_strategy(
                    user_input=interaction_data.user_input,
                    client_profile=client_profile,
                    session_history=session_history,
                    psychology_profile=updated_psychology_profile,
                    holistic_profile=holistic_profile,
                    customer_archetype=updated_psychology_profile.get('customer_archetype')
                )
            
            # Dołącz sales indicators do odpowiedzi
            if sales_indicators and not ai_response.get('sales_indicators'):
                ai_response['sales_indicators'] = sales_indicators
                logger.info(f"📊 [STEP 4] Sales indicators attached to AI response")
            
            logger.info(f"✅ [ULTRA BRAIN PIPELINE] Completed! Full AI analysis ready")
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ [ULTRA BRAIN PIPELINE] Pipeline failed: {e}")
            return self._create_ai_fallback(str(e))
    
    # === HELPER METHODS ===
    
    async def _get_session_context(self, db: AsyncSession, session_id: int) -> Optional[Dict[str, Any]]:
        """Pobiera kontekst sesji (session + client)"""
        try:
            # Pobierz sesję
            session_query = select(SessionModel).where(SessionModel.id == session_id)
            session_result = await db.execute(session_query)
            session = session_result.scalar_one_or_none()
            
            if not session:
                return None
            
            # Pobierz klienta
            client_query = select(Client).where(Client.id == session.client_id)
            client_result = await db.execute(client_query)
            client = client_result.scalar_one_or_none()
            
            return {
                'session': session,
                'client': client,
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting session context: {e}")
            return None
    
    def _prepare_base_interaction_data(
        self, 
        session_id: int, 
        interaction_data: InteractionCreateNested
    ) -> Dict[str, Any]:
        """Przygotowuje podstawowe dane interakcji (bez AI)"""
        return {
            "session_id": session_id,
            "user_input": interaction_data.user_input,
            "ai_response_json": {},  # Wypełniane przez AI pipeline
            "feedback_data": []
        }
    
    def _is_clarification_interaction(self, interaction_data: InteractionCreateNested) -> bool:
        """Sprawdza czy to clarification interaction"""
        return bool(
            interaction_data.additional_context or 
            getattr(interaction_data, 'clarifying_answer', None)
        )
    
    async def _notify_websocket_clients(self, session_id: int, interaction_data: Dict[str, Any]):
        """Notify WebSocket clients about new AI analysis"""
        try:
            message = {
                "event": "analysis_complete",
                "session_id": session_id,
                "data": {
                    "interaction_id": interaction_data.get("id"),
                    "ai_response": interaction_data.get("ai_response_json", {})
                },
                "timestamp": datetime.now().isoformat()
            }
            await connection_manager.send_personal_message(message, session_id)
            logger.info(f"📤 WebSocket notification sent for session {session_id}")
        except Exception as e:
            logger.error(f"❌ Error sending WebSocket notification for session {session_id}: {e}")
    
    def _create_ai_fallback(self, error_message: str = "") -> Dict[str, Any]:
        """Tworzy fallback AI response gdy pipeline fails"""
        return {
            "main_analysis": "AI niedostępny. Postępuj zgodnie z procedurami.",
            "suggested_actions": [
                {"action": "Kontynuuj rozmowę", "reasoning": "Zbierz więcej informacji"}
            ],
            "quick_response": "Rozumiem. Czy mógłby Pan powiedzieć więcej?",
            "is_fallback": True,
            "error_reason": error_message,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _create_fallback_interaction(
        self,
        db: AsyncSession,
        session_id: int,
        interaction_data: InteractionCreateNested,
        error_message: str
    ):
        """Tworzy fallback interakcję gdy AI pipeline całkowicie fails"""
        try:
            base_data = self._prepare_base_interaction_data(session_id, interaction_data)
            base_data["ai_response_json"] = self._create_ai_fallback(error_message)
            
            # TYMCZASOWO: Direct DB operation, później przeniesiemy do Repository
            from app.models.domain import Interaction
            db_interaction = Interaction(**base_data)
            db.add(db_interaction)
            await db.flush()
            await db.refresh(db_interaction)
            # Notify WebSocket clients even for fallback interactions
            await self._notify_websocket_clients(session_id, db_interaction.__dict__)
            return db_interaction
        except Exception as e:
            logger.error(f"❌ Even fallback interaction failed: {e}")
            raise ValueError(f"Critical error creating interaction: {e}")
    
    # === SERVICE HEALTH & STATUS ===
    
    def get_service_status(self) -> Dict[str, Any]:
        """Zwraca status serwisu interakcji i połączonych AI services"""
        ai_health = check_ai_services_health()
        
        return {
            'interaction_service_status': 'active',
            'ai_services_health': ai_health,
            'psychology_engine_available': session_psychology_engine is not None,
            'repository_available': self.interaction_repo is not None,
            'timestamp': datetime.now().isoformat()
        }


# === SINGLETON INSTANCE ===

# Globalna instancja serwisu
_interaction_service_instance: Optional[InteractionService] = None


def get_interaction_service() -> InteractionService:
    """
    Zwraca singleton instancję InteractionService
    
    Returns:
        InteractionService: Instancja serwisu
    """
    global _interaction_service_instance
    
    if _interaction_service_instance is None:
        _interaction_service_instance = InteractionService()
        logger.info("✅ InteractionService singleton created")
    
    return _interaction_service_instance


# === HEALTH CHECK ===

def check_interaction_service_health() -> Dict[str, Any]:
    """
    Sprawdza stan zdrowia InteractionService
    
    Returns:
        Dict: Status healthcheck
    """
    try:
        service = get_interaction_service()
        return service.get_service_status()
    except Exception as e:
        return {
            'interaction_service_status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }