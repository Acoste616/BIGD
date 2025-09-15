#!/usr/bin/env python3
"""
Test integracji SemanticValidatorService z InteractionService
"""
import asyncio
import sys
import os

# Dodaj ścieżkę do modułów aplikacji
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.interaction_service import InteractionService
from app.services.ai.semantic_validator_service import SemanticValidatorService

async def test_interaction_service_initialization():
    """Test czy InteractionService poprawnie inicjalizuje SemanticValidatorService"""
    print("🧪 Test 1: Inicjalizacja InteractionService z SemanticValidatorService...")
    
    try:
        # Inicjalizuj InteractionService
        interaction_service = InteractionService()
        
        # Sprawdź czy semantic_validator został zainicjalizowany
        if hasattr(interaction_service, 'semantic_validator'):
            if isinstance(interaction_service.semantic_validator, SemanticValidatorService):
                print("   ✅ Test przeszedł - SemanticValidatorService poprawnie zainicjalizowany")
                return True
            else:
                print(f"   ❌ Test nie przeszedł - semantic_validator ma niepoprawny typ: {type(interaction_service.semantic_validator)}")
                return False
        else:
            print("   ❌ Test nie przeszedł - brak atrybutu semantic_validator")
            return False
            
    except Exception as e:
        print(f"   ❌ Test nie przeszedł - błąd podczas inicjalizacji: {e}")
        return False

async def test_semantic_validator_methods():
    """Test czy SemanticValidatorService ma wszystkie wymagane metody"""
    print("🧪 Test 2: Sprawdzenie metod SemanticValidatorService...")
    
    try:
        validator = SemanticValidatorService()
        
        required_methods = [
            'validate_holistic_synthesis',
            'validate_psychology_profile',
            'validate_sales_strategy'
        ]
        
        missing_methods = []
        for method_name in required_methods:
            if not hasattr(validator, method_name):
                missing_methods.append(method_name)
            elif not callable(getattr(validator, method_name)):
                missing_methods.append(f"{method_name} (not callable)")
        
        if missing_methods:
            print(f"   ❌ Test nie przeszedł - brakujące metody: {missing_methods}")
            return False
        else:
            print("   ✅ Test przeszedł - wszystkie wymagane metody są dostępne")
            return True
            
    except Exception as e:
        print(f"   ❌ Test nie przeszedł - błąd: {e}")
        return False

async def test_validation_integration():
    """Test czy walidacja jest poprawnie zintegrowana"""
    print("🧪 Test 3: Test integracji walidacji...")
    
    try:
        interaction_service = InteractionService()
        validator = interaction_service.semantic_validator
        
        # Test danych poprawnych
        valid_data = {
            "holistic_summary": "Test summary for integration",
            "main_drive": "Test drive",
            "communication_style": {"preferred_approach": "Test approach"},
            "key_levers": ["Test lever 1", "Test lever 2", "Test lever 3"],
            "red_flags": ["Test flag 1", "Test flag 2"],
            "confidence": 75
        }
        
        is_valid, error_message = validator.validate_holistic_synthesis(valid_data)
        
        if is_valid:
            print("   ✅ Test przeszedł - walidacja działa poprawnie")
            return True
        else:
            print(f"   ❌ Test nie przeszedł - nieoczekiwany błąd walidacji: {error_message}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test nie przeszedł - błąd integracji: {e}")
        return False

async def test_error_handling():
    """Test obsługi błędów walidacji"""
    print("🧪 Test 4: Test obsługi błędów walidacji...")
    
    try:
        validator = SemanticValidatorService()
        
        # Test danych niepoprawnych
        invalid_data = {
            "holistic_summary": "Test",
            # Brak wymaganych pól
            "confidence": 200  # Poza zakresem
        }
        
        is_valid, error_message = validator.validate_holistic_synthesis(invalid_data)
        
        if not is_valid and error_message:
            print(f"   ✅ Test przeszedł - błędy poprawnie wykryte: {error_message[:50]}...")
            return True
        else:
            print("   ❌ Test nie przeszedł - nie wykryto błędów w niepoprawnych danych")
            return False
            
    except Exception as e:
        print(f"   ❌ Test nie przeszedł - nieoczekiwany błąd: {e}")
        return False

async def test_service_status():
    """Test czy InteractionService poprawnie raportuje status"""
    print("🧪 Test 5: Test statusu serwisu...")
    
    try:
        interaction_service = InteractionService()
        status = interaction_service.get_service_status()
        
        if isinstance(status, dict) and 'interaction_service_status' in status:
            print("   ✅ Test przeszedł - status serwisu dostępny")
            return True
        else:
            print(f"   ❌ Test nie przeszedł - niepoprawny format statusu: {status}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test nie przeszedł - błąd pobierania statusu: {e}")
        return False

async def main():
    """Główna funkcja testowa"""
    print("🚀 Rozpoczynam testy integracji SemanticValidatorService...\n")
    
    tests = [
        test_interaction_service_initialization,
        test_semantic_validator_methods,
        test_validation_integration,
        test_error_handling,
        test_service_status
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
        print()
    
    # Podsumowanie
    passed = sum(results)
    total = len(results)
    
    print(f"📊 PODSUMOWANIE TESTÓW INTEGRACJI:")
    print(f"   ✅ Przeszło: {passed}/{total}")
    print(f"   ❌ Nie przeszło: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Wszystkie testy integracji przeszły!")
        print("\n📋 Potwierdzenie integracji:")
        print("   ✅ SemanticValidatorService poprawnie zainicjalizowany w InteractionService")
        print("   ✅ Wszystkie wymagane metody walidacji dostępne")
        print("   ✅ Walidacja semantyczna działa poprawnie")
        print("   ✅ Obsługa błędów walidacji funkcjonuje")
        print("   ✅ Status serwisu dostępny")
        print("\n🔒 System zabezpieczony przed zapisem niepoprawnych danych AI!")
        return 0
    else:
        print("\n⚠️ Niektóre testy integracji nie przeszły. Sprawdź konfigurację.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)