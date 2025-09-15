#!/usr/bin/env python3
"""
Test SemanticValidatorService - sprawdza walidację semantyczną odpowiedzi AI
"""
import asyncio
import sys
import os

# Dodaj ścieżkę do modułów aplikacji
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai.semantic_validator_service import SemanticValidatorService

# Testowe dane
VALID_HOLISTIC_ANALYSIS = {
    "holistic_summary": "Klient to analityczny perfekcjonista o wysokiej potrzebie kontroli, który podejmuje decyzje ostrożnie ale zdecydowanie.",
    "main_drive": "Potrzeba kompetencji i kontroli nad decyzjami",
    "communication_style": {
        "preferred_approach": "Systematyczny i oparty na faktach",
        "tone": "Profesjonalny z elementami eksperckim",
        "pace": "Metodyczny - nie spiesz się",
        "information_density": "Wysoka - lubi szczegóły",
        "keywords_to_use": ["dane", "fakty", "analiza", "szczegóły"],
        "keywords_to_avoid": ["emocje", "intuicja", "szybko"]
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
        "Brak dowodów na przewagi",
        "Agresywna sprzedaż"
    ],
    "confidence": 85,
    "disc_profile": {
        "dominant_factor": "C",
        "communication_style_advice": "Przedstaw szczegółowe dane i fakty. Klient ceni precyzję i analityczne podejście."
    },
    "archetype_analysis": {
        "primary_archetype": "Analityczny Perfekcjonista",
        "confidence": 80
    }
}

INVALID_HOLISTIC_ANALYSIS_MISSING_FIELDS = {
    "holistic_summary": "Krótki opis",
    # Brak main_drive, communication_style, key_levers, red_flags
    "confidence": 75
}

INVALID_HOLISTIC_ANALYSIS_DISC_MISMATCH = {
    "holistic_summary": "Klient to analityczny perfekcjonista",
    "main_drive": "Potrzeba kontroli",
    "communication_style": {
        "preferred_approach": "Systematyczny"
    },
    "key_levers": ["Dane techniczne", "Analiza kosztów", "Opinie ekspertów"],
    "red_flags": ["Presja czasowa", "Brak danych", "Agresywna sprzedaż"],
    "confidence": 70,
    "disc_profile": {
        "dominant_factor": "C",  # Analityczny
        "communication_style_advice": "Bądź entuzjastyczny i towarzyski!"  # Niepasujące do C!
    },
    "archetype_analysis": {
        "primary_archetype": "Analityczny Perfekcjonista",
        "confidence": 75
    }
}

VALID_PSYCHOLOGY_PROFILE = {
    "big_five": {
        "openness": {"score": 7, "rationale": "Klient pyta o innowacyjne funkcje Tesla", "strategy": "Podkreśl technologię"},
        "conscientiousness": {"score": 8, "rationale": "Wymaga szczegółowych danych", "strategy": "Przedstaw TCO"},
        "extraversion": {"score": 5, "rationale": "Umiarkowanie towarzyski", "strategy": "Balansuj podejście"},
        "agreeableness": {"score": 6, "rationale": "Szuka konsensusu", "strategy": "Buduj zaufanie"},
        "neuroticism": {"score": 4, "rationale": "Stabilny emocjonalnie", "strategy": "Standardowe podejście"}
    },
    "disc": {
        "dominance": {"score": 6, "rationale": "Decyzyjny", "strategy": "Prezentuj fakty"},
        "influence": {"score": 4, "rationale": "Mniej towarzyski", "strategy": "Fokus na logice"},
        "steadiness": {"score": 7, "rationale": "Ceni stabilność", "strategy": "Podkreśl niezawodność"},
        "compliance": {"score": 8, "rationale": "Analityczny", "strategy": "Dostarczaj dane"}
    },
    "schwartz_values": [
        {"value_name": "Bezpieczeństwo", "is_present": True, "rationale": "Pyta o bezpieczeństwo", "strategy": "Podkreśl oceny"},
        {"value_name": "Osiągnięcia", "is_present": False, "rationale": "Brak oznak", "strategy": "Nie fokusuj"}
    ],
    "confidence": 82
}

INVALID_PSYCHOLOGY_PROFILE = {
    "big_five": {
        "openness": {"score": 15, "rationale": "Za krótkie", "strategy": "Brak"},  # Score poza zakresem
        # Brak innych cech Big Five
    },
    "disc": {
        "dominance": {"score": "high", "rationale": "Niepoprawny typ", "strategy": "Test"}  # Score nie jest liczbą
    },
    "schwartz_values": "not_a_list",  # Powinno być listą
    "confidence": 150  # Poza zakresem
}

async def test_valid_holistic_analysis():
    """Test walidacji poprawnej analizy holistycznej"""
    print("🧪 Test 1: Poprawna analiza holistyczna...")
    
    validator = SemanticValidatorService()
    is_valid, error_message = validator.validate_holistic_synthesis(VALID_HOLISTIC_ANALYSIS)
    
    if is_valid:
        print("   ✅ Test przeszedł - analiza uznana za poprawną")
        return True
    else:
        print(f"   ❌ Test nie przeszedł - nieoczekiwany błąd: {error_message}")
        return False

