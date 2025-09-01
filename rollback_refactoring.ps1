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
        Copy-Item "$backupDir\ai_service_backup.py" "backend\app\services\ai_service.py" -Force
        Copy-Item "$backupDir\ai_service_new_backup.py" "backend\app\services\ai_service_new.py" -Force
        Copy-Item "$backupDir\session_psychology_service_backup.py" "backend\app\services\session_psychology_service.py" -Force
        Copy-Item "$backupDir\useUltraBrain_backup.js" "frontend\src\hooks\useUltraBrain.js" -Force
        docker-compose restart backend frontend
    }
    "complete" {
        Write-Host "Level 2: Complete rollback..."
        docker-compose down --volumes --remove-orphans
        Remove-Item "backend\app\services\ai_service_unified.py" -ErrorAction SilentlyContinue
        Remove-Item "backend\app\services\session_psychology\" -Recurse -Force -ErrorAction SilentlyContinue
        Copy-Item "$backupDir\ai_service_backup.py" "backend\app\services\ai_service.py" -Force
        Copy-Item "$backupDir\ai_service_new_backup.py" "backend\app\services\ai_service_new.py" -Force
        Copy-Item "$backupDir\session_psychology_service_backup.py" "backend\app\services\session_psychology_service.py" -Force
        Copy-Item "$backupDir\useUltraBrain_backup.js" "frontend\src\hooks\useUltraBrain.js" -Force
        docker system prune -f
        docker-compose up -d
    }
    "nuclear" {
        Write-Host "Level 3: Nuclear rollback..."
        docker-compose down --volumes --remove-orphans
        docker system prune -a -f
        Copy-Item "$backupDir\ai_service_backup.py" "backend\app\services\ai_service.py" -Force
        Copy-Item "$backupDir\ai_service_new_backup.py" "backend\app\services\ai_service_new.py" -Force
        Copy-Item "$backupDir\session_psychology_service_backup.py" "backend\app\services\session_psychology_service.py" -Force
        Copy-Item "$backupDir\useUltraBrain_backup.js" "frontend\src\hooks\useUltraBrain.js" -Force
        docker-compose build --no-cache
        docker-compose up -d
    }
}

Write-Host "✅ Rollback completed. Verifying system..." -ForegroundColor Green

Start-Sleep 30
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ Backend is healthy" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🔍 Check system manually at http://localhost:3000" -ForegroundColor Yellow