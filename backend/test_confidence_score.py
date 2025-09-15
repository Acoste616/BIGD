#!/usr/bin/env python3
"""
Test zaawansowanego algorytmu Confidence Score w HolisticSynthesisService
"""
import asyncio
import sys
import os

# Dodaj ścieżkę do modułów aplikacji
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.ai.holistic_synthesis_service import HolisticSynthesisService

# Konfiguracja bazy danych
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Testowe dane
TEST_HOLISTIC_ANALYSIS = {
    "holistic_summary": "Klient to analityczny perfekcjonista o wysokiej potrzebie kontroli",
    "main_drive": "Potrzeba kompetencji i kontroli nad decyzjami",
    "communication_style": {
        "preferred_approach": "Systematyczny i oparty na faktach",
        "tone": "Profesjonalny z elementami eksperckim",
        "pace": "Metodyczny - nie spiesz się",
        "information_density": "Wysoka - lubi szczegóły"
    },
    "key_levers": [
        "Dane techniczne i porównania",
        "Opinie ekspertów i recenzje",
        "TCO i długoterminowa wartość",
        "Prestiż marki i innowacyjność"
    ],
    "red_flags": [
        "Presja czasowa",
        "Niejasne korzyści finansowe",
        "Brak dowodów na przewagi"
    ]
}

TEST_INTERACTIONS = [
    {"user_input": "Interesuje mnie Tesla Model S. Czy to bezpieczny samochód?"},
    {"user_input": "Jakie są koszty eksploatacji w porównaniu do BMW?"},
    {"user_input": "Czy Tesla ma dobrą sieć serwisową w Polsce?"},
    {"user_input": "Ile kosztuje ubezpieczenie Tesla?"},
    {"user_input": "Jakie są opinie innych użytkowników?"}
]

TEST_PREVIOUS_PSYCHOLOGY = {
    "archetype_analysis": {
        "primary_archetype": "Potrzeba kompetencji i kontroli nad decyzjami",
        "confidence": 75
    },
    "disc_profile": {
        "dominant_factor": "C",
        "secondary_factor": "D"
    }
}

async def test_confidence_score_basic():
    """Test podstawowego obliczania confidence score"""
    print("🧮 Test 1: Podstawowe obliczanie confidence score...")
    
    async with AsyncSessionLocal() as session:
        try:
            service = HolisticSynthesisService(session)
            
            # Test z 5 interakcjami (powinno dać base_score = 30)
            confidence = await service._calculate_confidence_score(
                new_analysis=TEST_HOLISTIC_ANALYSIS,
                all_interactions=TEST_INTERACTIONS,
                previous_session_psychology=None
            )
            
            print(f"   Confidence score (5 interactions, no previous): {confidence}%")
            assert 25 <= confidence <= 60, f"Oczekiwano 25-60%, otrzymano {confidence}%"
            print("   ✅ Test podstawowy przeszedł")
            return True
            
        except Exception as e:
            print(f"   ❌ Błąd w teście podstawowym: {e}")
            return False

async def test_confidence_score_consistency():
    """Test bonusu za spójność z poprzednią analizą"""
    print("🔄 Test 2: Bonus za spójność...")
    
    async with AsyncSessionLocal() as session:
        try:
            service = HolisticSynthesisService(session)
            
            # Test ze spójną poprzednią analizą
            confidence = await service._calculate_confidence_score(
                new_analysis=TEST_HOLISTIC_ANALYSIS,
                all_interactions=TEST_INTERACTIONS,
                previous_session_psychology=TEST_PREVIOUS_PSYCHOLOGY
            )
            
            print(f"   Confidence score (with consistent previous): {confidence}%")
            assert confidence >= 50, f"Oczekiwano co najmniej 50% z bonusem, otrzymano {confidence}%"
            print("   ✅ Test spójności przeszedł")
            return True
            
        except Exception as e:
            print(f"   ❌ Błąd w teście spójności: {e}")
            return False

async def test_confidence_score_contradiction():
    """Test kary za sprzeczność z poprzednią analizą"""
    print("⚠️ Test 3: Kara za sprzeczność...")
    
    async with AsyncSessionLocal() as session:
        try:
            service = HolisticSynthesisService(session)
            
            # Stwórz sprzeczną poprzednią analizę
            contradictory_previous = {
                "archetype_analysis": {
                    "primary_archetype": "Impulsywny Odkrywca",  # Różny od "Potrzeba kompetencji..."
                    "confidence": 80
                },
                "disc_profile": {
                    "dominant_factor": "I",  # Różny od "C"
                    "secondary_factor": "D"
                }
            }
            
            confidence = await service._calculate_confidence_score(
                new_analysis=TEST_HOLISTIC_ANALYSIS,
                all_interactions=TEST_INTERACTIONS,
                previous_session_psychology=contradictory_previous
            )
            
            print(f"   Confidence score (with contradictory previous): {confidence}%")
            # Powinno być niższe niż test podstawowy z powodu kar
            assert confidence <= 40, f"Oczekiwano maksymalnie 40% z karą, otrzymano {confidence}%"
            print("   ✅ Test sprzeczności przeszedł")
            return True
            
        except Exception as e:
            print(f"   ❌ Błąd w teście sprzeczności: {e}")
            return False

