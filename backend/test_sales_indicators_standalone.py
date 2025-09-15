"""
Samodzielny test dla SalesIndicatorsService
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.sales_indicators_service import SalesIndicatorsService

def test_sales_indicators_service():
    """Test samodzielny dla SalesIndicatorsService"""
    # Arrange
    service = SalesIndicatorsService()
    
    sample_psychometric_data = {
        "confidence_score": 85,
        "big_five": {
            "openness": {"score": 8, "rationale": "Wysoka otwartość", "strategy": "Innowacje"},
            "conscientiousness": {"score": 7, "rationale": "Wysoka sumienność", "strategy": "Szczegóły"},
            "extraversion": {"score": 6, "rationale": "Średnia ekstrawersja", "strategy": "Komunikacja"},
            "agreeableness": {"score": 5, "rationale": "Neutralna ugodowość", "strategy": "Równowaga"},
            "neuroticism": {"score": 3, "rationale": "Niska neurotyczność", "strategy": "Stabilność"}
        },
        "disc": {
            "dominance": {"score": 7, "rationale": "Wysoka dominacja", "strategy": "Kontrola"},
            "influence": {"score": 5, "rationale": "Średnie wpływy", "strategy": "Perswazja"},
            "steadiness": {"score": 4, "rationale": "Niska stabilność", "strategy": "Zmienność"},
            "compliance": {"score": 6, "rationale": "Średnia zgodność", "strategy": "Procedury"}
        },
        "schwartz_values": [
            {"value_name": "Achievement", "strength": 8, "rationale": "Wartość osiągnięć", "strategy": "Status", "is_present": True},
            {"value_name": "Security", "strength": 6, "rationale": "Wartość bezpieczeństwa", "strategy": "Stabilność", "is_present": True}
        ],
        "archetype": {
            "archetype_key": "wizjoner",
            "archetype_name": "🚀 Wizjoner",
            "confidence": 90
        }
    }
    
    # Act
    result = service.calculate_indicators(sample_psychometric_data)
    
    # Assert
    print("=== Test SalesIndicatorsService ===")
    print(f"Purchase Temperature: {result.purchase_temperature.value}% ({result.purchase_temperature.temperature_level})")
    print(f"Churn Risk: {result.churn_risk.value}% ({result.churn_risk.risk_level})")
    print(f"Sales Potential: {result.sales_potential.value:,} PLN ({result.sales_potential.probability}%)")
    print(f"Customer Journey Stage: {result.customer_journey_stage.value} ({result.customer_journey_stage.progress_percentage}%)")
    
    # Sprawdź czy wszystkie wymagane pola są obecne
    assert result.purchase_temperature is not None
    assert result.customer_journey_stage is not None
    assert result.churn_risk is not None
    assert result.sales_potential is not None
    
    # Sprawdź typy danych
    assert isinstance(result.purchase_temperature.value, int)
    assert isinstance(result.churn_risk.value, int)
    assert isinstance(result.sales_potential.value, (int, float))
    assert isinstance(result.customer_journey_stage.progress_percentage, int)
    
    # Sprawdź zakresy wartości
    assert 0 <= result.purchase_temperature.value <= 100
    assert 0 <= result.churn_risk.value <= 100
    assert result.sales_potential.value >= 0
    assert 0 <= result.customer_journey_stage.progress_percentage <= 100
    
    print("✅ Wszystkie testy zakończone sukcesem!")
    return True

if __name__ == "__main__":
    test_sales_indicators_service()