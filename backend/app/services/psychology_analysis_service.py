"""
PsychologyAnalysisService v1.0 - Pure Psychometric Analysis Service
Extracted from SessionOrchestratorService monolith - Phase 2A

Single Responsibility: Pure psychometric analysis of customer interactions
- Big Five personality trait analysis
- DISC assessment processing  
- Schwartz values evaluation
- AI prompt construction and response parsing
- Psychology data validation and repair
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PsychologyAnalysisService:
    """
    🧠 Pure Psychometric Analysis Service
    
    Responsible for:
    1. Building AI prompts for psychological analysis
    2. Parsing and validating AI responses
    3. Creating fallback psychology profiles
    4. Managing psychology confidence scoring
    """
    
    def __init__(self, ai_service=None):
        """
        Initialize the psychology analysis service with AI service dependency
        
        Args:
            ai_service: AIService instance for LLM calls
        """
        self.ai_service = ai_service
        if not ai_service:
            # Import here to avoid circular imports
            from app.services.ai_service import ai_service_unified
            self.ai_service = ai_service_unified
            
    async def analyze_interaction(self, conversation_history: str, current_profile: Dict = None, confidence: int = 0) -> Dict[str, Any]:
        """
        🎯 MAIN PUBLIC INTERFACE - Complete psychometric analysis of customer interaction
        
        Args:
            conversation_history: Full conversation history as formatted string
            current_profile: Existing psychology profile (if any)
            confidence: Current confidence level (0-100)
            
        Returns:
            dict: Complete psychology analysis with confidence scores and validation
            
        Raises:
            Exception: When AI analysis fails and fallback is needed
        """
        try:
            logger.info(f"🧠 [PSYCHOLOGY ANALYSIS] Starting analysis - confidence: {confidence}%")
            
            # STEP 1: Build comprehensive AI prompt for psychology analysis
            ai_prompt = self._build_cumulative_psychology_prompt(
                history=conversation_history,
                current_profile=current_profile or {},
                confidence=confidence
            )
            
            logger.info(f"🤖 [PSYCHOLOGY ANALYSIS] Sending prompt to AI ({len(ai_prompt)} chars)")
            
            # STEP 2: Call AI service for psychological analysis
            ai_response = await self.ai_service._call_llm_with_retry(
                system_prompt="Jesteś ekspertem psychologii sprzedaży generującym kompletny profil klienta.",
                user_prompt=ai_prompt
            )
            
            # STEP 3: Extract content from AI response
            ai_response_content = ai_response.get('content', '') if isinstance(ai_response, dict) else str(ai_response)
            
            # STEP 4: Parse and validate AI response
            logger.info(f"🔍 [PSYCHOLOGY ANALYSIS] Parsing AI response ({len(ai_response_content)} chars)")
            parsed_result = self._parse_psychology_ai_response(ai_response_content)
            
            if not parsed_result:
                logger.warning(f"⚠️ [PSYCHOLOGY ANALYSIS] AI parsing failed, using fallback")
                return self._create_fallback_psychology_profile()
            
            # STEP 5: Validate and repair psychology data
            validated_result = self._validate_and_repair_psychology(parsed_result, self.ai_service)
            
            logger.info(f"✅ [PSYCHOLOGY ANALYSIS] Analysis complete - confidence: {validated_result.get('psychology_confidence', 0)}%")
            return validated_result
            
        except Exception as e:
            logger.error(f"❌ [PSYCHOLOGY ANALYSIS] Analysis failed: {e}")
            return self._create_fallback_psychology_profile()

    def _build_cumulative_psychology_prompt(self, history: str, current_profile: Dict, confidence: int) -> str:
        """
        🧠⚡ ULTRA MÓZG v4.1 - Enhanced prompt z few-shot learning i Zero Null Policy
        """
        archetyp_definitions = "\n".join([
            "- 🔬 Analityk: Wysoka Sumienność, Compliance (DISC), Wartość: Bezpieczeństwo",
            "- 🚀 Wizjoner: Wysoka Otwartość, Dominance + Influence (DISC), Wartość: Osiągnięcia", 
            "- 🤝 Relacyjny Budowniczy: Wysoka Ugodowość, Steadiness (DISC), Wartość: Życzliwość",
            "- ⚡ Szybki Decydent: Wysoka Ekstrawersja, Dominance (DISC), Wartość: Władza"
        ])
        
        # 🎯 FEW-SHOT LEARNING EXAMPLES - zgodnie z blueprintem
        few_shot_examples = """
