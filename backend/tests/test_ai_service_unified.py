"""
UNIFIED AI SERVICE TESTS - Comprehensive validation
Ensures the unified service maintains ALL functionality from original services
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any

from app.services.ai_service_unified import (
    AIServiceUnified, 
    initialize_ai_service, 
    generate_sales_analysis,
    generate_psychometric_analysis
)
from app.services.qdrant_service import QdrantService


class TestAIServiceUnified:
    """Test the unified AI service implementation"""
    
    @pytest.fixture
    def mock_qdrant_service(self):
        """Mock QdrantService for testing"""
        return MagicMock(spec=QdrantService)
    
    @pytest.fixture
    def sample_session_history(self):
        """Sample session history with archetype evolution"""
        return [
            {
                "user_input": "Interesuje mnie Tesla Model S",
                "ai_response": "Świetny wybór!",
                "timestamp": "2025-08-31T10:00:00",
                "customer_archetype": {
                    "archetype_name": "analityk",
                    "confidence": 0.7
                }
            },
            {
                "user_input": "Chcę najnowsze technologie",
                "ai_response": "Tesla oferuje najnowocześniejsze...",
                "timestamp": "2025-08-31T10:05:00",
                "customer_archetype": {
                    "archetype_name": "wizjoner_przyszlosci",
                    "confidence": 0.85
                }
            },
            {
                "user_input": "Ile to kosztuje?",
                "ai_response": "Cena zależy od...",
                "timestamp": "2025-08-31T10:10:00",
                "customer_archetype": {
                    "archetype_name": "wizjoner_przyszlosci",
                    "confidence": 0.9
                }
            }
        ]

    @pytest.mark.asyncio
    async def test_initialization_success(self, mock_qdrant_service):
        """Test successful service initialization"""
        with patch('app.services.ai_service_unified.initialize_ai_services') as mock_init:
            with patch('app.services.ai_service_unified.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service_unified.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service') as mock_holistic:
                        
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = AsyncMock()
                        mock_holistic.return_value = AsyncMock()
                        
                        service = AIServiceUnified(mock_qdrant_service)
                        
                        assert service.qdrant_service == mock_qdrant_service
                        assert service._metrics['requests_processed'] == 0
                        assert service._metrics['errors_encountered'] == 0
                        assert service._metrics['last_health_check'] is not None
                        mock_init.assert_called_once_with(mock_qdrant_service)

    @pytest.mark.asyncio
    async def test_initialization_failure(self, mock_qdrant_service):
        """Test initialization failure handling"""
        with patch('app.services.ai_service_unified.initialize_ai_services') as mock_init:
            mock_init.side_effect = Exception("Initialization failed")
            
            with pytest.raises(RuntimeError, match="AI Service initialization failed"):
                AIServiceUnified(mock_qdrant_service)

    @pytest.mark.asyncio
    async def test_archetype_evolution_analysis_with_changes(self, mock_qdrant_service, sample_session_history):
        """Test archetype evolution analysis with changes"""
        with patch('app.services.ai_service_unified.initialize_ai_services'):
            with patch('app.services.ai_service_unified.get_psychology_service'):
                with patch('app.services.ai_service_unified.get_sales_strategy_service'):
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service'):
                        
                        service = AIServiceUnified(mock_qdrant_service)
                        
                        result = service._analyze_archetype_evolution(
                            sample_session_history,
                            "wizjoner_przyszlosci"
                        )
                        
                        # Verify evolution analysis
                        assert result['initial_archetype'] == "analityk"
                        assert result['current_archetype'] == "wizjoner_przyszlosci"
                        assert result['is_stable'] == False  # There was a change
                        assert result['total_interactions'] == 3
                        assert len(result['changes']) == 1
                        assert result['changes'][0]['from'] == "analityk"
                        assert result['changes'][0]['to'] == "wizjoner_przyszlosci"
                        assert 0.0 <= result['stability_confidence'] <= 1.0

    @pytest.mark.asyncio
    async def test_archetype_evolution_analysis_stable(self, mock_qdrant_service):
        """Test archetype evolution analysis with stable archetype"""
        stable_history = [
            {"customer_archetype": {"archetype_name": "analityk", "confidence": 0.8}},
            {"customer_archetype": {"archetype_name": "analityk", "confidence": 0.85}},
            {"customer_archetype": {"archetype_name": "analityk", "confidence": 0.9}}
        ]
        
        with patch('app.services.ai_service_unified.initialize_ai_services'):
            with patch('app.services.ai_service_unified.get_psychology_service'):
                with patch('app.services.ai_service_unified.get_sales_strategy_service'):
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service'):
                        
                        service = AIServiceUnified(mock_qdrant_service)
                        
                        result = service._analyze_archetype_evolution(stable_history, "analityk")
                        
                        assert result['initial_archetype'] == "analityk"
                        assert result['current_archetype'] == "analityk"
                        assert result['is_stable'] == True
                        assert len(result['changes']) == 0
                        assert result['stability_confidence'] == 1.0

    @pytest.mark.asyncio
    async def test_archetype_evolution_analysis_empty_history(self, mock_qdrant_service):
        """Test archetype evolution analysis with empty history"""
        with patch('app.services.ai_service_unified.initialize_ai_services'):
            with patch('app.services.ai_service_unified.get_psychology_service'):
                with patch('app.services.ai_service_unified.get_sales_strategy_service'):
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service'):
                        
                        service = AIServiceUnified(mock_qdrant_service)
                        
                        result = service._analyze_archetype_evolution([], None)
                        
                        assert result['initial_archetype'] is None
                        assert result['current_archetype'] is None
                        assert result['is_stable'] == True
                        assert len(result['changes']) == 0
                        assert result['stability_confidence'] == 0.0
                        assert result['total_interactions'] == 0

    @pytest.mark.asyncio
    async def test_generate_analysis_success(self, mock_qdrant_service, sample_session_history):
        """Test successful generate_analysis method"""
        with patch('app.services.ai_service_unified.initialize_ai_services'):
            with patch('app.services.ai_service_unified.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service_unified.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service') as mock_holistic:
                        
                        # Setup mocks
                        mock_strategy_service = AsyncMock()
                        expected_strategy = {
                            "response": "Doskonała decyzja! Tesla Model S...",
                            "suggested_actions": ["Sprawdź budżet", "Omów finansowanie"],
                            "reasoning": "Klient przeszedł od analitycznego do wizjonerskiego myślenia"
                        }
                        mock_strategy_service.generate_sales_strategy.return_value = expected_strategy
                        
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = mock_strategy_service
                        mock_holistic.return_value = AsyncMock()
                        
                        service = AIServiceUnified(mock_qdrant_service)
                        
                        result = await service.generate_analysis(
                            user_input="Chcę kupić Teslę",
                            client_profile={"id": "client_123", "name": "Jan Kowalski"},
                            session_history=sample_session_history,
                            session_context={"session_id": "sess_456"},
                            customer_archetype={"archetype_name": "wizjoner_przyszlosci"}
                        )
                        
                        # Verify response structure
                        assert result["response"] == expected_strategy["response"]
                        assert "archetype_evolution_analysis" in result
                        assert "_metadata" in result
                        assert result["_metadata"]["service_version"] == "unified_v1.0"
                        assert "processing_time_ms" in result["_metadata"]
                        
                        # Verify archetype evolution was analyzed
                        evolution = result["archetype_evolution_analysis"]
                        assert evolution["initial_archetype"] == "analityk"
                        assert evolution["current_archetype"] == "wizjoner_przyszlosci"
                        assert not evolution["is_stable"]

    @pytest.mark.asyncio
    async def test_generate_analysis_error_handling(self, mock_qdrant_service):
        """Test error handling in generate_analysis"""
        with patch('app.services.ai_service_unified.initialize_ai_services'):
            with patch('app.services.ai_service_unified.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service_unified.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service') as mock_holistic:
                        
                        # Setup failing service
                        mock_strategy_service = AsyncMock()
                        mock_strategy_service.generate_sales_strategy.side_effect = Exception("LLM timeout")
                        
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = mock_strategy_service
                        mock_holistic.return_value = AsyncMock()
                        
                        service = AIServiceUnified(mock_qdrant_service)
                        
                        result = await service.generate_analysis(
                            user_input="Test input",
                            client_profile={"id": "client_123"},
                            session_history=[],
                            session_context={}
                        )
                        
                        # Verify enhanced fallback response
                        assert "error_details" in result
                        assert result["error_details"]["error_message"] == "LLM timeout"
                        assert result["_metadata"]["is_fallback"] == True
                        assert result["response"] == "Przepraszam, wystąpił błąd podczas analizy. Skupmy się na Twoich potrzebach."
                        assert len(result["suggested_actions"]) > 0

    @pytest.mark.asyncio
    async def test_metrics_tracking(self, mock_qdrant_service):
        """Test that metrics are properly tracked"""
        with patch('app.services.ai_service_unified.initialize_ai_services'):
            with patch('app.services.ai_service_unified.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service_unified.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service') as mock_holistic:
                        
                        mock_strategy_service = AsyncMock()
                        mock_strategy_service.generate_sales_strategy.return_value = {
                            "response": "Test response"
                        }
                        
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = mock_strategy_service
                        mock_holistic.return_value = AsyncMock()
                        
                        service = AIServiceUnified(mock_qdrant_service)
                        
                        initial_requests = service._metrics['requests_processed']
                        
                        await service.generate_analysis(
                            user_input="Test",
                            client_profile={},
                            session_history=[],
                            session_context={}
                        )
                        
                        # Verify metrics were updated
                        assert service._metrics['requests_processed'] == initial_requests + 1
                        assert service._metrics['average_response_time'] > 0

    @pytest.mark.asyncio
    async def test_service_status(self, mock_qdrant_service):
        """Test service status reporting"""
        with patch('app.services.ai_service_unified.initialize_ai_services'):
            with patch('app.services.ai_service_unified.get_psychology_service'):
                with patch('app.services.ai_service_unified.get_sales_strategy_service'):
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service'):
                        with patch('app.services.ai_service_unified.check_ai_services_health') as mock_health:
                            
                            mock_health.return_value = {"all_services": "healthy"}
                            
                            service = AIServiceUnified(mock_qdrant_service)
                            service._metrics['requests_processed'] = 100
                            service._metrics['errors_encountered'] = 5
                            
                            status = service.get_service_status()
                            
                            assert status['service_info']['name'] == 'AIServiceUnified'
                            assert status['service_info']['version'] == '1.0'
                            assert status['service_info']['status'] == 'active'
                            assert status['infrastructure']['qdrant_available'] == True
                            assert status['performance_metrics']['requests_processed'] == 100
                            assert status['performance_metrics']['errors_encountered'] == 5
                            assert status['performance_metrics']['error_rate_percent'] == 5.0


class TestCompatibilityFunctions:
    """Test backward compatibility functions"""
    
    @pytest.mark.asyncio
    async def test_global_generate_sales_analysis(self, mock_qdrant_service):
        """Test global generate_sales_analysis function"""
        with patch('app.services.ai_service_unified.initialize_ai_services'):
            with patch('app.services.ai_service_unified.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service_unified.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service') as mock_holistic:
                        
                        mock_strategy_service = AsyncMock()
                        expected_response = {
                            "response": "Global function test",
                            "suggested_actions": ["Action 1"]
                        }
                        mock_strategy_service.generate_sales_strategy.return_value = expected_response
                        
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = mock_strategy_service
                        mock_holistic.return_value = AsyncMock()
                        
                        # Initialize global service
                        initialize_ai_service(mock_qdrant_service)
                        
                        # Test global function
                        result = await generate_sales_analysis(
                            user_input="Global test",
                            client_profile={"id": "client_123"},
                            session_history=[],
                            session_context={}
                        )
                        
                        assert result["response"] == expected_response["response"]
                        assert "_metadata" in result
                        assert result["_metadata"]["service_version"] == "unified_v1.0"

    @pytest.mark.asyncio
    async def test_generate_sales_analysis_with_sales_indicators(self, mock_qdrant_service):
        """Test that sales_indicators are properly attached"""
        with patch('app.services.ai_service_unified.initialize_ai_services'):
            with patch('app.services.ai_service_unified.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service_unified.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service') as mock_holistic:
                        
                        mock_strategy_service = AsyncMock()
                        mock_strategy_service.generate_sales_strategy.return_value = {
                            "response": "Test response"
                        }
                        
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = mock_strategy_service
                        mock_holistic.return_value = AsyncMock()
                        
                        initialize_ai_service(mock_qdrant_service)
                        
                        sales_indicators = {
                            "prl_score": 85,
                            "fds_score": 72,
                            "indicators": ["High potential", "Ready to buy"]
                        }
                        
                        result = await generate_sales_analysis(
                            user_input="Test",
                            client_profile={"id": "client_123"},
                            session_history=[],
                            session_context={},
                            sales_indicators=sales_indicators
                        )
                        
                        assert "sales_indicators" in result
                        assert result["sales_indicators"] == sales_indicators

    @pytest.mark.asyncio
    async def test_uninitialized_service_error(self):
        """Test error handling when service not initialized"""
        # Reset global state
        import app.services.ai_service_unified
        app.services.ai_service_unified.ai_service_unified = None
        
        result = await generate_sales_analysis(
            user_input="Test",
            client_profile={},
            session_history=[],
            session_context={}
        )
        
        assert "error" in result
        assert result["error"] == "AI Service not initialized"
        assert result["error_code"] == "SERVICE_NOT_INITIALIZED"
        assert result["is_fallback"] == True
        assert result["_metadata"]["service_version"] == "unified_v1.0"


class TestAIDojioCompatibility:
    """Test AI Dojo compatibility methods"""
    
    @pytest.mark.asyncio
    async def test_handle_training_conversation(self, mock_qdrant_service):
        """Test AI Dojo training conversation handling"""
        with patch('app.services.ai_service_unified.initialize_ai_services'):
            with patch('app.services.ai_service_unified.get_psychology_service') as mock_psych:
                with patch('app.services.ai_service_unified.get_sales_strategy_service') as mock_sales:
                    with patch('app.services.ai_service_unified.get_holistic_synthesis_service') as mock_holistic:
                        
                        mock_strategy_service = AsyncMock()
                        mock_strategy_service.generate_quick_response.return_value = {
                            "quick_response": {
                                "text": "Training response",
                                "tone": "educational"
                            }
                        }
                        
                        mock_psych.return_value = AsyncMock()
                        mock_sales.return_value = mock_strategy_service
                        mock_holistic.return_value = AsyncMock()
                        
                        service = AIServiceUnified(mock_qdrant_service)
                        
                        result = await service._handle_training_conversation(
                            message="How do I handle price objections?",
                            training_mode="knowledge_update",
                            context={"difficulty": "advanced"}
                        )
                        
                        assert "quick_response" in result
                        assert result["quick_response"]["text"] == "Training response"
                        assert result["_metadata"]["service_version"] == "unified_v1.0"
                        assert result["_metadata"]["training_mode"] == "knowledge_update"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])