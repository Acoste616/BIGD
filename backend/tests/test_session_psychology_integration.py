"""
Integration tests for SessionOrchestratorService with specialized services
Phase 2B - Service Integration Validation
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from app.services.session_orchestrator_service import SessionOrchestratorService
from app.services.psychology_analysis_service import PsychologyAnalysisService

class TestSessionPsychologyIntegration:
    """Test suite for SessionOrchestratorService integration with specialized services"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create mock psychology analysis service
        self.mock_psychology_service = Mock(spec=PsychologyAnalysisService)
        self.mock_psychology_service.analyze_interaction = AsyncMock()
        self.mock_psychology_service._create_fallback_psychology_profile = Mock()
        
        # Create session psychology engine with mocked service
        self.session_engine = SessionOrchestratorService(psychology_analysis_service=self.mock_psychology_service)
        
        # Mock database session
        self.mock_db = AsyncMock()
        self.mock_ai_service = Mock()
    
    @pytest.mark.asyncio
    async def test_psychology_service_delegation(self):
        """Test that SessionOrchestratorService properly delegates to specialized services"""
        # Arrange
        session_id = 1
        mock_session = Mock()
        mock_session.interactions = [Mock(user_input="Test interaction", timestamp=Mock())]
        mock_session.cumulative_psychology = {}
        mock_session.psychology_confidence = 0
        
        mock_psychology_result = {
            'cumulative_psychology': {
                'big_five': {
                    'conscientiousness': {'score': 8, 'rationale': 'Test', 'strategy': 'Test'}
                }
            },
            'psychology_confidence': 75,
            'customer_archetype': {'archetype_key': 'analityk'},
            'sales_indicators': {},
            'suggested_questions': []
        }
        
        # Mock database query
        self.mock_db.execute = AsyncMock()
        self.mock_db.execute.return_value.scalar_one_or_none.return_value = mock_session
        
        # Mock psychology service response
        self.mock_psychology_service.analyze_interaction.return_value = mock_psychology_result
        
        # Act
        result = await self.session_engine.update_and_get_psychology(session_id, self.mock_db, self.mock_ai_service)
        
        # Assert
        assert result is not None
        assert 'cumulative_psychology' in result
        assert 'customer_archetype' in result
        assert result['tesla_archetype_active'] == True
        
        # Verify delegation occurred
        self.mock_psychology_service.analyze_interaction.assert_called_once()
        call_args = self.mock_psychology_service.analyze_interaction.call_args
        assert 'conversation_history' in call_args.kwargs
        assert 'current_profile' in call_args.kwargs
        assert 'confidence' in call_args.kwargs
    
    @pytest.mark.asyncio 
    async def test_fallback_behavior_on_service_failure(self):
        """Test fallback behavior when PsychologyAnalysisService returns empty result"""
        # Arrange
        session_id = 1
        mock_session = Mock()
        mock_session.interactions = [Mock(user_input="Test", timestamp=Mock())]
        mock_session.cumulative_psychology = {}
        mock_session.psychology_confidence = 0
        
        # Mock database query
        self.mock_db.execute = AsyncMock()
        self.mock_db.execute.return_value.scalar_one_or_none.return_value = mock_session
        
        # Mock psychology service to return empty result
        self.mock_psychology_service.analyze_interaction.return_value = None
        
        # Mock fallback psychology profile
        fallback_profile = {
            'cumulative_psychology': {'big_five': {}},
            'psychology_confidence': 10,
            'sales_indicators': {}
        }
        self.mock_psychology_service._create_fallback_psychology_profile.return_value = fallback_profile
        
        # Act
        result = await self.session_engine.update_and_get_psychology(session_id, self.mock_db, self.mock_ai_service)
        
        # Assert - should get fallback result
        assert result is not None
        assert result['psychology_confidence'] >= 10  # Should have minimum confidence
        assert 'customer_archetype' in result
        
    def test_constructor_with_default_service(self):
        """Test that constructor creates default PsychologyAnalysisService when none provided"""
        # Act
        engine = SessionOrchestratorService()
        
        # Assert
        assert engine._psychology_analysis_service is not None
        assert isinstance(engine._psychology_analysis_service, PsychologyAnalysisService)
    
    def test_constructor_with_custom_service(self):
        """Test that constructor accepts custom PsychologyAnalysisService"""
        # Arrange
        custom_service = Mock(spec=PsychologyAnalysisService)
        
        # Act
        engine = SessionOrchestratorService(psychology_analysis_service=custom_service)
        
        # Assert
        assert engine._psychology_analysis_service is custom_service
    
    @pytest.mark.asyncio
    async def test_tesla_archetype_mapping_integration(self):
        """Test that Tesla archetype mapping still works after integration with ArchetypeService"""
        # Arrange
        psychology_result = {
            'cumulative_psychology': {
                'big_five': {
                    'conscientiousness': {'score': 9, 'rationale': 'High detail', 'strategy': 'Provide data'}
                },
                'disc': {
                    'compliance': {'score': 8, 'rationale': 'Follows process', 'strategy': 'Structure'}
                }
            },
            'psychology_confidence': 85
        }
        
        # Act - Use the ArchetypeService directly instead of the removed method
        tesla_archetype = await self.session_engine._archetype_service.determine_archetype(
            psychology_results=psychology_result,
            session_context={'interaction_count': 2}
        )
        
        # Assert
        assert tesla_archetype is not None
        assert 'archetype_key' in tesla_archetype
        assert 'confidence' in tesla_archetype
        assert tesla_archetype['confidence'] >= 60  # Should have reasonable confidence

if __name__ == "__main__":
    # Simple test runner for development
    pytest.main([__file__, "-v"])