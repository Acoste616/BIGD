# Feedback Loop Implementation Design

## 1. Overview

### 1.1 Purpose
This document outlines the design for implementing a comprehensive feedback loop system that enables the AI to learn from user feedback. Each rating (positive or negative) will become a permanent lesson for the AI, influencing its future recommendations.

### 1.2 System Architecture
The feedback loop system consists of two main components:
- Backend modifications to process feedback and create knowledge nuggets
- Frontend enhancements to provide immediate user feedback

### 1.3 Key Components
- Feedback processing in `feedback.py` router
- Knowledge nugget creation in `dojo_service.py`
- Qdrant integration for long-term knowledge storage
- Frontend feedback buttons with visual feedback

## 2. Backend Architecture

### 2.1 Current Feedback Flow
The current system has a basic feedback mechanism:
1. User clicks feedback button (thumbs up/down)
2. Feedback is stored in PostgreSQL database
3. Feedback data is stored in the `feedbacks` table with:
   - interaction_id
   - suggestion_id
   - rating (1 or -1)
   - feedback_type
   - is_processed_for_learning (flag to track if feedback was processed for learning)

### 2.2 Enhanced Feedback Flow
The new system will extend this flow:
1. User provides feedback through existing interface
2. System creates knowledge nugget based on feedback and AI suggestion
3. Knowledge nugget is vectorized and stored in Qdrant
4. Feedback record is marked as processed
5. AI can retrieve this knowledge in future interactions

### 2.3 Component Interactions
``mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant FeedbackRouter
    participant PostgreSQL
    participant DojoService
    participant QdrantService
    participant Qdrant

    User->>Frontend: Clicks feedback button
    Frontend->>FeedbackRouter: POST /interactions/{id}/feedback/
    FeedbackRouter->>PostgreSQL: Store feedback record
    FeedbackRouter->>DojoService: process_feedback_for_learning(feedback_id)
    DojoService->>PostgreSQL: Get feedback & interaction details
    DojoService->>DojoService: Create knowledge nugget
    DojoService->>QdrantService: add_knowledge(knowledge_data)
    QdrantService->>Qdrant: Store vectorized knowledge
    DojoService->>PostgreSQL: Mark feedback as processed
    FeedbackRouter->>Frontend: Return success response
```

## 3. Detailed Design

### 3.1 Backend Modifications

#### 3.1.1 Feedback Router Enhancement (`backend/app/routers/feedback.py`)
The feedback router will be enhanced to trigger the learning process after storing feedback:

1. After successfully storing feedback in PostgreSQL
2. Call the new `process_feedback_for_learning` method in DojoService
3. Handle any errors during the learning process without failing the feedback storage
4. Return success response to frontend

**Implementation Details:**
```python
# In the create_feedback endpoint
async def create_feedback(
    feedback: FeedbackCreate,
    interaction_id: int = Path(..., description="ID interakcji"), 
    db: AsyncSession = Depends(get_db)
):
    # Store feedback (existing functionality)
    interaction = await feedback_repository.add_feedback(db=db, feedback_data=feedback)
    
    # Trigger learning process (new functionality)
    try:
        # Get the ID of the newly created feedback
        # This requires modifying the feedback repository to return the feedback ID
        # or retrieving the latest feedback for this interaction
        await dojo_service.process_feedback_for_learning(
            interaction_id=interaction_id,
            suggestion_id=feedback.suggestion_id,
            suggestion_type=feedback.suggestion_type,
        )
    except Exception as e:
        # Log error but don't fail the feedback storage
        logger.error(f"Failed to process feedback for learning: {e}")
    
    return interaction
