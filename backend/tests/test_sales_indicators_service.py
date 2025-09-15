"""
Testy dla SalesIndicatorsService
"""
import pytest
from app.services.sales_indicators_service import SalesIndicatorsService
from app.schemas.indicators import RiskLevel, JourneyStage

@pytest.fixture
def sales_indicators_service():
    """Fixture dostarczający instancję SalesIndicatorsService"""
    return SalesIndicatorsService()

@pytest.fixture
def sample_psychometric_data():
    """Przykładowe dane psychometryczne do testów"""
    return {
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

def test_calculate_purchase_temperature(sales_indicators_service, sample_psychometric_data):
    """Test obliczania temperatury zakupowej"""
    # Act
    result = sales_indicators_service._calculate_purchase_temperature(sample_psychometric_data)
    
    # Assert
    assert result.value >= 0 and result.value <= 100
    assert result.temperature_level in ["cold", "warm", "hot"]
    assert isinstance(result.rationale, str) and len(result.rationale) > 0
    assert isinstance(result.strategy, str) and len(result.strategy) > 0
    assert result.confidence >= 0 and result.confidence <= 100

def test_calculate_churn_risk(sales_indicators_service, sample_psychometric_data):
    """Test obliczania ryzyka utraty"""
    # Act
    result = sales_indicators_service._calculate_churn_risk(sample_psychometric_data)
    
    # Assert
    assert result.value >= 0 and result.value <= 100
    assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
    assert isinstance(result.risk_factors, list)
    assert isinstance(result.rationale, str) and len(result.rationale) > 0
    assert isinstance(result.strategy, str) and len(result.strategy) > 0
    assert result.confidence >= 0 and result.confidence <= 100

def test_calculate_sales_potential(sales_indicators_service, sample_psychometric_data):
    """Test obliczania potencjału sprzedażowego"""
    # Act
    result = sales_indicators_service._calculate_sales_potential(sample_psychometric_data)
    
    # Assert
    assert result.value >= 0
    assert result.probability >= 0 and result.probability <= 100
    assert isinstance(result.estimated_timeframe, str) and len(result.estimated_timeframe) > 0
    assert isinstance(result.rationale, str) and len(result.rationale) > 0
    assert isinstance(result.strategy, str) and len(result.strategy) > 0
    assert result.confidence >= 0 and result.confidence <= 100

def test_calculate_customer_journey_stage(sales_indicators_service, sample_psychometric_data):
    """Test obliczania etapu podróży klienta"""
    # Act
    result = sales_indicators_service._calculate_customer_journey_stage(sample_psychometric_data)
    
    # Assert
    assert result.value in [JourneyStage.AWARENESS, JourneyStage.CONSIDERATION, 
                           JourneyStage.EVALUATION, JourneyStage.DECISION, JourneyStage.PURCHASE]
    assert result.progress_percentage >= 0 and result.progress_percentage <= 100
    assert isinstance(result.rationale, str) and len(result.rationale) > 0
    assert isinstance(result.strategy, str) and len(result.strategy) > 0
    assert result.confidence >= 0 and result.confidence <= 100

def test_calculate_indicators(sales_indicators_service, sample_psychometric_data):
    """Test obliczania wszystkich wskaźników"""
    # Act
    result = sales_indicators_service.calculate_indicators(sample_psychometric_data)
    
    # Assert
    assert result.purchase_temperature is not None
    assert result.customer_journey_stage is not None
    assert result.churn_risk is not None
    assert result.sales_potential is not None

def test_fallback_behavior(sales_indicators_service):
    """Test zachowania awaryjnego przy braku danych"""
    # Arrange
    empty_data = {}
    
    # Act
    temp_result = sales_indicators_service._calculate_purchase_temperature(empty_data)
    churn_result = sales_indicators_service._calculate_churn_risk(empty_data)
    potential_result = sales_indicators_service._calculate_sales_potential(empty_data)
    journey_result = sales_indicators_service._calculate_customer_journey_stage(empty_data)
    
    # Assert
    # Upewnij się, że wszystkie funkcje zwracają wartości domyślne zamiast rzucać wyjątki
    assert temp_result.value >= 0 and temp_result.value <= 100
    assert churn_result.value >= 0 and churn_result.value <= 100
    assert potential_result.value >= 0
    assert journey_result.progress_percentage >= 0 and journey_result.progress_percentage <= 100