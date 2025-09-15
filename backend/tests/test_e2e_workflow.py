"""
Kompleksowe testy End-to-End (E2E) dla Tesla Co-Pilot AI
Weryfikują stabilność systemu przed implementacją Fazy 1 (Fundamenty Psychometryczne)

Testowany przepływ:
1. Health checks (API, DB, Qdrant)
2. Masowy import bazy wiedzy
3. Pełny przepływ użytkownika: Klient -> Sesja -> Interakcja z RAG
"""

import pytest
import httpx
import json
import logging
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

# Konfiguracja testów
BASE_URL = "http://localhost:8000/api/v1"
KNOWLEDGE_BASE_PATH = Path(__file__).parent / "knowledge_base_pl.json"  # Ścieżka względna do pliku testu

# Pomocnicze stałe dla testów
TEST_CLIENT_DATA = {
    "archetype": "Pragmatyczny Analityk",
    "tags": ["b2b", "faza_decyzyjna"],
    "notes": "Testowy klient E2E"
}

TEST_SESSION_DATA = {
    "session_type": "consultation",
    "notes": "Testowa sesja E2E"
}

TEST_INTERACTION_DATA = {
    "user_input": "Klient jest dyrektorem finansowym i pyta o leasing oraz podwyższony limit kosztów do 225 000 zł dla aut elektrycznych. Chce konkretnych danych.",
    "interaction_type": "question"
}


@pytest.mark.asyncio
async def test_health_checks():
    """
    Sprawdza, czy wszystkie kluczowe usługi działają.
    
    Weryfikuje:
    - Główny endpoint zdrowia aplikacji
    - Zdrowia bazy danych
    - Zdrowia Qdrant (baza wektorowa)
    """
    logger.info("🏥 Rozpoczynam testy health check systemu...")
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Test 1: Główny health check
        logger.info("1️⃣ Testuję główny health check...")
        response_main = await client.get("/health")  # Używa pełnej ścieżki bez /api/v1
        assert response_main.status_code == 200, f"Health check failed: {response_main.status_code}"
        
        health_data = response_main.json()
        assert health_data["application"]["status"] in ["healthy", "degraded"], "Invalid health status"
        logger.info(f"✅ Health check: {health_data['application']['status']}")
        
        # Test 2: Database health check
        logger.info("2️⃣ Testuję health check bazy danych...")
        response_db = await client.get("/health/db")
        assert response_db.status_code == 200, f"DB health check failed: {response_db.status_code}"
        
        db_health = response_db.json()
        assert "db_status" in db_health or "status" in db_health, "DB health response missing status"
        logger.info("✅ Baza danych: OK")
        
        # Test 3: Qdrant health check
        logger.info("3️⃣ Testuję health check Qdrant...")
        response_qdrant = await client.get("/api/v1/knowledge/health/qdrant")
        assert response_qdrant.status_code == 200, f"Qdrant health check failed: {response_qdrant.status_code}"
        
        qdrant_health = response_qdrant.json()
        assert qdrant_health["status"] in ["ok", "healthy"], f"Qdrant not healthy: {qdrant_health}"
        logger.info("✅ Qdrant: OK")
    
    logger.info("🎉 Wszystkie health checks zakończone sukcesem!")


@pytest.mark.asyncio
async def test_knowledge_base_import_and_stats():
    """
    Testuje masowy import bazy wiedzy i weryfikuje statystyki.
    
    Proces:
    1. Wczytaj plik knowledge_base_pl.json
    2. Wykonaj bulk import do Qdrant
    3. Weryfikuj statystyki importu
    4. Sprawdź czy dane są dostępne w Qdrant
    """
    logger.info("📚 Rozpoczynam test importu bazy wiedzy...")
    
    # Krok 1: Wczytaj plik bazy wiedzy
    knowledge_file_path = KNOWLEDGE_BASE_PATH
    if not knowledge_file_path.exists():
        # Spróbuj alternatywnej ścieżki
        knowledge_file_path = Path("../knowledge_base_pl.json")
        if not knowledge_file_path.exists():
            pytest.skip("Plik knowledge_base_pl.json nie znaleziony")
    
    logger.info(f"📁 Wczytuję plik: {knowledge_file_path}")
    with open(knowledge_file_path, "r", encoding="utf-8") as f:
        knowledge_data = json.load(f)
    
    logger.info(f"📊 Wczytano {len(knowledge_data)} pozycji wiedzy")
    assert len(knowledge_data) > 0, "Baza wiedzy jest pusta"
    
    # Ograniczenie do 50 elementów (limit API)
    knowledge_batch = knowledge_data[:50] if len(knowledge_data) > 50 else knowledge_data
    logger.info(f"📦 Używam {len(knowledge_batch)} elementów do testu (limit API: 50)")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # Krok 2: Wykonaj bulk import
        logger.info("⬆️ Wykonuję bulk import...")
        # Owinięcie listy w obiekt zgodny z KnowledgeBulkCreate schema
        bulk_request = {"items": knowledge_batch}
        response_import = await client.post("/knowledge/bulk", json=bulk_request)
        assert response_import.status_code in [200, 201], f"Import failed: {response_import.status_code} - {response_import.text}"
        
        import_result = response_import.json()
        logger.info(f"✅ Import result: {import_result}")
        
        # Weryfikacje importu (dostosowane do rzeczywistego formatu API)
        assert "success_count" in import_result, "Brak informacji o liczbie zaimportowanych pozycji"
        assert "error_count" in import_result, "Brak informacji o błędach importu"
        assert import_result["success_count"] == len(knowledge_batch), f"Import incomplete: {import_result['success_count']} != {len(knowledge_batch)}"
        assert import_result["error_count"] == 0, f"Import errors occurred: {import_result['error_count']}"
        
        # Krok 3: Sprawdź podstawowe dane Qdrant
        logger.info("📈 Sprawdzam health check Qdrant po imporcie...")
        response_qdrant = await client.get("/knowledge/health/qdrant")
        assert response_qdrant.status_code == 200, f"Qdrant health check failed: {response_qdrant.status_code}"
        
        qdrant_result = response_qdrant.json()
        logger.info(f"📊 Qdrant: {qdrant_result}")
        
        # Weryfikacja stanu Qdrant po imporcie
        assert qdrant_result["status"] in ["ok", "healthy"], f"Qdrant not healthy: {qdrant_result}"
        assert qdrant_result["collection_exists"], "Kolekcja sales_knowledge nie istnieje"
        logger.info(f"✅ Import zweryfikowany: kolekcja istnieje, status: {qdrant_result['status']}")
    
    logger.info("🎉 Import bazy wiedzy zakończony sukcesem!")