async def test_confidence_score_quality():
    """Test bonusu za jakość analizy"""
    print("⭐ Test 4: Bonus za jakość analizy...")
    
    async with AsyncSessionLocal() as session:
        try:
            service = HolisticSynthesisService(session)
            
            # Test z niepełną analizą (mniej pól)
            incomplete_analysis = {
                "holistic_summary": "Podstawowy opis klienta",
                "main_drive": "Nieznany"
                # Brak communication_style, key_levers, red_flags
            }
            
            confidence_incomplete = await service._calculate_confidence_score(
                new_analysis=incomplete_analysis,
                all_interactions=TEST_INTERACTIONS,
                previous_session_psychology=None
            )
            
            confidence_complete = await service._calculate_confidence_score(
                new_analysis=TEST_HOLISTIC_ANALYSIS,
                all_interactions=TEST_INTERACTIONS,
                previous_session_psychology=None
            )
            
            print(f"   Confidence (incomplete): {confidence_incomplete}%")
            print(f"   Confidence (complete): {confidence_complete}%")
            
            assert confidence_complete > confidence_incomplete, "Kompletna analiza powinna mieć wyższy confidence"
            print("   ✅ Test jakości przeszedł")
            return True
            
        except Exception as e:
            print(f"   ❌ Błąd w teście jakości: {e}")
            return False

async def test_full_integration():
    """Test pełnej integracji z metodą run_holistic_synthesis"""
    print("🔗 Test 5: Pełna integracja...")
    
    async with AsyncSessionLocal() as session:
        try:
            service = HolisticSynthesisService(session)
            
            # Przygotuj testowy profil psychometryczny
            test_psychology_profile = {
                "big_five": {
                    "openness": {"score": 7, "rationale": "Test", "strategy": "Test"},
                    "conscientiousness": {"score": 8, "rationale": "Test", "strategy": "Test"},
                    "extraversion": {"score": 5, "rationale": "Test", "strategy": "Test"},
                    "agreeableness": {"score": 6, "rationale": "Test", "strategy": "Test"},
                    "neuroticism": {"score": 4, "rationale": "Test", "strategy": "Test"}
                },
                "disc": {
                    "dominance": {"score": 6, "rationale": "Test", "strategy": "Test"},
                    "influence": {"score": 4, "rationale": "Test", "strategy": "Test"},
                    "steadiness": {"score": 7, "rationale": "Test", "strategy": "Test"},
                    "compliance": {"score": 8, "rationale": "Test", "strategy": "Test"}
                },
                "schwartz_values": [
                    {"value_name": "Bezpieczeństwo", "is_present": True, "rationale": "Test", "strategy": "Test"}
                ],
                "confidence": 75
            }
            
            # Dodaj kontekst z interakcjami
            additional_context = {
                "all_interactions": TEST_INTERACTIONS,
                "previous_psychology": TEST_PREVIOUS_PSYCHOLOGY
            }
            
            # Wywołaj główną metodę
            result = await service.run_holistic_synthesis(
                raw_psychology_profile=test_psychology_profile,
                additional_context=additional_context
            )
            
            # Sprawdź czy confidence został obliczony przez nowy algorytm
            assert "confidence" in result, "Brak pola confidence w wyniku"
            confidence = result["confidence"]
            print(f"   Final confidence score: {confidence}%")
            
            # Sprawdź czy confidence jest w rozsądnym zakresie
            assert 0 <= confidence <= 100, f"Confidence poza zakresem: {confidence}%"
            
            # Sprawdź czy synthesis_confidence też został zaktualizowany
            assert result.get("synthesis_confidence") == confidence, "synthesis_confidence nie został zaktualizowany"
            
            print("   ✅ Test pełnej integracji przeszedł")
            return True
            
        except Exception as e:
            print(f"   ❌ Błąd w teście integracji: {e}")
            return False

async def main():
    """Główna funkcja testowa"""
    print("🚀 Rozpoczynam testy zaawansowanego Confidence Score...\n")
    
    tests = [
        test_confidence_score_basic,
        test_confidence_score_consistency,
        test_confidence_score_contradiction,
        test_confidence_score_quality,
        test_full_integration
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
        print()
    
    # Podsumowanie
    passed = sum(results)
    total = len(results)
    
    print(f"📊 PODSUMOWANIE TESTÓW CONFIDENCE SCORE:")
    print(f"   ✅ Przeszło: {passed}/{total}")
    print(f"   ❌ Nie przeszło: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Wszystkie testy przeszły! Zaawansowany Confidence Score działa poprawnie.")
        return 0
    else:
        print("\n⚠️ Niektóre testy nie przeszły. Sprawdź implementację.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)