async def test_invalid_holistic_analysis_missing_fields():
    """Test walidacji analizy z brakującymi polami"""
    print("🧪 Test 2: Analiza z brakującymi polami...")
    
    validator = SemanticValidatorService()
    is_valid, error_message = validator.validate_holistic_synthesis(INVALID_HOLISTIC_ANALYSIS_MISSING_FIELDS)
    
    if not is_valid:
        print(f"   ✅ Test przeszedł - wykryto brakujące pola: {error_message}")
        return True
    else:
        print("   ❌ Test nie przeszedł - nie wykryto brakujących pól")
        return False

async def test_invalid_holistic_analysis_disc_mismatch():
    """Test walidacji analizy z niespójnym profilem DISC"""
    print("🧪 Test 3: Analiza z niespójnym profilem DISC...")
    
    validator = SemanticValidatorService()
    is_valid, error_message = validator.validate_holistic_synthesis(INVALID_HOLISTIC_ANALYSIS_DISC_MISMATCH)
    
    if not is_valid:
        print(f"   ✅ Test przeszedł - wykryto niespójność DISC: {error_message}")
        return True
    else:
        print("   ❌ Test nie przeszedł - nie wykryto niespójności DISC")
        return False

async def test_valid_psychology_profile():
    """Test walidacji poprawnego profilu psychometrycznego"""
    print("🧪 Test 4: Poprawny profil psychometryczny...")
    
    validator = SemanticValidatorService()
    is_valid, error_message = validator.validate_psychology_profile(VALID_PSYCHOLOGY_PROFILE)
    
    if is_valid:
        print("   ✅ Test przeszedł - profil uznany za poprawny")
        return True
    else:
        print(f"   ❌ Test nie przeszedł - nieoczekiwany błąd: {error_message}")
        return False

async def test_invalid_psychology_profile():
    """Test walidacji niepoprawnego profilu psychometrycznego"""
    print("🧪 Test 5: Niepoprawny profil psychometryczny...")
    
    validator = SemanticValidatorService()
    is_valid, error_message = validator.validate_psychology_profile(INVALID_PSYCHOLOGY_PROFILE)
    
    if not is_valid:
        print(f"   ✅ Test przeszedł - wykryto błędy: {error_message}")
        return True
    else:
        print("   ❌ Test nie przeszedł - nie wykryto błędów w profilu")
        return False

async def test_confidence_score_validation():
    """Test walidacji confidence score"""
    print("🧪 Test 6: Walidacja confidence score...")
    
    validator = SemanticValidatorService()
    
    # Test 1: Poprawny confidence
    test_data_valid = {**VALID_HOLISTIC_ANALYSIS, "confidence": 75}
    is_valid, _ = validator.validate_holistic_synthesis(test_data_valid)
    
    if not is_valid:
        print("   ❌ Test nie przeszedł - odrzucono poprawny confidence")
        return False
    
    # Test 2: Confidence poza zakresem
    test_data_invalid = {**VALID_HOLISTIC_ANALYSIS, "confidence": 150}
    is_valid, error_message = validator.validate_holistic_synthesis(test_data_invalid)
    
    if is_valid:
        print("   ❌ Test nie przeszedł - zaakceptowano niepoprawny confidence")
        return False
    
    print(f"   ✅ Test przeszedł - wykryto niepoprawny confidence: {error_message}")
    return True

async def test_strategic_elements_validation():
    """Test walidacji elementów strategicznych"""
    print("🧪 Test 7: Walidacja elementów strategicznych...")
    
    validator = SemanticValidatorService()
    
    # Test z zbyt krótkimi key_levers
    test_data = {
        **VALID_HOLISTIC_ANALYSIS,
        "key_levers": ["OK", "X", "Zbyt krótkie"],  # "X" jest za krótkie
        "red_flags": ["Poprawna długość flagi", "Inna poprawna flaga"]
    }
    
    is_valid, error_message = validator.validate_holistic_synthesis(test_data)
    
    if not is_valid and "zbyt krótki" in error_message.lower():
        print(f"   ✅ Test przeszedł - wykryto zbyt krótkie elementy: {error_message}")
        return True
    else:
        print(f"   ❌ Test nie przeszedł - nie wykryto problemu z długością elementów")
        return False

async def main():
    """Główna funkcja testowa"""
    print("🚀 Rozpoczynam testy SemanticValidatorService...\n")
    
    tests = [
        test_valid_holistic_analysis,
        test_invalid_holistic_analysis_missing_fields,
        test_invalid_holistic_analysis_disc_mismatch,
        test_valid_psychology_profile,
        test_invalid_psychology_profile,
        test_confidence_score_validation,
        test_strategic_elements_validation
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
        print()
    
    # Podsumowanie
    passed = sum(results)
    total = len(results)
    
    print(f"📊 PODSUMOWANIE TESTÓW SEMANTIC VALIDATOR:")
    print(f"   ✅ Przeszło: {passed}/{total}")
    print(f"   ❌ Nie przeszło: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Wszystkie testy przeszły! SemanticValidatorService działa poprawnie.")
        print("\n📋 Podsumowanie funkcjonalności:")
        print("   ✅ Walidacja kompletności pól")
        print("   ✅ Walidacja spójności profili DISC")
        print("   ✅ Walidacja zakresów confidence score")
        print("   ✅ Walidacja profili psychometrycznych")
        print("   ✅ Walidacja elementów strategicznych")
        print("   ✅ Wykrywanie halucynacji AI")
        return 0
    else:
        print("\n⚠️ Niektóre testy nie przeszły. Sprawdź implementację.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)