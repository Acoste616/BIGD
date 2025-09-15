#!/usr/bin/env python3
"""
Standalone test for the profile merging functionality
"""

def merge_psychological_profiles(existing_profile: dict, new_analysis: dict) -> dict:
    """
    Merge new psychometric analysis with existing cumulative profile.
    
    Args:
        existing_profile: Current cumulative psychology profile
        new_analysis: New analysis to be merged
        
    Returns:
        dict: Merged psychology profile with averaged numerical values and updated categorical data
    """
    if not existing_profile:
        return new_analysis.copy() if new_analysis else {}
        
    if not new_analysis:
        return existing_profile.copy()
    
    # Create a copy of the existing profile to avoid modifying the original
    merged_profile = existing_profile.copy()
    
    try:
        # Merge Big Five traits
        if "big_five" in new_analysis and new_analysis["big_five"]:
            if "big_five" not in merged_profile:
                merged_profile["big_five"] = {}
            
            for trait_name, trait_data in new_analysis["big_five"].items():
                if trait_name in merged_profile["big_five"] and merged_profile["big_five"][trait_name]:
                    # Average the scores with appropriate weighting
                    existing_trait = merged_profile["big_five"][trait_name]
                    new_trait = trait_data
                    
                    # Simple averaging for scores
                    if "score" in existing_trait and "score" in new_trait:
                        merged_profile["big_five"][trait_name]["score"] = (
                            existing_trait["score"] + new_trait["score"]
                        ) // 2
                    
                    # Update rationale and strategy with new data
                    if "rationale" in new_trait:
                        merged_profile["big_five"][trait_name]["rationale"] = new_trait["rationale"]
                    if "strategy" in new_trait:
                        merged_profile["big_five"][trait_name]["strategy"] = new_trait["strategy"]
                else:
                    # Add new trait
                    merged_profile["big_five"][trait_name] = trait_data.copy()
        
        # Merge DISC profile
        if "disc" in new_analysis and new_analysis["disc"]:
            if "disc" not in merged_profile:
                merged_profile["disc"] = {}
            
            for trait_name, trait_data in new_analysis["disc"].items():
                if trait_name in merged_profile["disc"] and merged_profile["disc"][trait_name]:
                    # Average the scores with appropriate weighting
                    existing_trait = merged_profile["disc"][trait_name]
                    new_trait = trait_data
                    
                    # Simple averaging for scores
                    if "score" in existing_trait and "score" in new_trait:
                        merged_profile["disc"][trait_name]["score"] = (
                            existing_trait["score"] + new_trait["score"]
                        ) // 2
                    
                    # Update rationale and strategy with new data
                    if "rationale" in new_trait:
                        merged_profile["disc"][trait_name]["rationale"] = new_trait["rationale"]
                    if "strategy" in new_trait:
                        merged_profile["disc"][trait_name]["strategy"] = new_trait["strategy"]
                else:
                    # Add new trait
                    merged_profile["disc"][trait_name] = trait_data.copy()
        
        # Merge Schwartz values
        if "schwartz_values" in new_analysis and new_analysis["schwartz_values"]:
            if "schwartz_values" not in merged_profile:
                merged_profile["schwartz_values"] = []
            
            # For simplicity, we'll replace the Schwartz values with the new ones
            # In a more sophisticated implementation, we might want to merge them
            merged_profile["schwartz_values"] = new_analysis["schwartz_values"].copy()
        
        # Update observations summary if present
        if "observations_summary" in new_analysis:
            merged_profile["observations_summary"] = new_analysis["observations_summary"]
        
        return merged_profile
        
    except Exception as e:
        # Return the existing profile if merging fails
        return existing_profile

def test_merge_profiles():
    """Test the profile merging functionality"""
    
    # Test case 1: Empty existing profile
    existing = {}
    new = {
        "big_five": {
            "openness": {"score": 7, "rationale": "Test", "strategy": "Test strategy"}
        }
    }
    
    result = merge_psychological_profiles(existing, new)
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
    
    result = merge_psychological_profiles(existing, new)
    
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
    
    result = merge_psychological_profiles(existing, new)
    
    # Check that dominance was averaged (5+7)//2 = 6
    assert result["disc"]["dominance"]["score"] == 6, f"Expected score 6, got {result['disc']['dominance']['score']}"
    # Check that new trait was added
    assert "influence" in result["disc"], "influence should be in result"
    assert result["disc"]["influence"]["score"] == 6, f"Expected score 6, got {result['disc']['influence']['score']}"
    
    print("✓ Test 3 passed: Merge DISC profile")
    
    # Test case 4: Merge Schwartz values
    existing = {
        "schwartz_values": [
            {"value_name": "Security", "strength": 7, "rationale": "Original", "strategy": "Original strategy", "is_present": True}
        ]
    }
    
    new = {
        "schwartz_values": [
            {"value_name": "Achievement", "strength": 8, "rationale": "New value", "strategy": "New strategy", "is_present": True},
            {"value_name": "Security", "strength": 9, "rationale": "Updated", "strategy": "Updated strategy", "is_present": True}
        ]
    }
    
    result = merge_psychological_profiles(existing, new)
    
    # Schwartz values should be replaced with new ones
    assert len(result["schwartz_values"]) == 2
    assert result["schwartz_values"][0]["value_name"] == "Achievement"
    assert result["schwartz_values"][1]["value_name"] == "Security"
    assert result["schwartz_values"][1]["strength"] == 9
    
    print("✓ Test 4 passed: Merge Schwartz values")
    
    print("All tests passed! ✅")

if __name__ == "__main__":
    test_merge_profiles()