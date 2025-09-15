"""
Test walidacji schematu dla SalesIndicatorsAnalysis
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.schemas.indicators import SalesIndicatorsAnalysis

def test_schema_validation():
    """Test walidacji schematu odpowiedzi"""
    # Arrange
    sample_response = {
        "purchase_temperature": {
            "value": 75,
            "temperature_level": "hot",
            "rationale": "Klient zadaje szczegółowe pytania o finansowanie i terminy dostawy",
            "strategy": "Przyspiesz proces - zaproponuj spotkanie w ciągu 48h",
            "confidence": 85
        },
        "customer_journey_stage": {
            "value": "evaluation",
            "progress_percentage": 70,
            "next_stage": "decision",
            "rationale": "Porównuje szczegółowo z konkurencją - typowy etap oceny",
            "strategy": "Dostarcz przewagę konkurencyjną i case studies",
            "confidence": 90
        },
        "churn_risk": {
            "value": 25,
            "risk_level": "low",
            "risk_factors": ["Długi proces decyzyjny"],
            "rationale": "Aktywne zaangażowanie, szczegółowe pytania - niskie ryzyko",
            "strategy": "Utrzymaj regularny kontakt, nie wywieraj presji",
            "confidence": 80
        },
        "sales_potential": {
            "value": 450000.0,
            "probability": 75,
            "estimated_timeframe": "3-4 tygodnie",
            "rationale": "Budżet 25M PLN na flotę, wysoka pozycja decyzyjna",
            "strategy": "Przygotuj szczegółową propozycję biznesową z ROI",
            "confidence": 85
        }
    }
    
    # Act & Assert
    try:
        validated_data = SalesIndicatorsAnalysis(**sample_response)
        print("=== Test walidacji schematu ===")
        print("✅ Walidacja schematu zakończona sukcesem!")
        print(f"Purchase Temperature: {validated_data.purchase_temperature.value}%")
        print(f"Churn Risk: {validated_data.churn_risk.value}% ({validated_data.churn_risk.risk_level})")
        print(f"Sales Potential: {validated_data.sales_potential.value:,} PLN")
        print(f"Customer Journey Stage: {validated_data.customer_journey_stage.value}")
        return True
    except Exception as e:
        print(f"❌ Błąd walidacji schematu: {e}")
        return False

if __name__ == "__main__":
    test_schema_validation()