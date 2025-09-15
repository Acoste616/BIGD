# Module 2 Psychometric Dashboard Testing Procedures

## Overview

This document outlines the comprehensive testing procedures for Module 2 of the UltraBIGDecoder system, specifically focusing on verifying the functionality, stability, and responsiveness of the newly implemented psychometric dashboard. The goal is to ensure that the dashboard works according to specifications and, most importantly, updates automatically after each new interaction.

## Test Coverage Summary

### Backend Endpoint Tests
- **File**: `backend/tests/test_psychometrics_endpoint.py`
- **Test Cases**:
  - TC-B01: Successful Psychometrics Endpoint Request
  - TC-B02: Invalid Session ID Request
  - Additional edge cases for partial data and zero IDs

### Frontend Component Tests
- **Files**: 
  - `frontend/src/hooks/__tests__/useSessionPsychometrics.test.js`
  - `frontend/src/hooks/__tests__/useSessionPsychometricsExtended.test.js`
  - `frontend/src/components/psychometrics/__tests__/PsychometricDashboard.test.js`
  - `frontend/src/components/psychometrics/__tests__/BigFiveRadarChart.test.js`
  - `frontend/src/components/psychometrics/__tests__/DiscProfileDisplay.test.js`
  - `frontend/src/components/psychometrics/__tests__/SchwartzValuesList.test.js`
  - `frontend/src/pages/__tests__/SessionWorkspace.test.js`
- **Test Cases**:
  - TC-F01: Initial Dashboard Load
  - TC-F02: Component Visualization
  - Extended tests for edge cases and error handling

### Real-time Update Tests
- **Files**:
  - `frontend/src/components/__tests__/ConversationStreamWebSocket.test.js`
  - `frontend/src/pages/__tests__/SessionWorkspaceRealTime.test.js`
  - `frontend/src/hooks/__tests__/useSessionPsychometricsRealTime.test.js`
  - `backend/tests/test_e2e_psychometrics_realtime.py`
- **Test Cases**:
  - TC-E01: Automatic Dashboard Update
  - TC-E02: Psychometric Profile Evolution

## Detailed Test Procedures

### Phase 1: Backend Endpoint Verification

#### Test Case TC-B01: Successful Psychometrics Endpoint Request

**Objective**: Verify that the backend endpoint returns correct data for valid session IDs.

**Preconditions**:
- Backend service is running
- Database contains at least one session with interactions
- Session has psychometric data

**Test Steps**:
1. Identify a session ID with existing interactions
2. Send GET request to the psychometrics endpoint: `GET /sessions/{session_id}/psychometrics`
3. Validate response status code is 200 OK
4. Validate response data structure contains all required fields:
   - confidence_score (integer)
   - summary (string)
   - big_five (object)
   - archetype (object)
   - disc_profile (object)
   - schwartz_values (array)
   - evolution_trend (object)

**Expected Results**:
- HTTP status code 200 OK
- Response body contains all required fields with correct data types
- No null values in critical fields
- Confidence score is between 0-100
- Big Five traits contain score, rationale, and strategy
- Archetype contains key, name, confidence, and description

#### Test Case TC-B02: Invalid Session ID Request

**Objective**: Verify that the endpoint properly handles invalid session IDs.

**Preconditions**:
- Backend service is running
- Use a non-existent session ID

**Test Steps**:
1. Send GET request to the psychometrics endpoint with invalid session ID: `GET /sessions/999/psychometrics`
2. Validate response status code
3. Validate error message in response body

**Expected Results**:
- HTTP status code 404 Not Found
- Appropriate error message in response body containing "nie została znaleziona"

### Phase 2: Static Frontend Rendering Verification

#### Test Case TC-F01: Initial Dashboard Load

**Objective**: Verify that the frontend components properly render with data from the backend.

**Preconditions**:
- Frontend application is running
- Backend service is accessible
- At least one session with psychometric data exists

**Test Steps**:
1. Navigate to SessionWorkspace page
2. Select a session with psychometric data
3. Observe component loading behavior
4. Verify data flow through frontend hooks
5. Check that PsychometricDashboard component renders without errors
6. Verify that useSessionPsychometrics hook fetches data correctly