```

#### 3.1.2 Dojo Service Enhancement (`backend/app/services/dojo_service.py`)
A new method `process_feedback_for_learning` will be added to create knowledge nuggets:

1. Retrieve feedback record and associated interaction data
2. Extract AI suggestion content using suggestion_id
3. Create knowledge nugget based on feedback type:
   - Positive feedback: "For client with archetype 'X', suggestion about Y was effective"
   - Negative feedback: "For client with archetype 'X', suggestion based on Y was ineffective"
4. Pass knowledge nugget to QdrantService for storage
5. Mark feedback record as processed

**Implementation Details:**
```python
class AdminDialogueService:
    # ... existing code ...
    
    async def process_feedback_for_learning(
        self,
        interaction_id: int,
        suggestion_id: str,
        suggestion_type: str,
        rating: int
    ) -> bool:
        """
        Process feedback for learning by creating knowledge nuggets
        
        Args:
            interaction_id: ID of the interaction
            suggestion_id: ID of the suggestion being rated
            suggestion_type: Type of suggestion (quick_response, suggested_action)
            rating: Rating value (1 for positive, -1 for negative)
            

        Returns:
            bool: True if processing was successful
        """
        try:
            # 1. Retrieve interaction and session data
            interaction = await self._get_interaction(interaction_id)
            if not interaction:
                logger.error(f"Interaction {interaction_id} not found")
                return False
            
            session = await self._get_session(interaction.session_id)
            client = await self._get_client(session.client_id)
            
            # 2. Extract suggestion content from AI response
            suggestion_content = self._extract_suggestion_content(
                interaction.ai_response_json,
                suggestion_id,
                suggestion_type
            )
            
            if not suggestion_content:
                logger.error(f"Suggestion {suggestion_id} not found in interaction {interaction_id}")
                return False
            
            # 3. Create knowledge nugget
            knowledge_nugget = self._create_knowledge_nugget(
                client=client,
                suggestion_content=suggestion_content,
                suggestion_type=suggestion_type,
                rating=rating
            )
            
            # 4. Store in Qdrant
            await self.qdrant_service.add_knowledge(
                content=knowledge_nugget["content"],
                title=knowledge_nugget["title"],
                knowledge_type=knowledge_nugget["knowledge_type"],
                archetype=knowledge_nugget["archetype"],
                tags=knowledge_nugget["tags"],
                source=knowledge_nugget["source"]
            )
            
            # 5. Mark feedback as processed
            await self._mark_feedback_as_processed(interaction_id, suggestion_id)
            
            logger.info(f"Successfully processed feedback for learning: {suggestion_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing feedback for learning: {e}")
            return False
    
    def _extract_suggestion_content(
        self,
        ai_response: Dict[str, Any],
        suggestion_id: str,
        suggestion_type: str
    ) -> Optional[str]:
        """
        Extract suggestion content from AI response based on ID and type
        """
        if suggestion_type == "quick_response":
            if ai_response.get("quick_response", {}).get("id") == suggestion_id:
                return ai_response["quick_response"]["text"]
        elif suggestion_type == "suggested_action":
            for action in ai_response.get("suggested_actions", []):
                if action.get("id") == suggestion_id:
                    return action.get("text") or action.get("action")
        
        return None
    
    def _create_knowledge_nugget(
        self,
        client: Any,
        suggestion_content: str,
        suggestion_type: str,
        rating: int
    ) -> Dict[str, Any]:
        """
        Create a knowledge nugget from feedback data
        """
        client_archetype = getattr(client, "archetype", "Unknown")
        
        if rating > 0:  # Positive feedback
            title = f"Effective {suggestion_type} for {client_archetype} archetype"
            content = f"For client with archetype '{client_archetype}', suggestion '{suggestion_content}' was effective."
        else:  # Negative feedback
            title = f"Ineffective {suggestion_type} for {client_archetype} archetype"
            content = f"For client with archetype '{client_archetype}', suggestion '{suggestion_content}' was ineffective."
        
        return {
            "title": title,
            "content": content,
            "knowledge_type": "feedback_learning",
            "archetype": client_archetype,
            "tags": ["feedback", "learning", suggestion_type],
            "source": "user_feedback"
        }
