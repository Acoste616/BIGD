"""
SessionOrchestratorService v4.0 - Pure Business Logic Orchestrator
ORCHESTRATOR for psychology analysis workflow

🎯 PHASE 2 COMPLETION - Final Transformation:
- Pure orchestrator with zero database dependencies
- Clean delegation to specialized services
- Business logic coordination only
- Crystal clear responsibilities

📊 Architecture Evolution - Phase 2 Complete:
- Phase 2A: Extracted PsychologyAnalysisService (419 lines)
- Phase 2B: Integrated services with delegation pattern
- Phase 2C: Extracted ArchetypeService (511 lines)
- Phase 2D: Extracted SessionStateService (375 lines)
- Phase 2E: Renamed to SessionOrchestratorService (clean naming)

🏗️ Service Orchestration Philosophy:
- Coordinates specialized services without direct I/O
- Transforms complex workflows into simple service calls
- Maintains business logic flow and error handling
- Zero knowledge of persistence details
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_service import ai_service_unified as ai_service
from .psychology_analysis_service import PsychologyAnalysisService
from .archetype_service import create_archetype_service
from .session_state_service import create_session_state_service

logger = logging.getLogger(__name__)

class SessionOrchestratorService:
    """
    🎼 CORE ORCHESTRATOR: Business Logic Coordination Service
    
    🎯 PURE ORCHESTRATION RESPONSIBILITIES:
    - Coordinates psychology analysis workflow
    - Delegates to specialized services
    - Transforms suggested_questions to interactive format
    - Manages business logic flow and error handling
    - Zero database knowledge or direct I/O operations
    
    🔧 Service Dependencies:
    1. PsychologyAnalysisService - Pure AI psychology analysis
    2. ArchetypeService - Customer archetype determination  
    3. SessionStateService - All database I/O operations
    """
    
    def __init__(self, psychology_analysis_service: PsychologyAnalysisService = None, archetype_service = None, session_state_service = None):
        """
        Initialize SessionOrchestratorService with dependency injection
        
        Args:
            psychology_analysis_service: Service for pure psychometric analysis
            archetype_service: Service for customer archetype detection
            session_state_service: Service for session state and database operations
        """
        # 🔧 PHASE 2: Complete service dependency injection
        self._psychology_analysis_service = psychology_analysis_service or PsychologyAnalysisService()
        self._archetype_service = archetype_service or create_archetype_service("tesla")
        self._session_state_service = session_state_service or create_session_state_service()
        
        logger.info("✅ [SESSION ORCHESTRATOR] Initialized with complete service dependency injection")
    
    # 🎼 ORCHESTRATION METHODS
    
    async def answer_clarifying_question(self, session_id: int, question_id: str, answer: str, db: AsyncSession):
        """
        🎯 Orchestrate clarifying question workflow
        
        Coordinates the complete flow when user answers clarifying questions
        """
        try:
            logger.info(f"🎯 [ORCHESTRATOR] Processing clarifying question {question_id}: {answer}")
            
            # Delegate question processing to SessionStateService
            updated_context = await self._session_state_service.update_clarifying_questions(
                session_id=session_id,
                question_id=question_id,
                answer=answer,
                db=db
            )
            
            # Trigger complete psychology analysis workflow
            updated_profile = await self.orchestrate_psychology_analysis(session_id, db, None)
            
            logger.info(f"✅ [ORCHESTRATOR] Question {question_id} workflow completed")
            return updated_profile
            
        except Exception as e:
            logger.error(f"❌ [ORCHESTRATOR] Error in clarifying question workflow: {e}")
            raise

    def _convert_to_interactive_questions(self, suggested_questions: List[Dict]) -> List[Dict]:
        """
        🔧 Business Logic: Transform AI suggestions to interactive UI format
        
        Converts raw AI suggestions into user-friendly interactive questions
        """
        interactive_questions = []
        
        for i, sq in enumerate(suggested_questions):
            question_text = sq.get('question', '')
            psychological_target = sq.get('psychological_target', 'general assessment')
            
            # Generate sensible A/B options based on question type
            if any(word in question_text.lower() for word in ['czy', 'jak często', 'jakie']):
                option_a = "Tak, potwierdza"
                option_b = "Nie, zaprzecza"
            elif 'jak' in question_text.lower():
                option_a = "Szybko, bezpośrednio" 
                option_b = "Powoli, szczegółowo"
            elif 'co' in question_text.lower():
                option_a = "Korzyści ogólne"
                option_b = "Szczegóły techniczne"
            else:
                option_a = "Potwierdza"
                option_b = "Zaprzecza"
            
            interactive_questions.append({
                "id": f"sq_{i+1}",
                "question": question_text,
                "option_a": option_a,
                "option_b": option_b,
                "psychological_target": psychological_target
            })
        
        return interactive_questions

    async def orchestrate_psychology_analysis(self, session_id: int, db: AsyncSession, ai_service) -> Dict[str, Any]:
        """
        🎼 MAIN ORCHESTRATION: Complete psychology analysis workflow
        
        Coordinates the entire psychology analysis pipeline:
        1. Get session context (SessionStateService)
        2. Analyze psychology (PsychologyAnalysisService)  
        3. Determine archetype (ArchetypeService)
        4. Save results (SessionStateService)
        5. Return complete profile
        
        Args:
            session_id: ID of the session to analyze
            db: Database session for service coordination
            ai_service: Legacy parameter, services handle AI internally
            
        Returns:
            dict: Complete psychology profile ready for use
        """
        try:
            logger.info(f"🎼 [ORCHESTRATOR] Starting complete psychology analysis workflow for session {session_id}")
            
            # 🔧 STEP 1: Get session context from SessionStateService
            session_context = await self._session_state_service.get_session_context(session_id, db)
            
            conversation_history = session_context['conversation_history']
            interaction_count = session_context['interaction_count']
            current_profile = session_context['current_psychology_profile']
            current_confidence = session_context['current_confidence']
            
            logger.info(f"📋 [ORCHESTRATOR] Session context loaded: {interaction_count} interactions, confidence: {current_confidence}%")

            # 🔧 STEP 2: Delegate psychology analysis to PsychologyAnalysisService
            logger.info(f"🤝 [ORCHESTRATOR] Delegating psychology analysis to specialized service")
            
            parsed_result = await self._psychology_analysis_service.analyze_interaction(
                conversation_history=conversation_history,
                current_profile=current_profile,
                confidence=current_confidence
            )
            
            if not parsed_result or not parsed_result.get('cumulative_psychology'):
                logger.warning(f"⚠️ [ORCHESTRATOR] Psychology analysis failed, using fallback workflow")
                return await self._orchestrate_fallback_profile(interaction_count)
            
            # 🔧 STEP 3: Delegate archetype determination to ArchetypeService
            cumulative_psychology = parsed_result.get('cumulative_psychology', {})

            tesla_archetype = await self._archetype_service.determine_archetype(
                psychology_results={'cumulative_psychology': cumulative_psychology},
                session_context={'interaction_count': interaction_count}
            )

            # Update analysis results with archetype
            parsed_result['customer_archetype'] = tesla_archetype
            parsed_result['tesla_archetype_mapped'] = True

            # 🔧 STEP 4: Transform suggested questions to interactive format
            interactive_questions = self._convert_to_interactive_questions(
                parsed_result.get('suggested_questions', [])
            )
            
            # Prepare complete analysis data
            analysis_data = parsed_result.copy()
            analysis_data['active_clarifying_questions'] = interactive_questions

            # 🔧 STEP 5: Delegate persistence to SessionStateService
            await self._session_state_service.update_session_with_analysis(
                session_id=session_id,
                analysis_data=analysis_data,
                db=db
            )

            # 🔧 STEP 6: Build complete orchestrated response
            analysis_level = "pełna" if interaction_count >= 3 else "wstępna"
            logger.info(f"🎯 [ORCHESTRATOR] Analysis level: {analysis_level} (interactions: {interaction_count})")

            complete_profile = {
                'cumulative_psychology': cumulative_psychology,
                'customer_archetype': tesla_archetype,
                'psychology_confidence': parsed_result.get('psychology_confidence', 0),
                'sales_indicators': parsed_result.get('sales_indicators', {}),
                'active_clarifying_questions': interactive_questions,
                'analysis_timestamp': datetime.now().isoformat(),
                'tesla_archetype_active': True,
                'analysis_level': analysis_level,
                'interaction_count': interaction_count
            }

            logger.info(f"✅ [ORCHESTRATOR] Complete psychology workflow finished! Confidence: {complete_profile['psychology_confidence']}%, Level: {analysis_level}")

            return complete_profile
            
        except Exception as e:
            logger.error(f"❌ [ORCHESTRATOR] Error during psychology workflow orchestration: {e}")
            return self._psychology_analysis_service._create_fallback_psychology_profile(interaction_count if 'interaction_count' in locals() else 0)

    async def _orchestrate_fallback_profile(self, interaction_count: int = 0) -> Dict[str, Any]:
        """
        🔧 Fallback Orchestration: Coordinate fallback profile creation
        """
        try:
            # Delegate fallback creation to PsychologyAnalysisService
            fallback_psychology = self._psychology_analysis_service._create_fallback_psychology_profile(interaction_count)
            
            # Delegate fallback archetype to ArchetypeService
            tesla_archetype = await self._archetype_service.determine_archetype(
                psychology_results={'cumulative_psychology': fallback_psychology.get('cumulative_psychology', {})},
                session_context={'interaction_count': interaction_count}
            )
            
            # Orchestrate complete fallback profile
            analysis_level = "pełna" if interaction_count >= 3 else "wstępna"
            
            complete_profile = {
                'cumulative_psychology': fallback_psychology.get('cumulative_psychology', {}),
                'customer_archetype': tesla_archetype,
                'psychology_confidence': fallback_psychology.get('psychology_confidence', 10),
                'sales_indicators': fallback_psychology.get('sales_indicators', {}),
                'active_clarifying_questions': [],
                'analysis_timestamp': datetime.now().isoformat(),
                'tesla_archetype_active': True,
                'analysis_level': analysis_level,
                'interaction_count': interaction_count
            }
            
            logger.info(f"✅ [ORCHESTRATOR] Fallback profile orchestration complete")
            return complete_profile
            
        except Exception as e:
            logger.error(f"❌ [ORCHESTRATOR] Error in fallback orchestration: {e}")
            # Ultimate fallback - minimal structure
            return {
                'cumulative_psychology': {},
                'customer_archetype': {'archetype_key': 'neutral', 'confidence': 10},
                'psychology_confidence': 10,
                'sales_indicators': {},
                'active_clarifying_questions': [],
                'analysis_timestamp': datetime.now().isoformat(),
                'tesla_archetype_active': False,
                'analysis_level': 'wstępna',
                'interaction_count': interaction_count
            }

    # 🔧 BACKWARD COMPATIBILITY METHODS

    async def update_and_get_psychology(self, session_id: int, db: AsyncSession, ai_service) -> Dict[str, Any]:
        """
        🔄 Backward Compatibility: Redirect to main orchestration method
        
        @deprecated: Use orchestrate_psychology_analysis for new code
        """
        logger.info("🔄 [COMPATIBILITY] Redirecting to orchestrate_psychology_analysis")
        return await self.orchestrate_psychology_analysis(session_id, db, ai_service)

    async def update_cumulative_profile(self, session_id: int, old_db: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        @deprecated: Legacy method maintained for compatibility
        """
        logger.warning("⚠️ [DEPRECATED] update_cumulative_profile is deprecated. Use orchestrate_psychology_analysis.")
        return {}

# 🎼 SINGLETON ORCHESTRATOR INSTANCE
session_orchestrator_service = SessionOrchestratorService()

# 🔄 BACKWARD COMPATIBILITY ALIAS
session_psychology_engine = session_orchestrator_service