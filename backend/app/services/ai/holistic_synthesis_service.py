"""
HolisticSynthesisService - Wyspecjalizowany serwis do tworzenia DNA Klienta
Odpowiedzialny za: holistyczną syntezę profilu psychometrycznego, sales indicators
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_ai_service import BaseAIService
from ..redis_cache_service import RedisCacheService

logger = logging.getLogger(__name__)


# Zahardkodowane prompty zostały usunięte - teraz ładowane dynamicznie z bazy danych



class HolisticSynthesisService(BaseAIService):
    """
    Wyspecjalizowany serwis do tworzenia holistycznej syntezy - "DNA Klienta".
    
    Funkcjonalności:
    - Synteza profilu psychometrycznego w holistyczny profil
    - Identyfikacja głównych motywatorów i dźwigni
    - Generowanie wskaźników sprzedażowych
    - Określanie readiness do zakupu
    """
    
    def __init__(self, session):
        super().__init__(session)
        
        # Inicjalizuj serwis cache'owania
        self.cache_service = RedisCacheService()
        
        logger.info("✅ HolisticSynthesisService initialized with Redis cache")
    
    async def run_holistic_synthesis(
        self,
        raw_psychology_profile: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Przeprowadza holistyczną syntezę profilu psychometrycznego w DNA Klienta
        z wykorzystaniem Redis cache dla optymalizacji wydajności.
        
        Args:
            raw_psychology_profile: Surowy profil psychometryczny (Big Five + DISC + Schwartz)
            additional_context: Dodatkowy kontekst (historia rozmów, profil klienta)
            
        Returns:
            Dict: Holistyczny profil klienta (DNA Klienta)
        """
        try:
            logger.info("🧬 Rozpoczynam holistyczną syntezę DNA Klienta...")
            
            # KROK 1: Generuj unikalny klucz cache'a na podstawie danych wejściowych
            cache_key = self.cache_service.generate_cache_key(
                service_name="holistic_synthesis",
                psychology_profile=raw_psychology_profile,
                additional_context=additional_context
            )
            
            # KROK 2: Sprawdź cache Redis
            cached_result = await self.cache_service.get_cache(cache_key)
            if cached_result and cached_result.get("data"):
                logger.info(f"🎯 Cache HIT dla holistycznej syntezy: {cache_key}")
                # Zwróć dane z cache (bez metadanych cache'a)
                return cached_result["data"]
            
            logger.info(f"❌ Cache MISS dla holistycznej syntezy: {cache_key}")
            
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

            # KROK 1: Pobierz szablon promptu z bazy danych
            prompt_template_obj = await self.prompt_repo.get_active_prompt_by_name(
                name="holistic_synthesis"
            )
            
            if not prompt_template_obj:
                # Obsługa błędu, jeśli prompt nie istnieje w bazie
                raise ValueError("Aktywny szablon promptu 'holistic_synthesis' nie został znaleziony w bazie danych.")
            
            system_prompt = prompt_template_obj.content

            # Wywołaj LLM z dynamicznym promptem
            response = await self._call_llm_with_retry(
                system_prompt=system_prompt,
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
            
            # KROK 2: Oblicz zaawansowany confidence score
            confidence_score = await self._calculate_confidence_score(
                new_analysis=holistic_profile,
                all_interactions=additional_context.get('all_interactions', []) if additional_context else [],
                previous_session_psychology=additional_context.get('previous_psychology') if additional_context else None
            )
            
            # Zastąp confidence score obliczonym przez zaawansowany algorytm
            holistic_profile['confidence'] = confidence_score
            holistic_profile['synthesis_confidence'] = confidence_score  # Aktualizuj też synthesis_confidence
            
            # KROK 3: Zapisz wynik w cache Redis (TTL: 30 minut)
            await self.cache_service.set_cache(
                key=cache_key,
                data=holistic_profile,
                ttl=1800  # 30 minut
            )
            logger.info(f"💾 Wynik holistycznej syntezy zapisany w cache: {cache_key}")
            
            logger.info(f"✅ DNA Klienta wygenerowane - Advanced Confidence: {confidence_score}%")
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

            # KROK 1: Pobierz szablon promptu z bazy danych
            prompt_template_obj = await self.prompt_repo.get_active_prompt_by_name(
                name="sales_indicators"
            )
            
            if not prompt_template_obj:
                # Obsługa błędu, jeśli prompt nie istnieje w bazie
                raise ValueError("Aktywny szablon promptu 'sales_indicators' nie został znaleziony w bazie danych.")
            
            system_prompt = prompt_template_obj.content

            # Wywołaj LLM z dynamicznym promptem
            response = await self._call_llm_with_retry(
                system_prompt=system_prompt,
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
    
    async def _calculate_confidence_score(
        self,
        new_analysis: dict,
        all_interactions: list,
        previous_session_psychology: dict | None
    ) -> int:
        """
        Oblicza wskaźnik pewności dla nowej analizy psychometrycznej.
        
        Args:
            new_analysis: Nowa analiza holistyczna
            all_interactions: Lista wszystkich interakcji w sesji
            previous_session_psychology: Poprzedni profil psychometryczny (jeśli istnieje)
            
        Returns:
            int: Wskaźnik pewności (0-100)
        """
        try:
            logger.info("🧮 Obliczam zaawansowany confidence score...")
            
            # Krok 1: Oblicz BaseScore na podstawie liczby interakcji
            num_interactions = len(all_interactions)
            base_score = min(20 + (num_interactions - 3) * 5, 50) if num_interactions >= 3 else 0
            
            logger.debug(f"Base score: {base_score} (interactions: {num_interactions})")
            
            consistency_bonus = 0
            contradiction_penalty = 0
            
            # Krok 2: Oblicz Bonus/Karę, jeśli istnieje poprzednia analiza do porównania
            if previous_session_psychology and previous_session_psychology.get("archetype_analysis"):
                previous_archetype = previous_session_psychology["archetype_analysis"].get("primary_archetype")
                # Sprawdź czy nowa analiza ma archetype_analysis (może być w różnych formatach)
                new_archetype = None
                
                if new_analysis.get("archetype_analysis"):
                    new_archetype = new_analysis["archetype_analysis"].get("primary_archetype")
                elif new_analysis.get("main_drive"):  # Fallback - użyj main_drive jako proxy
                    new_archetype = new_analysis.get("main_drive")
                
                if previous_archetype and new_archetype:
                    if previous_archetype == new_archetype:
                        consistency_bonus = 15  # Zwiększony bonus za spójność
                        logger.debug(f"Consistency bonus: +{consistency_bonus} (same archetype: {previous_archetype})")
                    else:
                        contradiction_penalty = 20
                        logger.debug(f"Contradiction penalty: -{contradiction_penalty} (different archetypes: {previous_archetype} vs {new_archetype})")
                
                # Dodatkowe porównanie dla profilu DISC (jeśli dostępny)
                if (previous_session_psychology.get("disc_profile") and 
                    new_analysis.get("communication_style")):
                    # Porównaj style komunikacji jako proxy dla DISC
                    prev_style = previous_session_psychology["disc_profile"].get("dominant_factor")
                    new_style = new_analysis["communication_style"].get("preferred_approach")
                    
                    if prev_style and new_style:
                        # Proste mapowanie stylów komunikacji na DISC
                        style_consistency = self._compare_communication_styles(prev_style, new_style)
                        if style_consistency:
                            consistency_bonus += 10
                            logger.debug(f"Communication style consistency bonus: +10")
                        else:
                            contradiction_penalty += 10
                            logger.debug(f"Communication style contradiction penalty: -10")
            
            # Krok 3: Bonus za jakość analizy (sprawdź kompletność danych)
            quality_bonus = self._calculate_quality_bonus(new_analysis)
            logger.debug(f"Quality bonus: +{quality_bonus}")
            
            # Krok 4: Zsumuj wynik i ogranicz do przedziału 0-100
            final_score = base_score + consistency_bonus + quality_bonus - contradiction_penalty
            final_score = max(0, min(100, final_score))  # Ograniczenie wyniku do przedziału [0, 100]
            
            logger.info(f"📊 Confidence score calculated: {final_score}% (base: {base_score}, consistency: +{consistency_bonus}, quality: +{quality_bonus}, penalty: -{contradiction_penalty})")
            
            return int(final_score)
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas obliczania confidence score: {e}")
            # Fallback - zwróć średni wynik
            return 50
    
    def _compare_communication_styles(self, disc_factor: str, communication_approach: str) -> bool:
        """
        Porównuje styl DISC z podejściem komunikacyjnym
        
        Args:
            disc_factor: Dominujący czynnik DISC (D, I, S, C)
            communication_approach: Preferowane podejście komunikacyjne
            
        Returns:
            bool: True jeśli style są spójne
        """
        # Mapowanie DISC na style komunikacji
        disc_to_communication = {
            'D': ['bezpośredni', 'decyzyjny', 'szybki'],
            'I': ['towarzyski', 'entuzjastyczny', 'perswazyjny'],
            'S': ['cierpliwy', 'stabilny', 'metodyczny'],
            'C': ['analityczny', 'systematyczny', 'oparty na faktach']
        }
        
        if disc_factor in disc_to_communication:
            expected_styles = disc_to_communication[disc_factor]
            return any(style.lower() in communication_approach.lower() for style in expected_styles)
        
        return False
    
    def _calculate_quality_bonus(self, analysis: dict) -> int:
        """
        Oblicza bonus za jakość analizy na podstawie kompletności danych
        
        Args:
            analysis: Analiza holistyczna
            
        Returns:
            int: Bonus za jakość (0-25)
        """
        quality_score = 0
        
        # Sprawdź obecność kluczowych elementów
        required_fields = [
            'holistic_summary',
            'main_drive', 
            'communication_style',
            'key_levers',
            'red_flags'
        ]
        
        for field in required_fields:
            if analysis.get(field):
                quality_score += 3  # 3 punkty za każde pole
        
        # Bonus za szczegółowość communication_style
        comm_style = analysis.get('communication_style', {})
        if isinstance(comm_style, dict) and len(comm_style) >= 3:
            quality_score += 5
        
        # Bonus za liczbę key_levers i red_flags
        key_levers = analysis.get('key_levers', [])
        red_flags = analysis.get('red_flags', [])
        
        if len(key_levers) >= 3:
            quality_score += 3
        if len(red_flags) >= 3:
            quality_score += 2
        
        return min(quality_score, 25)  # Maksymalnie 25 punktów bonusu
    
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
