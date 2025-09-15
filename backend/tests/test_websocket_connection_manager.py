"""
Test cases for WebSocket ConnectionManager
"""
import pytest
import json
from unittest.mock import AsyncMock, Mock
from fastapi import WebSocket

from app.routers.stream import ConnectionManager


class TestConnectionManager:
    """Test cases for the WebSocket ConnectionManager class"""
    
    @pytest.fixture
    def connection_manager(self):
        """Fixture to create a ConnectionManager instance"""
        return ConnectionManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Fixture to create a mock WebSocket"""
        websocket = Mock(spec=WebSocket)
        websocket.accept = AsyncMock()
        websocket.send_text = AsyncMock()
        websocket.receive_text = AsyncMock()
        return websocket
    
    def test_init(self, connection_manager):
        """Test that ConnectionManager initializes correctly"""
        assert isinstance(connection_manager.active_connections, dict)
        assert len(connection_manager.active_connections) == 0
    
    @pytest.mark.asyncio
    async def test_connect(self, connection_manager, mock_websocket):
        """Test connecting a WebSocket"""
        session_id = 123
        await connection_manager.connect(mock_websocket, session_id)
        
        # Verify websocket was accepted
        mock_websocket.accept.assert_called_once()
        
        # Verify connection was stored
        assert session_id in connection_manager.active_connections
        assert mock_websocket in connection_manager.active_connections[session_id]
    
    def test_disconnect(self, connection_manager, mock_websocket):
        """Test disconnecting a WebSocket"""
        session_id = 123
        
        # First connect
        if session_id not in connection_manager.active_connections:
            connection_manager.active_connections[session_id] = []
        connection_manager.active_connections[session_id].append(mock_websocket)
        
        # Then disconnect
        connection_manager.disconnect(mock_websocket, session_id)
        
        # Verify connection was removed
        assert mock_websocket not in connection_manager.active_connections.get(session_id, [])
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self, connection_manager, mock_websocket):
        """Test sending a message to a WebSocket"""
        session_id = 123
        message = {"event": "test", "data": "test data"}
        
        # First connect
        if session_id not in connection_manager.active_connections:
            connection_manager.active_connections[session_id] = []
        connection_manager.active_connections[session_id].append(mock_websocket)
        
        # Send message
        await connection_manager.send_personal_message(message, session_id)
        
        # Verify message was sent
        mock_websocket.send_text.assert_called_once_with(json.dumps(message))
    
    @pytest.mark.asyncio
    async def test_send_personal_message_no_connections(self, connection_manager):
        """Test sending a message when there are no connections"""
        session_id = 123
        message = {"event": "test", "data": "test data"}
        
        # Should not raise an exception
        await connection_manager.send_personal_message(message, session_id)