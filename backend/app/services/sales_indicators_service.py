"""
SalesIndicatorsService - Serwis do obliczania wskaźników sprzedażowych

Implementacja logiki biznesowej dla 4 kluczowych wskaźników:
- Temperatura Zakupowa (Purchase Temperature)
- Ryzyko Utraty (Churn Risk)
- Potencjał Sprzedażowy (Sales Potential)
"""

import logging
from typing import Dict, Any, Optional
from app.schemas.indicators import (
    PurchaseTemperature, 
    ChurnRisk, 
    SalesPotential, 
    SalesIndicatorsAnalysis,
    RiskLevel
)

logger = logging.getLogger(__name__)

class SalesIndicatorsService:
    """
    Serwis do obliczania wskaźników sprzedażowych na podstawie danych psychometrycznych
    """
    
    def calculate_indicators(self, psychometric_data: Dict[str, Any]) -> SalesIndicatorsAnalysis:
        """
        Główna metoda obliczająca wszystkie wskaźniki sprzedażowe
        
        Args:
            psychometric_data: Dane psychometryczne z sesji
            
        Returns:
            SalesIndicatorsAnalysis: Kompletna analiza wskaźników sprzedażowych
        """
        try:
            # Oblicz poszczególne wskaźniki
            purchase_temp = self._calculate_purchase_temperature(psychometric_data)
            churn_risk = self._calculate_churn_risk(psychometric_data)
            sales_potential = self._calculate_sales_potential(psychometric_data)
            customer_journey = self._calculate_customer_journey_stage(psychometric_data)
            
            # Utwórz kompletną analizę
            analysis = SalesIndicatorsAnalysis(
                purchase_temperature=purchase_temp,
                customer_journey_stage=customer_journey,
                churn_risk=churn_risk,
                sales_potential=sales_potential
            )
            
            logger.info("✅ [SALES INDICATORS] Wskaźniki sprzedażowe obliczone pomyślnie")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ [SALES INDICATORS] Błąd podczas obliczania wskaźników: {e}")
            raise

    def _calculate_purchase_temperature(self, psychometric_data: Dict[str, Any]) -> PurchaseTemperature:
        """
        Oblicza temperaturę zakupową (0-100) na podstawie cech Big Five i wartości Schwartz
        
        Wysoka sumienność i niska neurotyczność zwiększają temperaturę
        Wartości zorientowane na osiągnięcia zwiększają temperaturę
        """
        try:
            big_five = psychometric_data.get("big_five", {})
            schwartz_values = psychometric_data.get("schwartz_values", [])
            archetype = psychometric_data.get("archetype", {})
            
            # Bazowa temperatura
            base_temp = 50
            
            # Modyfikator Big Five
            big_five_modifier = 0
            if big_five:
                # Wysoka sumienność zwiększa temperaturę
                conscientiousness = big_five.get("conscientiousness", {}).get("score", 5)
                big_five_modifier += (conscientiousness - 5) * 3  # -15 do +15
                
                # Niska neurotyczność zwiększa temperaturę
                neuroticism = big_five.get("neuroticism", {}).get("score", 5)
                big_five_modifier += (5 - neuroticism) * 2  # -10 do +10
                
                # Wysoka otwartość zwiększa temperaturę
                openness = big_five.get("openness", {}).get("score", 5)
                big_five_modifier += (openness - 5) * 1  # -5 do +5
            
            # Modyfikator Schwartz Values
            schwartz_modifier = 0
            achievement_oriented_values = ["achievement", "power", "self_direction"]
            for value in schwartz_values:
                if isinstance(value, dict) and value.get("is_present", False):
                    value_name = value.get("value_name", "").lower()
                    if any(ach_val in value_name for ach_val in achievement_oriented_values):
                        schwartz_modifier += 5
            
            # Oblicz końcową temperaturę
            temperature = base_temp + big_five_modifier + schwartz_modifier
            temperature = max(0, min(100, temperature))  # Clamp to 0-100
            
            # Określ poziom temperatury
            if temperature >= 70:
                temp_level = "hot"
            elif temperature >= 40:
                temp_level = "warm"
            else:
                temp_level = "cold"
            
            # Ustal pewność i strategię
            confidence = min(90, max(30, 50 + abs(temperature - 50)))  # Im bardziej ekstremalna wartość, tym większa pewność
            
            rationale = f"Temperatura zakupowa {temperature}% obliczona na podstawie "
            if big_five:
                rationale += f"profilu Big Five (sumienność: {conscientiousness}, neurotyczność: {neuroticism}) "
            if schwartz_modifier > 0:
                rationale += f"oraz wartości osiągnięciowych "
            if archetype:
                rationale += f"w archetypie {archetype.get('archetype_name', 'nieznanym')}"
            
            strategy = "Zastosuj strategię sprzedażową dostosowaną do temperatury zakupowej: "
            if temp_level == "hot":
                strategy += "Przyspiesz proces sprzedaży, zaproponuj spotkanie w ciągu 48h"
            elif temp_level == "warm":
                strategy += "Utrzymuj regularny kontakt i dostarczaj wartościowe informacje"
            else:
                strategy += "Rozgrzej kontakt poprzez edukację i budowanie relacji"
            
            return PurchaseTemperature(
                value=temperature,
                temperature_level=temp_level,
                rationale=rationale,
                strategy=strategy,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"❌ [PURCHASE TEMP] Błąd podczas obliczania temperatury zakupowej: {e}")
            # Fallback values
            return PurchaseTemperature(
                value=50,
                temperature_level="warm",
                rationale="Fallback - błąd w obliczeniach, ustawiono średnią temperaturę",
                strategy="Utrzymuj standardowy kontakt sprzedażowy",
                confidence=30
            )

    def _calculate_churn_risk(self, psychometric_data: Dict[str, Any]) -> ChurnRisk:
        """
        Oblicza ryzyko utraty klienta (low/medium/high) na podstawie profilu DISC i interakcji
        """
        try:
            disc = psychometric_data.get("disc", {})
            archetype = psychometric_data.get("archetype", {})
            big_five = psychometric_data.get("big_five", {})
            
            # Bazowe ryzyko
            base_risk = 50
            
            # Modyfikator DISC
            disc_modifier = 0
            if disc:
                # Wysoka dominacja może zwiększać ryzyko jeśli nie są spełnione potrzeby
                dominance = disc.get("dominance", {}).get("score", 5)
                disc_modifier += (dominance - 5) * 2  # -10 do +10
                
                # Wysoka zgodność może zmniejszać ryzyko
                steadiness = disc.get("steadiness", {}).get("score", 5)
                disc_modifier -= (steadiness - 5) * 2  # -10 do +10
                
                # Wysoka zgodność z procedurami może zmniejszać ryzyko
                compliance = disc.get("compliance", {}).get("score", 5)
                disc_modifier -= (compliance - 5) * 1  # -5 do +5
            
            # Modyfikator Big Five
            big_five_modifier = 0
            if big_five:
                # Wysoka neurotyczność zwiększa ryzyko
                neuroticism = big_five.get("neuroticism", {}).get("score", 5)
                big_five_modifier += (neuroticism - 5) * 2  # -10 do +10
                
                # Niska ugodowość może zwiększać ryzyko
                agreeableness = big_five.get("agreeableness", {}).get("score", 5)
                big_five_modifier += (5 - agreeableness) * 1  # -5 do +5
            
            # Oblicz końcowe ryzyko
            risk_value = base_risk + disc_modifier + big_five_modifier
            risk_value = max(0, min(100, risk_value))  # Clamp to 0-100
            
            # Określ poziom ryzyka
            if risk_value >= 70:
                risk_level = RiskLevel.HIGH
            elif risk_value >= 30:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Identyfikuj czynniki ryzyka
            risk_factors = []
            if dominance > 7:
                risk_factors.append("Wysoka dominacja - wymaga kontroli")
            if neuroticism > 7:
                risk_factors.append("Wysoka neurotyczność - podatność na stres")
            if steadiness < 3:
                risk_factors.append("Niska stabilność - niestała decyzyjność")
            if compliance > 7 and archetype.get("archetype_key") != "analityk":
                risk_factors.append("Wysoka potrzeba kontroli - wymaga szczegółowych danych")
            
            if not risk_factors:
                risk_factors = ["Brak wyraźnych czynników ryzyka"]
            
            # Ustal pewność i strategię
            confidence = min(90, max(30, 50 + abs(risk_value - 50)))  # Im bardziej ekstremalna wartość, tym większa pewność
            
            rationale = f"Ryzyko utraty {risk_value}% obliczone na podstawie "
            if disc:
                rationale += f"profilu DISC (dominacja: {dominance}, stabilność: {steadiness}) "
            if big_five:
                rationale += f"i cech Big Five (neurotyczność: {neuroticism})"
            if archetype:
                rationale += f" w archetypie {archetype.get('archetype_name', 'nieznanym')}"
            
            strategy = "Zastosuj strategię zarządzania ryzykiem: "
            if risk_level == RiskLevel.HIGH:
                strategy += "Utrzymuj bardzo bliski kontakt, dostarczaj regularne aktualizacje i zapobiegaj niepokojom"
            elif risk_level == RiskLevel.MEDIUM:
                strategy += "Monitoruj regularnie zaangażowanie i reaguj na sygnały niepokoju"
            else:
                strategy += "Utrzymuj standardowy kontakt, nie wywieraj presji"
            
            return ChurnRisk(
                value=risk_value,
                risk_level=risk_level,
                risk_factors=risk_factors,
                rationale=rationale,
                strategy=strategy,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"❌ [CHURN RISK] Błąd podczas obliczania ryzyka utraty: {e}")
            # Fallback values
            return ChurnRisk(
                value=50,
                risk_level=RiskLevel.MEDIUM,
                risk_factors=["Błąd w obliczeniach - ryzyko średnie"],
                rationale="Fallback - błąd w obliczeniach, ustawiono średnie ryzyko",
                strategy="Monitoruj regularnie zaangażowanie klienta",
                confidence=30
            )

    def _calculate_sales_potential(self, psychometric_data: Dict[str, Any]) -> SalesPotential:
        """
        Oblicza potencjał sprzedażowy na podstawie archetypu klienta i pewności analizy
        """
        try:
            archetype = psychometric_data.get("archetype", {})
            confidence_score = psychometric_data.get("confidence_score", 50)
            big_five = psychometric_data.get("big_five", {})
            
            # Bazowa wartość potencjału (w PLN)
            base_value = 1000000.0  # 1M PLN
            
            # Modyfikator archetypu
            archetype_multiplier = 1.0
            archetype_key = archetype.get("archetype_key", "")
            
            if archetype_key == "wizjoner":
                archetype_multiplier = 2.0  # Wizjonerzy mają największy potencjał
            elif archetype_key == "szybki_decydent":
                archetype_multiplier = 1.8  # Szybcy decydenci są bardzo wartościowi
            elif archetype_key == "analityk":
                archetype_multiplier = 1.5  # Analitycy są wartościowi, ale potrzebują więcej czasu
            elif archetype_key == "relacyjny_budowniczy":
                archetype_multiplier = 1.3  # Relacyjni budowniczy są wartościowi w kontekście zespołowym
            
            # Modyfikator pewności analizy
            confidence_modifier = confidence_score / 100.0  # 0.0 do 1.0
            
            # Modyfikator Big Five
            big_five_modifier = 1.0
            if big_five:
                # Wysoka otwartość zwiększa potencjał
                openness = big_five.get("openness", {}).get("score", 5)
                big_five_modifier += (openness - 5) * 0.1  # -0.5 do +0.5
                
                # Wysoka ekstrawersja zwiększa potencjał
                extraversion = big_five.get("extraversion", {}).get("score", 5)
                big_five_modifier += (extraversion - 5) * 0.05  # -0.25 do +0.25
            
            # Oblicz końcową wartość
            potential_value = base_value * archetype_multiplier * confidence_modifier * big_five_modifier
            potential_value = max(0, potential_value)  # Nie może być ujemna
            
            # Oblicz prawdopodobieństwo sprzedaży (0-100)
            probability = min(95, max(10, confidence_score * 1.2))  # 10-95%
            
            # Szacowany czas realizacji
            if archetype_key == "szybki_decydent":
                timeframe = "1-2 tygodnie"
            elif archetype_key == "wizjoner":
                timeframe = "4-8 tygodni"
            elif archetype_key == "analityk":
                timeframe = "6-12 tygodni"
            else:
                timeframe = "4-6 tygodni"
            
            # Ustal pewność i strategię
            confidence = min(95, max(20, confidence_score))  # Bazujemy na pewności analizy psychometrycznej
            
            rationale = f"Potencjał sprzedażowy {potential_value:,.0f} PLN obliczony na podstawie "
            if archetype:
                rationale += f"archetypu {archetype.get('archetype_name', 'nieznanego')} "
            rationale += f"i pewności analizy ({confidence_score}%)"
            if big_five:
                rationale += f" oraz cech Big Five (otwartość: {openness}, ekstrawersja: {extraversion})"
            
            strategy = "Zastosuj strategię sprzedaży dostosowaną do potencjału: "
            if archetype_key == "wizjoner":
                strategy += "Prezentuj innowacyjność i przyszłość, podkreślaj status i prestiż"
            elif archetype_key == "szybki_decydent":
                strategy += "Prezentuj kluczowe korzyści szybko, oferuj natychmiastowe działanie"
            elif archetype_key == "analityk":
                strategy += "Dostarczaj twarde dane i statystyki, prezentuj TCO i ROI"
            elif archetype_key == "relacyjny_budowniczy":
                strategy += "Buduj osobistą relację, podkreślaj korzyści dla zespołu/rodziny"
            else:
                strategy += "Zastosuj zrównoważone podejście sprzedażowe"
            
            return SalesPotential(
                value=potential_value,
                probability=probability,
                estimated_timeframe=timeframe,
                rationale=rationale,
                strategy=strategy,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"❌ [SALES POTENTIAL] Błąd podczas obliczania potencjału sprzedażowego: {e}")
            # Fallback values
            return SalesPotential(
                value=1000000.0,
                probability=50,
                estimated_timeframe="4-6 tygodni",
                rationale="Fallback - błąd w obliczeniach, ustawiono średni potencjał",
                strategy="Zastosuj standardowe podejście sprzedażowe",
                confidence=30
            )

    def _calculate_customer_journey_stage(self, psychometric_data: Dict[str, Any]) -> Any:
        """
        Oblicza etap podróży klienta na podstawie danych psychometrycznych i interakcji
        """
        from app.schemas.indicators import CustomerJourneyStage, JourneyStage
        
        try:
            archetype = psychometric_data.get("archetype", {})
            confidence_score = psychometric_data.get("confidence_score", 50)
            big_five = psychometric_data.get("big_five", {})
            disc = psychometric_data.get("disc", {})
            
            # Określ etap podróży na podstawie pewności analizy
            if confidence_score >= 80:
                stage = JourneyStage.DECISION
                progress = 85
                next_stage = None
            elif confidence_score >= 60:
                stage = JourneyStage.EVALUATION
                progress = 70
                next_stage = JourneyStage.DECISION
            elif confidence_score >= 40:
                stage = JourneyStage.CONSIDERATION
                progress = 50
                next_stage = JourneyStage.EVALUATION
            else:
                stage = JourneyStage.AWARENESS
                progress = 30
                next_stage = JourneyStage.CONSIDERATION
            
            # Dostosuj na podstawie archetypu
            archetype_key = archetype.get("archetype_key", "")
            if archetype_key == "szybki_decydent":
                # Szybcy decydenci przechodzą szybciej przez etapy
                progress = min(100, progress + 15)
            elif archetype_key == "analityk":
                # Analitycy wolniej przechodzą przez etapy
                progress = max(10, progress - 10)
            
            # Ustal pewność i strategię
            confidence = min(90, max(20, confidence_score))
            
            rationale = f"Etap podróży '{stage.value}' określony na podstawie "
            rationale += f"pewności analizy ({confidence_score}%)"
            if archetype:
                rationale += f" i archetypu {archetype.get('archetype_name', 'nieznanego')}"
            
            strategy = "Zastosuj strategię dopasowaną do etapu podróży: "
            if stage == JourneyStage.AWARENESS:
                strategy += "Buduj świadomość korzyści i wartości"
            elif stage == JourneyStage.CONSIDERATION:
                strategy += "Prezentuj porównania i różnice konkurencyjne"
            elif stage == JourneyStage.EVALUATION:
                strategy += "Dostarczaj szczegółowe dane i case studies"
            else:
                strategy += "Przyspiesz proces decyzyjny i przygotuj ofertę"
            
            return CustomerJourneyStage(
                value=stage,
                progress_percentage=progress,
                next_stage=next_stage,
                rationale=rationale,
                strategy=strategy,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"❌ [JOURNEY STAGE] Błąd podczas obliczania etapu podróży: {e}")
            # Fallback values
            from app.schemas.indicators import JourneyStage
            return CustomerJourneyStage(
                value=JourneyStage.CONSIDERATION,
                progress_percentage=50,
                next_stage=JourneyStage.EVALUATION,
                rationale="Fallback - błąd w obliczeniach, ustawiono średni etap",
                strategy="Zastosuj zrównoważone podejście do etapu podróży",
                confidence=30
            )
