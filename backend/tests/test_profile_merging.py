import pytest
from app.services.session_psychology_service import SessionPsychologyEngine

@pytest.fixture
def psychology_engine():
    """Create an instance of SessionPsychologyEngine for testing"""
    return SessionPsychologyEngine()

def test_merge_psychological_profiles_empty_existing(psychology_engine):
    """Test merging when existing profile is empty"""
    existing_profile = {}
    new_analysis = {
        "big_five": {
            "openness": {"score": 7, "rationale": "Test", "strategy": "Test strategy"}
        }
    }
    
    result = psychology_engine._merge_psychological_profiles(existing_profile, new_analysis)
    
    assert result == new_analysis

def test_merge_psychological_profiles_empty_new(psychology_engine):
    """Test merging when new analysis is empty"""
    existing_profile = {
        "big_five": {
            "openness": {"score": 7, "rationale": "Test", "strategy": "Test strategy"}
        }
    }
    new_analysis = {}
    
    result = psychology_engine._merge_psychological_profiles(existing_profile, new_analysis)
    
    assert result == existing_profile

def test_merge_psychological_profiles_both_empty(psychology_engine):
    """Test merging when both profiles are empty"""
    existing_profile = {}
    new_analysis = {}
    
    result = psychology_engine._merge_psychological_profiles(existing_profile, new_analysis)
    
    assert result == {}

def test_merge_big_five_traits(psychology_engine):
    """Test merging Big Five traits"""
    existing_profile = {
        "big_five": {
            "openness": {"score": 6, "rationale": "Original", "strategy": "Original strategy"}
        }
    }
    
    new_analysis = {
        "big_five": {
            "openness": {"score": 8, "rationale": "Updated", "strategy": "New strategy"},
            "conscientiousness": {"score": 7, "rationale": "New trait", "strategy": "New trait strategy"}
        }
    }
    
    result = psychology_engine._merge_psychological_profiles(existing_profile, new_analysis)
    
    # Check that openness was averaged (6+8)//2 = 7
    assert result["big_five"]["openness"]["score"] == 7
    # Check that rationale and strategy were updated
    assert result["big_five"]["openness"]["rationale"] == "Updated"
    assert result["big_five"]["openness"]["strategy"] == "New strategy"
    # Check that new trait was added
    assert "conscientiousness" in result["big_five"]
    assert result["big_five"]["conscientiousness"]["score"] == 7

def test_merge_disc_profile(psychology_engine):
    """Test merging DISC profile"""
    existing_profile = {
        "disc": {
            "dominance": {"score": 5, "rationale": "Original", "strategy": "Original strategy"}
        }
    }
    
    new_analysis = {
        "disc": {
            "dominance": {"score": 7, "rationale": "Updated", "strategy": "New strategy"},
            "influence": {"score": 6, "rationale": "New trait", "strategy": "New trait strategy"}
        }
    }
    
    result = psychology_engine._merge_psychological_profiles(existing_profile, new_analysis)
    
    # Check that dominance was averaged (5+7)//2 = 6
    assert result["disc"]["dominance"]["score"] == 6
    # Check that rationale and strategy were updated
    assert result["disc"]["dominance"]["rationale"] == "Updated"
    assert result["disc"]["dominance"]["strategy"] == "New strategy"
    # Check that new trait was added
    assert "influence" in result["disc"]
    assert result["disc"]["influence"]["score"] == 6

def test_merge_schwartz_values(psychology_engine):
    """Test merging Schwartz values"""
    existing_profile = {
        "schwartz_values": [
            {"value_name": "Security", "strength": 7, "rationale": "Original", "strategy": "Original strategy", "is_present": True}
        ]
    }
    
    new_analysis = {
        "schwartz_values": [
            {"value_name": "Achievement", "strength": 8, "rationale": "New value", "strategy": "New strategy", "is_present": True},
            {"value_name": "Security", "strength": 9, "rationale": "Updated", "strategy": "Updated strategy", "is_present": True}
        ]
    }
    
    result = psychology_engine._merge_psychological_profiles(existing_profile, new_analysis)
    
    # Schwartz values should be replaced with new ones
    assert len(result["schwartz_values"]) == 2
    assert result["schwartz_values"][0]["value_name"] == "Achievement"
    assert result["schwartz_values"][1]["value_name"] == "Security"
    assert result["schwartz_values"][1]["strength"] == 9

def test_merge_observations_summary(psychology_engine):
    """Test merging observations summary"""
    existing_profile = {
        "observations_summary": "Original summary"
    }
    
    new_analysis = {
        "observations_summary": "Updated summary with new insights"
    }
    
    result = psychology_engine._merge_psychological_profiles(existing_profile, new_analysis)
    
    # Observations summary should be updated
    assert result["observations_summary"] == "Updated summary with new insights"