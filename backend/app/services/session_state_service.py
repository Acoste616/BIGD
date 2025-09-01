"""
SessionStateService v1.0 - Session State Management and Database Operations
Extracted from SessionOrchestratorService monolith - Phase 2D

Single Responsibility: Session state management and database I/O operations
- All database communication for session-related operations
- Session data aggregation and context management
- Isolation of I/O logic from business logic
- Clean interface for session state operations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.domain import Session, Interaction, Client
from app.repositories.session_repository import SessionRepository
from app.repositories.interaction_repository import InteractionRepository

logger = logging.getLogger(__name__)

class SessionStateService:
    """
    🗃️ Session State Management Service
    
    Responsible for:
    1. All database operations related to sessions
    2. Session data aggregation and context preparation
    3. Session history building and formatting
    4. Psychology data persistence
    5. Interactive questions management
    6. Session analytics and metadata
    
    This service isolates all I/O operations from business logic,
    making the psychology engine a pure orchestrator.
    """
    
    def __init__(self, session_repository: SessionRepository = None, interaction_repository: InteractionRepository = None):
        """
        Initialize SessionStateService with repository dependencies
        
        Args:
            session_repository: Repository for session database operations
            interaction_repository: Repository for interaction database operations
        """
        self._session_repo = session_repository or SessionRepository()
        self._interaction_repo = interaction_repository or InteractionRepository()
        
        logger.info("✅ [SESSION STATE] SessionStateService initialized with repository dependencies")
    
    # === PUBLIC INTERFACE ===
    
    async def get_session_context(self, session_id: int, db: AsyncSession) -> Dict[str, Any]:
        """
        🔍 Main interface: Get complete session context for analysis
        
        Args:
            session_id: ID of the session to analyze
            db: Database session
            
        Returns:
            dict: Complete session context including history, profile, and metadata
        """
        try:
            logger.info(f"📋 [SESSION STATE] Building context for session {session_id}")
            
            # Get session with interactions
            session = await self._get_session_with_interactions(db, session_id)
            
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Build comprehensive context
            context = {
                'session_id': session_id,
                'conversation_history': self._build_conversation_history(session.interactions),
                'interaction_count': len(session.interactions) if session.interactions else 0,
                'current_psychology_profile': dict(session.cumulative_psychology or {}),
                'current_confidence': int(session.psychology_confidence or 0),
                'active_questions': session.active_clarifying_questions or [],
                'customer_archetype': session.customer_archetype,
                'sales_indicators': session.sales_indicators,
                'session_metadata': {
                    'start_timestamp': session.start_timestamp,
                    'psychology_updated_at': session.psychology_updated_at,
                    'is_active': session.is_active,
                    'status': session.status
                }
            }
            
            logger.info(f"✅ [SESSION STATE] Context built: {context['interaction_count']} interactions, confidence: {context['current_confidence']}%")
            return context
            
        except Exception as e:
            logger.error(f"❌ [SESSION STATE] Error building session context: {e}")
            raise
    
    async def update_session_with_analysis(self, session_id: int, analysis_data: Dict[str, Any], db: AsyncSession) -> None:
        """
        💾 Main interface: Update session with complete analysis results
        
        Args:
            session_id: ID of the session to update
            analysis_data: Complete analysis results to save
            db: Database session
        """
        try:
            logger.info(f"💾 [SESSION STATE] Updating session {session_id} with analysis data")
            
            # Prepare update data
            update_data = {
                'cumulative_psychology': analysis_data.get('cumulative_psychology'),
                'psychology_confidence': analysis_data.get('psychology_confidence', 0),
                'active_clarifying_questions': analysis_data.get('active_clarifying_questions', []),
                'customer_archetype': analysis_data.get('customer_archetype'),
                'psychology_updated_at': datetime.now(),
                'sales_indicators': analysis_data.get('sales_indicators', {})
            }
            
            # Execute update
            await db.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(**update_data)
            )
            
            logger.info(f"✅ [SESSION STATE] Session {session_id} updated successfully")
            
        except Exception as e:
            logger.error(f"❌ [SESSION STATE] Error updating session {session_id}: {e}")
            raise
    
    async def update_clarifying_questions(self, session_id: int, question_id: str, answer: str, db: AsyncSession) -> Dict[str, Any]:
        """
        ❓ Handle clarifying question responses and update session
        
        Args:
            session_id: ID of the session
            question_id: ID of the answered question
            answer: The answer provided
            db: Database session
            
        Returns:
            dict: Updated session context
        """
        try:
            logger.info(f"❓ [SESSION STATE] Processing clarifying question {question_id} for session {session_id}")
            
            # Get current session
            session = await self._get_session_with_interactions(db, session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Process question answer
            active_questions = session.active_clarifying_questions or []
            answered_question = None
            remaining_questions = []
            
            for q in active_questions:
                if q.get('id') == question_id:
                    answered_question = q
                else:
                    remaining_questions.append(q)
            
            if not answered_question:
                raise ValueError(f"Question {question_id} not found in active questions")
            
            # Add observation to psychology context
            current_profile = dict(session.cumulative_psychology or {})
            if 'observations' not in current_profile:
                current_profile['observations'] = []
            
            current_profile['observations'].append({
                'question': answered_question.get('question', ''),
                'answer': answer,
                'timestamp': datetime.now().isoformat(),
                'psychological_target': answered_question.get('psychological_target', 'general')
            })
            
            # Update session
            await db.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(
                    active_clarifying_questions=remaining_questions,
                    cumulative_psychology=current_profile
                )
            )
            
            logger.info(f"✅ [SESSION STATE] Clarifying question processed, {len(remaining_questions)} questions remaining")
            
            # Return updated context
            return await self.get_session_context(session_id, db)
            
        except Exception as e:
            logger.error(f"❌ [SESSION STATE] Error processing clarifying question: {e}")
            raise
    
    async def get_session_analytics(self, session_id: int, db: AsyncSession) -> Dict[str, Any]:
        """
        📊 Get comprehensive session analytics and metrics
        
        Args:
            session_id: ID of the session
            db: Database session
            
        Returns:
            dict: Session analytics data
        """
        try:
            logger.info(f"📊 [SESSION STATE] Generating analytics for session {session_id}")
            
            session = await self._get_session_with_interactions(db, session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            interactions = session.interactions or []
            
            analytics = {
                'session_id': session_id,
                'interaction_count': len(interactions),
                'psychology_confidence': session.psychology_confidence or 0,
                'analysis_level': 'pełna' if len(interactions) >= 3 else 'wstępna',
                'archetype_data': session.customer_archetype,
                'sales_indicators': session.sales_indicators,
                'active_questions_count': len(session.active_clarifying_questions or []),
                'session_duration': self._calculate_session_duration(interactions),
                'last_interaction': interactions[-1].timestamp if interactions else None,
                'psychology_updated_at': session.psychology_updated_at,
                'session_status': session.status,
                'is_active': session.is_active
            }
            
            logger.info(f"✅ [SESSION STATE] Analytics generated for session {session_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ [SESSION STATE] Error generating analytics: {e}")
            raise
    
    # === PRIVATE HELPER METHODS ===
    
    async def _get_session_with_interactions(self, db: AsyncSession, session_id: int) -> Optional[Session]:
        """Get session with all related interactions loaded"""
        try:
            query = (
                select(Session)
                .options(selectinload(Session.interactions))
                .where(Session.id == session_id)
            )
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"❌ [SESSION STATE] Error fetching session {session_id}: {e}")
            raise
    
    def _build_conversation_history(self, interactions: List[Interaction]) -> str:
        """
        Build formatted conversation history for analysis
        
        Args:
            interactions: List of session interactions
            
        Returns:
            str: Formatted conversation history
        """
        if not interactions:
            return "BRAK HISTORII ROZMOWY"
        
        history_parts = ["=== HISTORIA CAŁEJ SESJI ==="]
        
        # Sort interactions by timestamp
        sorted_interactions = sorted(
            interactions, 
            key=lambda x: x.timestamp if hasattr(x.timestamp, 'timestamp') else x.timestamp
        )
        
        for i, interaction in enumerate(sorted_interactions):
            timestamp = interaction.timestamp.strftime("%H:%M:%S") if interaction.timestamp else "unknown"
            user_input = interaction.user_input or ""
            
            # Truncate very long inputs
            if len(user_input) > 500:
                user_input = user_input[:500] + "..."
            
            history_parts.append(f"[{i+1}] {timestamp} - Sprzedawca: \"{user_input}\"")
            
            # Add AI insights if available
            if interaction.ai_response_json:
                insights = interaction.ai_response_json.get('main_analysis', '')
                if insights:
                    history_parts.append(f"    AI Insight: {insights[:200]}...")
        
        history_parts.append("=== KONIEC HISTORII ===")
        return "\\n".join(history_parts)
    
    def _build_simple_history(self, interactions: List[Interaction]) -> str:
        """
        Build simple history format for lightweight operations
        
        Args:
            interactions: List of session interactions
            
        Returns:
            str: Simple formatted history
        """
        if not interactions:
            return "Brak poprzedniej historii rozmowy."
        
        history_parts = []
        for i, interaction in enumerate(interactions, 1):
            user_input = interaction.user_input or ""
            timestamp = interaction.timestamp.strftime("%H:%M") if interaction.timestamp else "unknown"
            
            # Truncate very long inputs
            if len(user_input) > 500:
                user_input = user_input[:500] + "..."
            
            history_parts.append(f"{i}. [{timestamp}] Sprzedawca: \"{user_input}\"")
        
        return "\\n".join(history_parts)
    
    def _calculate_session_duration(self, interactions: List[Interaction]) -> Optional[float]:
        """Calculate session duration in minutes"""
        if not interactions or len(interactions) < 2:
            return None
        
        try:
            first_interaction = min(interactions, key=lambda x: x.timestamp)
            last_interaction = max(interactions, key=lambda x: x.timestamp)
            
            duration = last_interaction.timestamp - first_interaction.timestamp
            return duration.total_seconds() / 60  # Convert to minutes
            
        except Exception as e:
            logger.warning(f"⚠️ [SESSION STATE] Could not calculate session duration: {e}")
            return None
    
    # === SERVICE STATUS ===
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            'service_name': 'SessionStateService',
            'status': 'active',
            'repositories': {
                'session_repository': self._session_repo is not None,
                'interaction_repository': self._interaction_repo is not None
            },
            'timestamp': datetime.now().isoformat()
        }

# Factory function for dependency injection
def create_session_state_service(
    session_repository: SessionRepository = None,
    interaction_repository: InteractionRepository = None
) -> SessionStateService:
    """
    🏭 Factory function for creating SessionStateService instances
    
    Args:
        session_repository: Optional session repository
        interaction_repository: Optional interaction repository
        
    Returns:
        SessionStateService: Configured service instance
    """
    return SessionStateService(session_repository, interaction_repository)

# Create default service instance
session_state_service = create_session_state_service()