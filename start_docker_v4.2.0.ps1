# ========================================
# SALES COPILOT v4.2.0 - URUCHAMIANIE DOCKER (PowerShell)
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SALES COPILOT v4.2.0 - URUCHAMIANIE DOCKER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "[1/6] Sprawdzanie Docker i Docker Compose..." -ForegroundColor Yellow
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
Write-Host "[2/6] Zatrzymywanie istniejących kontenerów..." -ForegroundColor Yellow
docker-compose down --volumes --remove-orphans
Write-Host "✅ Kontenery zatrzymane" -ForegroundColor Green

Write-Host ""
Write-Host "[3/6] Usuwanie starych obrazów..." -ForegroundColor Yellow
docker system prune -f
Write-Host "✅ Stare obrazy usunięte" -ForegroundColor Green

Write-Host ""
Write-Host "[4/6] Budowanie nowych obrazów v4.2.0..." -ForegroundColor Yellow
docker-compose build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Błąd podczas budowania obrazów!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Obrazy v4.2.0 zbudowane" -ForegroundColor Green

Write-Host ""
Write-Host "[5/6] Uruchamianie serwisów v4.2.0..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Błąd podczas uruchamiania serwisów!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Serwisy v4.2.0 uruchomione" -ForegroundColor Green

Write-Host ""
Write-Host "[6/6] Sprawdzanie statusu serwisów..." -ForegroundColor Yellow
Start-Sleep -Seconds 15
docker-compose ps

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DOCKER v4.2.0 URUCHOMIONY POMYŚLNIE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Frontend (Ultra Brain v4.2.0): http://localhost:3000" -ForegroundColor Green
Write-Host "🧠 Backend (Modular Architecture): http://localhost:8000" -ForegroundColor Green
Write-Host "📊 API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "🗄️  Database: localhost:5432" -ForegroundColor Green
Write-Host "🔍 Qdrant Vector DB: localhost:6333" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 AI Dojo: http://localhost:3000/admin/dojo" -ForegroundColor Cyan
Write-Host "🔬 Nowa Analiza: http://localhost:3000/analysis/new" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Logi backendu: docker-compose logs -f backend" -ForegroundColor Yellow
Write-Host "📋 Logi frontendu: docker-compose logs -f frontend" -ForegroundColor Yellow
Write-Host ""

Read-Host "Naciśnij Enter aby kontynuować..."
