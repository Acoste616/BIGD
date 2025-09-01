@echo off
chcp 65001 >nul

REM ========================================
REM SALES COPILOT v4.2.0 - URUCHAMIANIE DOCKER (Command Prompt)
REM ========================================

echo ========================================
echo SALES COPILOT v4.2.0 - URUCHAMIANIE DOCKER
echo ========================================

echo.
echo [1/6] Sprawdzanie Docker i Docker Compose...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker nie jest zainstalowany!
    pause
    exit /b 1
)
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose nie jest zainstalowany!
    pause
    exit /b 1
)
echo ✅ Docker i Docker Compose są dostępne

echo.
echo [2/6] Zatrzymywanie istniejących kontenerów...
docker-compose down --volumes --remove-orphans
echo ✅ Kontenery zatrzymane

echo.
echo [3/6] Usuwanie starych obrazów...
docker system prune -f
echo ✅ Stare obrazy usunięte

echo.
echo [4/6] Budowanie nowych obrazów v4.2.0...
docker-compose build --no-cache
if %errorlevel% neq 0 (
    echo ❌ Błąd podczas budowania obrazów!
    pause
    exit /b 1
)
echo ✅ Obrazy v4.2.0 zbudowane

echo.
echo [5/6] Uruchamianie serwisów v4.2.0...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Błąd podczas uruchamiania serwisów!
    pause
    exit /b 1
)
echo ✅ Serwisy v4.2.0 uruchomione

echo.
echo [6/6] Sprawdzanie statusu serwisów...
timeout /t 15 /nobreak >nul
docker-compose ps

echo.
echo ========================================
echo DOCKER v4.2.0 URUCHOMIONY POMYŚLNIE!
echo ========================================
echo.
echo 🚀 Frontend (Ultra Brain v4.2.0): http://localhost:3000
echo 🧠 Backend (Modular Architecture): http://localhost:8000
echo 📊 API Documentation: http://localhost:8000/docs
echo 🗄️  Database: localhost:5432
echo 🔍 Qdrant Vector DB: localhost:6333
echo.
echo 🎯 AI Dojo: http://localhost:3000/admin/dojo
echo 🔬 Nowa Analiza: http://localhost:3000/analysis/new
echo.
echo 📋 Logi backendu: docker-compose logs -f backend
echo 📋 Logi frontendu: docker-compose logs -f frontend
echo.

pause
