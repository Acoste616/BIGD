# Session Life Cycle - Post-Deployment Verification Procedures

## Overview
This document provides comprehensive procedures for verifying the successful deployment of the Session Life Cycle functionality in the AI Sales Co-Pilot system.

## Immediate Post-Deployment Verification (0-30 minutes)

### System Health Check
- [ ] Verify all containers are running:
  ```bash
  docker-compose ps
  ```
- [ ] Check container logs for errors:
  ```bash
  docker-compose logs --tail=50
  ```
- [ ] Verify health check endpoints:
  - Backend: `curl -f http://localhost:8000/health`
  - Frontend: `curl -f http://localhost:3000`

### Service Availability Verification
- [ ] Backend API accessible:
  - [ ] Root endpoint: `http://localhost:8000/`
  - [ ] Health endpoint: `http://localhost:8000/health`
  - [ ] Docs endpoint: `http://localhost:8000/docs`
- [ ] Frontend application accessible:
  - [ ] Main page: `http://localhost:3000`
  - [ ] Sessions dashboard: `http://localhost:3000/sessions`
- [ ] WebSocket connection test:
  - [ ] WebSocket endpoint accessible: `ws://localhost:8000/ws`

### Database Verification
- [ ] Database connectivity:
  ```bash
  docker-compose exec db pg_isready -U postgres
  ```
- [ ] Database schema validation:
  ```bash
  docker-compose exec db psql -U postgres -d sales_copilot -c "\dt"
  ```
- [ ] Verify new session fields exist:
  ```bash
  docker-compose exec db psql -U postgres -d sales_copilot -c "\d sessions"
  ```

## Functional Verification (30 minutes - 2 hours)

### API Endpoint Testing

#### GET /sessions/ Endpoint
- [ ] Test with no parameters:
  ```bash
  curl -X GET "http://localhost:8000/api/v1/sessions/" -H "accept: application/json"
  ```
- [ ] Test with pagination parameters:
  ```bash
  curl -X GET "http://localhost:8000/api/v1/sessions/?skip=0&limit=5" -H "accept: application/json"
  ```
- [ ] Verify response structure:
  - [ ] Returns array of session objects
  - [ ] Each session has required fields (id, client_id, status, start_timestamp)
  - [ ] Status values are consistent (active/closed)

#### POST /sessions/{session_id}/conclude Endpoint
- [ ] Create test session if needed:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/clients/{client_id}/sessions/" -H "accept: application/json"
  ```
- [ ] Test successful session conclusion:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/sessions/{session_id}/conclude" \
       -H "accept: application/json" \
       -H "Content-Type: application/json" \
       -d '{"outcome":"interested","notes":"Test notes","summary":"Test summary"}'
  ```
- [ ] Verify response:
  - [ ] HTTP 200 status code
  - [ ] Session status is 'closed'
  - [ ] outcome_data contains provided values

### Frontend Functionality Testing

#### Dashboard Verification
- [ ] Navigate to Sessions dashboard
- [ ] Verify page loads without errors
- [ ] Check session list displays correctly:
  - [ ] Active sessions show "Aktywna" status
  - [ ] Closed sessions show "Zakończona" status
  - [ ] Session data is accurate
- [ ] Verify statistics cards:
  - [ ] All sessions count is correct
  - [ ] Active sessions count is correct
  - [ ] Closed sessions count is correct

#### Session Conclusion Workflow
- [ ] Identify an active session
- [ ] Click "Finalizuj Sesję" button
- [ ] Verify modal opens correctly
- [ ] Fill conclusion form:
  - [ ] Select outcome from dropdown
  - [ ] Enter notes
  - [ ] Enter summary
- [ ] Submit form
- [ ] Verify:
  - [ ] Modal closes
  - [ ] Success message appears
  - [ ] Session list updates
  - [ ] Concluded session shows as closed
  - [ ] Statistics update correctly

### Data Integrity Verification

#### Cross-Component Consistency
- [ ] Create new session via API
- [ ] Verify session appears in frontend dashboard
- [ ] Conclude session via frontend
- [ ] Verify session status updated in API response
- [ ] Verify database record updated correctly

#### Database Record Verification
- [ ] Connect to database:
  ```bash
  docker-compose exec db psql -U postgres -d sales_copilot
  ```