```

#### 3.1.3 Knowledge Nugget Structure
Each knowledge nugget will contain:
- Title: Brief description of the learning
- Content: Detailed learning from the feedback
- Knowledge type: "feedback_learning"
- Archetype: Client archetype (if available)
- Tags: ["feedback", "learning", suggestion_type]
- Source: "user_feedback"

### 3.2 Frontend Modifications

#### 3.2.1 Feedback Buttons Component (`frontend/src/components/FeedbackButtons.js`)
Enhancements to provide immediate visual feedback:
1. Add loading state during feedback submission
2. Show success message after feedback is processed
3. Implement subtle animation or color change to confirm receipt

**Implementation Details:**
```javascript
const FeedbackButtons = ({ 
  interactionId, 
  suggestionId, 
  suggestionType,
  onFeedbackSent = null 
}) => {
  const [feedback, setFeedback] = useState(null); // null, 1, -1
  const [loading, setLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleFeedback = async (score) => {
    if (loading || feedback === score) return;
    
    setLoading(true);
    try {
      const feedbackData = {
        interaction_id: interactionId,
        suggestion_id: suggestionId,
        suggestion_type: suggestionType,
        score: score
      };

      await feedbackApi.createFeedback(interactionId, feedbackData);
      setFeedback(score);
      
      // Show success message
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
      
      if (onFeedbackSent) {
        onFeedbackSent(suggestionId, score);
      }
      
    } catch (error) {
      console.error('❌ Błąd podczas wysyłania feedback:', error);
      // Show error message
    } finally {
      setLoading(false);
    }
  };

  if (showSuccess) {
    return (
      <Chip
        icon={<CheckCircle />}
        label="Dziękujemy, uczę się!"
        color="success"
        size="small"
        variant="filled"
      />
    );
  }

  if (feedback !== null) {
    return (
      <Chip
        icon={<CheckCircle />}
        label={feedback === 1 ? "Przydatne" : "Nie przydatne"}
        color={feedback === 1 ? "success" : "error"}
        size="small"
        variant="filled"
      />
    );
  }

  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <Tooltip title="Przydatna sugestia">
        <IconButton
          size="small"
          onClick={() => handleFeedback(1)}
          disabled={loading}
          sx={{
            color: 'success.main',
            '&:hover': { backgroundColor: 'success.lighter' }
          }}
        >
          <ThumbUp fontSize="small" />
        </IconButton>
      </Tooltip>
      
      <Tooltip title="Nie przydatna sugestia">
        <IconButton
          size="small"
          onClick={() => handleFeedback(-1)}
          disabled={loading}
          sx={{
            color: 'error.main',
            '&:hover': { backgroundColor: 'error.lighter' }
          }}
        >
          <ThumbDown fontSize="small" />
        </IconButton>
      </Tooltip>
      
      {loading && <CircularProgress size={20} />}
    </Box>
  );
};
```

#### 3.2.2 Feedback Hook (`frontend/src/hooks/useInteractionFeedback.js`)
Update to handle new feedback flow:
1. Maintain compatibility with existing API
2. Add success/error handling for feedback submission
3. Provide visual feedback state to components

**Implementation Details:**
```javascript
export const useInteractionFeedback = (interactionId) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [submittedRating, setSubmittedRating] = useState(null);
  const [feedbackData, setFeedbackData] = useState(null);

  const submitFeedback = async (rating) => {
    // Sprawdź czy już zagłosowano
    if (submittedRating !== null) {
      console.warn('Feedback już został wysłany dla tej interakcji');
      return;
    }

    // Walidacja rating
    if (rating !== 1 && rating !== -1) {
      setError('Nieprawidłowa ocena. Użyj 1 lub -1.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // DEPRECATED: Stary hook - używaj FeedbackButtons dla granularnego feedback
      const response = { success: true };
      setSubmittedRating(rating);
      setFeedbackData(response);
      setSuccess('Dziękujemy, uczę się!');
      
      // Auto-clear success state po 3 sekundach
      setTimeout(() => {
        setSuccess(null);
      }, 3000);

    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Nie udało się zapisać oceny. Spróbuj ponownie.';
      setError(errorMessage);
      console.error('Feedback submission failed:', err);
      
      // Auto-clear error po 5 sekundach
      setTimeout(() => {
        setError(null);
      }, 5000);
    } finally {
      setIsLoading(false);
    }
  };

  const resetFeedback = () => {
    setSubmittedRating(null);
    setFeedbackData(null);
    setError(null);
    setSuccess(null);
    setIsLoading(false);
  };

  const canVote = !isLoading && submittedRating === null;
  const isPositiveVote = submittedRating === 1;
  const isNegativeVote = submittedRating === -1;
  const hasVoted = submittedRating !== null;

  return {
    // Stan
    isLoading,
    error,
    success,
    submittedRating,
    feedbackData,
    hasVoted,
    
    // Helper flags
    canVote,
    isPositiveVote,
    isNegativeVote,
    
    // Funkcje
    submitFeedback,
    resetFeedback
  };
};
```

## 4. Data Models

### 4.1 Feedback Model (Existing)

The existing Feedback model will be used with a minor modification to track if feedback has been processed for learning. The `is_processed_for_learning` field already exists and will be utilized for this purpose.
```python
class Feedback(Base):
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False)
    suggestion_id = Column(String(36), nullable=True, index=True)
    rating = Column(Integer, nullable=False)  # 1 (positive) or -1 (negative)
    feedback_type = Column(String, nullable=True)  # quick_response, suggested_action
    comment = Column(Text, nullable=True)
    is_processed_for_learning = Column(Integer, nullable=False, default=0, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### 4.2 Knowledge Nugget Structure (New)
```javascript
{
  title: "Feedback Learning: [Summary]",
  content: "[Detailed learning from feedback]",
  knowledge_type: "feedback_learning",
  archetype: "[Client archetype if available]",
  tags: ["feedback", "learning", "[suggestion_type]"],
  source: "user_feedback"
}
```

## 5. Implementation Plan

### 5.1 Phase 1: Backend Implementation
1. Enhance feedback router to trigger learning process
2. Implement knowledge nugget creation in DojoService
3. Add method to mark feedback as processed
4. Implement error handling and logging

### 5.2 Phase 2: Frontend Implementation
1. Update FeedbackButtons component with visual feedback
2. Enhance useInteractionFeedback hook
3. Test integration with backend

### 5.3 Phase 3: Testing and Validation
1. Unit tests for new backend functionality
2. Integration tests for complete feedback loop
3. Validate knowledge storage in Qdrant
4. Verify feedback processing flag works correctly

## 6. Testing Strategy

### 6.1 Unit Tests
- Test knowledge nugget creation with different feedback types
- Test suggestion content extraction from AI responses
- Test error handling in feedback processing

### 6.2 Integration Tests
- Test complete feedback loop from user action to Qdrant storage
- Test error scenarios (missing interaction data, Qdrant unavailable)
- Test that feedback is still stored even if learning process fails

### 6.3 Manual Testing
- Verify visual feedback in UI
- Confirm knowledge nuggets are created correctly
- Validate that processed feedback flag is set

## 6. Error Handling

### 6.1 Failure Scenarios
1. Failed to retrieve interaction data
2. Failed to extract suggestion content
3. Failed to create knowledge nugget
4. Failed to store in Qdrant
5. Failed to mark feedback as processed

### 6.2 Recovery Mechanisms
1. Log errors with detailed context
2. Retry mechanism for Qdrant storage
3. Ensure feedback is still stored even if learning process fails
4. Provide monitoring for unprocessed feedback

## 7. Monitoring and Metrics

### 7.1 Key Metrics
1. Number of feedback items processed for learning
2. Success rate of knowledge nugget creation
3. Qdrant storage success rate
4. Time taken to process feedback for learning

### 7.2 Monitoring Implementation
1. Add logging for each step of the process
2. Create metrics for success/failure rates
3. Set up alerts for critical failures

### 7.3 Logging Details
- Log when feedback is received for processing
- Log successful knowledge nugget creation
- Log Qdrant storage operations
- Log when feedback is marked as processed
- Log any errors with detailed context

### 7.4 Prometheus Metrics
- Counter for feedback items processed
- Counter for successful knowledge nugget creations
- Counter for Qdrant storage operations
- Histogram for processing time
- Counter for errors by type
