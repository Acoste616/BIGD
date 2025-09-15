#!/usr/bin/env python3
"""
Simple test for the profile merging functionality without external dependencies
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.session_psychology_service import SessionPsychologyEngine

def test_merge_profiles():
    """Test the profile merging functionality"""
    engine = SessionPsychologyEngine()
    
    # Test case 1: Empty existing profile
    existing = {}
    new = {
        "big_five": {
            "openness": {"score": 7, "rationale": "Test", "strategy": "Test strategy"}
        }
    }
    
    result = engine._merge_psychological_profiles(existing, new)
    assert result == new, f"Expected {new}, got {result}"
    print("✓ Test 1 passed: Empty existing profile")
    
    # Test case 2: Merge Big Five traits
    existing = {
        "big_five": {
            "openness": {"score": 6, "rationale": "Original", "strategy": "Original strategy"}
        }
    }
    
    new = {
        "big_five": {
            "openness": {"score": 8, "rationale": "Updated", "strategy": "New strategy"},
            "conscientiousness": {"score": 7, "rationale": "New trait", "strategy": "New trait strategy"}
        }
    }
    
    result = engine._merge_psychological_profiles(existing, new)
    
    # Check that openness was averaged (6+8)//2 = 7
    assert result["big_five"]["openness"]["score"] == 7, f"Expected score 7, got {result['big_five']['openness']['score']}"
    # Check that rationale and strategy were updated
    assert result["big_five"]["openness"]["rationale"] == "Updated", f"Expected 'Updated', got {result['big_five']['openness']['rationale']}"
    assert result["big_five"]["openness"]["strategy"] == "New strategy", f"Expected 'New strategy', got {result['big_five']['openness']['strategy']}"
    # Check that new trait was added
    assert "conscientiousness" in result["big_five"], "conscientiousness should be in result"
    assert result["big_five"]["conscientiousness"]["score"] == 7, f"Expected score 7, got {result['big_five']['conscientiousness']['score']}"
    
    print("✓ Test 2 passed: Merge Big Five traits")
    
    # Test case 3: Merge DISC profile
    existing = {
        "disc": {
            "dominance": {"score": 5, "rationale": "Original", "strategy": "Original strategy"}
        }
    }
    
    new = {
        "disc": {
            "dominance": {"score": 7, "rationale": "Updated", "strategy": "New strategy"},
            "influence": {"score": 6, "rationale": "New trait", "strategy": "New trait strategy"}
        }
    }
    
    result = engine._merge_psychological_profiles(existing, new)
    
    # Check that dominance was averaged (5+7)//2 = 6
    assert result["disc"]["dominance"]["score"] == 6, f"Expected score 6, got {result['disc']['dominance']['score']}"
    # Check that new trait was added
    assert "influence" in result["disc"], "influence should be in result"
    assert result["disc"]["influence"]["score"] == 6, f"Expected score 6, got {result['disc']['influence']['score']}"
    
    print("✓ Test 3 passed: Merge DISC profile")
    
    print("All tests passed! ✅")

if __name__ == "__main__":
    test_merge_profiles()