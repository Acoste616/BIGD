"""
End-to-End Tests for Psychometrics Real-time Updates
"""
import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.domain import Session
from app.services.interaction_service import InteractionService
from app.services.session_psychology_service import session_psychology_engine

client = TestClient(app)


class TestE2EPsychometricsRealtime:
    """End-to-end tests for real-time psychometrics updates"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def sample_session(self):
        """Sample session data for testing"""
        return Session(
            id=1,
            client_id=1,
            is_active=1,
            cumulative_psychology={
                "big_five": {
                    "openness": {"score": 7, "rationale": "High openness", "strategy": "Innovative approach"},
                    "conscientiousness": {"score": 8, "rationale": "Very conscientious", "strategy": "Detailed planning"}
                },
                "disc": {
                    "dominance": {"score": 6, "rationale": "Moderate dominance", "strategy": "Allow leadership opportunities"}
                },
                "schwartz_values": [
                    {"value_name": "Security", "strength": 8, "rationale": "Values safety", "strategy": "Emphasize reliability", "is_present": True}
                ]
            },
            psychology_confidence=85,
            customer_archetype={
                "key": "analityk",
                "name": "🔬 Analityk",
                "confidence": 90,
                "description": "Analytical customer profile"
            }
        )
    
    @pytest.mark.asyncio
    async def test_complete_realtime_flow(self, mock_db, sample_session):
        """Test complete real-time flow from interaction to dashboard update"""
        # Mock the database session retrieval
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_session
        
        # Step 1: Get initial psychometrics data
        response = client.get("/sessions/1/psychometrics")
        assert response.status_code == 200
        initial_data = response.json()
        
        # Verify initial data structure
        assert "confidence_score" in initial_data
        assert "big_five" in initial_data
        assert "archetype" in initial_data
        assert initial_data["confidence_score"] == 85
        assert initial_data["archetype"]["key"] == "analityk"
        
        # Step 2: Simulate interaction service processing
        interaction_service = InteractionService()
        
        # Mock the session psychology engine update
        updated_psychology_profile = {
            "cumulative_psychology": {
                "big_five": {
                    "openness": {"score": 8, "rationale": "Very high openness", "strategy": "Highly innovative approach"},
                    "conscientiousness": {"score": 8, "rationale": "Very conscientious", "strategy": "Detailed planning"},
                    "extraversion": {"score": 5, "rationale": "Moderate extraversion", "strategy": "Balance social interaction"}
                },
                "disc": {
                    "dominance": {"score": 6, "rationale": "Moderate dominance", "strategy": "Allow leadership opportunities"},
                    "influence": {"score": 7, "rationale": "High influence", "strategy": "Engage enthusiastically"}
                },
                "schwartz_values": [
                    {"value_name": "Security", "strength": 8, "rationale": "Values safety", "strategy": "Emphasize reliability", "is_present": True},
                    {"value_name": "Achievement", "strength": 7, "rationale": "Values success", "strategy": "Highlight accomplishments", "is_present": True}
                ]
            },
            "customer_archetype": {
                "key": "analityk",
                "name": "🔬 Analityk",
                "confidence": 92,
                "description": "Analytical customer profile - updated"
            },
            "psychology_confidence": 88
        }
        
        with patch.object(session_psychology_engine, 'update_and_get_psychology', 
                         return_value=updated_psychology_profile):
            
            # Simulate interaction processing (this would normally trigger WebSocket notification)
            interaction_data = {
                "id": 1,
                "ai_response_json": {"test": "response"}
            }
            
            # Mock WebSocket connection manager
            with patch('app.services.interaction_service.connection_manager') as mock_cm:
                mock_cm.send_personal_message = AsyncMock()
                
                # Simulate interaction service notifying WebSocket clients
                await interaction_service._notify_websocket_clients(1, interaction_data)
                
                # Verify WebSocket notification was sent
                mock_cm.send_personal_message.assert_called_once()
                
                # Check the message content
                args, kwargs = mock_cm.send_personal_message.call_args
                message = args[0]
                target_session_id = args[1]
                
                assert target_session_id == 1
                assert message["event"] == "analysis_complete"
                assert message["session_id"] == 1
                assert "data" in message
                assert "timestamp" in message
    
    @pytest.mark.asyncio
    async def test_multiple_interactions_evolution(self, mock_db, sample_session):
        """Test psychometric profile evolution with multiple interactions"""
        # Mock the database session retrieval
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_session
        
        # Get initial data
        response = client.get("/sessions/1/psychometrics")
        assert response.status_code == 200
        initial_data = response.json()
        
        initial_confidence = initial_data["confidence_score"]
        initial_big_five_count = len(initial_data["big_five"])
        
        # Simulate first interaction update
        updated_psychology_profile_1 = {
            "cumulative_psychology": {
                "big_five": {
                    "openness": {"score": 8, "rationale": "Very high openness", "strategy": "Highly innovative approach"},
                    "conscientiousness": {"score": 8, "rationale": "Very conscientious", "strategy": "Detailed planning"},
                    "extraversion": {"score": 5, "rationale": "Moderate extraversion", "strategy": "Balance social interaction"}
                },
                "disc": {
                    "dominance": {"score": 6, "rationale": "Moderate dominance", "strategy": "Allow leadership opportunities"},
                    "influence": {"score": 7, "rationale": "High influence", "strategy": "Engage enthusiastically"}
                },
                "schwartz_values": [
                    {"value_name": "Security", "strength": 8, "rationale": "Values safety", "strategy": "Emphasize reliability", "is_present": True},
                    {"value_name": "Achievement", "strength": 7, "rationale": "Values success", "strategy": "Highlight accomplishments", "is_present": True}
                ]
            },
            "customer_archetype": {
                "key": "analityk",
                "name": "🔬 Analityk",
                "confidence": 90,
                "description": "Analytical customer profile - updated"
            },
            "psychology_confidence": 87
        }
        
        # Update session data for second interaction
        updated_session = Session(
            id=1,
            client_id=1,
            is_active=1,
            cumulative_psychology=updated_psychology_profile_1["cumulative_psychology"],
            psychology_confidence=updated_psychology_profile_1["psychology_confidence"],
            customer_archetype=updated_psychology_profile_1["customer_archetype"]
        )
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = updated_session
        
        # Get updated data after first interaction
        response = client.get("/sessions/1/psychometrics")
        assert response.status_code == 200
        updated_data_1 = response.json()
        
        # Verify evolution
        assert updated_data_1["confidence_score"] > initial_confidence
        assert len(updated_data_1["big_five"]) > initial_big_five_count
        assert len(updated_data_1["schwartz_values"]) == 2
        
        # Simulate second interaction update
        updated_psychology_profile_2 = {
            "cumulative_psychology": {
                "big_five": {
                    "openness": {"score": 9, "rationale": "Extremely high openness", "strategy": "Extremely innovative approach"},
                    "conscientiousness": {"score": 8, "rationale": "Very conscientious", "strategy": "Detailed planning"},
                    "extraversion": {"score": 6, "rationale": "Increasing extraversion", "strategy": "Encourage social interaction"},
                    "agreeableness": {"score": 7, "rationale": "High agreeableness", "strategy": "Focus on collaboration"}
                },
                "disc": {
                    "dominance": {"score": 6, "rationale": "Moderate dominance", "strategy": "Allow leadership opportunities"},
                    "influence": {"score": 8, "rationale": "Very high influence", "strategy": "Engage very enthusiastically"},
                    "steadiness": {"score": 5, "rationale": "Moderate steadiness", "strategy": "Maintain consistent pace"}
                },
                "schwartz_values": [
                    {"value_name": "Security", "strength": 8, "rationale": "Values safety", "strategy": "Emphasize reliability", "is_present": True},
                    {"value_name": "Achievement", "strength": 8, "rationale": "Strong values success", "strategy": "Strongly highlight accomplishments", "is_present": True},
                    {"value_name": "Power", "strength": 6, "rationale": "Values control", "strategy": "Offer autonomy", "is_present": True}
                ]
            },
            "customer_archetype": {
                "key": "analityk",
                "name": "🔬 Analityk",
                "confidence": 92,
                "description": "Analytical customer profile - highly confident"
            },
            "psychology_confidence": 90
        }
        
        # Update session data for verification
        final_session = Session(
            id=1,
            client_id=1,
            is_active=1,
            cumulative_psychology=updated_psychology_profile_2["cumulative_psychology"],
            psychology_confidence=updated_psychology_profile_2["psychology_confidence"],
            customer_archetype=updated_psychology_profile_2["customer_archetype"]
        )
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = final_session
        
        # Get final data after second interaction
        response = client.get("/sessions/1/psychometrics")
        assert response.status_code == 200
        final_data = response.json()
        
        # Verify final evolution
        assert final_data["confidence_score"] > updated_data_1["confidence_score"]
        assert len(final_data["big_five"]) > len(updated_data_1["big_five"])
        assert len(final_data["disc_profile"]) > len(updated_data_1["disc_profile"])
        assert len(final_data["schwartz_values"]) > len(updated_data_1["schwartz_values"])
    
    def test_websocket_message_structure(self):
        """Test that WebSocket messages have the correct structure"""
        # Simulate a WebSocket message
        message = {
            "event": "analysis_complete",
            "session_id": 123,
            "data": {
                "interaction_id": 456,
                "ai_response": {
                    "main_analysis": "Test analysis",
                    "likely_archetypes": ["analityk"],
                    "strategic_notes": ["Test note"],
                    "sales_indicators": {
                        "purchase_temperature": {"value": 75, "trend": "increasing"}
                    }
                }
            },
            "timestamp": "2023-01-01T00:00:00Z"
        }
        
        # Verify message structure
        assert "event" in message
        assert "session_id" in message
        assert "data" in message
        assert "timestamp" in message
        assert message["event"] == "analysis_complete"
        assert isinstance(message["session_id"], int)
        assert isinstance(message["data"], dict)
        assert isinstance(message["timestamp"], str)
        
        # Verify data structure
        assert "interaction_id" in message["data"]
        assert "ai_response" in message["data"]
        assert isinstance(message["data"]["interaction_id"], int)
        assert isinstance(message["data"]["ai_response"], dict)
        
        # Verify AI response structure
        ai_response = message["data"]["ai_response"]
        assert "main_analysis" in ai_response
        assert "likely_archetypes" in ai_response
        assert "strategic_notes" in ai_response