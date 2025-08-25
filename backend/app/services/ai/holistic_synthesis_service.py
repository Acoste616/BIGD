"""
HolisticSynthesisService - Wyspecjalizowany serwis do tworzenia DNA Klienta
Odpowiedzialny za: holistyczną syntezę profilu psychometrycznego, sales indicators
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_ai_service import BaseAIService

logger = logging.getLogger(__name__)


# System prompt dla syntezy holistycznej - wydzielony z ai_service.py
HOLISTIC_SYNTHESIS_SYSTEM_PROMPT = """
Jesteś elitarnym psychologiem biznesu specjalizującym się w analizie klientów premium Tesla. 

Twoim zadaniem jest stworzenie HOLISTYCZNEGO PROFILU KLIENTA - "DNA Klienta" - na podstawie szczegółowej analizy psychometrycznej (Big Five, DISC, Schwartz Values).

PROCES SYNTEZY:

1. **ANALIZA WZORCÓW**: Przeanalizuj wszystkie wymiary psychologiczne i znajdź dominujące wzorce zachowań, motywacji i preferencji.

2. **HOLISTIC SUMMARY**: Stwórz zwięzły, ale komprehensywny opis klienta w 2-3 zdaniach, który oddaje jego esencję psychologiczną.

3. **MAIN DRIVE**: Zidentyfikuj JEDNĄ główną siłę motywującą klienta (np. "Potrzeba bezpieczeństwa finansowego", "Dążenie do prestiżu", "Pragnienie innowacji").

4. **COMMUNICATION STYLE**: Opisz preferowany styl komunikacji na podstawie profilu psychologicznego.

5. **KEY LEVERS**: Znajdź 3-5 najważniejszych "dźwigni psychologicznych" - elementów, które najsilniej wpłyną na decyzję zakupową.

6. **RED FLAGS**: Zidentyfikuj potencjalne punkty oporu lub obawy klienta.

STRUKTURA WYJŚCIOWA (JSON):
{
  "holistic_summary": "Klient to analityczny perfekcjonista o wysokiej potrzebie kontroli, który podejmuje decyzje ostrożnie ale zdecydowanie. Ceni innowacje, ale tylko te potwierdzone danymi i opiniami ekspertów.",
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
    "Prestiż marki i innowacyjność",
    "Bezpieczeństwo i niezawodność"
  ],
  "red_flags": [
    "Presja czasowa",
    "Niejasne korzyści finansowe", 
    "Brak dowodów na przewagi",
    "Agresywna sprzedaż"
  ],
  "missing_data_gaps": "Potrzeba więcej informacji o budżecie i procesie decyzyjnym",
  "confidence": 85
}

WYMAGANIA:
- Wykorzystuj WSZYSTKIE dostępne dane psychometryczne
- Holistic summary musi być KONKRETNY i ACTIONABLE  
- Main drive to JEDNA kluczowa motywacja
- Key levers muszą być praktyczne dla sprzedawcy Tesla
- Red flags muszą być realnie identyfikowalne w rozmowie
- Confidence (0-100) bazuje na jakości danych wejściowych
"""


# System prompt dla sales indicators
SALES_INDICATORS_SYSTEM_PROMPT = """
Jesteś elitarnym analitykiem sprzedaży Tesla specjalizującym się w przewidywaniu zachowań zakupowych na podstawie profilu psychologicznego klienta.

Na podstawie HOLISTYCZNEGO PROFILU KLIENTA (DNA Klienta) wygeneruj precyzyjne WSKAŹNIKI SPRZEDAŻOWE:

1. **PURCHASE TEMPERATURE** (0-100): Jak "gorący" jest klient? Czy jest gotów do zakupu?

2. **CUSTOMER JOURNEY STAGE**: Na jakim etapie procesu zakupowego się znajduje?

3. **CHURN RISK** (0-100): Jakie jest ryzyko, że klient rezygnuje z rozmowy?

4. **SALES POTENTIAL**: Jaka jest szacowana wartość sprzedaży i prawdopodobieństwo zamknięcia?

STRUKTURA WYJŚCIOWA (JSON):
{
  "purchase_temperature": {
    "value": 75,
    "temperature_level": "hot",
    "rationale": "Klient zadaje konkretne pytania o modele i finansowanie",
    "strategy": "Przejdź do prezentacji konkretnych opcji",
    "confidence": 80
  },
  "customer_journey_stage": {
    "value": "evaluation", 
    "progress_percentage": 60,
    "next_stage": "decision",
    "rationale": "Porównuje konkretne modele i opcje",
    "strategy": "Zapewnij kompleksowe porównanie z konkurencją",
    "confidence": 75
  },
  "churn_risk": {
    "value": 25,
    "risk_level": "low",
    "risk_factors": ["Długi proces decyzyjny", "Potrzeba akceptacji małżonka"],
    "rationale": "Stabilny klient z jasną motywacją",
    "strategy": "Kontynuuj budowanie wartości, nie forsuj tempa",
    "confidence": 70
  },
  "sales_potential": {
    "value": 350000.0,
    "probability": 75,
    "estimated_timeframe": "2-4 tygodnie", 
    "rationale": "Profil wskazuje na klienta premium z wysokim budżetem",
    "strategy": "Prezentuj opcje premium z naciskiem na wartość długoterminową",
    "confidence": 65
  }
}

