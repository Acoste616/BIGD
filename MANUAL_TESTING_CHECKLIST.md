# Session Life Cycle - Manual Testing Checklist

## Overview
This document provides a comprehensive checklist for manually testing the Session Life Cycle functionality in the AI Sales Co-Pilot system. Follow these steps to verify that all components work correctly before deployment.

## Pre-Testing Requirements
- [ ] Docker containers are running (backend, frontend, postgres, qdrant, redis)
- [ ] Database is accessible and contains test data
- [ ] API endpoints are responsive
- [ ] Frontend application loads in browser

## Backend API Testing

### 1. GET /sessions/ Endpoint
- [ ] Call endpoint with no parameters
  - [ ] Returns HTTP 200 status code
  - [ ] Returns array of session objects
  - [ ] Each session object contains required fields (id, client_id, status, start_timestamp, etc.)
- [ ] Call endpoint with skip and limit parameters
  - [ ] Returns correct number of sessions based on limit
  - [ ] Skips correct number of sessions based on skip parameter

### 2. POST /sessions/{session_id}/conclude Endpoint
- [ ] Call endpoint with valid session ID and complete conclusion data
  - [ ] Returns HTTP 200 status code
  - [ ] Returns updated session object with status='closed'
  - [ ] Returns session object with outcome_data containing provided values
- [ ] Call endpoint with valid session ID and minimal conclusion data (only outcome)
  - [ ] Returns HTTP 200 status code
  - [ ] Returns updated session object with status='closed'
  - [ ] Returns session object with outcome_data containing provided outcome and null notes/summary
- [ ] Call endpoint with invalid session ID
  - [ ] Returns HTTP 404 status code
  - [ ] Returns error message indicating session not found
- [ ] Call endpoint for already closed session
  - [ ] Returns HTTP 400 status code
  - [ ] Returns error message indicating session is already closed
- [ ] Call endpoint with missing required outcome field
  - [ ] Returns HTTP 422 status code
  - [ ] Returns validation error message

## Frontend Manual Testing

### 1. Dashboard Display
- [ ] Navigate to Sessions dashboard
  - [ ] Page loads without errors
  - [ ] Calls GET /sessions/ endpoint
  - [ ] Session list renders correctly
  - [ ] Active sessions visually differentiated from closed sessions
  - [ ] Statistics cards display correct counts

### 2. Session Conclusion Workflow
- [ ] Click "Finalizuj Sesję" button for active session
  - [ ] Conclude session modal opens
  - [ ] Modal displays correct session ID
- [ ] Fill conclusion form with test data
  - [ ] Form accepts outcome selection
  - [ ] Form accepts notes input
  - [ ] Form accepts summary input
- [ ] Submit conclusion form with complete data
  - [ ] Triggers POST /sessions/{session_id}/conclude endpoint
  - [ ] Displays loading indicator during API call
  - [ ] Modal closes after successful API response
  - [ ] Success message displayed to user
  - [ ] Session list automatically refreshes
  - [ ] Concluded session now shows as closed in the list

### 3. Error Handling
- [ ] Submit conclusion form with invalid session ID (manually modify if possible)
  - [ ] Error message displayed to user
  - [ ] Form remains open for correction
- [ ] Submit conclusion form when backend is unavailable
  - [ ] Appropriate error message displayed
  - [ ] User can retry or cancel

### 4. UI Refresh Verification
- [ ] After concluding a session
  - [ ] Dashboard automatically refreshes session list
  - [ ] Concluded session shows as closed with proper styling
  - [ ] Statistics cards update to reflect new closed session count
  - [ ] Active session count decreases by one
  - [ ] Closed session count increases by one

## Database Verification
- [ ] Direct database query for concluded session
  - [ ] Session record status changed to 'closed'
  - [ ] Session record contains outcome_data with provided values
  - [ ] Session end_timestamp is set (if applicable)

## Data Integrity Checks
- [ ] All session objects returned by GET /sessions/ have consistent structure
- [ ] Concluded sessions maintain all previous data except status and outcome_data
- [ ] Client information is correctly associated with sessions
- [ ] Timestamps are properly formatted

## Edge Cases
- [ ] Conclude session with very long notes/summary text
- [ ] Conclude session with special characters in notes/summary
- [ ] Conclude multiple sessions in quick succession
- [ ] Refresh dashboard immediately after concluding session
- [ ] Navigate away from dashboard and return after concluding session

## Post-Testing Verification
- [ ] All success criteria met
- [ ] No errors in application logs
- [ ] Application functions correctly
- [ ] Deployment ready

## Test Data Requirements
- [ ] At least 3 active sessions for testing
- [ ] At least 2 closed sessions for verification
- [ ] Test client records associated with sessions
- [ ] Sample conclusion data with various outcomes