# Psychometric Dashboard Implementation Design

## 1. Overview

This design document outlines the implementation of a fully functional, integrated, and dynamically updated psychometric dashboard that transforms existing fragmented components into a cohesive, real-time tool for client profile analysis. The implementation will be divided into two main phases: backend refactoring and API endpoint creation, followed by frontend implementation and real-time integration.

## 2. Backend Architecture

### 2.1 SessionPsychologyEngine Refactoring

The `SessionPsychologyEngine` class in `backend/app/services/session_psychology_service.py` requires refactoring to improve code organization and maintainability.

#### 2.1.1 Profile Merging Method

A new private method `_merge_psychological_profiles` will be created to handle the logic of combining new psychometric analysis with existing cumulative session profiles:

```python
def _merge_psychological_profiles(self, existing_profile: dict, new_analysis: dict) -> dict:
    """
    Merge new psychometric analysis with existing cumulative profile.
    
    Args:
        existing_profile: Current cumulative psychology profile
        new_analysis: New analysis to be merged
        
    Returns:
        dict: Merged psychology profile with averaged numerical values and updated categorical data
    """
    # Implementation details...
    pass
```

Key features of this method:
- Resilient to missing keys
- Intelligent averaging of numerical values
- Proper updating of categorical data
- Comprehensive logging for tracking profile updates

#### 2.1.2 Method Integration

The existing `update_cumulative_profile` method will be updated to utilize the new `_merge_psychological_profiles` method for profile combination logic.

### 2.2 New API Endpoint

A new endpoint will be added to retrieve psychometric data for a specific session.

#### 2.2.1 Endpoint Specification

Location: `backend/app/routers/sessions.py`

New endpoint: `GET /sessions/{session_id}/psychometrics`

#### 2.2.2 Response Structure

The endpoint will return data in the following JSON structure:

```json
{
  "confidence_score": 85,
  "summary": "Client profile analysis summary",
  "big_five": {
    "openness": {"score": 7, "rationale": "...", "strategy": "..."},
    "conscientiousness": {"score": 8, "rationale": "...", "strategy": "..."},
    "extraversion": {"score": 5, "rationale": "...", "strategy": "..."},
    "agreeableness": {"score": 4, "rationale": "...", "strategy": "..."},
    "neuroticism": {"score": 3, "rationale": "...", "strategy": "..."}
  },
  "archetype": {
    "key": "analityk",
    "name": "🔬 Analityk",
    "confidence": 90,
    "description": "..."
  },
  "disc_profile": {
    "dominance": {"score": 6, "rationale": "...", "strategy": "..."},
    "influence": {"score": 4, "rationale": "...", "strategy": "..."},
    "steadiness": {"score": 3, "rationale": "...", "strategy": "..."},
    "compliance": {"score": 8, "rationale": "...", "strategy": "..."}
  },
  "schwartz_values": [
    {"value_name": "Bezpieczeństwo", "strength": 8, "rationale": "...", "strategy": "...", "is_present": true}
  ],
  "evolution_trend": {
    "big_five_trends": {...},
    "disc_trends": {...},
    "schwartz_trends": {...}
  }
}
```

#### 2.2.3 Error Handling

The endpoint will properly handle cases where a session with the given ID does not exist, returning a 404 error.

## 3. Frontend Architecture

### 3.1 New Hook: usePsychometrics

Location: `frontend/src/hooks/usePsychometrics.js`

#### 3.1.1 Hook Structure

The new hook will manage the psychometric profile state and provide functions to fetch data:

```javascript
const usePsychometrics = (sessionId) => {
  const [psychometricsData, setPsychometricsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fetchPsychometrics = async (sessionId) => {
    // Implementation details...
  };
  
  return {
    psychometricsData,
    loading,
    error,
    fetchPsychometrics
  };
};
```

#### 3.1.2 Data Fetching

The `fetchPsychometrics` function will make an asynchronous request to the new backend endpoint and update the component state with the retrieved data.

### 3.2 PsychometricDashboard Component

Location: `frontend/src/components/psychometrics/PsychometricDashboard.js`

#### 3.2.1 Component Integration

The component will utilize the `usePsychometrics` hook to fetch and manage data for the active session.