- [ ] Query concluded session:
  ```sql
  SELECT id, status, outcome_data FROM sessions WHERE id = {session_id};
  ```
- [ ] Verify:
  - [ ] Status is 'closed'
  - [ ] outcome_data contains correct JSON
  - [ ] All other session data preserved

## Performance Verification (2-4 hours)

### Response Time Testing
- [ ] Test GET /sessions/ endpoint response time:
  ```bash
  time curl -s -o /dev/null -w "%{time_total}s" "http://localhost:8000/api/v1/sessions/"
  ```
- [ ] Test POST /sessions/{session_id}/conclude endpoint response time
- [ ] Verify response times are within acceptable limits (< 2 seconds)

### Load Testing (Optional)
- [ ] Simulate multiple concurrent users accessing sessions
- [ ] Verify system handles load without degradation
- [ ] Check resource utilization during load

### Resource Utilization Monitoring
- [ ] Monitor CPU usage:
  ```bash
  docker stats --no-stream
  ```
- [ ] Monitor memory usage
- [ ] Monitor disk I/O
- [ ] Verify resource usage within acceptable limits

## Security Verification

### API Security
- [ ] Verify CORS settings are correct
- [ ] Test unauthorized access to endpoints (should be blocked)
- [ ] Verify input validation works correctly

### Data Security
- [ ] Verify sensitive data is not exposed in logs
- [ ] Check database permissions
- [ ] Verify encryption settings (if applicable)

## Integration Verification

### Cross-Service Communication
- [ ] Verify backend can communicate with database
- [ ] Verify backend can communicate with Redis
- [ ] Verify backend can communicate with Qdrant
- [ ] Verify frontend can communicate with backend

### WebSocket Integration
- [ ] Test WebSocket connection
- [ ] Verify real-time updates work
- [ ] Check WebSocket error handling

## User Acceptance Verification

### Stakeholder Testing
- [ ] Have key stakeholders test critical workflows
- [ ] Collect feedback on functionality
- [ ] Address any immediate concerns

### User Experience Validation
- [ ] Verify UI/UX meets design requirements
- [ ] Check responsive design on different screen sizes
- [ ] Validate accessibility features

## Long-term Monitoring Setup (4+ hours)

### Log Monitoring
- [ ] Set up log aggregation (if not already done)
- [ ] Configure alerting for critical errors
- [ ] Verify log retention policies

### Performance Monitoring
- [ ] Set up application performance monitoring
- [ ] Configure response time alerts
- [ ] Set up database performance monitoring

### Health Check Monitoring
- [ ] Configure uptime monitoring
- [ ] Set up health check alerts
- [ ] Verify notification channels

## Documentation Updates

### Update Required Documentation
- [ ] Update API documentation
- [ ] Update user guides
- [ ] Update system architecture documentation
- [ ] Update deployment documentation

### Version Control
- [ ] Tag successful deployment in version control
- [ ] Update changelog
- [ ] Archive deployment artifacts

## Success Criteria Validation

### All Tests Pass
- [ ] Automated tests pass
- [ ] Manual tests pass
- [ ] Performance tests pass
- [ ] Security tests pass

### User Validation
- [ ] Stakeholders approve deployment
- [ ] No critical issues reported
- [ ] User feedback is positive

### System Stability
- [ ] No system crashes or restarts
- [ ] Resource utilization stable
- [ ] Error rates within acceptable limits

## Reporting

### Deployment Success Report
- [ ] Document deployment details
- [ ] Record test results
- [ ] Note any issues encountered and resolutions
- [ ] Capture performance metrics
- [ ] Update deployment history

### Communication
- [ ] Notify stakeholders of successful deployment
- [ ] Provide access to updated documentation
- [ ] Schedule follow-up review if needed

## Ongoing Verification

### Daily Checks (First Week)
- [ ] Monitor application logs
- [ ] Check system performance
- [ ] Verify user feedback
- [ ] Confirm no new issues

### Weekly Reviews (First Month)
- [ ] Review system performance metrics
- [ ] Assess user adoption
- [ ] Identify improvement opportunities
- [ ] Update monitoring configurations

### Monthly Assessments
- [ ] Comprehensive system health review
- [ ] Performance optimization assessment
- [ ] Security review
- [ ] Planning for future enhancements