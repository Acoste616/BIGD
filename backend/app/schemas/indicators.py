"""
MODUŁ 4: Schematy Pydantic dla Zaawansowanych Wskaźników Sprzedażowych

Definiuje struktury danych dla 4 kluczowych wskaźników:
- Temperatura Zakupowa (Purchase Temperature)
- Etap Podróży Klienta (Customer Journey Stage)
- Ryzyko Utraty (Churn Risk)
- Potencjał Sprzedażowy (Sales Potential)
"""

from pydantic import BaseModel, Field
from typing import Union, Literal, Optional
from enum import Enum

class JourneyStage(str, Enum):
    """Możliwe etapy podróży klienta w lejku sprzedażowym"""
    AWARENESS = "awareness"           # Świadomość potrzeby
    CONSIDERATION = "consideration"   # Rozważanie opcji  
    EVALUATION = "evaluation"        # Ocena i porównanie
    DECISION = "decision"            # Podejmowanie decyzji
    PURCHASE = "purchase"            # Zakup/Finalizacja

class RiskLevel(str, Enum):
    """Poziomy ryzyka utraty klienta"""
    LOW = "low"           # Niskie ryzyko (0-30%)
    MEDIUM = "medium"     # Średnie ryzyko (30-70%) 
    HIGH = "high"         # Wysokie ryzyko (70-100%)

class SalesIndicator(BaseModel):
    """Bazowy model dla wskaźnika sprzedażowego"""
    value: Union[str, int, float] = Field(..., description="Wartość wskaźnika")
    rationale: str = Field(..., description="Uzasadnienie AI - dlaczego taka wartość")
    strategy: str = Field(..., description="Rekomendowana strategia sprzedażowa")
    confidence: int = Field(default=0, ge=0, le=100, description="Pewność AI co do oceny (0-100%)")

class PurchaseTemperature(SalesIndicator):
    """🌡️ Temperatura Zakupowa - jak 'gorący' jest lead"""
    value: int = Field(..., ge=0, le=100, description="Temperatura w skali 0-100%")
    temperature_level: Literal["cold", "warm", "hot"] = Field(..., description="Kategoria temperatury")
    
class CustomerJourneyStage(SalesIndicator):
    """🗺️ Etap Podróży Klienta - pozycja w lejku sprzedażowym"""
    value: JourneyStage = Field(..., description="Aktualny etap podróży")
    progress_percentage: int = Field(..., ge=0, le=100, description="Postęp w lejku (0-100%)")
    next_stage: Optional[JourneyStage] = Field(None, description="Następny etap w procesie")

class ChurnRisk(SalesIndicator):
    """⚖️ Ryzyko Utraty - prawdopodobieństwo utraty klienta"""
    value: int = Field(..., ge=0, le=100, description="Ryzyko w procentach (0-100%)")
    risk_level: RiskLevel = Field(..., description="Kategoria ryzyka")
    risk_factors: list[str] = Field(default=[], description="Lista zidentyfikowanych czynników ryzyka")

class SalesPotential(SalesIndicator):
    """💰 Potencjał Sprzedażowy - szacowana wartość i prawdopodobieństwo"""
    value: float = Field(..., ge=0, description="Szacowana wartość transakcji w PLN")
    probability: int = Field(..., ge=0, le=100, description="Prawdopodobieństwo zamknięcia sprzedaży (%)")
    estimated_timeframe: str = Field(..., description="Szacowany czas do zamknięcia (np. '2-4 tygodnie')")
    
class SalesIndicatorsAnalysis(BaseModel):
    """Kompletna analiza wszystkich 4 wskaźników sprzedażowych"""
    purchase_temperature: PurchaseTemperature = Field(..., description="🌡️ Temperatura Zakupowa")
    customer_journey_stage: CustomerJourneyStage = Field(..., description="🗺️ Etap Podróży Klienta") 
    churn_risk: ChurnRisk = Field(..., description="⚖️ Ryzyko Utraty")
    sales_potential: SalesPotential = Field(..., description="💰 Potencjał Sprzedażowy")
    
    analysis_timestamp: Optional[str] = Field(None, description="Timestamp analizy")
    session_id: Optional[int] = Field(None, description="ID sesji dla której przeprowadzono analizę")
    
    class Config:
        """Konfiguracja modelu"""
        use_enum_values = True
        schema_extra = {
            "example": {
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
        }
