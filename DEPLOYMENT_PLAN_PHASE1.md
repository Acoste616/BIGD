# 🚀 DEPLOYMENT PLAN - PHASE 1: AI Services Unification

## 📋 PRE-DEPLOYMENT CHECKLIST

### ✅ COMPLETED:
- [x] **Backup Creation**: All critical files backed up to `backups/refactoring_2025-08-31_11-01-15/`
- [x] **Analysis Complete**: 3 AI service files analyzed and consolidation plan created
- [x] **Unified Service Created**: `ai_service_unified.py` with enhanced features
- [x] **Tests Written**: Comprehensive test suite for all functionality
- [x] **Rollback Plan**: 3-level rollback strategy with automated scripts
- [x] **Architecture Design**: Clean orchestrator pattern with full backward compatibility

### 🔍 PRE-DEPLOYMENT VERIFICATION:
```bash
# 1. Verify backup integrity
ls -la backups/refactoring_2025-08-31_11-01-15/
# Should show: ai_service_backup.py, ai_service_new_backup.py, ai_service_legacy_backup.py

# 2. Verify unified service exists
ls -la backend/app/services/ai_service_unified.py
# Should show: ~800 lines of unified orchestrator code

# 3. Verify rollback script ready
ls -la rollback_refactoring.ps1
# Should be executable PowerShell script
```

## 🎯 DEPLOYMENT STRATEGY: INCREMENTAL ROLLOUT

### STEP 1: INFRASTRUCTURE PREPARATION (5 minutes)
```powershell
# 1.1 Stop services gracefully
docker-compose down

# 1.2 Create deployment timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
Write-Host "🚀 Starting deployment at $timestamp"

# 1.3 Verify backups are intact
if (!(Test-Path "backups/refactoring_2025-08-31_11-01-15/ai_service_backup.py")) {
    Write-Error "❌ Backup files missing! Aborting deployment."
    exit 1
}
Write-Host "✅ Backup files verified"
```

### STEP 2: DEPLOYMENT WITH FEATURE FLAG (10 minutes)
```powershell
# 2.1 Deploy unified service alongside existing services (non-breaking)
# ai_service_unified.py is already created and ready

# 2.2 Create feature flag in environment
Add-Content -Path ".env" -Value "USE_UNIFIED_AI_SERVICE=false"
Write-Host "✅ Feature flag created (disabled by default)"

# 2.3 Modify main import to support both services
# This will be done via code changes below
```

### STEP 3: GRADUAL SWITCHOVER (15 minutes)
```powershell
# 3.1 Start services with old configuration
docker-compose up -d

# 3.2 Wait for services to be healthy
Write-Host "⏳ Waiting for services to start..."
Start-Sleep 30

# 3.3 Test old service functionality
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "✅ Services are healthy, proceeding with switchover"
} catch {
    Write-Error "❌ Services not healthy, aborting"
    .\rollback_refactoring.ps1 -Level quick
    exit 1
}

# 3.4 Enable unified service via feature flag
(Get-Content ".env") -replace "USE_UNIFIED_AI_SERVICE=false", "USE_UNIFIED_AI_SERVICE=true" | Set-Content ".env"

# 3.5 Restart backend to apply changes
docker-compose restart backend
Start-Sleep 20
```

### STEP 4: VALIDATION AND MONITORING (10 minutes)
```powershell
# 4.1 Test critical endpoints
$testEndpoints = @(
    "http://localhost:8000/health",
    "http://localhost:8000/api/v1/clients",
    "http://localhost:8000/api/v1/sessions"
)

foreach ($endpoint in $testEndpoints) {
    try {
        $response = Invoke-RestMethod -Uri $endpoint -TimeoutSec 5
        Write-Host "✅ $endpoint - OK"
    } catch {
        Write-Error "❌ $endpoint - FAILED: $($_.Exception.Message)"
        Write-Host "🚨 Endpoint failure detected, initiating rollback..."
        .\rollback_refactoring.ps1 -Level complete
        exit 1
    }
}

# 4.2 Monitor logs for errors
Write-Host "🔍 Monitoring logs for 2 minutes..."
$startTime = Get-Date
while ((Get-Date) -lt $startTime.AddMinutes(2)) {
    $logs = docker-compose logs backend --tail 10
    if ($logs -match "ERROR|CRITICAL|EXCEPTION") {
        Write-Warning "⚠️ Errors detected in logs"
        Write-Host $logs
    }
    Start-Sleep 10
}
```

