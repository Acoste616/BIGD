"""
Simple test script for the feedback loop implementation
"""
import sys
import os
from unittest.mock import Mock, patch

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Mock the Qdrant service to avoid connection issues
with patch('app.services.qdrant_service.QdrantService'):
    from app.services.dojo_service import AdminDialogueService

def test_extract_suggestion_content():
    """Test the _extract_suggestion_content method"""
    service = AdminDialogueService()
    
    # Test quick response extraction
    ai_response = {
        "quick_response": {
            "id": "qr_123",
            "text": "This is a quick response"
        }
    }
    
    content = service._extract_suggestion_content(
        ai_response, "qr_123", "quick_response"
    )
    
    print(f"Quick response content: {content}")
    assert content == "This is a quick response"
    
    # Test suggested action extraction
    ai_response = {
        "suggested_actions": [
            {
                "id": "sa_456",
                "text": "This is a suggested action"
            }
        ]
    }
    
    content = service._extract_suggestion_content(
        ai_response, "sa_456", "suggested_action"
    )
    
    print(f"Suggested action content: {content}")
    assert content == "This is a suggested action"
    
    # Test enhanced extraction with nested structures
    ai_response = {
        "quick_response": {
            "id": "qr_789",
            "content": "This is a quick response with content field"
        }
    }
    
    content = service._extract_suggestion_content(
        ai_response, "qr_789", "quick_response"
    )
    
    print(f"Quick response content (from content field): {content}")
    assert content == "This is a quick response with content field"
    
    print("All tests passed!")

def test_create_knowledge_nugget():
    """Test the _create_knowledge_nugget method"""
    service = AdminDialogueService()
    
    # Create a mock client
    client = Mock()
    client.archetype = "Driver"
    
    # Test positive feedback
    nugget = service._create_knowledge_nugget(
        client=client,
        suggestion_content="This is a suggestion",
        suggestion_type="quick_response",
        rating=1
    )
    
    print(f"Positive nugget title: {nugget['title']}")
    print(f"Positive nugget content: {nugget['content']}")
    assert nugget["title"] == "Effective quick_response for Driver archetype"
    assert "was effective" in nugget["content"]
    
    # Test negative feedback
    nugget = service._create_knowledge_nugget(
        client=client,
        suggestion_content="This is a suggestion",
        suggestion_type="suggested_action",
        rating=-1
    )
    
    print(f"Negative nugget title: {nugget['title']}")
    print(f"Negative nugget content: {nugget['content']}")
    assert nugget["title"] == "Ineffective suggested_action for Driver archetype"
    assert "was ineffective" in nugget["content"]
    
    print("Knowledge nugget tests passed!")

if __name__ == "__main__":
    test_extract_suggestion_content()
    test_create_knowledge_nugget()
    print("All tests completed successfully!")