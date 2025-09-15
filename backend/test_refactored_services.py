#!/usr/bin/env python3
"""
Test refaktoryzowanych serwisów AI - sprawdza czy dynamiczne pobieranie promptów działa
"""
import asyncio
import sys
import os

# Dodaj ścieżkę do modułów aplikacji
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.ai.psychology_service import PsychologyService
from app.services.ai.sales_strategy_service import SalesStrategyService
from app.repositories.prompt_template_repository import PromptTemplateRepository

# Konfiguracja bazy danych
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Testowe dane
TEST_CONVERSATION = [
    {"user_input": "Interesuje mnie Tesla Model S. Czy to bezpieczny samochód?", "timestamp": "2025-01-01T10:00:00"},
    {"user_input": "Jakie są koszty eksploatacji w porównaniu do BMW?", "timestamp": "2025-01-01T10:05:00"}
]

TEST_CLIENT_PROFILE = {
    "alias": "Test Client",
    "archetype": "Pragmatyczny Analityk"
}

async def test_psychology_service():
    """Test PsychologyService z dynamicznym promptem"""
    print("🧠 Testuję PsychologyService...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Inicjalizuj serwis
            psychology_service = PsychologyService(session)
            
            # Test generowania analizy psychometrycznej
            result = await psychology_service.generate_psychometric_analysis(
                conversation_history=TEST_CONVERSATION,
                additional_context={"client_profile": TEST_CLIENT_PROFILE}
            )
            
            # Sprawdź czy wynik ma oczekiwaną strukturę
            assert "big_five" in result, "Brak analizy Big Five"
            assert "disc" in result, "Brak analizy DISC"
            assert "schwartz_values" in result, "Brak wartości Schwartza"
            assert "analysis_timestamp" in result, "Brak timestamp"
            
            print("✅ PsychologyService działa poprawnie z dynamicznym promptem!")
            print(f"   - Confidence: {result.get('confidence', 0)}%")
            print(f"   - Model: {result.get('model_used', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Błąd w PsychologyService: {e}")
            return False

async def test_sales_strategy_service():
    """Test SalesStrategyService z dynamicznym promptem"""
    print("🎯 Testuję SalesStrategyService...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Inicjalizuj serwis
            sales_service = SalesStrategyService(session)
            
            # Test generowania strategii sprzedażowej
            result = await sales_service.generate_sales_strategy(
                user_input="Czy Tesla Model S jest warta swojej ceny?",
                client_profile=TEST_CLIENT_PROFILE,
                session_history=TEST_CONVERSATION
            )
            
            # Sprawdź czy wynik ma oczekiwaną strukturę
            assert "quick_response" in result, "Brak quick_response"
            assert "strategic_recommendation" in result, "Brak strategic_recommendation"
            assert "generated_at" in result, "Brak timestamp"
            
            print("✅ SalesStrategyService działa poprawnie z dynamicznym promptem!")
            print(f"   - Confidence: {result.get('confidence', 0)}%")
            print(f"   - Model: {result.get('model_used', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Błąd w SalesStrategyService: {e}")
            return False

async def test_prompt_repository():
    """Test PromptTemplateRepository"""
    print("📋 Testuję PromptTemplateRepository...")
    
    async with AsyncSessionLocal() as session:
        try:
            repo = PromptTemplateRepository(session)
            
            # Test pobierania promptu psychology_analysis
            psychology_prompt = await repo.get_active_prompt_by_name("psychology_analysis")
            assert psychology_prompt is not None, "Prompt psychology_analysis nie został znaleziony"
            assert str(psychology_prompt.status) == "PromptStatus.ACTIVE" or psychology_prompt.status.value == "ACTIVE", f"Prompt nie jest aktywny: {psychology_prompt.status}"
            
            # Test pobierania promptu sales_strategy_generation
            sales_prompt = await repo.get_active_prompt_by_name("sales_strategy_generation")
            assert sales_prompt is not None, "Prompt sales_strategy_generation nie został znaleziony"
            assert str(sales_prompt.status) == "PromptStatus.ACTIVE" or sales_prompt.status.value == "ACTIVE", f"Prompt nie jest aktywny: {sales_prompt.status}"
            
            print("✅ PromptTemplateRepository działa poprawnie!")
            print(f"   - psychology_analysis: {len(psychology_prompt.content)} znaków")
            print(f"   - sales_strategy_generation: {len(sales_prompt.content)} znaków")
            
            return True
            
        except Exception as e:
            print(f"❌ Błąd w PromptTemplateRepository: {e}")
            return False

async def main():
    """Główna funkcja testowa"""
    print("🚀 Rozpoczynam test refaktoryzowanych serwisów AI...\n")
    
    results = []
    
    # Test 1: PromptTemplateRepository
    results.append(await test_prompt_repository())
    print()
    
    # Test 2: PsychologyService
    results.append(await test_psychology_service())
    print()
    
    # Test 3: SalesStrategyService
    results.append(await test_sales_strategy_service())
    print()
    
    # Podsumowanie
    passed = sum(results)
    total = len(results)
    
    print(f"📊 PODSUMOWANIE TESTÓW:")
    print(f"   ✅ Przeszło: {passed}/{total}")
    print(f"   ❌ Nie przeszło: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Wszystkie testy przeszły! Refaktoryzacja zakończona sukcesem.")
        return 0
    else:
        print("\n⚠️ Niektóre testy nie przeszły. Sprawdź logi powyżej.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)