**Expected Results**:
- Dashboard loads without errors
- API call to psychometrics endpoint is executed
- Frontend hooks properly process response
- All sub-components render with data
- Loading states are displayed appropriately
- Error states are handled gracefully

#### Test Case TC-F02: Component Visualization

**Objective**: Verify that all dashboard components display data correctly.

**Preconditions**:
- Dashboard is loaded with psychometric data

**Test Steps**:
1. Inspect PsychometricDashboard component
2. Verify BigFiveRadarChart component displays data
3. Verify DiscProfileDisplay component displays data
4. Verify SchwartzValuesList component displays data
5. Check browser console for errors
6. Validate that tooltips and interactive elements work correctly

**Expected Results**:
- All visualization components render without errors
- Data is properly mapped to visual elements
- No JavaScript errors in console
- UI elements display appropriate information
- Tooltips show strategy information on hover
- Interactive elements respond to user actions

### Phase 3: Dynamic End-to-End Real-Time Update Test

#### Test Case TC-E01: Automatic Dashboard Update

**Objective**: Verify that the dashboard automatically updates when new interactions are added.

**Preconditions**:
- SessionWorkspace is open with active session
- Dashboard is displaying initial psychometric data
- WebSocket connection is established

**Test Steps**:
1. Record initial state of dashboard
2. Add a new significant interaction through the conversation interface
3. Observe dashboard without manual refresh
4. Compare initial and updated states
5. Verify WebSocket message is received and processed

**Expected Results**:
- Dashboard updates automatically within seconds of interaction submission
- Visual changes are observable
- No manual refresh required
- WebSocket message is received and processed
- Updated psychometric data reflects new interaction

#### Test Case TC-E02: Psychometric Profile Evolution

**Objective**: Verify that psychometric profiles evolve with new interactions.

**Preconditions**:
- Session with existing psychometric profile
- Multiple interactions to add

**Test Steps**:
1. Record baseline psychometric data
2. Add first new interaction
3. Observe profile changes
4. Add second interaction
5. Observe further evolution
6. Validate confidence score adjustments
7. Verify trend tracking is updated

**Expected Results**:
- Psychometric profiles show meaningful changes with new data
- Confidence scores adjust appropriately
- Evolution trends are calculable
- No regression in previously established traits
- Trend tracking reflects changes over time

## Test Execution Instructions

### Backend Tests

To run the backend tests:
```bash
cd backend
python -m pytest tests/test_psychometrics_endpoint.py -v
python -m pytest tests/test_e2e_psychometrics_realtime.py -v
```

### Frontend Tests

To run the frontend tests:
```bash
cd frontend
npm test
```

Or to run specific test files:
```bash
npm test -- src/hooks/__tests__/useSessionPsychometrics.test.js
npm test -- src/components/psychometrics/__tests__/PsychometricDashboard.test.js
```

## Success Criteria

For the testing mission to be considered successful, all the following must pass:

1. **TC-B01**: Backend endpoint returns correct data for valid sessions
2. **TC-B02**: Backend properly handles invalid session IDs
3. **TC-F01**: Frontend dashboard loads and renders without errors
4. **TC-F02**: All visualization components display data correctly
5. **TC-E01**: Dashboard automatically updates after new interactions
6. **TC-E02**: Psychometric profiles evolve meaningfully with new data

## Failure Conditions

The testing mission will be considered failed if any of the following occur:

1. Either backend test case (TC-B01, TC-B02) fails
2. Dashboard fails to load or renders with errors (TC-F01, TC-F02)
3. Dashboard requires manual refresh to update (TC-E01 fails)
4. Psychometric profiles do not evolve with new interactions (TC-E02 fails)
5. Critical errors occur during testing that prevent continuation

## Implementation Verification Points

### Backend Verification

- [x] SessionPsychologyEngine correctly processes interactions
- [x] Psychometrics endpoint returns expected data
- [x] WebSocket properly broadcasts analysis completion
- [x] Database updates are consistent and timely

### Frontend Verification

- [x] Data fetching hooks fetch and process data correctly
- [x] PsychometricDashboard component renders all sub-components
- [x] Real-time updates occur without page refresh
- [x] Error handling is appropriate and user-friendly

### Integration Verification

- [x] Data flows correctly from backend to frontend
- [x] WebSocket connections are stable and reliable
- [x] Updates are processed in the correct order
- [x] System performance is acceptable under test conditions