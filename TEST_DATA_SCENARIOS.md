# Session Life Cycle - Test Data and Scenarios

## Overview
This document provides test data and scenarios for manually testing the Session Life Cycle functionality in the AI Sales Co-Pilot system.

## Test Data Requirements

### Client Records
Create the following test clients:

1. **Client A**
   - Alias: "Jan Kowalski"
   - Notes: "Long-term client interested in premium packages"
   - Archetype: "Analytical Decision Maker"
   - Tags: ["premium", "long-term", "tech-savvy"]

2. **Client B**
   - Alias: "Anna Nowak"
   - Notes: "New prospect showing initial interest"
   - Archetype: "Spontaneous Buyer"
   - Tags: ["new", "budget-conscious"]

3. **Client C**
   - Alias: "Piotr Wiśniewski"
   - Notes: "Previous client returning for additional services"
   - Archetype: "Loyal Customer"
   - Tags: ["returning", "upsell-opportunity"]

### Session Records

#### Active Sessions
1. **Session 1**
   - Client: Jan Kowalski (Client A)
   - Status: active
   - Start Time: 2025-09-11 10:00:00
   - Notes: "Initial consultation for new product line"

2. **Session 2**
   - Client: Anna Nowak (Client B)
   - Status: active
   - Start Time: 2025-09-11 11:30:00
   - Notes: "Product demonstration session"

3. **Session 3**
   - Client: Piotr Wiśniewski (Client C)
   - Status: active
   - Start Time: 2025-09-11 14:15:00
   - Notes: "Follow-up on previous services"

#### Closed Sessions
1. **Session 4**
   - Client: Jan Kowalski (Client A)
   - Status: closed
   - Start Time: 2025-09-10 09:00:00
   - End Time: 2025-09-10 10:30:00
   - Outcome Data:
     - Outcome: "closed_deal"
     - Notes: "Signed contract for premium package"
     - Summary: "Successful negotiation resulting in closed deal"

2. **Session 5**
   - Client: Anna Nowak (Client B)
   - Status: closed
   - Start Time: 2025-09-10 13:00:00
   - End Time: 2025-09-10 14:00:00
   - Outcome Data:
     - Outcome: "not_interested"
     - Notes: "Not interested in current offerings"
     - Summary: "Client not interested at this time"

## Test Scenarios

### Scenario 1: Basic Session Conclusion
**Objective**: Verify basic functionality of concluding an active session

**Preconditions**:
- Session 1 (Jan Kowalski) is active
- User is logged into the dashboard

**Steps**:
1. Navigate to Sessions dashboard
2. Locate Session 1 in the list
3. Click "Finalizuj Sesję" button
4. In the modal:
   - Select "Zainteresowany" as outcome
   - Enter "Client showed strong interest in premium features" as notes
   - Enter "Positive consultation with clear intent to purchase" as summary
5. Click "Finalizuj"

**Expected Results**:
- Modal closes successfully
- Session 1 shows as "Zakończona" in the list
- Statistics update (Active: 2, Closed: 3)
- Database record shows status='closed' and correct outcome_data

### Scenario 2: Minimal Data Conclusion
**Objective**: Verify session conclusion with minimal required data

**Preconditions**:
- Session 2 (Anna Nowak) is active
- User is logged into the dashboard

**Steps**:
1. Navigate to Sessions dashboard
2. Locate Session 2 in the list
3. Click "Finalizuj Sesję" button
4. In the modal:
   - Select "Potrzebuje czasu" as outcome
   - Leave notes and summary fields empty
5. Click "Finalizuj"

**Expected Results**:
- Modal closes successfully
- Session 2 shows as "Zakończona" in the list
- Statistics update (Active: 1, Closed: 4)
- Database record shows status='closed' with outcome_data containing only outcome

### Scenario 3: Error Handling - Invalid Session ID
**Objective**: Verify proper error handling for non-existent session

**Preconditions**:
- User has access to API testing tool
- Session with ID 999999 does not exist

**Steps**:
1. Send POST request to `/api/v1/sessions/999999/conclude`
2. Include valid conclusion data in request body

**Expected Results**:
- HTTP 404 status code returned
- Error message: "Sesja o ID 999999 nie została znaleziona"

### Scenario 4: Error Handling - Already Closed Session
**Objective**: Verify proper error handling for attempting to close already closed session

**Preconditions**:
- Session 4 (Jan Kowalski) is already closed
- User is logged into the dashboard