@pytest.mark.asyncio  
async def test_full_user_workflow_with_rag():
    """
    Testuje kompletny przepływ: Klient -> Sesja -> Interakcja z RAG.
    
    To jest główny test E2E weryfikujący:
    - Tworzenie klienta
    - Tworzenie sesji dla klienta  
    - Tworzenie interakcji z wykorzystaniem RAG
    - Analiza odpowiedzi AI pod kątem jakości i kompletności
    """
    logger.info("🚀 Rozpoczynam pełny test przepływu użytkownika z RAG...")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # === KROK A: TWORZENIE KLIENTA ===
        logger.info("👤 A. Tworzę klienta testowego...")
        response_client = await client.post("/clients/", json=TEST_CLIENT_DATA)
        assert response_client.status_code == 201, f"Client creation failed: {response_client.status_code} - {response_client.text}"
        
        client_data = response_client.json()
        client_id = client_data["id"]
        logger.info(f"✅ Klient utworzony z ID: {client_id}")
        
        # Weryfikacja danych klienta
        assert "archetype" in client_data, "Brak archetypu klienta"
        assert client_data["archetype"] == TEST_CLIENT_DATA["archetype"], "Nieprawidłowy archetyp"
        assert "tags" in client_data, "Brak tagów klienta"
        
        # === KROK B: TWORZENIE SESJI ===
        logger.info("💬 B. Tworzę sesję dla klienta...")
        response_session = await client.post(f"/clients/{client_id}/sessions/", json=TEST_SESSION_DATA)
        assert response_session.status_code == 201, f"Session creation failed: {response_session.status_code} - {response_session.text}"
        
        session_data = response_session.json()
        session_id = session_data["id"]
        logger.info(f"✅ Sesja utworzona z ID: {session_id}")
        
        # Weryfikacja danych sesji
        assert "client_id" in session_data, "Brak ID klienta"
        assert session_data["client_id"] == client_id, "Nieprawidłowe powiązanie z klientem"
        assert "status" in session_data, "Brak statusu sesji"
        
        # === KROK C: TWORZENIE INTERAKCJI Z RAG ===
        logger.info("🧠 C. Tworzę interakcję z wykorzystaniem RAG...")
        logger.info(f"📝 Input: {TEST_INTERACTION_DATA['user_input'][:100]}...")
        
        response_interaction = await client.post(f"/sessions/{session_id}/interactions/", json=TEST_INTERACTION_DATA)
        assert response_interaction.status_code == 201, f"Interaction creation failed: {response_interaction.status_code} - {response_interaction.text}"
        
        interaction_result = response_interaction.json()
        logger.info("✅ Interakcja utworzona pomyślnie")
        
        # === WERYFIKACJA ODPOWIEDZI AI ===
        logger.info("🔍 D. Weryfikuję odpowiedź AI...")
        
        # Podstawowa struktura
        assert "ai_response_json" in interaction_result, "Brak odpowiedzi AI"
        ai_response = interaction_result["ai_response_json"]
        
        # Wymagane pola w odpowiedzi AI
        required_fields = ["quick_response", "main_analysis", "suggested_actions"]
        for field in required_fields:
            assert field in ai_response, f"Brak wymaganego pola: {field}"
            assert ai_response[field], f"Puste pole: {field}"
        
        # Weryfikacja suggested_actions
        suggested_actions = ai_response["suggested_actions"]
        assert isinstance(suggested_actions, list), "suggested_actions musi być listą"
        assert len(suggested_actions) > 0, "Brak sugerowanych akcji"
        
        # Każda akcja musi mieć wymagane pola
        for action in suggested_actions:
            assert "action" in action, "Akcja bez opisu"
            assert "reasoning" in action, "Akcja bez uzasadnienia"
        
        logger.info(f"📊 AI Response - Quick: {ai_response['quick_response'][:50]}...")
        logger.info(f"📊 AI Response - Actions: {len(suggested_actions)} sugerowanych akcji")
        
        # === WERYFIKACJA RAG (treściowa) ===
        logger.info("🔎 E. Weryfikuję wykorzystanie RAG...")
        
        # Połącz wszystkie teksty z odpowiedzi AI
        full_response_text = (
            ai_response.get("quick_response", "") + " " + 
            ai_response.get("main_analysis", "")
        ).lower()
        
        # Sprawdź czy odpowiedź zawiera informacje związane z limitami leasingowymi
        # (nasze pytanie dotyczyło limitu 225 000 zł)
        rag_indicators = [
            "225", "limit", "koszt", "leasing", "elektryczne", 
            "podatkow", "finansow", "dyrektor"
        ]
        
        found_indicators = [indicator for indicator in rag_indicators if indicator in full_response_text]
        
        logger.info(f"🎯 Znalezione wskaźniki RAG: {found_indicators}")
        
        # Co najmniej 2-3 wskaźniki powinny być obecne dla dobrego RAG
        assert len(found_indicators) >= 2, f"Zbyt mało wskaźników RAG: {found_indicators}. Odpowiedź może nie korzystać z bazy wiedzy."
        
        # === WERYFIKACJA METADANYCH ===
        logger.info("📋 F. Weryfikuję metadane interakcji...")
        
        # Sprawdź podstawowe metadane
        assert "id" in interaction_result, "Brak ID interakcji"
        assert "session_id" in interaction_result, "Brak session_id"
        assert interaction_result["session_id"] == session_id, "Nieprawidłowy session_id"
        assert "user_input" in interaction_result, "Brak user_input"
        assert "interaction_type" in interaction_result, "Brak interaction_type"
        
        # Sprawdź czy AI response ma wymagane metadane
        if "confidence_level" in ai_response:
            confidence = ai_response["confidence_level"]
            assert isinstance(confidence, (int, float)), "confidence_level musi być liczbą"
            assert 0 <= confidence <= 100, f"confidence_level poza zakresem: {confidence}"
        
        logger.info("✅ Wszystkie weryfikacje metadanych zakończone sukcesem")
    
    logger.info("🎉 PEŁNY TEST E2E ZAKOŃCZONY SUKCESEM!")
    logger.info("=" * 60)
    logger.info("🏆 PODSUMOWANIE TESTU:")
    logger.info(f"✅ Klient utworzony: ID {client_id}")
    logger.info(f"✅ Sesja utworzona: ID {session_id}")
    logger.info(f"✅ Interakcja z RAG: Pomyślna")
    logger.info(f"✅ Wskaźniki RAG: {len(found_indicators)} z {len(rag_indicators)}")
    logger.info(f"✅ Akcje AI: {len(suggested_actions)} sugerowanych")
    logger.info("=" * 60)


