#!/bin/bash
echo "--- Uruchamianie testów E2E dla Co-Pilot AI ---"

# Przejdź do katalogu backendu
cd backend

# Uruchom testy za pomocą pytest
poetry run pytest tests/test_e2e_workflow.py -v

echo "--- Testy zakończone ---"
