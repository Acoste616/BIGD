# 🛡️ ROLLBACK PLAN - AI Services Refactoring
**Emergency Recovery Procedures**

## 🚨 WHEN TO EXECUTE ROLLBACK

Execute rollback immediately if ANY of these occur:
- ❌ Any API endpoint returns 500 errors
- ❌ Frontend cannot connect to backend services
- ❌ AI responses stop generating
- ❌ System performance degrades >50%
- ❌ Critical functionality breaks

## 🔧 ROLLBACK PROCEDURES

### LEVEL 1: QUICK ROLLBACK (5 minutes)
**Use when: Minor issues, service errors**

```powershell
# Step 1: Navigate to project root
cd d:\UltraBIGDecoder

# Step 2: Restore backup files
Copy-Item "backups\refactoring_2025-08-31_11-01-15\ai_service_backup.py" "backend\app\services\ai_service.py" -Force
Copy-Item "backups\refactoring_2025-08-31_11-01-15\ai_service_new_backup.py" "backend\app\services\ai_service_new.py" -Force
Copy-Item "backups\refactoring_2025-08-31_11-01-15\session_psychology_service_backup.py" "backend\app\services\session_psychology_service.py" -Force
Copy-Item "backups\refactoring_2025-08-31_11-01-15\useUltraBrain_backup.js" "frontend\src\hooks\useUltraBrain.js" -Force

# Step 3: Restart services
docker-compose restart backend frontend
```

### LEVEL 2: COMPLETE ROLLBACK (10 minutes)
**Use when: Major system failures, data corruption**

```powershell
# Step 1: Stop all services
docker-compose down --volumes --remove-orphans

# Step 2: Remove any new files created during refactoring
Remove-Item "backend\app\services\ai_service_unified.py" -ErrorAction SilentlyContinue
Remove-Item "backend\app\services\session_psychology\" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "frontend\src\hooks\useInteractionHandling.js" -ErrorAction SilentlyContinue
Remove-Item "frontend\src\hooks\useSessionManagement.js" -ErrorAction SilentlyContinue

# Step 3: Restore all backup files
$backupDir = "backups\refactoring_2025-08-31_11-01-15"
Copy-Item "$backupDir\ai_service_backup.py" "backend\app\services\ai_service.py" -Force
Copy-Item "$backupDir\ai_service_new_backup.py" "backend\app\services\ai_service_new.py" -Force  
Copy-Item "$backupDir\session_psychology_service_backup.py" "backend\app\services\session_psychology_service.py" -Force
Copy-Item "$backupDir\useUltraBrain_backup.js" "frontend\src\hooks\useUltraBrain.js" -Force

# Step 4: Clean Docker environment
docker system prune -f
docker volume prune -f

# Step 5: Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Step 6: Verify services
Start-Sleep 30
curl http://localhost:8000/health
```

### LEVEL 3: NUCLEAR ROLLBACK (20 minutes) 
**Use when: Complete system breakdown, database issues**

```powershell
# Step 1: Complete shutdown
docker-compose down --volumes --remove-orphans
docker system prune -a -f

# Step 2: Git-based recovery (if using git)
git stash
git checkout HEAD~1  # Go back to previous commit
git clean -fd       # Remove untracked files

# Step 3: Manual file restoration
$backupDir = "backups\refactoring_2025-08-31_11-01-15"
Get-ChildItem $backupDir | ForEach-Object {
    $targetPath = $_.Name -replace "_backup", ""
    $targetPath = $targetPath -replace "\.py$", ".py" 
    $targetPath = $targetPath -replace "\.js$", ".js"
    
    if ($_.Name -like "*ai_service*") {
        Copy-Item $_.FullName "backend\app\services\$targetPath" -Force
    }
    elseif ($_.Name -like "*session_psychology*") {
        Copy-Item $_.FullName "backend\app\services\$targetPath" -Force  
    }
    elseif ($_.Name -like "*useUltraBrain*") {
        Copy-Item $_.FullName "frontend\src\hooks\$targetPath" -Force
    }
}

# Step 4: Database rollback (if needed)
docker-compose up -d postgres
docker exec ultrabigdecoder-postgres-1 psql -U user -d sales_copilot -c "SELECT NOW();"

# Step 5: Full system rebuild
docker-compose build --no-cache --pull
docker-compose up -d

# Step 6: Wait and verify
Start-Sleep 60
curl http://localhost:8000/health
curl http://localhost:3000
```