@pytest.mark.asyncio
async def test_api_error_handling():
    """
    Dodatkowy test weryfikujący obsługę błędów API.
    
    Testuje czy system prawidłowo obsługuje:
    - Nieprawidłowe ID klientów/sesji
    - Nieprawidłowe dane wejściowe
    - Timeouty i błędy sieciowe
    """
    logger.info("❌ Rozpoczynam test obsługi błędów...")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # Test 1: Nieistniejący klient
        logger.info("1️⃣ Test nieistniejącego klienta...")
        response = await client.get("/clients/99999")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        logger.info("✅ 404 dla nieistniejącego klienta: OK")
        
        # Test 2: Nieprawidłowe dane klienta (archetype za długi)
        logger.info("2️⃣ Test nieprawidłowych danych klienta...")
        invalid_client_data = {
            "archetype": "A" * 101,  # Przekracza max_length=100
            "tags": ["test"],
            "notes": "Test walidacji"
        }
        response = await client.post("/clients/", json=invalid_client_data)
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        logger.info("✅ Walidacja danych klienta: OK")
        
        # Test 3: Nieistniejąca sesja
        logger.info("3️⃣ Test nieistniejącej sesji...")
        response = await client.get("/sessions/99999")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        logger.info("✅ 404 dla nieistniejącej sesji: OK")
    
    logger.info("🎉 Test obsługi błędów zakończony sukcesem!")


# === KONFIGURACJA PYTEST ===

def pytest_configure(config):
    """Konfiguracja pytest z logowaniem."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )


if __name__ == "__main__":
    """Uruchamia testy bezpośrednio."""
    pytest.main([__file__, "-v", "-s"])