=== PRZYKŁAD 1: ANALITYCZNY CFO ===
HISTORIA: "CFO firmy logistycznej pyta o TCO dla 25 Tesli Model Y. Ciągle dopytuje o koszty serwisu, harmonogram przeglądów. Chce twarde dane oszczędności paliwa vs diesel. Mówi: 'Emocje są ważne, ale liczą się dla mnie liczby w Excelu'"

OCZEKIWANY JSON:
{
  "cumulative_psychology": {
    "big_five": {
      "openness": {"score": 6, "rationale": "Otwarty na nowe technologie (Tesla), ale potrzebuje danych", "strategy": "Prezentuj innowacje z konkretnymi metrykami"},
      "conscientiousness": {"score": 9, "rationale": "Bardzo sumienną analiza, Excel, szczegółowe pytania", "strategy": "Dostarczaj precyzyjne dokumenty i harmonogramy"},
      "extraversion": {"score": 4, "rationale": "Skupiony na danych, a nie na emocjach czy relacjach", "strategy": "Komunikacja rzeczowa, bez small talk"},
      "agreeableness": {"score": 5, "rationale": "Neutralny - skupia się na faktach", "strategy": "Argumenty merytoryczne, nie emocjonalne"},
      "neuroticism": {"score": 3, "rationale": "Kontroluje sytuację przez analizę - niski stres", "strategy": "Daj mu kontrolę przez dostęp do danych"}
    }
  },
  "psychology_confidence": 85,
  "customer_archetype": {
    "archetype_key": "analityk",
    "confidence": 90,
    "description": "CFO analityczny, podejmuje decyzje na danych"
  }
}

=== PRZYKŁAD 2: SZYBKI DECYDENT ===
HISTORIA: "CEO startup chce 5 Tesli 'od zaraz'. Pyta: 'Kiedy mogę mieć auta? Jaka cena za pakiet? Podpisujemy dziś czy jutro?' Nie interesują go szczegóły techniczne."

OCZEKIWANY JSON:
{
  "cumulative_psychology": {
    "big_five": {
      "openness": {"score": 8, "rationale": "Bardzo otwarty na nowe rozwiązania - chce 'od zaraz'", "strategy": "Prezentuj najnowsze funkcje i możliwości"},
      "conscientiousness": {"score": 4, "rationale": "Nie skupia się na szczegółach - chce szybkiej decyzji", "strategy": "Skup się na korzyściach, nie procesie"},
      "extraversion": {"score": 9, "rationale": "Bardzo aktywny, dominujący, chce kontrolować tempo", "strategy": "Pozwól mu prowadzić rozmowę"},
      "agreeableness": {"score": 6, "rationale": "Współpracuje ale na swoich warunkach", "strategy": "Dostosuj się do jego tempa"},
      "neuroticism": {"score": 2, "rationale": "Bardzo pewny siebie, brak stresu decyzyjnego", "strategy": "Nie przedłużaj procesu niepotrzebnie"}
    }
  },
  "psychology_confidence": 80,
  "customer_archetype": {
    "archetype_key": "szybki_decydent",
    "confidence": 85,
    "description": "CEO dynamiczny, szybkie decyzje biznesowe"
  }
}

⚠️ ZERO NULL POLICY: NIGDY nie zwracaj null w polach score, rationale, strategy! Jeśli nie jesteś pewien wartości, oszacuj najbardziej prawdopodobną i wyjaśnij w rationale dlaczego.
"""

        return f"""
