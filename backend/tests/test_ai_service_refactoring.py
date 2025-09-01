"""
CRITICAL TESTS - AI Services Refactoring Safety Net
Tests to ensure ZERO functionality loss during consolidation
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any, Optional

# Import all AI service variants to test compatibility
from app.services.ai_service import AIService as AIServiceCurrent, initialize_ai_service, generate_sales_analysis
from app.services.ai_service_new import AIService as AIServiceNew
from app.services.qdrant_service import QdrantService


class TestAIServiceCompatibility:
    """Test suite ensuring backward compatibility during refactoring"""
    
    @pytest.fixture
    async def mock_qdrant_service(self):
        """Mock QdrantService for testing"""
        mock_service = MagicMock(spec=QdrantService)
        return mock_service
    
    @pytest.fixture
    async def sample_client_profile(self):
        """Sample client profile for testing"""
        return {
            "id": "client_123",
            "name": "Jan Kowalski",
            "company": "Tech Corp",
            "industry": "Technology"
        }
    
    @pytest.fixture
    async def sample_session_history(self):
        """Sample session history for testing"""
        return [
            {
                "user_input": "Interesuje mnie Tesla Model S",
                "ai_response": "Świetny wybór! Tesla Model S to...",
                "timestamp": "2025-08-31T10:00:00",
                "customer_archetype": {
                    "archetype_name": "wizjoner_przyszlosci",
                    "confidence": 0.85
                }
            },
            {
                "user_input": "Jaka jest cena?", 
                "ai_response": "Cena Tesla Model S zależy od...",
                "timestamp": "2025-08-31T10:05:00"
            }
        ]
    
    @pytest.fixture
    async def sample_session_context(self):
        """Sample session context"""
        return {
            "session_id": "session_456",
            "session_type": "sales_consultation",
            "stage": "discovery",
            "language": "pl"
        }
    
    @pytest.fixture
    async def sample_psychology_profile(self):
        """Sample psychology profile"""
        return {
            "big_five": {
                "openness": {"score": 8, "rationale": "Klient pyta o innowacje"},
                "conscientiousness": {"score": 6, "rationale": "Planuje zakup"},
                "extraversion": {"score": 7, "rationale": "Aktywna komunikacja"},
                "agreeableness": {"score": 5, "rationale": "Neutralny ton"},
                "neuroticism": {"score": 3, "rationale": "Spokojny klient"}
            },
            "disc": {
                "dominance": {"score": 6, "rationale": "Szybkie decyzje"},
                "influence": {"score": 7, "rationale": "Towarzyski"},
                "steadiness": {"score": 5, "rationale": "Umiarkowany"},
                "compliance": {"score": 4, "rationale": "Nie nadmiernie analityczny"}
            },
            "schwartz_values": [
                {"value_name": "Osiągnięcia", "is_present": True},
                {"value_name": "Stymulacja", "is_present": True}
            ]
        }


class TestAIServiceCurrentFunctionality:
    """Test current ai_service.py functionality"""
    
    @pytest.mark.asyncio
    async def test_ai_service_initialization(self, mock_qdrant_service):
        """Test AIService initialization"""
        with patch('app.services.ai_service.initialize_ai_services') as mock_init:
            with patch('app.services.ai_service.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service.get_holistic_synthesis_service') as mock_holistic:
                        # Setup mocks
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = AsyncMock()
                        mock_holistic.return_value = AsyncMock()
                        
                        # Test initialization
                        service = AIServiceCurrent(mock_qdrant_service)
                        
                        # Verify initialization calls
                        mock_init.assert_called_once_with(mock_qdrant_service)
                        assert service.qdrant_service == mock_qdrant_service
                        assert service._psychology_service is not None
                        assert service._sales_strategy_service is not None
                        assert service._holistic_service is not None
    
    @pytest.mark.asyncio
    async def test_generate_analysis_success(self, mock_qdrant_service, sample_client_profile, 
                                           sample_session_history, sample_session_context):
        """Test generate_analysis method success path"""
        with patch('app.services.ai_service.initialize_ai_services'):
            with patch('app.services.ai_service.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service.get_holistic_synthesis_service') as mock_holistic:
                        # Setup service
                        mock_psychology = AsyncMock()
                        mock_strategy = AsyncMock()
                        mock_holistic_service = AsyncMock()
                        
                        mock_psych.return_value = mock_psychology
                        mock_sales.return_value = mock_strategy
                        mock_holistic.return_value = mock_holistic_service
                        
                        # Mock strategy response
                        expected_strategy = {
                            "response": "Doskonały wybór! Tesla to przyszłość...",
                            "suggested_actions": ["Zapytaj o budżet", "Sprawdź potrzeby"],
                            "reasoning": "Klient wykazuje zainteresowanie innowacjami"
                        }
                        mock_strategy.generate_sales_strategy.return_value = expected_strategy
                        
                        # Create service and test
                        service = AIServiceCurrent(mock_qdrant_service)
                        
                        result = await service.generate_analysis(
                            user_input="Interesuje mnie Tesla",
                            client_profile=sample_client_profile,
                            session_history=sample_session_history,
                            session_context=sample_session_context
                        )
                        
                        # Verify result
                        assert result["response"] == expected_strategy["response"]
                        assert "archetype_evolution_analysis" in result
                        assert result["archetype_evolution_analysis"]["current_archetype"] is None
    
    @pytest.mark.asyncio  
    async def test_archetype_evolution_analysis(self, mock_qdrant_service):
        """Test _analyze_archetype_evolution method"""
        with patch('app.services.ai_service.initialize_ai_services'):
            with patch('app.services.ai_service.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service.get_holistic_synthesis_service') as mock_holistic:
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = AsyncMock()
                        mock_holistic.return_value = AsyncMock()
                        
                        service = AIServiceCurrent(mock_qdrant_service)
                        
                        # Test with archetype changes
                        session_history = [
                            {"customer_archetype": {"archetype_name": "analityk"}},
                            {"customer_archetype": {"archetype_name": "wizjoner"}},
                            {"customer_archetype": {"archetype_name": "wizjoner"}}
                        ]
                        
                        result = service._analyze_archetype_evolution(session_history, "wizjoner")
                        
                        assert result["initial_archetype"] == "analityk"
                        assert result["current_archetype"] == "wizjoner"
                        assert not result["is_stable"]
                        assert len(result["changes"]) == 1
                        assert result["changes"][0]["from"] == "analityk"
                        assert result["changes"][0]["to"] == "wizjoner"

    @pytest.mark.asyncio
    async def test_generate_analysis_error_handling(self, mock_qdrant_service, sample_client_profile,
                                                   sample_session_history, sample_session_context):
        """Test error handling in generate_analysis"""
        with patch('app.services.ai_service.initialize_ai_services'):
            with patch('app.services.ai_service.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service.get_holistic_synthesis_service') as mock_holistic:
                        # Setup failing service
                        mock_strategy = AsyncMock()
                        mock_strategy.generate_sales_strategy.side_effect = Exception("LLM Error")
                        
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = mock_strategy
                        mock_holistic.return_value = AsyncMock()
                        
                        service = AIServiceCurrent(mock_qdrant_service)
                        
                        result = await service.generate_analysis(
                            user_input="Test input",
                            client_profile=sample_client_profile,
                            session_history=sample_session_history,
                            session_context=sample_session_context
                        )
                        
                        # Verify fallback response
                        assert "error" in result
                        assert result["response"] == "Przepraszam, wystąpił błąd podczas analizy. Skupmy się na kliencie."
                        assert "suggested_actions" in result


class TestAIServiceNewFunctionality:
    """Test ai_service_new.py functionality"""
    
    @pytest.mark.asyncio
    async def test_ai_service_new_initialization(self, mock_qdrant_service):
        """Test AIServiceNew initialization"""
        with patch('app.services.ai_service_new.initialize_ai_services') as mock_init:
            with patch('app.services.ai_service_new.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service_new.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service_new.get_holistic_synthesis_service') as mock_holistic:
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = AsyncMock()
                        mock_holistic.return_value = AsyncMock()
                        
                        service = AIServiceNew(mock_qdrant_service)
                        
                        mock_init.assert_called_once_with(mock_qdrant_service)
                        assert service.qdrant_service == mock_qdrant_service

    @pytest.mark.asyncio
    async def test_generate_analysis_compatibility(self, mock_qdrant_service, sample_client_profile,
                                                 sample_session_history, sample_session_context):
        """Test that AIServiceNew has same interface as AIServiceCurrent"""
        with patch('app.services.ai_service_new.initialize_ai_services'):
            with patch('app.services.ai_service_new.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service_new.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service_new.get_holistic_synthesis_service') as mock_holistic:
                        
                        mock_strategy = AsyncMock()
                        mock_strategy.generate_sales_strategy.return_value = {
                            "response": "Test response",
                            "suggested_actions": ["Action 1"]
                        }
                        
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = mock_strategy
                        mock_holistic.return_value = AsyncMock()
                        
                        service = AIServiceNew(mock_qdrant_service)
                        
                        result = await service.generate_analysis(
                            user_input="Test",
                            client_profile=sample_client_profile,
                            session_history=sample_session_history,
                            session_context=sample_session_context
                        )
                        
                        assert "response" in result
                        assert result["response"] == "Test response"


class TestCompatibilityFunctions:
    """Test global compatibility functions"""
    
    @pytest.mark.asyncio
    async def test_generate_sales_analysis_function(self, mock_qdrant_service, sample_client_profile,
                                                   sample_session_history, sample_session_context):
        """Test global generate_sales_analysis function"""
        with patch('app.services.ai_service.initialize_ai_services'):
            with patch('app.services.ai_service.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service.get_holistic_synthesis_service') as mock_holistic:
                        
                        mock_strategy = AsyncMock()
                        expected_response = {
                            "response": "Global function test",
                            "suggested_actions": ["Global action"]
                        }
                        mock_strategy.generate_sales_strategy.return_value = expected_response
                        
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = mock_strategy
                        mock_holistic.return_value = AsyncMock()
                        
                        # Initialize global service
                        initialize_ai_service(mock_qdrant_service)
                        
                        # Test global function
                        result = await generate_sales_analysis(
                            user_input="Global test",
                            client_profile=sample_client_profile,
                            session_history=sample_session_history,
                            session_context=sample_session_context
                        )
                        
                        assert result["response"] == expected_response["response"]
    
    @pytest.mark.asyncio
    async def test_generate_sales_analysis_uninitialized(self, sample_client_profile,
                                                        sample_session_history, sample_session_context):
        """Test error handling when AI service not initialized"""
        # Reset global state
        import app.services.ai_service
        app.services.ai_service.ai_service = None
        
        result = await generate_sales_analysis(
            user_input="Test",
            client_profile=sample_client_profile,
            session_history=sample_session_history,
            session_context=sample_session_context
        )
        
        assert "error" in result
        assert result["error"] == "AI Service not initialized"
        assert result["is_fallback"] is True


class TestServiceStatusAndHealth:
    """Test service monitoring and health checks"""
    
    @pytest.mark.asyncio
    async def test_service_status(self, mock_qdrant_service):
        """Test get_service_status method"""
        with patch('app.services.ai_service.initialize_ai_services'):
            with patch('app.services.ai_service.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service.get_holistic_synthesis_service') as mock_holistic:
                        with patch('app.services.ai_service.check_ai_services_health') as mock_health:
                            
                            mock_psych.return_value = AsyncMock()
                            mock_sales.return_value = AsyncMock() 
                            mock_holistic.return_value = AsyncMock()
                            mock_health.return_value = {"all_services": "healthy"}
                            
                            service = AIServiceCurrent(mock_qdrant_service)
                            status = service.get_service_status()
                            
                            assert status["orchestrator_status"] == "active"
                            assert status["qdrant_available"] is True
                            assert "specialized_services" in status
                            assert "timestamp" in status
    
    @pytest.mark.asyncio
    async def test_cache_clearing(self, mock_qdrant_service):
        """Test clear_all_caches method"""
        with patch('app.services.ai_service.initialize_ai_services'):
            with patch('app.services.ai_service.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service.get_holistic_synthesis_service') as mock_holistic:
                        with patch('app.services.ai_service.AIServiceFactory') as mock_factory:
                            
                            mock_psych.return_value = AsyncMock()
                            mock_sales.return_value = AsyncMock()
                            mock_holistic.return_value = AsyncMock()
                            
                            service = AIServiceCurrent(mock_qdrant_service)
                            service.clear_all_caches()
                            
                            mock_factory.clear_all_caches.assert_called_once()


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([__file__, "-v", "--tb=short"])