#### 3.2.2 Data Propagation

The component will pass appropriate state fragments (big_five, archetype, etc.) as props to existing child components:
- BigFiveRadarChart
- CustomerArchetypeDisplay
- DiscProfileDisplay
- SchwartzValuesList

#### 3.2.3 UI Enhancements

The dashboard will display the summary and confidence_score in its header section.

### 3.3 SessionWorkspace Integration

Location: `frontend/src/pages/SessionWorkspace.js`

#### 3.3.1 Real-time Updates

The hook will be integrated with the session management component to identify when a new interaction is successfully added and processed.

#### 3.3.2 Automatic Refresh

Directly after this event, the `fetchPsychometrics(sessionId)` function will be called to refresh the psychometric dashboard data, ensuring dynamic updates.

## 4. Data Flow Architecture

```mermaid
graph TD
    A[User Interaction] --> B[SessionWorkspace]
    B --> C[New Interaction Added]
    C --> D[Backend Processing]
    D --> E[SessionPsychologyEngine Update]
    E --> F[Cumulative Psychology Updated]
    F --> G[GET /sessions/{id}/psychometrics]
    G --> H[usePsychometrics Hook]
    H --> I[PsychometricDashboard Component]
    I --> J[Visualization Components]
```

## 5. Business Logic Layer

### 5.1 Profile Merging Logic

The `_merge_psychological_profiles` method will implement the following logic:
1. Validate incoming data structures
2. Handle missing keys gracefully
3. Average numerical values with appropriate weighting
4. Update categorical data based on confidence levels
5. Log all changes for audit purposes

### 5.2 Confidence Scoring

The system will calculate and maintain confidence scores for psychometric analysis:
- Track data quality and completeness
- Adjust confidence based on interaction history
- Provide visual indicators of analysis reliability

## 6. API Endpoints Reference

### 6.1 New Endpoint

```
GET /sessions/{session_id}/psychometrics
```

**Description**: Retrieve aggregated psychometric data for a specific session

**Parameters**:
- session_id (path): ID of the session to retrieve data for

**Response**:
- 200: Successful retrieval with psychometric data
- 404: Session not found

### 6.2 Existing Related Endpoints

```
GET /sessions/{session_id}
GET /sessions/
POST /sessions/{session_id}/conclude
```

## 7. Data Models & ORM Mapping

### 7.1 Session Model (Extended)

The existing Session model will be used with additional psychometric fields:

```python
class Session(Base):
    # Existing fields...
    
    # Psychometric fields
    cumulative_psychology = Column(JSONB, nullable=True)
    psychology_confidence = Column(Integer, default=0, nullable=True)
    active_clarifying_questions = Column(JSONB, nullable=True)
    customer_archetype = Column(JSONB, nullable=True)
    psychology_updated_at = Column(DateTime, nullable=True)
    sales_indicators = Column(JSONB, nullable=True)
```

### 7.2 Response Schema

The response will follow the Pydantic schema:

```python
class PsychometricData(BaseModel):
    confidence_score: int
    summary: str
    big_five: dict
    archetype: dict
    disc_profile: dict
    schwartz_values: list
    evolution_trend: dict
```

## 8. Testing Strategy

### 8.1 Backend Testing

Unit tests will be implemented for:
1. Profile merging logic in `_merge_psychological_profiles`
2. API endpoint response formatting
3. Error handling for non-existent sessions
4. Data validation and sanitization

### 8.2 Frontend Testing

Frontend tests will cover:
1. Hook state management
2. Data fetching and error handling
3. Component rendering with various data states
4. Real-time update functionality

### 8.3 Integration Testing

End-to-end tests will verify:
1. Complete data flow from interaction to dashboard update
2. Proper error handling across the stack
3. Performance under various load conditions

## 9. Success Criteria

The implementation will be considered successful when:
1. The GET /sessions/{session_id}/psychometrics endpoint is functional and returns properly formatted data
2. The PsychometricDashboard.js component fully renders all visual data based on API responses
3. After adding a new interaction in SessionWorkspace, the PsychometricDashboard automatically refreshes and displays the updated psychometric profile without manual page refresh