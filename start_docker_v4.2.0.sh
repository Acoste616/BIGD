#!/bin/bash

# ========================================
# SALES COPILOT v4.2.0 - URUCHAMIANIE DOCKER
# ========================================

echo "========================================"
echo "SALES COPILOT v4.2.0 - URUCHAMIANIE DOCKER"
echo "========================================"

echo ""
echo "[1/6] Sprawdzanie Docker i Docker Compose..."
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
echo "[2/6] Zatrzymywanie istniejących kontenerów..."
docker-compose down --volumes --remove-orphans
echo "✅ Kontenery zatrzymane"

echo ""
echo "[3/6] Usuwanie starych obrazów..."
docker system prune -f
echo "✅ Stare obrazy usunięte"

echo ""
echo "[4/6] Budowanie nowych obrazów v4.2.0..."
docker-compose build --no-cache
if [ $? -ne 0 ]; then
    echo "❌ Błąd podczas budowania obrazów!"
    exit 1
fi
echo "✅ Obrazy v4.2.0 zbudowane"

echo ""
echo "[5/6] Uruchamianie serwisów v4.2.0..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Błąd podczas uruchamiania serwisów!"
    exit 1
fi
echo "✅ Serwisy v4.2.0 uruchomione"

echo ""
echo "[6/6] Sprawdzanie statusu serwisów..."
sleep 15
docker-compose ps

echo ""
echo "========================================"
echo "DOCKER v4.2.0 URUCHOMIONY POMYŚLNIE!"
echo "========================================"
echo ""
echo "🚀 Frontend (Ultra Brain v4.2.0): http://localhost:3000"
echo "🧠 Backend (Modular Architecture): http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🗄️  Database: localhost:5432"
echo "🔍 Qdrant Vector DB: localhost:6333"
echo ""
echo "🎯 AI Dojo: http://localhost:3000/admin/dojo"
echo "🔬 Nowa Analiza: http://localhost:3000/analysis/new"
echo ""
echo "📋 Logi backendu: docker-compose logs -f backend"
echo "📋 Logi frontendu: docker-compose logs -f frontend"
echo ""

read -p "Naciśnij Enter aby kontynuować..."
