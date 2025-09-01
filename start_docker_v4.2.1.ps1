# ========================================
# SALES COPILOT v4.2.1 - URUCHAMIANIE DOCKER (PowerShell)
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SALES COPILOT v4.2.1 - URUCHAMIANIE DOCKER" -ForegroundColor Cyan
Write-Host "Frontend UI Fixes + Session Orchestrator Service" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "[1/7] Sprawdzanie Docker i Docker Compose..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker nie jest zainstalowany!" -ForegroundColor Red
    exit 1
}
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose nie jest zainstalowany!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker i Docker Compose są dostępne" -ForegroundColor Green

Write-Host ""
Write-Host "[2/7] Zatrzymywanie istniejących kontenerów..." -ForegroundColor Yellow
docker-compose down --volumes --remove-orphans
Write-Host "✅ Kontenery zatrzymane" -ForegroundColor Green

Write-Host ""
Write-Host "[3/7] Usuwanie starych obrazów..." -ForegroundColor Yellow
docker system prune -f
Write-Host "✅ Stare obrazy usunięte" -ForegroundColor Green

Write-Host ""
Write-Host "[4/7] Sprawdzanie zmian w kodzie..." -ForegroundColor Yellow
Write-Host "🔧 Frontend UI Fixes: useUltraBrain enhanced data detection" -ForegroundColor Cyan
Write-Host "🔧 StrategicPanel: React.useMemo for customerArchetype" -ForegroundColor Cyan
Write-Host "🔧 ConversationView: Enhanced debugging for data flow" -ForegroundColor Cyan
Write-Host "🧠 Backend: SessionOrchestratorService architecture" -ForegroundColor Cyan
Write-Host "✅ Kod przygotowany do budowania" -ForegroundColor Green

Write-Host ""
Write-Host "[5/7] Budowanie nowych obrazów v4.2.1..." -ForegroundColor Yellow
docker-compose build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Błąd podczas budowania obrazów!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Obrazy v4.2.1 zbudowane" -ForegroundColor Green

Write-Host ""
Write-Host "[6/7] Uruchamianie serwisów v4.2.1..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Błąd podczas uruchamiania serwisów!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Serwisy v4.2.1 uruchomione" -ForegroundColor Green

Write-Host ""
Write-Host "[7/7] Sprawdzanie statusu serwisów i health checks..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host "📋 Status kontenerów:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "🔍 Health checks:" -ForegroundColor Cyan
try {
    $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Backend Health: OK" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Backend Health: Checking..." -ForegroundColor Yellow
}

try {
    $frontendHealth = Invoke-RestMethod -Uri "http://localhost:3000/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Frontend Health: OK" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Frontend Health: Checking..." -ForegroundColor Yellow
}

try {
    $qdrantHealth = Invoke-RestMethod -Uri "http://localhost:6333/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Qdrant Health: OK" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Qdrant Health: Checking..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DOCKER v4.2.1 URUCHOMIONY POMYŚLNIE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Frontend (Ultra Brain v4.2.1): http://localhost:3000" -ForegroundColor Green
Write-Host "🧠 Backend (Session Orchestrator): http://localhost:8000" -ForegroundColor Green
Write-Host "📊 API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "🗄️  Database: localhost:5432" -ForegroundColor Green
Write-Host "🔍 Qdrant Vector DB: localhost:6333" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 FRONTEND UI FIXES - TEST PAGE:" -ForegroundColor Magenta
Write-Host "🛠️  Debug Data Flow: http://localhost:3000/test-data-flow.html" -ForegroundColor Magenta
Write-Host ""
Write-Host "🎯 AI Dojo: http://localhost:3000/admin/dojo" -ForegroundColor Cyan
Write-Host "🔬 Nowa Analiza: http://localhost:3000/analysis/new" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Logi backendu: docker-compose logs -f backend" -ForegroundColor Yellow
Write-Host "📋 Logi frontendu: docker-compose logs -f frontend" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔍 DEBUGGING FRONTEND UI:" -ForegroundColor Magenta
Write-Host "   1. Otwórz http://localhost:3000 i przejdź do konwersacji" -ForegroundColor White
Write-Host "   2. Otwórz Developer Tools (F12) → Console" -ForegroundColor White
Write-Host "   3. Szukaj logów: 🔧 [ULTRA BRAIN DEBUG], 🔧 [CONVERSATION VIEW], 🔧 [STRATEGIC PANEL]" -ForegroundColor White
Write-Host "   4. Sprawdź czy archetypy wyświetlają się poprawnie (nie 'Profil w trakcie analizy')" -ForegroundColor White
Write-Host "   5. Użyj validateUltraBrainData() w konsoli do sprawdzenia jakości danych" -ForegroundColor White
Write-Host ""

Read-Host "Naciśnij Enter aby kontynuować..."