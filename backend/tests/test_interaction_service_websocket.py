"""
Test cases for InteractionService WebSocket notifications
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.interaction_service import InteractionService
from app.schemas.interaction import InteractionCreateNested


class TestInteractionServiceWebSocket:
    """Test cases for InteractionService WebSocket functionality"""
    
    @pytest.fixture
    def interaction_service(self):
        """Fixture to create an InteractionService instance"""
        return InteractionService()
    
    @pytest.fixture
    def mock_db(self):
        """Fixture to create a mock database session"""
        return Mock(spec=AsyncSession)
    
    @pytest.fixture
    def mock_interaction_data(self):
        """Fixture to create mock interaction data"""
        return InteractionCreateNested(
            user_input="Test input",
            interaction_type="question"
        )
    
    @pytest.mark.asyncio
    async def test_notify_websocket_clients(self, interaction_service):
        """Test notifying WebSocket clients"""
        session_id = 123
        interaction_data = {
            "id": 456,
            "ai_response_json": {"test": "response"}
        }
        
        # Mock the connection_manager
        with patch('app.services.interaction_service.connection_manager') as mock_cm:
            mock_cm.send_personal_message = AsyncMock()
            
            # Call the method
            await interaction_service._notify_websocket_clients(session_id, interaction_data)
            
            # Verify the WebSocket notification was sent
            mock_cm.send_personal_message.assert_called_once()
            
            # Check the message content
            args, kwargs = mock_cm.send_personal_message.call_args
            message = args[0]  # First argument is the message
            target_session_id = args[1]  # Second argument is the session_id
            
            assert target_session_id == session_id
            assert message["event"] == "analysis_complete"
            assert message["session_id"] == session_id
            assert message["data"]["interaction_id"] == interaction_data["id"]
            assert message["data"]["ai_response"] == interaction_data["ai_response_json"]