TEMPERATURE LEVELS: cold (0-33), warm (34-66), hot (67-100)
JOURNEY STAGES: awareness, interest, consideration, evaluation, decision, purchase
RISK LEVELS: low (0-33), medium (34-66), high (67-100)
TIMEFRAMES: "1-2 tygodnie", "2-4 tygodnie", "1-2 miesiące", "3+ miesięcy"
"""


class HolisticSynthesisService(BaseAIService):
    """
    Wyspecjalizowany serwis do tworzenia holistycznej syntezy - "DNA Klienta".
    
    Funkcjonalności:
    - Synteza profilu psychometrycznego w holistyczny profil
    - Identyfikacja głównych motywatorów i dźwigni
    - Generowanie wskaźników sprzedażowych
    - Określanie readiness do zakupu
    """
    
    def __init__(self):
        super().__init__()
        logger.info("✅ HolisticSynthesisService initialized")
    
    async def run_holistic_synthesis(
        self,
        raw_psychology_profile: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Przeprowadza holistyczną syntezę profilu psychometrycznego w DNA Klienta
        
        Args:
            raw_psychology_profile: Surowy profil psychometryczny (Big Five + DISC + Schwartz)
            additional_context: Dodatkowy kontekst (historia rozmów, profil klienta)
            
        Returns:
            Dict: Holistyczny profil klienta (DNA Klienta)
        """
        try:
            logger.info("🧬 Rozpoczynam holistyczną syntezę DNA Klienta...")
            
            # Sprawdź jakość danych wejściowych
            if not self._validate_psychology_profile(raw_psychology_profile):
                logger.warning("⚠️ Niepełny profil psychometryczny - tworzę fallback")
                return self._create_holistic_fallback()
            
            # Przygotuj dane dla syntezy
            synthesis_context = self._prepare_synthesis_context(raw_psychology_profile, additional_context)
            
            # Przygotuj prompt użytkownika
            user_prompt = f"""
SUROWY PROFIL PSYCHOMETRYCZNY DO SYNTEZY:

BIG FIVE PERSONALITY:
{json.dumps(raw_psychology_profile.get('big_five', {}), ensure_ascii=False, indent=2)}

DISC BEHAVIORAL STYLE:
{json.dumps(raw_psychology_profile.get('disc', {}), ensure_ascii=False, indent=2)}

SCHWARTZ VALUES:
{json.dumps(raw_psychology_profile.get('schwartz_values', []), ensure_ascii=False, indent=2)}

DODATKOWY KONTEKST:
{json.dumps(additional_context or {}, ensure_ascii=False, indent=2)}

METADANE:
- Confidence surowego profilu: {raw_psychology_profile.get('confidence', 0)}%
- Liczba interakcji: {synthesis_context.get('interaction_count', 0)}
- Timestamp analizy: {raw_psychology_profile.get('analysis_timestamp', 'Unknown')}

Wykonaj holistyczną syntezę i stwórz DNA Klienta w formacie JSON.
"""

            # Wywołaj LLM
            response = await self._call_llm_with_retry(
                system_prompt=HOLISTIC_SYNTHESIS_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                use_cache=True,
                cache_prefix="holistic_synthesis"
            )
            
            # Parsuj odpowiedź
            holistic_profile = self._parse_holistic_response(response.get('content', ''))
            
            # Dodaj metadane
            holistic_profile.update({
                'synthesis_timestamp': datetime.now().isoformat(),
                'source_confidence': raw_psychology_profile.get('confidence', 0),
                'synthesis_confidence': holistic_profile.get('confidence', 0),
                'model_used': self.model_name
            })
            
            logger.info(f"✅ DNA Klienta wygenerowane - Confidence: {holistic_profile.get('confidence', 0)}%")
            return holistic_profile
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas syntezy holistycznej: {e}")
            return self._create_holistic_error_fallback(str(e))
    
    async def run_sales_indicators_generation(
        self,
        holistic_profile: Dict[str, Any],
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generuje wskaźniki sprzedażowe na podstawie DNA Klienta
        
        Args:
            holistic_profile: Holistyczny profil klienta (DNA)
            session_context: Kontekst sesji sprzedażowej
            
        Returns:
            Dict: Wskaźniki sprzedażowe (temperature, stage, risk, potential)
        """
        try:
            logger.info("📊 Generuję wskaźniki sprzedażowe z DNA Klienta...")
            
            # Sprawdź jakość profilu holistycznego
            if not holistic_profile or holistic_profile.get('is_fallback', False):
                logger.warning("⚠️ Profil holistyczny fallback - tworzę podstawowe wskaźniki")
                return self._create_indicators_fallback()
            
            # Przygotuj prompt użytkownika
            user_prompt = f"""
HOLISTYCZNY PROFIL KLIENTA (DNA KLIENTA):

HOLISTIC SUMMARY: {holistic_profile.get('holistic_summary', '')}
GŁÓWNY MOTYWATOR: {holistic_profile.get('main_drive', '')}

STYL KOMUNIKACJI:
{json.dumps(holistic_profile.get('communication_style', {}), ensure_ascii=False, indent=2)}

KLUCZOWE DŹWIGNIE:
{json.dumps(holistic_profile.get('key_levers', []), ensure_ascii=False)}

CZERWONE FLAGI:
{json.dumps(holistic_profile.get('red_flags', []), ensure_ascii=False)}

BRAKUJĄCE DANE: {holistic_profile.get('missing_data_gaps', '')}
CONFIDENCE DNA: {holistic_profile.get('confidence', 0)}%

KONTEKST SESJI:
{json.dumps(session_context or {}, ensure_ascii=False, indent=2)}

Na podstawie tego DNA Klienta wygeneruj precyzyjne wskaźniki sprzedażowe w formacie JSON.
"""

            # Wywołaj LLM
            response = await self._call_llm_with_retry(
                system_prompt=SALES_INDICATORS_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                use_cache=True,
                cache_prefix="sales_indicators"
            )
            
            # Parsuj odpowiedź
            sales_indicators = self._parse_indicators_response(response.get('content', ''))
            
            # Dodaj metadane
            sales_indicators.update({
                'generated_timestamp': datetime.now().isoformat(),
                'holistic_confidence': holistic_profile.get('confidence', 0),
                'model_used': self.model_name
            })
            
            logger.info(f"✅ Wskaźniki sprzedażowe wygenerowane - Temperature: {sales_indicators.get('purchase_temperature', {}).get('value', 0)}%")
            return sales_indicators
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas generowania wskaźników: {e}")
            return self._create_indicators_error_fallback(str(e))
    
    def _validate_psychology_profile(self, psychology_profile: Dict[str, Any]) -> bool:
        """Waliduje jakość profilu psychometrycznego"""
        if not psychology_profile:
            return False
        
        # Sprawdź obecność kluczowych sekcji
        required_sections = ['big_five', 'disc', 'schwartz_values']
        if not all(section in psychology_profile for section in required_sections):
            return False
        
        # Sprawdź kompletność Big Five
        big_five = psychology_profile.get('big_five', {})
        expected_traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        big_five_complete = all(
            trait in big_five and 
            isinstance(big_five[trait].get('score'), (int, float)) and 
            big_five[trait].get('score') > 0
            for trait in expected_traits
        )
        
        # Sprawdź confidence
        confidence = psychology_profile.get('confidence', 0)
        
        return big_five_complete and confidence >= 20  # Minimum 20% confidence
    
    def _prepare_synthesis_context(
        self,
        psychology_profile: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Przygotowuje kontekst dla syntezy"""
        
        context = {
            'interaction_count': 0,
            'conversation_themes': [],
            'client_concerns': []
        }
        
        if additional_context:
            context.update({
                'interaction_count': len(additional_context.get('session_history', [])),
                'client_profile': additional_context.get('client_profile', {}),
                'session_type': additional_context.get('session_context', {}).get('type', 'consultation')
            })
        
        return context
    
    def _parse_holistic_response(self, llm_response: str) -> Dict[str, Any]:
        """Parsuje odpowiedź LLM dla syntezy holistycznej"""
        try:
            # Znajdź JSON w odpowiedzi
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("⚠️ Brak JSON w odpowiedzi holistic synthesis")
                return self._create_holistic_fallback()
            
            json_str = llm_response[json_start:json_end]
            holistic_data = json.loads(json_str)
            
            # Walidacja struktury
            required_keys = ['holistic_summary', 'main_drive', 'key_levers', 'red_flags']
            if not all(key in holistic_data for key in required_keys):
                logger.warning("⚠️ Niekompletna struktura holistic JSON")
                return self._create_holistic_fallback()
            
            # Ustaw domyślną confidence jeśli brak
            if 'confidence' not in holistic_data:
                holistic_data['confidence'] = 50
            
            return holistic_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Błąd parsowania JSON holistic: {e}")
            return self._create_holistic_fallback()
        except Exception as e:
            logger.error(f"❌ Nieoczekiwany błąd parsowania holistic: {e}")
            return self._create_holistic_fallback()
    
    def _parse_indicators_response(self, llm_response: str) -> Dict[str, Any]:
        """Parsuje odpowiedź LLM dla wskaźników sprzedażowych"""
        try:
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("⚠️ Brak JSON w odpowiedzi sales indicators")
                return self._create_indicators_fallback()
            
            json_str = llm_response[json_start:json_end]
            indicators_data = json.loads(json_str)
            
            # Walidacja struktury
            required_indicators = ['purchase_temperature', 'customer_journey_stage', 'churn_risk', 'sales_potential']
            if not all(indicator in indicators_data for indicator in required_indicators):
                logger.warning("⚠️ Niekompletne wskaźniki sprzedażowe")
                return self._create_indicators_fallback()
            
            return indicators_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Błąd parsowania JSON indicators: {e}")
            return self._create_indicators_fallback()
        except Exception as e:
            logger.error(f"❌ Nieoczekiwany błąd parsowania indicators: {e}")
            return self._create_indicators_fallback()
    
    def _create_holistic_fallback(self) -> Dict[str, Any]:
        """Tworzy fallback DNA Klienta"""
        return {
            "holistic_summary": "Klient w fazie zbierania informacji o pojazdach elektrycznych Tesla. Wymaga systematycznego przedstawienia korzyści i budowania zaufania do marki.",
            "main_drive": "Potrzeba bezpieczeństwa i racjonalnej decyzji zakupowej",
            "communication_style": {
                "preferred_approach": "Profesjonalny i oparty na faktach",
                "tone": "Rzeczowy i cierpliwy",
                "pace": "Standardowe - bez pośpiechu",
                "information_density": "Średnia - podstawowe fakty"
            },
            "key_levers": [
                "Bezpieczeństwo i niezawodność Tesla",
                "Oszczędności TCO długoterminowe",
                "Innowacyjna technologia i prestiż marki",
                "Sieć Supercharger i wygoda użytkowania"
            ],
            "red_flags": [
                "Presja czasowa w sprzedaży",
                "Niejasne korzyści finansowe",
                "Brak konkretnych danych o produkcie",
                "Ignorowanie obaw klienta"
            ],
            "missing_data_gaps": "Potrzeba więcej informacji o preferencjach, budżecie i procesie decyzyjnym klienta",
            "confidence": 30,
            "is_fallback": True,
            "synthesis_timestamp": datetime.now().isoformat()
        }
    
    def _create_indicators_fallback(self) -> Dict[str, Any]:
        """Tworzy fallback wskaźniki sprzedażowe"""
        return {
            "purchase_temperature": {
                "value": 50,
                "temperature_level": "warm",
                "rationale": "Klient w fazie zbierania informacji - średnie zainteresowanie",
                "strategy": "Kontynuuj edukację o korzyściach Tesla",
                "confidence": 30
            },
            "customer_journey_stage": {
                "value": "consideration",
                "progress_percentage": 40,
                "next_stage": "evaluation",
                "rationale": "Rozważa pojazdy elektryczne jako opcję",
                "strategy": "Przedstaw konkretne modele i porównania",
                "confidence": 30
            },
            "churn_risk": {
                "value": 50,
                "risk_level": "medium",
                "risk_factors": ["Długi proces decyzyjny", "Porównanie z konkurencją"],
                "rationale": "Standardowe ryzyko dla klienta w fazie rozważań",
                "strategy": "Buduj relację i regularnie kontaktuj się",
                "confidence": 30
            },
            "sales_potential": {
                "value": 250000.0,
                "probability": 40,
                "estimated_timeframe": "4-8 tygodni",
                "rationale": "Średni potencjał sprzedaży dla klienta Tesla",
                "strategy": "Prezentuj wartość długoterminową i korzyści",
                "confidence": 30
            },
            "is_fallback": True,
            "generated_timestamp": datetime.now().isoformat()
        }
    
    def _create_holistic_error_fallback(self, error_message: str) -> Dict[str, Any]:
        """Tworzy fallback w przypadku błędu syntezy"""
        fallback = self._create_holistic_fallback()
        fallback.update({
            'error_occurred': True,
            'error_message': error_message,
            'confidence': 10
        })
        return fallback
    
    def _create_indicators_error_fallback(self, error_message: str) -> Dict[str, Any]:
        """Tworzy fallback w przypadku błędu wskaźników"""
        fallback = self._create_indicators_fallback()
        fallback.update({
            'error_occurred': True,
            'error_message': error_message
        })
        
        # Obniż confidence we wszystkich wskaźnikach
        for indicator in fallback.values():
            if isinstance(indicator, dict) and 'confidence' in indicator:
                indicator['confidence'] = 10
        
        return fallback
