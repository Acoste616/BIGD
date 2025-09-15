"""
Integration tests for session endpoints
"""
import sys
import os
import pytest

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fastapi.testclient import TestClient
from main import app
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.domain import Client, Session as SessionModel
from datetime import datetime

client = TestClient(app)

# Test data setup
@pytest.fixture(scope="function")
def test_db():
    """Create test database session"""
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    # Create a test client
    test_client = Client(alias="Test Client")
    db.add(test_client)
    db.commit()
    db.refresh(test_client)
    
    yield db, test_client
    
    # Cleanup
    # Delete all sessions for this client first
    sessions = db.query(SessionModel).filter(SessionModel.client_id == test_client.id).all()
    for session in sessions:
        db.delete(session)
    db.delete(test_client)
    db.commit()

def test_session_lifecycle_integration(test_db):
    """Test the complete session lifecycle: create, list, conclude, list again"""
    db, test_client = test_db
    
    # 1. Create a new session via API
    response = client.post(f"/api/v1/clients/{test_client.id}/sessions/")
    assert response.status_code == 201
    
    created_session = response.json()
    session_id = created_session["id"]
    assert created_session["client_id"] == test_client.id
    assert created_session["status"] == "active"
    
    # 2. List all sessions and verify our session is there
    response = client.get("/api/v1/sessions/")
    assert response.status_code == 200
    
    sessions = response.json()
    session_ids = [s["id"] for s in sessions]
    assert session_id in session_ids
    
    # Find our session in the list
    our_session = next(s for s in sessions if s["id"] == session_id)
    assert our_session["status"] == "active"
    
    # 3. Conclude the session
    conclusion_data = {
        "outcome": "interested",
        "notes": "Client showed interest in our product",
        "summary": "Positive interaction with potential for closing a deal"
    }
    
    response = client.post(f"/api/v1/sessions/{session_id}/conclude", json=conclusion_data)
    assert response.status_code == 200
    
    concluded_session = response.json()
    assert concluded_session["id"] == session_id
    assert concluded_session["status"] == "closed"
    assert concluded_session["outcome_data"]["outcome"] == "interested"
    assert concluded_session["outcome_data"]["notes"] == "Client showed interest in our product"
    assert concluded_session["outcome_data"]["summary"] == "Positive interaction with potential for closing a deal"
    
    # 4. List all sessions again and verify status changed
    response = client.get("/api/v1/sessions/")
    assert response.status_code == 200
    
    sessions = response.json()
    our_session = next(s for s in sessions if s["id"] == session_id)
    assert our_session["status"] == "closed"
    
    # 5. Try to conclude the session again (should fail)
    response = client.post(f"/api/v1/sessions/{session_id}/conclude", json=conclusion_data)
    assert response.status_code == 400
    assert "jest już zamknięta" in response.json()["detail"]