## ✅ VERIFICATION STEPS

After rollback, verify these critical functions:

### Backend Verification:
```powershell
# Test AI Service endpoints
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/clients" -Method GET
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sessions" -Method GET

# Check logs for errors
docker-compose logs backend | Select-String -Pattern "ERROR|CRITICAL"
```

### Frontend Verification:
```powershell
# Check if frontend loads
Start-Process "http://localhost:3000"

# Check console for JavaScript errors
# Manual: Open DevTools -> Console, look for red errors
```

### Database Verification:
```powershell
# Test database connectivity
docker exec ultrabigdecoder-postgres-1 psql -U user -d sales_copilot -c "\dt"
docker exec ultrabigdecoder-postgres-1 psql -U user -d sales_copilot -c "SELECT COUNT(*) FROM clients;"
```

## 📊 SUCCESS CRITERIA

Rollback is successful when:
- ✅ Backend returns HTTP 200 on /health endpoint
- ✅ Frontend loads without JavaScript errors  
- ✅ Database queries execute successfully
- ✅ AI analysis endpoints return valid responses
- ✅ No error logs in last 5 minutes

## 🔍 POST-ROLLBACK ANALYSIS

### 1. Collect Failure Evidence:
```powershell
# Backup current logs before they get overwritten
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
docker-compose logs > "logs\rollback_analysis_$timestamp.log"

# Save error screenshots
# Manual: Take screenshots of any error messages
```

### 2. Document What Went Wrong:
```markdown
# ROLLBACK INCIDENT REPORT

**Date/Time**: [timestamp]
**Rollback Level**: [1/2/3]
**Triggering Issue**: [description]
**Services Affected**: [list]
**Recovery Time**: [minutes]

## Root Cause Analysis:
[What caused the failure]

## Prevention Measures:
[How to prevent this in future]
```

### 3. Plan Recovery Strategy:
- Identify specific failure points
- Create more targeted tests
- Plan incremental deployment approach
- Consider feature flags for gradual rollout

## 🛠️ ROLLBACK SCRIPT (AUTOMATED)

Save this as `rollback_refactoring.ps1`:

```powershell
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("quick", "complete", "nuclear")]
    [string]$Level
)

Write-Host "🚨 EXECUTING $Level ROLLBACK..." -ForegroundColor Red

$backupDir = "backups\refactoring_2025-08-31_11-01-15"

switch ($Level) {
    "quick" {
        Write-Host "Level 1: Quick rollback..."
        Copy-Item "$backupDir\*" "backend\app\services\" -Include "*ai_service*", "*session_psychology*" -Force
        Copy-Item "$backupDir\useUltraBrain_backup.js" "frontend\src\hooks\useUltraBrain.js" -Force
        docker-compose restart backend frontend
    }
    "complete" {
        Write-Host "Level 2: Complete rollback..."
        docker-compose down --volumes --remove-orphans
        # [Insert complete rollback steps]
        docker-compose up -d
    }
    "nuclear" {
        Write-Host "Level 3: Nuclear rollback..."
        docker-compose down --volumes --remove-orphans
        docker system prune -a -f
        # [Insert nuclear rollback steps]
        docker-compose build --no-cache
        docker-compose up -d
    }
}

Write-Host "✅ Rollback completed. Verifying system..." -ForegroundColor Green

# Verify system health
Start-Sleep 30
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "✅ Backend is healthy" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed" -ForegroundColor Red
}

Write-Host "🔍 Check system manually at http://localhost:3000" -ForegroundColor Yellow
```

## 📱 EMERGENCY CONTACTS

**When rollback fails completely:**
1. Document everything
2. Stop all Docker services
3. Contact system administrator  
4. Consider restoring from system backup
5. Plan emergency maintenance window

---

**Remember**: Rollback is not failure - it's smart risk management! 🛡️