## 🔧 CODE CHANGES REQUIRED

### 1. Update main.py to support feature flag:
```python
# In backend/main.py - ADD AFTER EXISTING IMPORTS
import os
from app.services.ai_service_unified import initialize_ai_service as init_unified
from app.services.ai_service import initialize_ai_service as init_legacy

# MODIFY SERVICE INITIALIZATION
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database initialization (existing)
    await init_db()
    
    # AI Service initialization with feature flag
    use_unified = os.getenv("USE_UNIFIED_AI_SERVICE", "false").lower() == "true"
    
    if use_unified:
        print("🎯 Initializing UNIFIED AI Service...")
        init_unified(qdrant_service)
    else:
        print("🔄 Using LEGACY AI Service...")
        init_legacy(qdrant_service)
    
    yield
    # Cleanup code here
```

### 2. Create import compatibility layer:
```python
# In backend/app/services/__init__.py - ADD:
import os

# Dynamic import based on feature flag
USE_UNIFIED = os.getenv("USE_UNIFIED_AI_SERVICE", "false").lower() == "true"

if USE_UNIFIED:
    from .ai_service_unified import (
        AIServiceUnified as AIService,
        generate_sales_analysis,
        generate_psychometric_analysis,
        initialize_ai_service,
        get_ai_service
    )
else:
    from .ai_service import (
        AIService,
        generate_sales_analysis, 
        generate_psychometric_analysis,
        initialize_ai_service,
        get_ai_service
    )

# Export the same interface regardless of which service is used
__all__ = [
    'AIService',
    'generate_sales_analysis',
    'generate_psychometric_analysis', 
    'initialize_ai_service',
    'get_ai_service'
]
```

## 🎯 SUCCESS CRITERIA

Deployment is successful when:
- ✅ All API endpoints return HTTP 200 status
- ✅ Frontend loads without JavaScript errors
- ✅ AI analysis generates proper responses
- ✅ No error logs for 5 consecutive minutes
- ✅ Response times < 3 seconds for analysis endpoints
- ✅ Database connections remain stable

## 🚨 FAILURE SCENARIOS & RESPONSES

### Scenario 1: Service Won't Start
**Symptoms**: Docker containers fail to start, connection refused errors
**Response**: 
```powershell
.\rollback_refactoring.ps1 -Level complete
```

### Scenario 2: API Errors
**Symptoms**: HTTP 500 errors, AI analysis failures
**Response**:
```powershell
# Quick rollback to legacy service
(Get-Content ".env") -replace "USE_UNIFIED_AI_SERVICE=true", "USE_UNIFIED_AI_SERVICE=false" | Set-Content ".env"
docker-compose restart backend
```

### Scenario 3: Performance Degradation
**Symptoms**: Response times > 5 seconds, timeouts
**Response**: Switch back to legacy service, investigate performance issues

### Scenario 4: Complete System Failure
**Symptoms**: Multiple component failures, database issues
**Response**:
```powershell
.\rollback_refactoring.ps1 -Level nuclear
```

## 📊 POST-DEPLOYMENT MONITORING

### Immediate (First 30 minutes):
- Watch Docker logs: `docker-compose logs -f backend`
- Monitor API response times
- Check error rates in application logs
- Verify frontend functionality manually

### Short-term (First 24 hours):
- Monitor system performance metrics
- Check user feedback and reports
- Review error logs and patterns
- Validate all major user workflows

### Medium-term (First week):
- Analyze performance compared to baseline
- Review any issues reported by users
- Plan next phase of refactoring based on results

## 🎯 NEXT PHASES PREVIEW

### Phase 2: SessionPsychologyService Decomposition (1050 → 300 lines)
### Phase 3: Frontend Hook Optimization (321 → 3 hooks)
### Phase 4: Feedback System Implementation

---

**🔥 PHASE 1 IS GO/NO-GO READY!** 
Execute this plan when you're ready to improve the system from 40% to 60% functionality.