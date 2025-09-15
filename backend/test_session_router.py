"""
Unit tests for the session router endpoints
"""
import pytest
from app.schemas.session import SessionConclusion

# Test the SessionConclusion schema
def test_session_conclusion_schema():
    """Test that the SessionConclusion schema works correctly"""
    # Valid data
    conclusion = SessionConclusion(
        outcome="interested",
        notes="Test notes",
        summary="Test summary"
    )
    assert conclusion.outcome == "interested"
    assert conclusion.notes == "Test notes"
    assert conclusion.summary == "Test summary"
    
    # Valid data with optional fields
    conclusion_min = SessionConclusion(
        outcome="not_interested"
    )
    assert conclusion_min.outcome == "not_interested"
    assert conclusion_min.notes is None
    assert conclusion_min.summary is None