🧠⚡ Jesteś ekspertem psychologii sprzedaży w systemie Ultra Mózg. Generujesz KOMPLETNY, ZEROWO-NULLOWY profil klienta.

{few_shot_examples}

🎯 TWOJE ZADANIE - 5 KROKÓW:

KROK 1 - AKTUALIZACJA PROFILU:
Na podstawie pełnej historii sesji i obecnego profilu, zaktualizuj profil psychometryczny.
⚠️ KRYTYCZNE: WSZYSTKIE pola score, rationale, strategy MUSZĄ mieć wartości (nie null)!

KROK 2 - OCENA PEWNOŚCI:
Oblicz poziom pewności analizy (0-100%) na podstawie dostępnych danych.

KROK 3 - SUGGESTED QUESTIONS:
Jeśli pewność < 80%, wygeneruj 2-4 konkretne pytania.

KROK 4 - SYNTEZA ARCHETYPU:
Jeśli pewność >= 70%, przypisz klienta do archetypu:
{archetyp_definitions}

KROK 5 - WSKAŹNIKI SPRZEDAŻOWE:
Wskaźniki MUSZĄ być zgodne z archetypem z KROKU 4!

DANE WEJŚCIOWE:

HISTORIA SESJI:
{history}

OBECNY PROFIL PSYCHOMETRYCZNY (confidence: {confidence}%):
{json.dumps(current_profile, ensure_ascii=False, indent=2) if current_profile else "BRAK PROFILU"}

