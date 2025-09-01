@echo off
echo ========================================
echo SALES COPILOT v4.2.1 - URUCHAMIANIE DOCKER
echo Frontend UI Fixes + Session Orchestrator Service
echo ========================================
echo.

echo [1/7] Sprawdzanie Docker i Docker Compose...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker nie jest zainstalowany!
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose nie jest zainstalowany!
    pause
    exit /b 1
)
echo ✅ Docker i Docker Compose są dostępne

echo.
echo [2/7] Zatrzymywanie istniejących kontenerów...
docker-compose down --volumes --remove-orphans
echo ✅ Kontenery zatrzymane

echo.
echo [3/7] Usuwanie starych obrazów...
docker system prune -f
echo ✅ Stare obrazy usunięte

echo.
echo [4/7] Sprawdzanie zmian w kodzie...
echo 🔧 Frontend UI Fixes: useUltraBrain enhanced data detection
echo 🔧 StrategicPanel: React.useMemo for customerArchetype
echo 🔧 ConversationView: Enhanced debugging for data flow
echo 🧠 Backend: SessionOrchestratorService architecture
echo ✅ Kod przygotowany do budowania

echo.
echo [5/7] Budowanie nowych obrazów v4.2.1...
docker-compose build --no-cache
if errorlevel 1 (
    echo ❌ Błąd podczas budowania obrazów!
    pause
    exit /b 1
)
echo ✅ Obrazy v4.2.1 zbudowane

echo.
echo [6/7] Uruchamianie serwisów v4.2.1...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Błąd podczas uruchamiania serwisów!
    pause
    exit /b 1
)
echo ✅ Serwisy v4.2.1 uruchomione

echo.
echo [7/7] Sprawdzanie statusu serwisów...
timeout /t 20 /nobreak >nul
docker-compose ps

echo.
echo ========================================
echo DOCKER v4.2.1 URUCHOMIONY POMYŚLNIE!
echo ========================================
echo.
echo 🚀 Frontend (Ultra Brain v4.2.1): http://localhost:3000
echo 🧠 Backend (Session Orchestrator): http://localhost:8000
echo 📊 API Documentation: http://localhost:8000/docs
echo 🗄️ Database: localhost:5432
echo 🔍 Qdrant Vector DB: localhost:6333
echo.
echo 🔧 FRONTEND UI FIXES - TEST PAGE:
echo 🛠️ Debug Data Flow: http://localhost:3000/test-data-flow.html
echo.
echo 🎯 AI Dojo: http://localhost:3000/admin/dojo
echo 🔬 Nowa Analiza: http://localhost:3000/analysis/new
echo.
echo 📋 Logi backendu: docker-compose logs -f backend
echo 📋 Logi frontendu: docker-compose logs -f frontend
echo.
echo 🔍 DEBUGGING FRONTEND UI:
echo    1. Otwórz http://localhost:3000 i przejdź do konwersacji
echo    2. Otwórz Developer Tools (F12) → Console
echo    3. Szukaj logów: 🔧 [ULTRA BRAIN DEBUG], 🔧 [CONVERSATION VIEW], 🔧 [STRATEGIC PANEL]
echo    4. Sprawdź czy archetypy wyświetlają się poprawnie (nie 'Profil w trakcie analizy...')
echo    5. Użyj validateUltraBrainData() w konsoli do sprawdzenia jakości danych
echo.

pause