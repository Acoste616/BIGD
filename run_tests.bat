@echo off
echo --- Uruchamianie testow E2E dla Co-Pilot AI ---

REM Przejdz do katalogu backendu
cd backend

REM Uruchom testy za pomocą pytest
poetry run pytest tests/test_e2e_workflow.py -v

echo --- Testy zakonczone ---
pause