ZWRÓĆ WYNIK WYŁĄCZNIE JAKO JSON Z PEŁNYMI OBIEKTAMI:
{{
  "cumulative_psychology": {{
    "big_five": {{ 
      "openness": {{ "score": 7, "rationale": "Uzasadnienie AI", "strategy": "Strategia sprzedażowa" }},
      "conscientiousness": {{ "score": 8, "rationale": "Uzasadnienie AI", "strategy": "Strategia sprzedażowa" }},
      "extraversion": {{ "score": 5, "rationale": "Uzasadnienie AI", "strategy": "Strategia sprzedażowa" }},
      "agreeableness": {{ "score": 4, "rationale": "Uzasadnienie AI", "strategy": "Strategia sprzedażowa" }},
      "neuroticism": {{ "score": 3, "rationale": "Uzasadnienie AI", "strategy": "Strategia sprzedażowa" }}
    }},
    "disc": {{ 
      "dominance": {{ "score": 6, "rationale": "Uzasadnienie AI", "strategy": "Strategia sprzedażowa" }},
      "influence": {{ "score": 4, "rationale": "Uzasadnienie AI", "strategy": "Strategia sprzedażowa" }},
      "steadiness": {{ "score": 3, "rationale": "Uzasadnienie AI", "strategy": "Strategia sprzedażowa" }},
      "compliance": {{ "score": 8, "rationale": "Uzasadnienie AI", "strategy": "Strategia sprzedażowa" }}
    }},
    "schwartz_values": [{{ "value_name": "Bezpieczeństwo", "strength": 8, "rationale": "Uzasadnienie AI", "strategy": "Strategia sprzedażowa", "is_present": true }}, ...],
    "observations_summary": "Kluczowe obserwacje z całej sesji"
  }},
  "psychology_confidence": 85,
  "suggested_questions": [
    {{ "question": "Konkretne pytanie do klienta", "psychological_target": "Co ma sprawdzić" }}
  ],
  "customer_archetype": {{
    "archetype_key": "analityk",
    "archetype_name": "🔬 Analityk",
    "confidence": 90,
    "key_traits": ["analityczny", "ostrożny", "szczegółowy", "sceptyczny"],
    "description": "Klient o wysokiej sumienności i potrzebie bezpieczeństwa. Podejmuje decyzje na podstawie danych.",
    "sales_strategy": {{
      "do": ["Prezentuj szczegółowe dane TCO", "Pokazuj certyfikaty i nagrody", "Daj czas na przemyślenie", "Używaj wykresów i tabel"],
      "dont": ["Nie wywieraj presji czasowej", "Nie pomijaj technicznych szczegółów", "Nie używaj emocjonalnych argumentów", "Nie przerywaj jego analiz"]
    }},
    "motivation": "Bezpieczeństwo inwestycji i minimalizacja ryzyka",
    "communication_style": "Faktyczny, szczegółowy, oparty na danych"
  }},
  "sales_indicators": {{
    "purchase_temperature": {{
      "value": 75,
      "temperature_level": "hot", 
      "rationale": "Klient zadaje szczegółowe pytania o TCO i finansowanie",
      "strategy": "Przyspiesz proces - zaproponuj spotkanie w ciągu 48h",
      "confidence": 85
    }},
    "customer_journey_stage": {{
      "value": "evaluation",
      "progress_percentage": 70,
      "next_stage": "decision",
      "rationale": "Porównuje szczegółowo z konkurencją - typowy etap oceny", 
      "strategy": "Dostarcz przewagę konkurencyjną i case studies",
      "confidence": 90
    }},
    "churn_risk": {{
      "value": 25,
      "risk_level": "low",
      "risk_factors": ["Długi proces decyzyjny"],
      "rationale": "Aktywne zaangażowanie, szczegółowe pytania - niskie ryzyko",
      "strategy": "Utrzymaj regularny kontakt, nie wywieraj presji", 
      "confidence": 80
    }},
    "sales_potential": {{
      "value": 8000000.0,
      "probability": 75,
      "estimated_timeframe": "3-4 tygodnie",
      "rationale": "Budżet 25M PLN, pozycja CEO - wysokie prawdopodobieństwo",
      "strategy": "Przygotuj szczegółową propozycję biznesową z ROI",
      "confidence": 85
    }}
  }}
}}
"""

    def _validate_and_repair_psychology(self, raw_analysis: dict, ai_service) -> dict:
        """
        🔧 ULTRA MÓZG v4.1 - Walidacja i naprawa danych psychology
        
        Zgodnie z blueprintem - sprawdza czy kluczowe pola nie są null
        i naprawia je automatycznie jeśli trzeba.
        
        Args:
            raw_analysis: Surowa odpowiedź AI
            ai_service: Service do micro-prompt naprawy
            
        Returns:
            dict: Zwalidowany i naprawiony profil psychology
        """
        logger.info("🔧 [VALIDATION] Rozpoczynam walidację danych psychology...")
        
        repaired_analysis = raw_analysis.copy()
        null_fields_found = []
        
        # Sprawdź Big Five
        big_five = repaired_analysis.get('cumulative_psychology', {}).get('big_five', {})
        for trait_name in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            trait = big_five.get(trait_name, {})
            if not trait or trait.get('score') is None:
                null_fields_found.append(f'big_five.{trait_name}')
                # Strategia 1: Wartości domyślne (zgodnie z blueprintem)
                big_five[trait_name] = {
                    'score': 5,  # Neutralna wartość środkowa
                    'rationale': f'Oszacowanie domyślne - wymagane więcej danych o {trait_name}',
                    'strategy': f'Obserwuj zachowania związane z {trait_name} podczas kolejnych interakcji'
                }
        
        # Sprawdź DISC
        disc = repaired_analysis.get('cumulative_psychology', {}).get('disc', {})
        for trait_name in ['dominance', 'influence', 'steadiness', 'compliance']:
            trait = disc.get(trait_name, {})
            if not trait or trait.get('score') is None:
                null_fields_found.append(f'disc.{trait_name}')
                disc[trait_name] = {
                    'score': 5,
                    'rationale': f'Oszacowanie domyślne - wymagane więcej danych o {trait_name}',
                    'strategy': f'Zaobserwuj przejawy {trait_name} w komunikacji klienta'
                }
        
        # Sprawdź Schwartz Values
        schwartz = repaired_analysis.get('cumulative_psychology', {}).get('schwartz_values', [])
        if not schwartz or len(schwartz) == 0:
            null_fields_found.append('schwartz_values')
            repaired_analysis['cumulative_psychology']['schwartz_values'] = [
                {
                    'value_name': 'Bezpieczeństwo',
                    'strength': 5,
                    'rationale': 'Wartość domyślna - większość klientów B2B ceni bezpieczeństwo',
                    'strategy': 'Podkreślaj stabilność i niezawodność rozwiązania',
                    'is_present': True
                }
            ]
        
        # Sprawdź Customer Archetype
        archetype = repaired_analysis.get('customer_archetype', {})
        if not archetype or not archetype.get('archetype_key'):
            null_fields_found.append('customer_archetype')
            repaired_analysis['customer_archetype'] = {
                'archetype_key': 'neutral',
                'archetype_name': '🎯 Neutralny',
                'confidence': 30,
                'description': 'Profil ogólny - wymagane więcej informacji o kliencie',
                'key_traits': ['ostrożny', 'analityczny'],
                'sales_strategy': {
                    'do': ['Zbieraj więcej informacji', 'Zadawaj otwarte pytania', 'Obserwuj reakcje'],
                    'dont': ['Nie pressuj', 'Nie zakładaj preferencji', 'Nie przyspieszaj procesu']
                },
                'motivation': 'Potrzeba więcej danych aby określić główną motywację',
                'communication_style': 'Ostrożny, wyważony styl komunikacji'
            }
        
        # Sprawdź Psychology Confidence
        if repaired_analysis.get('psychology_confidence', 0) == 0:
            null_fields_found.append('psychology_confidence')
            repaired_analysis['psychology_confidence'] = 30  # Niska pewność przy null values
        
        # Logowanie wyników walidacji
        if null_fields_found:
            logger.warning(f"⚠️ [VALIDATION] Naprawiono {len(null_fields_found)} null values: {null_fields_found}")
        else:
            logger.info("✅ [VALIDATION] Wszystkie kluczowe pola wypełnione poprawnie")
        
        return repaired_analysis

    def _parse_psychology_ai_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """🧠⚡ Enhanced parsowanie z walidacją - Ultra Mózg v4.1"""
        try:
            # Znajdź JSON w odpowiedzi
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("⚠️ [PSYCHOLOGY PARSE] Brak JSON w odpowiedzi AI")
                return None
                
            json_str = ai_response[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            logger.info(f"✅ [PSYCHOLOGY PARSE] Sparsowano: confidence={parsed_data.get('psychology_confidence', 0)}%")
            
            # DEBUG: Log szczegółowych danych psychology
            cumulative = parsed_data.get('cumulative_psychology', {})
            big_five = cumulative.get('big_five', {})
            disc = cumulative.get('disc', {})
            archetype = parsed_data.get('customer_archetype', {})
            
            logger.info(f"🧠 [DEBUG BIG FIVE] {len([k for k,v in big_five.items() if v.get('score')])} traits validated")
            logger.info(f"🎯 [DEBUG DISC] {len([k for k,v in disc.items() if v.get('score')])} traits validated")  
            logger.info(f"👤 [DEBUG ARCHETYPE] {archetype.get('archetype_key', 'none')} confidence={archetype.get('confidence', 0)}%")
            
            # MODUŁ 4: Debug sales indicators
            sales_indicators = parsed_data.get('sales_indicators', {})
            logger.info(f"📊 [DEBUG INDICATORS] {len(sales_indicators)} indicators present")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ [PSYCHOLOGY PARSE] JSON decode error: {e}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ [PSYCHOLOGY PARSE] Unexpected error: {e}")
            return None

    def _create_fallback_psychology_profile(self, interaction_count: int = 0) -> Dict[str, Any]:
        """🔧 ULTRA MÓZG v4.1 - Enhanced fallback z Zero Null Policy"""
        analysis_level = "pełna" if interaction_count >= 3 else "wstępna"

        return {
            'cumulative_psychology': {
                'big_five': {
                    'openness': {'score': 5, 'rationale': 'Fallback - brak danych AI', 'strategy': 'Zbieraj więcej informacji o otwartości klienta'},
                    'conscientiousness': {'score': 5, 'rationale': 'Fallback - brak danych AI', 'strategy': 'Obserwuj poziom szczegółowości pytań'},
                    'extraversion': {'score': 5, 'rationale': 'Fallback - brak danych AI', 'strategy': 'Zwróć uwagę na styl komunikacji'},
                    'agreeableness': {'score': 5, 'rationale': 'Fallback - brak danych AI', 'strategy': 'Oceniaj poziom współpracy'},
                    'neuroticism': {'score': 5, 'rationale': 'Fallback - brak danych AI', 'strategy': 'Monitoruj oznaki stresu lub niepewności'}
                },
                'disc': {
                    'dominance': {'score': 5, 'rationale': 'Fallback - brak danych AI', 'strategy': 'Sprawdzaj kto prowadzi rozmowę'},
                    'influence': {'score': 5, 'rationale': 'Fallback - brak danych AI', 'strategy': 'Zwróć uwagę na emocjonalność'},
                    'steadiness': {'score': 5, 'rationale': 'Fallback - brak danych AI', 'strategy': 'Oceń poziom cierpliwości'},
                    'compliance': {'score': 5, 'rationale': 'Fallback - brak danych AI', 'strategy': 'Obserwuj podejście do procedur'}
                },
                'schwartz_values': [
                    {'value_name': 'Bezpieczeństwo', 'strength': 5, 'rationale': 'Fallback - wartość domyślna B2B', 'strategy': 'Podkreślaj stabilność', 'is_present': True}
                ],
                'observations_summary': 'Analiza niedostępna - wymagane więcej danych'
            },
            'psychology_confidence': 10,
            'suggested_questions': [
                {'question': 'Czy klient zadaje szczegółowe pytania?', 'psychological_target': 'conscientiousness'},
                {'question': 'Jak klient podejmuje decyzje?', 'psychological_target': 'decision_style'}
            ],
            'customer_archetype': {
                'archetype_key': 'neutral',
                'archetype_name': '🎯 Neutralny',
                'confidence': 10,
                'key_traits': ['ostrożny'],
                'description': 'Profil podstawowy - wymagane więcej informacji',
                'sales_strategy': {
                    'do': ['Zbieraj informacje', 'Zadawaj pytania', 'Obserwuj'],
                    'dont': ['Nie zakładaj', 'Nie pressuj', 'Nie przyspieszaj']
                },
                'motivation': 'Nieokreślona',
                'communication_style': 'Neutralny'
            },
            'sales_indicators': {
                'purchase_temperature': {'value': 30, 'temperature_level': 'cold', 'rationale': 'Fallback - brak danych', 'strategy': 'Rozgrzej kontakt', 'confidence': 10},
                'customer_journey_stage': {'value': 'awareness', 'progress_percentage': 20, 'next_stage': 'interest', 'rationale': 'Fallback - początek procesu', 'strategy': 'Buduj świadomość korzyści', 'confidence': 10},
                'churn_risk': {'value': 50, 'risk_level': 'medium', 'risk_factors': ['Brak danych'], 'rationale': 'Fallback - średnie ryzyko', 'strategy': 'Monitoruj zaangażowanie', 'confidence': 10},
                'sales_potential': {'value': 1000000.0, 'probability': 30, 'estimated_timeframe': '4-8 tygodni', 'rationale': 'Fallback - szacunek podstawowy', 'strategy': 'Zbieraj informacje o budżecie', 'confidence': 10}
            },
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_level': analysis_level,
            'interaction_count': interaction_count,
            'tesla_archetype_active': False  # Fallback - nie ma archetypu Tesli
        }

# Create service instance for dependency injection
psychology_analysis_service = PsychologyAnalysisService()