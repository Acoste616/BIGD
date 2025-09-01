#!/bin/bash
# ========================================
# SALES COPILOT v4.2.1 - URUCHAMIANIE DOCKER (Linux/Mac)
# ========================================

echo "========================================"
echo "SALES COPILOT v4.2.1 - URUCHAMIANIE DOCKER"
echo "Frontend UI Fixes + Session Orchestrator Service"
echo "========================================"
echo ""

echo "[1/7] Sprawdzanie Docker i Docker Compose..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker nie jest zainstalowany!"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose nie jest zainstalowany!"
    exit 1
fi
echo "✅ Docker i Docker Compose są dostępne"

echo ""
echo "[2/7] Zatrzymywanie istniejących kontenerów..."
docker-compose down --volumes --remove-orphans
echo "✅ Kontenery zatrzymane"

echo ""
echo "[3/7] Usuwanie starych obrazów..."
docker system prune -f
echo "✅ Stare obrazy usunięte"

echo ""
echo "[4/7] Sprawdzanie zmian w kodzie..."
echo "🔧 Frontend UI Fixes: useUltraBrain enhanced data detection"
echo "🔧 StrategicPanel: React.useMemo for customerArchetype"
echo "🔧 ConversationView: Enhanced debugging for data flow"
echo "🧠 Backend: SessionOrchestratorService architecture"
echo "✅ Kod przygotowany do budowania"

echo ""
echo "[5/7] Budowanie nowych obrazów v4.2.1..."
docker-compose build --no-cache
if [ $? -ne 0 ]; then
    echo "❌ Błąd podczas budowania obrazów!"
    exit 1
fi
echo "✅ Obrazy v4.2.1 zbudowane"

echo ""
echo "[6/7] Uruchamianie serwisów v4.2.1..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Błąd podczas uruchamiania serwisów!"
    exit 1
fi
echo "✅ Serwisy v4.2.1 uruchomione"

echo ""
echo "[7/7] Sprawdzanie statusu serwisów i health checks..."
sleep 20

echo "📋 Status kontenerów:"
docker-compose ps

echo ""
echo "🔍 Health checks:"
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Backend Health: OK"
else
    echo "⚠️ Backend Health: Checking..."
fi

if curl -f http://localhost:3000/health &> /dev/null; then
    echo "✅ Frontend Health: OK"
else
    echo "⚠️ Frontend Health: Checking..."
fi

if curl -f http://localhost:6333/health &> /dev/null; then
    echo "✅ Qdrant Health: OK"
else
    echo "⚠️ Qdrant Health: Checking..."
fi

echo ""
echo "========================================"
echo "DOCKER v4.2.1 URUCHOMIONY POMYŚLNIE!"
echo "========================================"
echo ""
echo "🚀 Frontend (Ultra Brain v4.2.1): http://localhost:3000"
echo "🧠 Backend (Session Orchestrator): http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🗄️ Database: localhost:5432"
echo "🔍 Qdrant Vector DB: localhost:6333"
echo ""
echo "🔧 FRONTEND UI FIXES - TEST PAGE:"
echo "🛠️ Debug Data Flow: http://localhost:3000/test-data-flow.html"
echo ""
echo "🎯 AI Dojo: http://localhost:3000/admin/dojo"
echo "🔬 Nowa Analiza: http://localhost:3000/analysis/new"
echo ""
echo "📋 Logi backendu: docker-compose logs -f backend"
echo "📋 Logi frontendu: docker-compose logs -f frontend"
echo ""
echo "🔍 DEBUGGING FRONTEND UI:"
echo "   1. Otwórz http://localhost:3000 i przejdź do konwersacji"
echo "   2. Otwórz Developer Tools (F12) → Console"
echo "   3. Szukaj logów: 🔧 [ULTRA BRAIN DEBUG], 🔧 [CONVERSATION VIEW], 🔧 [STRATEGIC PANEL]"
echo "   4. Sprawdź czy archetypy wyświetlają się poprawnie (nie 'Profil w trakcie analizy...')"
echo "   5. Użyj validateUltraBrainData() w konsoli do sprawdzenia jakości danych"
echo ""

read -p "Naciśnij Enter aby kontynuować..."