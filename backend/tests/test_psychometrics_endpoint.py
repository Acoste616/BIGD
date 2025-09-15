import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from app.core.database import get_db
from app.models.domain import Session
from unittest.mock import AsyncMock, patch

client = TestClient(app)

@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def override_get_db(mock_db):
    """Override get_db dependency with mock"""
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def sample_session():
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

def test_get_session_psychometrics_success(override_get_db, mock_db, sample_session):
    """Test successful retrieval of session psychometrics"""
    # Mock the session repository response
    mock_db.execute.return_value.scalar_one_or_none.return_value = sample_session
    
    response = client.get("/sessions/1/psychometrics")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that the response contains the expected fields with correct data types
    assert "confidence_score" in data
    assert isinstance(data["confidence_score"], int)
    assert 0 <= data["confidence_score"] <= 100
    
    assert "summary" in data
    assert isinstance(data["summary"], str)
    
    assert "big_five" in data
    assert isinstance(data["big_five"], dict)
    
    assert "archetype" in data
    assert isinstance(data["archetype"], dict)
    
    assert "disc_profile" in data
    assert isinstance(data["disc_profile"], dict)
    
    assert "schwartz_values" in data
    assert isinstance(data["schwartz_values"], list)
    
    assert "evolution_trend" in data
    assert isinstance(data["evolution_trend"], dict)
    
    # Check specific values
    assert data["confidence_score"] == 85
    assert len(data["big_five"]) > 0
    assert data["archetype"]["key"] == "analityk"
    
    # Check Big Five structure
    for trait_name, trait_data in data["big_five"].items():
        assert "score" in trait_data
        assert "rationale" in trait_data
        assert "strategy" in trait_data
        assert isinstance(trait_data["score"], int)
        assert isinstance(trait_data["rationale"], str)
        assert isinstance(trait_data["strategy"], str)
    
    # Check archetype structure
    assert "key" in data["archetype"]
    assert "name" in data["archetype"]
    assert "confidence" in data["archetype"]
    assert "description" in data["archetype"]
    assert isinstance(data["archetype"]["confidence"], int)
    
    # Check that there are no null values in critical fields
    assert data["big_five"] is not None
    assert data["archetype"] is not None
    assert data["disc_profile"] is not None

def test_get_session_psychometrics_not_found(override_get_db, mock_db):
    """Test retrieval of psychometrics for non-existent session"""
    # Mock the session repository to return None
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    
    response = client.get("/sessions/999/psychometrics")
    
    assert response.status_code == 404
    assert "nie została znaleziona" in response.json()["detail"]


def test_get_session_psychometrics_zero_id(override_get_db, mock_db):
    """Test retrieval of psychometrics with zero session ID"""
    # Mock the session repository to return None for zero ID
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    
    response = client.get("/sessions/0/psychometrics")
    
    assert response.status_code == 404
    assert "nie została znaleziona" in response.json()["detail"]

def test_get_session_psychometrics_empty_data(override_get_db, mock_db):
    """Test retrieval of psychometrics when session has no psychometric data"""
    empty_session = Session(
        id=1,
        client_id=1,
        is_active=1,
        cumulative_psychology=None,
        psychology_confidence=None,
        customer_archetype=None
    )
    
    mock_db.execute.return_value.scalar_one_or_none.return_value = empty_session
    
    response = client.get("/sessions/1/psychometrics")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return empty structures but no error
    assert data["confidence_score"] == 0
    assert data["big_five"] == {}
    assert data["disc_profile"] == {}
    assert data["schwartz_values"] == []


def test_get_session_psychometrics_partial_data(override_get_db, mock_db):
    """Test retrieval of psychometrics when session has partial psychometric data"""
    partial_session = Session(
        id=1,
        client_id=1,
        is_active=1,
        cumulative_psychology={
            "big_five": {
                "openness": {"score": 7, "rationale": "High openness", "strategy": "Innovative approach"}
            },
            "disc": {},
            "schwartz_values": []
        },
        psychology_confidence=60,
        customer_archetype={
            "key": "entuzjasta",
            "name": "🎯 Entuzjasta",
            "confidence": 70,
            "description": "Enthusiastic customer profile"
        }
    )
    
    mock_db.execute.return_value.scalar_one_or_none.return_value = partial_session
    
    response = client.get("/sessions/1/psychometrics")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return partial data correctly
    assert data["confidence_score"] == 60
    assert len(data["big_five"]) == 1
    assert "openness" in data["big_five"]
    assert data["archetype"]["key"] == "entuzjasta"
    assert isinstance(data["disc_profile"], dict)
    assert isinstance(data["schwartz_values"], list)


def test_get_session_psychometrics_invalid_session_id(override_get_db, mock_db):
    """Test retrieval of psychometrics with invalid session ID format"""
    # Mock the session repository to return None for invalid ID
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    
    response = client.get("/sessions/invalid/psychometrics")
    
    # Should return 422 for validation error
    assert response.status_code == 422
    
    # Check that all required fields are present even with empty data
    assert "summary" in data
    assert "archetype" in data
    assert "evolution_trend" in data
    assert isinstance(data["summary"], str)
    assert isinstance(data["archetype"], dict)
    assert isinstance(data["evolution_trend"], dict)