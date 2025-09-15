"""
Test for the new session endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
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
    db.delete(test_client)
    db.commit()

@pytest.fixture(scope="function")
def test_session(test_db):
    """Create a test session"""
    db, test_client = test_db
    
    # Create a test session
    test_session = SessionModel(
        client_id=test_client.id,
        status="active",
        start_timestamp=datetime.utcnow()
    )
    db.add(test_session)
    db.commit()
    db.refresh(test_session)
    
    yield db, test_client, test_session
    
    # Cleanup
    db.delete(test_session)
    db.commit()

def test_get_all_sessions_empty():
    """Test the GET /sessions/ endpoint with no sessions"""
    response = client.get("/sessions/")
    assert response.status_code == 200
    # Since we don't have sessions in the test database, we expect an empty list
    assert response.json() == []

def test_get_all_sessions_with_data(test_session):
    """Test the GET /sessions/ endpoint with sessions"""
    db, test_client, test_session_obj = test_session
    
    response = client.get("/sessions/")
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) > 0
    
    # Check if our test session is in the list
    session_ids = [s["id"] for s in sessions]
    assert test_session_obj.id in session_ids

def test_conclude_session_success(test_session):
    """Test the POST /sessions/{session_id}/conclude endpoint with valid data"""
    db, test_client, test_session_obj = test_session
    
    conclusion_data = {
        "outcome": "interested",
        "notes": "Test notes",
        "summary": "Test summary"
    }
    
    response = client.post(f"/sessions/{test_session_obj.id}/conclude", json=conclusion_data)
    assert response.status_code == 200
    
    # Check response data
    updated_session = response.json()
    assert updated_session["id"] == test_session_obj.id
    assert updated_session["status"] == "closed"
    assert updated_session["outcome_data"]["outcome"] == "interested"
    assert updated_session["outcome_data"]["notes"] == "Test notes"
    assert updated_session["outcome_data"]["summary"] == "Test summary"

def test_conclude_session_not_found():
    """Test the POST /sessions/{session_id}/conclude endpoint with invalid session ID"""
    conclusion_data = {
        "outcome": "interested",
        "notes": "Test notes",
        "summary": "Test summary"
    }
    
    response = client.post("/sessions/999999/conclude", json=conclusion_data)
    # This should return a 404 since session 999999 doesn't exist
    assert response.status_code == 404
    assert "nie została znaleziona" in response.json()["detail"]

def test_conclude_session_already_closed(test_session):
    """Test the POST /sessions/{session_id}/conclude endpoint for already closed session"""
    db, test_client, test_session_obj = test_session
    
    # First, close the session
    conclusion_data = {
        "outcome": "interested",
        "notes": "Test notes",
        "summary": "Test summary"
    }
    
    response = client.post(f"/sessions/{test_session_obj.id}/conclude", json=conclusion_data)
    assert response.status_code == 200
    
    # Try to close it again
    response = client.post(f"/sessions/{test_session_obj.id}/conclude", json=conclusion_data)
    assert response.status_code == 400
    assert "jest już zamknięta" in response.json()["detail"]

def test_conclude_session_minimal_data(test_session):
    """Test the POST /sessions/{session_id}/conclude endpoint with minimal data"""
    db, test_client, test_session_obj = test_session
    
    # Only required field
    conclusion_data = {
        "outcome": "not_interested"
    }
    
    response = client.post(f"/sessions/{test_session_obj.id}/conclude", json=conclusion_data)
    assert response.status_code == 200
    
    # Check response data
    updated_session = response.json()
    assert updated_session["id"] == test_session_obj.id
    assert updated_session["status"] == "closed"
    assert updated_session["outcome_data"]["outcome"] == "not_interested"
    assert updated_session["outcome_data"]["notes"] is None
    assert updated_session["outcome_data"]["summary"] is None