**Steps**:
1. Navigate to Sessions dashboard
2. Locate Session 4 in the list
3. Observe that "Finalizuj Sesję" button is disabled or not present
4. (If accessible through other means) Attempt to conclude Session 4

**Expected Results**:
- UI prevents concluding already closed sessions
- If API call is made: HTTP 400 status code returned
- Error message: "Sesja o ID {session_id} jest już zamknięta"

### Scenario 5: Form Validation
**Objective**: Verify form validation in session conclusion modal

**Preconditions**:
- Session 3 (Piotr Wiśniewski) is active
- User is logged into the dashboard

**Steps**:
1. Navigate to Sessions dashboard
2. Locate Session 3 in the list
3. Click "Finalizuj Sesję" button
4. Leave outcome field unselected
5. Enter text in notes and summary fields
6. Click "Finalizuj"

**Expected Results**:
- Form shows validation error for outcome field
- Modal remains open
- User can correct and resubmit

### Scenario 6: Long Text Input
**Objective**: Verify handling of long text inputs

**Preconditions**:
- Session 3 (Piotr Wiśniewski) is active
- User is logged into the dashboard

**Steps**:
1. Navigate to Sessions dashboard
2. Locate Session 3 in the list
3. Click "Finalizuj Sesję" button
4. Select "Zainteresowany" as outcome
5. Enter 1000-character string in notes field:
   "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt."
6. Enter 500-character string in summary field:
   "This is a comprehensive summary of the session interaction with the client. The discussion covered various aspects of our product offerings and the client's specific requirements. We identified several key areas of interest and potential opportunities for future collaboration."
7. Click "Finalizuj"

**Expected Results**:
- Modal closes successfully
- Session 3 shows as "Zakończona" in the list
- Long text is properly stored and retrieved
- No truncation or data loss

### Scenario 7: Special Characters
**Objective**: Verify handling of special characters in input

**Preconditions**:
- Session 3 (if still active) or create new session for testing
- User is logged into the dashboard

**Steps**:
1. Navigate to Sessions dashboard
2. Locate an active session
3. Click "Finalizuj Sesję" button
4. Select "Wymaga kontaktu" as outcome
5. Enter text with special characters in notes field:
   "Client's feedback: \"This product is amazing!\" & <very> important (to consider) - cost: $99.99; date: 10/10/2025 @ 3:30pm"
6. Enter text with Unicode characters in summary field:
   "Résumé of meeting with client: café, naïve, coöperation, piñata, résumé"
7. Click "Finalizuj"

**Expected Results**:
- Modal closes successfully
- Special characters are properly stored and displayed
- No encoding issues or data corruption

### Scenario 8: Multiple Rapid Conclusions
**Objective**: Verify system behavior when concluding multiple sessions rapidly

**Preconditions**:
- At least 3 active sessions available
- User is logged into the dashboard

**Steps**:
1. Navigate to Sessions dashboard
2. Click "Finalizuj Sesję" for first active session
3. Quickly fill and submit form
4. Immediately click "Finalizuj Sesję" for second active session
5. Quickly fill and submit form
6. Immediately click "Finalizuj Sesję" for third active session
7. Quickly fill and submit form

**Expected Results**:
- All three sessions conclude successfully
- UI updates correctly for each
- No race conditions or data corruption
- Statistics update accurately (Active: 0, Closed: +3)

### Scenario 9: Dashboard Refresh
**Objective**: Verify dashboard refresh functionality

**Preconditions**:
- Multiple sessions of different statuses exist
- User is logged into the dashboard

**Steps**:
1. Navigate to Sessions dashboard
2. Note current session counts and statuses
3. In another browser tab or through API, conclude one active session
4. Click the refresh button in the dashboard
5. Observe changes in session list and statistics

**Expected Results**:
- Session list updates to reflect concluded session
- Statistics cards show updated counts
- No page reload required

### Scenario 10: Database Integrity
**Objective**: Verify data integrity at the database level

**Preconditions**:
- Session has been concluded through normal workflow
- Database access is available

**Steps**:
1. Conclude a session through the normal UI workflow
2. Connect to PostgreSQL database
3. Query the session record:
   ```sql
   SELECT id, status, outcome_data, end_timestamp 
   FROM sessions 
   WHERE id = {concluded_session_id};
   ```
4. Verify data integrity:
   - Status is 'closed'
   - outcome_data contains correct JSON structure
   - end_timestamp is set (if applicable)

**Expected Results**:
- Database record accurately reflects UI actions
- Data structure is consistent
- No data loss or corruption