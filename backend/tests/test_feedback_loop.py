"""
Test cases for the feedback loop implementation
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.dojo_service import AdminDialogueService
from app.models.domain import Interaction, Session, Client, Feedback


class TestFeedbackLoop:
    """Test the feedback loop implementation"""

    @pytest.fixture
    def admin_dialogue_service(self):
        """Create an instance of AdminDialogueService for testing"""
        return AdminDialogueService()

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def sample_interaction(self):
        """Create a sample interaction with AI response"""
        interaction = Mock(spec=Interaction)
        interaction.session_id = 1
        interaction.ai_response_json = {
            "quick_response": {
                "id": "qr_123",
                "text": "This is a quick response"
            },
            "suggested_actions": [
                {
                    "id": "sa_456",
                    "text": "This is a suggested action"
                }
            ]
        }
        return interaction

    @pytest.fixture
    def sample_session(self):
        """Create a sample session"""
        session = Mock(spec=Session)
        session.client_id = 1
        return session

    @pytest.fixture
    def sample_client(self):
        """Create a sample client"""
        client = Mock(spec=Client)
        client.archetype = "Driver"
        return client

    @pytest.mark.asyncio
    async def test_process_feedback_for_learning_positive_quick_response(
        self, 
        admin_dialogue_service, 
        mock_db_session,
        sample_interaction,
        sample_session,
        sample_client
    ):
        """Test processing positive feedback for a quick response"""
        # Mock the repositories
        with patch('app.services.dojo_service.InteractionRepository') as mock_interaction_repo, \
             patch('app.services.dojo_service.SessionRepository') as mock_session_repo, \
             patch('app.services.dojo_service.ClientRepository') as mock_client_repo, \
             patch('app.services.dojo_service.FeedbackRepository') as mock_feedback_repo:
            
            # Setup mocks
            mock_interaction_instance = AsyncMock()
            mock_interaction_instance.get_interaction.return_value = sample_interaction
            mock_interaction_repo.return_value = mock_interaction_instance
            
            mock_session_instance = AsyncMock()
            mock_session_instance.get_session.return_value = sample_session
            mock_session_repo.return_value = mock_session_instance
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get_client.return_value = sample_client
            mock_client_repo.return_value = mock_client_instance
            
            mock_feedback_instance = AsyncMock()
            mock_feedback_instance.mark_feedback_as_processed.return_value = True
            mock_feedback_repo.return_value = mock_feedback_instance
            
            # Mock Qdrant service
            admin_dialogue_service.qdrant_service = AsyncMock()
            admin_dialogue_service.qdrant_service.add_knowledge.return_value = "point_123"
            
            # Call the method
            result = await admin_dialogue_service.process_feedback_for_learning(
                feedback_id=1,
                interaction_id=1,
                suggestion_id="qr_123",
                suggestion_type="quick_response",
                rating=1
            )
            
            # Assertions
            assert result is True
            mock_interaction_instance.get_interaction.assert_called_once_with(mock_db_session, 1)
            mock_session_instance.get_session.assert_called_once_with(mock_db_session, 1)
            mock_client_instance.get_client.assert_called_once_with(mock_db_session, 1)
            admin_dialogue_service.qdrant_service.add_knowledge.assert_called_once()
            mock_feedback_instance.mark_feedback_as_processed.assert_called_once_with(mock_db_session, 1)

    @pytest.mark.asyncio
    async def test_process_feedback_for_learning_negative_suggested_action(
        self, 
        admin_dialogue_service, 
        mock_db_session,
        sample_interaction,
        sample_session,
        sample_client
    ):
        """Test processing negative feedback for a suggested action"""
        # Mock the repositories
        with patch('app.services.dojo_service.InteractionRepository') as mock_interaction_repo, \
             patch('app.services.dojo_service.SessionRepository') as mock_session_repo, \
             patch('app.services.dojo_service.ClientRepository') as mock_client_repo, \
             patch('app.services.dojo_service.FeedbackRepository') as mock_feedback_repo:
            
            # Setup mocks
            mock_interaction_instance = AsyncMock()
            mock_interaction_instance.get_interaction.return_value = sample_interaction
            mock_interaction_repo.return_value = mock_interaction_instance
            
            mock_session_instance = AsyncMock()
            mock_session_instance.get_session.return_value = sample_session
            mock_session_repo.return_value = mock_session_instance
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get_client.return_value = sample_client
            mock_client_repo.return_value = mock_client_instance
            
            mock_feedback_instance = AsyncMock()
            mock_feedback_instance.mark_feedback_as_processed.return_value = True
            mock_feedback_repo.return_value = mock_feedback_instance
            
            # Mock Qdrant service
            admin_dialogue_service.qdrant_service = AsyncMock()
            admin_dialogue_service.qdrant_service.add_knowledge.return_value = "point_456"
            
            # Call the method
            result = await admin_dialogue_service.process_feedback_for_learning(
                feedback_id=2,
                interaction_id=1,
                suggestion_id="sa_456",
                suggestion_type="suggested_action",
                rating=-1
            )
            
            # Assertions
            assert result is True
            mock_interaction_instance.get_interaction.assert_called_once_with(mock_db_session, 1)
            mock_session_instance.get_session.assert_called_once_with(mock_db_session, 1)
            mock_client_instance.get_client.assert_called_once_with(mock_db_session, 1)
            admin_dialogue_service.qdrant_service.add_knowledge.assert_called_once()
            mock_feedback_instance.mark_feedback_as_processed.assert_called_once_with(mock_db_session, 2)

    def test_extract_suggestion_content_quick_response(self, admin_dialogue_service):
        """Test extracting content from quick response"""
        ai_response = {
            "quick_response": {
                "id": "qr_123",
                "text": "This is a quick response"
            }
        }
        
        content = admin_dialogue_service._extract_suggestion_content(
            ai_response, "qr_123", "quick_response"
        )
        
        assert content == "This is a quick response"

    def test_extract_suggestion_content_suggested_action(self, admin_dialogue_service):
        """Test extracting content from suggested action"""
        ai_response = {
            "suggested_actions": [
                {
                    "id": "sa_456",
                    "text": "This is a suggested action"
                }
            ]
        }
        
        content = admin_dialogue_service._extract_suggestion_content(
            ai_response, "sa_456", "suggested_action"
        )
        
        assert content == "This is a suggested action"

    def test_create_knowledge_nugget_positive(self, admin_dialogue_service, sample_client):
        """Test creating a positive knowledge nugget"""
        nugget = admin_dialogue_service._create_knowledge_nugget(
            client=sample_client,
            suggestion_content="This is a suggestion",
            suggestion_type="quick_response",
            rating=1
        )
        
        assert nugget["title"] == "Effective quick_response for Driver archetype"
        assert "was effective" in nugget["content"]
        assert nugget["knowledge_type"] == "feedback_learning"
        assert nugget["archetype"] == "Driver"
        assert "feedback" in nugget["tags"]
        assert "learning" in nugget["tags"]
        assert "quick_response" in nugget["tags"]
        assert nugget["source"] == "user_feedback"

    def test_create_knowledge_nugget_negative(self, admin_dialogue_service, sample_client):
        """Test creating a negative knowledge nugget"""
        nugget = admin_dialogue_service._create_knowledge_nugget(
            client=sample_client,
            suggestion_content="This is a suggestion",
            suggestion_type="suggested_action",
            rating=-1
        )
        
        assert nugget["title"] == "Ineffective suggested_action for Driver archetype"
        assert "was ineffective" in nugget["content"]
        assert nugget["knowledge_type"] == "feedback_learning"
        assert nugget["archetype"] == "Driver"
        assert "feedback" in nugget["tags"]
        assert "learning" in nugget["tags"]
        assert "suggested_action" in nugget["tags"]
        assert nugget["source"] == "user_feedback"