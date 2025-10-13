"""
SessionOrchestratorService - Orkiestrator analizy psychologicznej sesji

CREATED: 2025-10-13 - Missing critical service file
ROLE: Koordynuje analizę psychometryczną na poziomie sesji

Funkcjonalności:
- Orchestruje pełną analizę psychology dla sesji
- Obsługuje clarifying questions workflow
- Integruje się z AIService i bazą danych
- Zarządza stanem psychology profile w sesji
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.domain import Session as SessionModel, Interaction as InteractionModel
from app.services.ai_service import get_ai_service

logger = logging.getLogger(__name__)


class SessionOrchestratorService:
    """
    Orkiestrator analizy psychologicznej na poziomie sesji.
    
    Odpowiedzialny za:
    - Koordynację analizy psychometrycznej (Big Five, DISC, Schwartz)
    - Generowanie i zarządzanie clarifying questions
    - Update profilu psychologicznego sesji
    - Integrację między AI services i database
    """
    
    def __init__(self):
        """Inicjalizacja orchestratora"""
        logger.info("✅ SessionOrchestratorService initialized")
    
    async def orchestrate_psychology_analysis(
        self,
        session_id: int,
        db: AsyncSession,
        ai_service: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Orchestruje pełną analizę psychometryczną dla sesji
        
        Pipeline:
        1. Pobiera wszystkie interakcje z sesji
        2. Wywołuje AI do analizy psychometrycznej
        3. Wywołuje AI do holistycznej syntezy (DNA Klienta)
        4. Generuje sales indicators
        5. Aktualizuje profil sesji w bazie danych
        
        Args:
            session_id: ID sesji do analizy
            db: Sesja bazy danych
            ai_service: Instancja AIService (opcjonalna, użyje global jeśli None)
            
        Returns:
            Dict: Pełny profil psychometryczny sesji
            
        Raises:
            ValueError: Jeśli sesja nie istnieje
        """
        try:
            logger.info(f"🧠 [ORCHESTRATOR] Starting psychology analysis for session {session_id}")
            
            # 1. Pobierz sesję
            result = await db.execute(
                select(SessionModel).where(SessionModel.id == session_id)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # 2. Pobierz wszystkie interakcje dla sesji
            interactions_result = await db.execute(
                select(InteractionModel)
                .where(InteractionModel.session_id == session_id)
                .order_by(InteractionModel.timestamp.asc())
            )
            interactions = interactions_result.scalars().all()
            
            if not interactions:
                logger.warning(f"⚠️ No interactions found for session {session_id}")
                return self._create_empty_psychology_profile()
            
            # 3. Przygotuj conversation history dla AI
            conversation_history = []
            for interaction in interactions:
                if interaction.user_input:
                    conversation_history.append({
                        'role': 'user',
                        'content': interaction.user_input,
                        'timestamp': interaction.timestamp.isoformat() if interaction.timestamp else None
                    })
            
            # 4. Użyj AI service do analizy
            if ai_service is None:
                ai_service = get_ai_service()
            
            if not ai_service:
                logger.error("❌ AI Service not available")
                return self._create_empty_psychology_profile()
            
            # 5. Wywołaj analizę psychometryczną
            logger.info(f"🧠 Calling AI for psychometric analysis (session {session_id})")
            
            raw_psychology_profile = await ai_service.generate_psychometric_analysis(
                conversation_history=conversation_history,
                additional_context={
                    'session_id': session_id,
                    'interaction_count': len(interactions)
                }
            )
            
            # 6. Wywołaj holistyczną syntezę (DNA Klienta)
            logger.info(f"🧬 Calling AI for holistic synthesis (session {session_id})")
            
            holistic_profile = await ai_service._run_holistic_synthesis(
                raw_psychology_profile=raw_psychology_profile,
                additional_context={
                    'session_id': session_id,
                    'conversation_history': conversation_history[-5:]  # Ostatnie 5 interakcji
                }
            )
            
            # 7. Wygeneruj sales indicators
            logger.info(f"📊 Generating sales indicators (session {session_id})")
            
            sales_indicators = await ai_service._run_sales_indicators_generation(
                holistic_profile=holistic_profile,
                session_context={
                    'session_id': session_id,
                    'interaction_count': len(interactions)
                }
            )
            
            # 8. Skomponuj pełny profil
            complete_profile = {
                'session_id': session_id,
                'cumulative_psychology': raw_psychology_profile,
                'holistic_profile': holistic_profile,
                'sales_indicators': sales_indicators,
                'customer_archetype': holistic_profile.get('customer_archetype', {}),
                'psychology_confidence': self._calculate_confidence(raw_psychology_profile),
                'analysis_metadata': {
                    'interaction_count': len(interactions),
                    'last_updated': interactions[-1].timestamp.isoformat() if interactions else None
                }
            }
            
            # 9. Aktualizuj sesję w bazie danych
            await self._update_session_psychology(db, session_id, complete_profile)
            
            logger.info(f"✅ Psychology analysis completed for session {session_id}")
            
            return complete_profile
            
        except Exception as e:
            logger.error(f"❌ Error in psychology orchestration for session {session_id}: {e}", exc_info=True)
            return self._create_error_psychology_profile(str(e))
    
    async def answer_clarifying_question(
        self,
        session_id: int,
        question_id: str,
        answer: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Obsługuje odpowiedź na pytanie pomocnicze (clarifying question)
        
        Pipeline:
        1. Waliduje pytanie
        2. Zapisuje odpowiedź
        3. Uruchamia ponowną analizę psychometryczną
        4. Aktualizuje profil sesji
        
        Args:
            session_id: ID sesji
            question_id: ID pytania pomocniczego
            answer: Odpowiedź użytkownika
            db: Sesja bazy danych
            
        Returns:
            Dict: Zaktualizowany profil psychometryczny
        """
        try:
            logger.info(f"📋 Processing clarifying question {question_id} for session {session_id}")
            
            # 1. Pobierz sesję
            result = await db.execute(
                select(SessionModel).where(SessionModel.id == session_id)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # 2. Zapisz odpowiedź w session context
            # (możesz rozszerzyć to o dedykowaną tabelę dla clarifying questions)
            clarifying_answers = getattr(session, 'clarifying_answers', None) or {}
            clarifying_answers[question_id] = {
                'answer': answer,
                'timestamp': str(logger.handlers[0].formatter.formatTime(logger.makeRecord(
                    logger.name, logging.INFO, "", 0, "", (), None
                ))) if logger.handlers else None
            }
            
            # 3. Aktualizuj sesję
            await db.execute(
                update(SessionModel)
                .where(SessionModel.id == session_id)
                .values(additional_context=clarifying_answers)
            )
            await db.commit()
            
            # 4. Uruchom ponowną analizę psychometryczną
            logger.info(f"🔄 Re-running psychology analysis after clarifying question")
            
            updated_profile = await self.orchestrate_psychology_analysis(
                session_id=session_id,
                db=db
            )
            
            logger.info(f"✅ Clarifying question processed for session {session_id}")
            
            return updated_profile
            
        except Exception as e:
            logger.error(f"❌ Error processing clarifying question: {e}")
            raise
    
    async def _update_session_psychology(
        self,
        db: AsyncSession,
        session_id: int,
        psychology_profile: Dict[str, Any]
    ) -> None:
        """
        Aktualizuje profil psychologiczny w sesji
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            psychology_profile: Profil psychologiczny do zapisania
        """
        try:
            # Update session with psychology data
            await db.execute(
                update(SessionModel)
                .where(SessionModel.id == session_id)
                .values(
                    cumulative_psychology=psychology_profile.get('cumulative_psychology'),
                    holistic_profile=psychology_profile.get('holistic_profile'),
                    customer_archetype=psychology_profile.get('customer_archetype'),
                    psychology_confidence=psychology_profile.get('psychology_confidence', 0)
                )
            )
            await db.commit()
            
            logger.info(f"✅ Session {session_id} psychology profile updated in database")
            
        except Exception as e:
            logger.error(f"❌ Error updating session psychology: {e}")
            await db.rollback()
            raise
    
    def _calculate_confidence(self, psychology_profile: Dict[str, Any]) -> int:
        """
        Oblicza poziom pewności analizy psychologicznej
        
        Args:
            psychology_profile: Profil psychologiczny
            
        Returns:
            int: Confidence score (0-100)
        """
        try:
            # Podstawowy algorytm - można ulepszyć
            confidence_factors = []
            
            # Sprawdź kompletność Big Five
            big_five = psychology_profile.get('big_five', {})
            if big_five and len(big_five) >= 5:
                confidence_factors.append(1.0)
            
            # Sprawdź kompletność DISC
            disc = psychology_profile.get('disc', {})
            if disc and len(disc) >= 4:
                confidence_factors.append(1.0)
            
            # Sprawdź wartości Schwartza
            schwartz = psychology_profile.get('schwartz_values', [])
            if schwartz and len(schwartz) >= 3:
                confidence_factors.append(1.0)
            
            # Oblicz średnią
            if confidence_factors:
                avg = sum(confidence_factors) / len(confidence_factors)
                return int(avg * 100)
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Error calculating confidence: {e}")
            return 0
    
    def _create_empty_psychology_profile(self) -> Dict[str, Any]:
        """Tworzy pusty profil psychologiczny (fallback)"""
        return {
            'cumulative_psychology': {},
            'holistic_profile': {},
            'sales_indicators': {},
            'customer_archetype': {},
            'psychology_confidence': 0,
            'analysis_metadata': {
                'interaction_count': 0,
                'status': 'empty'
            }
        }
    
    def _create_error_psychology_profile(self, error: str) -> Dict[str, Any]:
        """Tworzy profil psychologiczny z błędem (fallback)"""
        return {
            'cumulative_psychology': {},
            'holistic_profile': {},
            'sales_indicators': {},
            'customer_archetype': {},
            'psychology_confidence': 0,
            'analysis_metadata': {
                'interaction_count': 0,
                'status': 'error',
                'error': error
            },
            'error': error
        }


# Global singleton instance
session_orchestrator_service = SessionOrchestratorService()
