@echo off
echo --- Uruchamianie testow E2E dla Co-Pilot AI ---

REM Przejdz do katalogu backendu
cd backend

REM Sprawdz czy poetry jest dostepne
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Poetry nie zostalo znalezione. Instalowanie...
    pip install poetry
)

REM Zainstaluj zaleznosci jesli potrzebne
echo Sprawdzanie zaleznosci...
poetry install

REM Uruchom testy jednostkowe dla sesji
echo Uruchamianie testow jednostkowych dla sesji...
poetry run pytest test_session_router.py -v
if %errorlevel% neq 0 (
    echo ❌ Testy jednostkowe dla sesji nie powiodly sie
    exit /b 1
)

REM Uruchom testy endpointow dla sesji
echo Uruchamianie testow endpointow dla sesji...
poetry run pytest test_session_endpoints.py -v
if %errorlevel% neq 0 (
    echo ❌ Testy endpointow dla sesji nie powiodly sie
    exit /b 1
)

REM Uruchom testy integracyjne
echo Uruchamianie testow integracyjnych...
poetry run pytest test_session_integration.py -v
if %errorlevel% neq 0 (
    echo ❌ Testy integracyjne nie powiodly sie
    exit /b 1
)

REM Uruchom testy E2E
echo Uruchamianie testow E2E...
poetry run pytest tests/test_e2e_workflow.py -v
if %errorlevel% neq 0 (
    echo ❌ Testy E2E nie powiodly sie
    exit /b 1
)

echo ✅ Wszystkie testy zakonczone pomyslnie
echo --- Testy zakonczone ---
pause