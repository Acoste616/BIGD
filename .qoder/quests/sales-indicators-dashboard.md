# Sales Indicators Dashboard Design Document

## 1. Overview

This document outlines the design for implementing a fully functional, dynamically updated sales indicators dashboard. The system will transform existing skeleton components into an analytical tool that generates real-time predictions based on session psychometric data.

### 1.1 Objectives

- Implement a backend predictive engine for sales indicators calculation
- Create a frontend dashboard that visualizes key sales metrics
- Enable real-time updates when new interaction data is added
- Provide actionable insights for sales representatives

### 1.2 Key Features

- **Purchase Temperature**: Measures how "hot" a lead is (0-100 scale)
- **Churn Risk**: Assesses the likelihood of losing a customer (low/medium/high)
- **Sales Potential**: Estimates deal value and probability (0-100 scale)
- **Real-time Updates**: Automatic refresh when new interactions are added

## 2. Architecture

### 2.1 System Components

The system consists of the following components:

- **Frontend Dashboard**: User interface for displaying sales indicators
- **API Layer**: Exposes endpoints for retrieving sales indicators
- **SalesIndicatorsService**: Core service for calculating sales indicators
- **SessionPsychologyEngine**: Processes psychometric data from sessions
- **Database**: Stores session and psychometric data
- **AI Services**: Provides AI-powered analysis capabilities
- **Session Workspace**: Collects user interaction data

### 2.2 Data Flow

1. User interaction data is collected in the Session Workspace
2. SessionPsychologyEngine processes psychometric data
3. SalesIndicatorsService calculates key metrics based on psychometric data
4. API endpoints expose calculated indicators
5. Frontend dashboard consumes and visualizes the data

## 3. Backend Implementation

### 3.1 SalesIndicatorsService

Location: `backend/app/services/sales_indicators_service.py`

#### 3.1.1 Class Definition

The SalesIndicatorsService class will contain the core logic for calculating sales indicators:

- **calculate_indicators()**: Main method that takes psychometric data and returns calculated indicators
- **_calculate_purchase_temperature()**: Calculates purchase temperature based on Big Five traits and Schwartz values
- **_calculate_churn_risk()**: Assesses churn risk based on DISC profile and interaction signals
- **_calculate_sales_potential()**: Estimates sales potential based on customer archetype and confidence score

#### 3.1.2 Calculation Logic

**Purchase Temperature (0-100):**
- High conscientiousness and low neuroticism increase temperature
- Achievement-oriented Schwartz values increase temperature
- Formula: Base score adjusted by trait multipliers

**Churn Risk (low/medium/high):**
- High Dominance and Compliance may indicate risk if needs aren't met
- Negative interaction signals increase risk
- Risk level determined by weighted scoring

**Sales Potential (0-100):**
- Archetype-based potential (e.g., "Explorer" has higher potential for innovative products)
- Psychology confidence score as a multiplier
- Formula: Archetype base value * confidence modifier

### 3.2 API Endpoint

Location: `backend/app/routers/sessions.py`

#### 3.2.1 Endpoint Definition

The API will expose a new endpoint to retrieve sales indicators for a specific session:

- **Endpoint**: GET /sessions/{session_id}/indicators
- **Purpose**: Retrieve calculated sales indicators based on session psychometric data
- **Parameters**: session_id (path parameter)
- **Response**: SalesIndicatorsAnalysis object containing all four indicators
- **Error Handling**: Returns 404 when session is not found

#### 3.2.2 Response Structure

The endpoint will return a JSON object containing all four sales indicators:

- **purchase_temperature**: Contains value (0-100), rationale, strategy, and confidence
- **churn_risk**: Contains level (low/medium/high), rationale, strategy, and confidence
- **sales_potential**: Contains value, probability, estimated timeframe, rationale, strategy, and confidence

## 4. Frontend Implementation

### 4.1 Custom Hook: useSalesIndicators

Location: `frontend/src/hooks/useSalesIndicators.js`

#### 4.1.1 Hook Definition

The useSalesIndicators hook will manage the state and data fetching for sales indicators:

- **State Management**: Handles indicatorsData, loading, and error states
- **Data Fetching**: Implements fetchIndicators function to retrieve data from the API
- **Automatic Updates**: Uses useEffect to fetch data when sessionId changes
- **Manual Refresh**: Provides refetch function for manual updates

### 4.2 SalesIndicatorsDashboard Component

Location: `frontend/src/components/indicators/SalesIndicatorsDashboard.js`

#### 4.2.1 Component Integration

The existing SalesIndicatorsDashboard component will be enhanced to use the new useSalesIndicators hook and display real-time data.

- **Hook Integration**: Uses useSalesIndicators to fetch and manage indicator data
- **State Handling**: Properly handles loading and error states
- **Data Passing**: Passes indicator data to child components
- **Real-time Updates**: Automatically updates when new data is fetched

### 4.3 SessionWorkspace Integration

Location: `frontend/src/pages/SessionWorkspace.js`

#### 4.3.1 Real-time Updates

After adding a new interaction, the system will automatically refresh the sales indicators:

- **Trigger Point**: After successful interaction addition
- **Cascade Refresh**: Refreshes both psychometric data and sales indicators
- **Synchronization**: Ensures indicators are based on the latest analysis

## 5. Data Models

### 5.1 SalesIndicators Schema

Defined in: `backend/app/schemas/indicators.py`

The schema defines the structure for all sales indicators:

- **SalesIndicator**: Base model containing value, rationale, strategy, and confidence
- **PurchaseTemperature**: Extends SalesIndicator with temperature-specific fields
- **ChurnRisk**: Extends SalesIndicator with risk level and factors
- **SalesPotential**: Extends SalesIndicator with probability and timeframe

## 6. Testing Strategy

### 6.1 Unit Tests

1. **SalesIndicatorsService Tests**:
   - Test calculation logic for each indicator
   - Test edge cases and error conditions
   - Validate output structure matches schema

2. **API Endpoint Tests**:
   - Test successful response with valid session ID
   - Test 404 response with invalid session ID
   - Validate response data structure

### 6.2 Integration Tests

1. **End-to-End Workflow**:
   - Create session with interactions
   - Verify indicators are calculated and returned
   - Add new interaction and verify real-time update

2. **Frontend Integration**:
   - Test hook data fetching
   - Verify dashboard component rendering
   - Test error and loading states

## 7. Success Criteria

### 7.1 Definition of Done

1. GET `/sessions/{session_id}/indicators` endpoint works and returns properly formatted calculated data
2. SalesIndicatorsDashboard fully renders all indicators (Temperature, Risk, Potential) based on API response
3. Critical test: After adding a new interaction in SessionWorkspace, the sales indicators dashboard automatically refreshes, reflecting predictions based on the latest psychometric analysis

### 7.2 Performance Requirements

- API response time < 500ms
- Dashboard update time < 1 second after interaction
- Error handling for missing or incomplete psychometric data