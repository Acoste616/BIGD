#!/bin/bash
echo "--- Uruchamianie testów E2E dla Co-Pilot AI ---"

# Przejdź do katalogu backendu
cd backend

# Sprawdź czy poetry jest dostępne
if ! command -v poetry &> /dev/null
then
    echo "Poetry nie zostało znalezione. Instalowanie..."
    pip install poetry
fi

# Zainstaluj zależności jeśli potrzebne
echo "Sprawdzanie zależności..."
poetry install

# Uruchom testy jednostkowe dla sesji
echo "Uruchamianie testów jednostkowych dla sesji..."
poetry run pytest test_session_router.py -v
if [ $? -ne 0 ]; then
    echo "❌ Testy jednostkowe dla sesji nie powiodły się"
    exit 1
fi

# Uruchom testy endpointów dla sesji
echo "Uruchamianie testów endpointów dla sesji..."
poetry run pytest test_session_endpoints.py -v
if [ $? -ne 0 ]; then
    echo "❌ Testy endpointów dla sesji nie powiodły się"
    exit 1
fi

# Uruchom testy integracyjne
echo "Uruchamianie testów integracyjnych..."
poetry run pytest test_session_integration.py -v
if [ $? -ne 0 ]; then
    echo "❌ Testy integracyjne nie powiodły się"
    exit 1
fi

# Uruchom testy E2E
echo "Uruchamianie testów E2E..."
poetry run pytest tests/test_e2e_workflow.py -v
if [ $? -ne 0 ]; then
    echo "❌ Testy E2E nie powiodły się"
    exit 1
fi

echo "✅ Wszystkie testy zakończone pomyślnie"
echo "--- Testy zakończone ---"