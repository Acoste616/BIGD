"""
Unit tests for PsychologyAnalysisService
Phase 2A - Extracted Service Validation
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock
from app.services.psychology_analysis_service import PsychologyAnalysisService

class TestPsychologyAnalysisService:
    """Test suite for the newly extracted PsychologyAnalysisService"""
    
    def setup_method(self):
        """Setup test environment"""
        # Mock AI service for testing
        self.mock_ai_service = Mock()
        self.mock_ai_service._call_llm_with_retry = AsyncMock()
        
        # Create service instance with mocked dependencies
        self.service = PsychologyAnalysisService(ai_service=self.mock_ai_service)
    
    @pytest.mark.asyncio
    async def test_analyze_interaction_success(self):
        """Test successful psychology analysis"""
        # Arrange
        conversation_history = "Klient pyta o TCO i szczegółowe dane finansowe"
        mock_ai_response = {
            'content': '''
            {
                "cumulative_psychology": {
                    "big_five": {
                        "conscientiousness": {"score": 8, "rationale": "Szczegółowe pytania", "strategy": "Podaj dane"}
                    }
                },
                "psychology_confidence": 75,
                "customer_archetype": {
                    "archetype_key": "analityk",
                    "confidence": 80
                }
            }
            '''
        }
        self.mock_ai_service._call_llm_with_retry.return_value = mock_ai_response
        
        # Act
        result = await self.service.analyze_interaction(conversation_history)
        
        # Assert
        assert result is not None
        assert 'cumulative_psychology' in result
        assert 'psychology_confidence' in result
        assert result['psychology_confidence'] >= 0
        
    @pytest.mark.asyncio
    async def test_analyze_interaction_fallback(self):
        """Test fallback behavior when AI fails"""
        # Arrange
        conversation_history = "Test conversation"
        self.mock_ai_service._call_llm_with_retry.side_effect = Exception("AI service failed")
        
        # Act
        result = await self.service.analyze_interaction(conversation_history)
        
        # Assert
        assert result is not None
        assert result['psychology_confidence'] == 10  # Fallback confidence
        assert result['customer_archetype']['archetype_key'] == 'neutral'
        
    def test_build_prompt_structure(self):
        """Test prompt building functionality"""
        # Arrange
        history = "Test conversation history"
        current_profile = {"big_five": {"openness": {"score": 6}}}
        confidence = 50
        
        # Act
        prompt = self.service._build_cumulative_psychology_prompt(history, current_profile, confidence)
        
        # Assert
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be substantial prompt
        assert "ULTRA MÓZG" in prompt
        assert "confidence: 50%" in prompt
        
    def test_validate_psychology_repair(self):
        """Test psychology data validation and repair"""
        # Arrange
        incomplete_data = {
            "cumulative_psychology": {
                "big_five": {
                    "openness": {"score": None}  # Null value that should be repaired
                }
            },
            "psychology_confidence": 0
        }
        
        # Act
        repaired_data = self.service._validate_and_repair_psychology(incomplete_data, None)
        
        # Assert
        assert repaired_data['cumulative_psychology']['big_five']['openness']['score'] == 5
        assert repaired_data['psychology_confidence'] == 30
        assert repaired_data['cumulative_psychology']['big_five']['openness']['rationale'] is not None
        
    def test_fallback_profile_structure(self):
        """Test fallback profile contains all required fields"""
        # Act
        fallback = self.service._create_fallback_psychology_profile(interaction_count=2)
        
        # Assert
        assert 'cumulative_psychology' in fallback
        assert 'big_five' in fallback['cumulative_psychology']
        assert 'disc' in fallback['cumulative_psychology']
        assert 'schwartz_values' in fallback['cumulative_psychology']
        assert 'customer_archetype' in fallback
        assert 'sales_indicators' in fallback
        assert fallback['interaction_count'] == 2
        assert fallback['analysis_level'] == 'wstępna'  # < 3 interactions

if __name__ == "__main__":
    # Simple test runner for development
    pytest.main([__file__, "-v"])