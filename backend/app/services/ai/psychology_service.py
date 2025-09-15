"""
PsychologyService - Wyspecjalizowany serwis do analizy psychometrycznej
Odpowiedzialny za: Big Five, DISC, Schwartz Values, Customer Archetypes
"""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .base_ai_service import BaseAIService

logger = logging.getLogger(__name__)


# Zahardkodowane prompty zostały usunięte - teraz ładowane dynamicznie z bazy danych


class PsychologyService(BaseAIService):
    """
    Wyspecjalizowany serwis do analizy psychometrycznej klientów.
    
    Funkcjonalności:
    - Analiza Big Five personality traits
    - Analiza DISC behavioral styles
    - Identyfikacja wartości Schwartza
    - Generowanie customer archetypes
    - Dual-stage psychometric analysis
    """
    
    def __init__(self, session):
        super().__init__(session)
        logger.info("✅ PsychologyService initialized")
    
    async def generate_psychometric_analysis(
        self,
        conversation_history: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generuje pełną analizę psychometryczną na podstawie historii rozmowy
        
        Args:
            conversation_history: Historia interakcji z klientem
            additional_context: Dodatkowy kontekst (profil klienta, notatki)
            
        Returns:
            Dict: Pełny profil psychometryczny (Big Five + DISC + Schwartz)
        """
        try:
            logger.info("🧠 Rozpoczynam analizę psychometryczną...")
            
            # Przygotuj dane wejściowe
            conversation_text = self._format_conversation_for_analysis(conversation_history)
            
            if not conversation_text.strip():
                return self._create_minimal_psychology_fallback()
            
            # Przygotuj prompt użytkownika
            user_prompt = f"""
TRANSKRYPCJA ROZMOWY SPRZEDAŻOWEJ:
{conversation_text}

DODATKOWY KONTEKST:
{json.dumps(additional_context or {}, ensure_ascii=False, indent=2)}

Przeanalizuj powyższą rozmowę i zwróć szczegółowy profil psychometryczny w formacie JSON.
"""

            # KROK 1: Pobierz szablon promptu z bazy danych
            prompt_template_obj = await self.prompt_repo.get_active_prompt_by_name(
                name="psychology_analysis"
            )
            
            if not prompt_template_obj:
                # Obsługa błędu, jeśli prompt nie istnieje w bazie
                raise ValueError("Aktywny szablon promptu 'psychology_analysis' nie został znaleziony w bazie danych.")
            
            system_prompt = prompt_template_obj.content

            # Wywołaj LLM z dynamicznym promptem
            response = await self._call_llm_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                use_cache=True,
                cache_prefix="psychology"
            )
            
            # Parsuj odpowiedź
            psychology_profile = self._parse_psychology_response(response.get('content', ''))
            
            # Dodaj metadane
            psychology_profile.update({
                'analysis_timestamp': datetime.now().isoformat(),
                'confidence': self._calculate_psychology_confidence(psychology_profile),
                'conversation_length': len(conversation_history),
                'model_used': self.model_name
            })
            
            logger.info(f"✅ Analiza psychometryczna ukończona - Confidence: {psychology_profile.get('confidence', 0)}%")
            return psychology_profile
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas analizy psychometrycznej: {e}")
            return self._create_psychology_error_fallback(str(e))
    
    async def generate_dual_stage_psychometric_analysis(
        self,
        user_input: str,
        session_context: Dict[str, Any],
        previous_psychology: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Generuje dwustopniową analizę psychometryczną:
        1. Aktualizuje profil psychologiczny
        2. Generuje pytania pomocnicze dla głębszej analizy
        
        Args:
            user_input: Najnowsza wypowiedź klienta
            session_context: Kontekst sesji
            previous_psychology: Poprzedni profil psychologiczny (jeśli dostępny)
            
        Returns:
            Tuple[Dict, List]: (zaktualizowany_profil, pytania_pomocnicze)
        """
        try:
            logger.info("🔄 Rozpoczynam dual-stage psychometric analysis...")
            
            # ETAP 1: Aktualizacja profilu
            updated_profile = await self._update_psychology_profile(
                user_input, session_context, previous_psychology
            )
            
            # ETAP 2: Generowanie pytań pomocniczych
            clarifying_questions = await self._generate_clarifying_questions(
                updated_profile, user_input
            )
            
            logger.info(f"✅ Dual-stage analysis ukończona - Generated {len(clarifying_questions)} questions")
            return updated_profile, clarifying_questions
            
        except Exception as e:
            logger.error(f"❌ Błąd w dual-stage analysis: {e}")
            return self._create_psychology_error_fallback(str(e)), []
    
    async def generate_customer_archetype(
        self,
        psychology_profile: Dict[str, Any],
        interaction_patterns: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generuje archetyp klienta na podstawie profilu psychologicznego
        
        Args:
            psychology_profile: Profil psychometryczny (Big Five + DISC + Schwartz)
            interaction_patterns: Wzorce interakcji (opcjonalne)
            
        Returns:
            Dict: Customer archetype z strategiami sprzedażowymi
        """
        try:
            logger.info("🎭 Generuję archetyp klienta...")
            
            # Analiza dominujących cech
            archetype_data = self._analyze_dominant_traits(psychology_profile)
            
            # Określ główny archetyp
            primary_archetype = self._determine_primary_archetype(archetype_data)
            
            # Wygeneruj strategie sprzedażowe
            sales_strategies = self._generate_archetype_strategies(primary_archetype, psychology_profile)
            
            # Stwórz pełny profil archetypu
            customer_archetype = {
                'archetype_name': primary_archetype['name'],
                'archetype_description': primary_archetype['description'],
                'confidence_score': archetype_data['confidence'],
                'dominant_traits': archetype_data['dominant_traits'],
                'sales_strategies': sales_strategies,
                'communication_style': primary_archetype['communication_preferences'],
                'motivators': primary_archetype['key_motivators'],
                'red_flags': primary_archetype['potential_objections'],
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Archetyp wygenerowany: {primary_archetype['name']}")
            return customer_archetype
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas generowania archetypu: {e}")
            return self._create_archetype_fallback()
    
    def _format_conversation_for_analysis(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Formatuje historię rozmowy dla analizy psychometrycznej"""
        if not conversation_history:
            return ""
        
        formatted_parts = []
        for idx, interaction in enumerate(conversation_history, 1):
            user_input = interaction.get('user_input', '').strip()
            if user_input:
                formatted_parts.append(f"[{idx}] KLIENT: {user_input}")
        
        return "\n".join(formatted_parts)
    
    def _parse_psychology_response(self, llm_response: str) -> Dict[str, Any]:
        """Parsuje odpowiedź LLM i zwraca strukturyzowany profil psychologiczny"""
        try:
            # Znajdź JSON w odpowiedzi
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("⚠️ Brak JSON w odpowiedzi LLM")
                return self._create_minimal_psychology_fallback()
            
            json_str = llm_response[json_start:json_end]
            psychology_data = json.loads(json_str)
            
            # Walidacja struktury
            required_keys = ['big_five', 'disc', 'schwartz_values']
            if not all(key in psychology_data for key in required_keys):
                logger.warning("⚠️ Niekompletna struktura psychology JSON")
                return self._create_minimal_psychology_fallback()
            
            return psychology_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Błąd parsowania JSON psychology: {e}")
            return self._create_minimal_psychology_fallback()
        except Exception as e:
            logger.error(f"❌ Nieoczekiwany błąd parsowania psychology: {e}")
            return self._create_minimal_psychology_fallback()
    
    def _calculate_psychology_confidence(self, psychology_profile: Dict[str, Any]) -> int:
        """Oblicza poziom pewności analizy psychometrycznej na podstawie kompletności danych"""
        try:
            confidence_factors = []
            
            # Big Five completeness
            big_five = psychology_profile.get('big_five', {})
            if big_five:
                big_five_scores = [trait.get('score', 0) for trait in big_five.values()]
                big_five_rationales = [bool(trait.get('rationale', '').strip()) for trait in big_five.values()]
                
                confidence_factors.append(len([s for s in big_five_scores if s > 0]) / 5.0)  # Score completeness
                confidence_factors.append(sum(big_five_rationales) / 5.0)  # Rationale completeness
            
            # DISC completeness  
            disc = psychology_profile.get('disc', {})
            if disc:
                disc_scores = [trait.get('score', 0) for trait in disc.values()]
                disc_rationales = [bool(trait.get('rationale', '').strip()) for trait in disc.values()]
                
                confidence_factors.append(len([s for s in disc_scores if s > 0]) / 4.0)
                confidence_factors.append(sum(disc_rationales) / 4.0)
            
            # Schwartz Values presence
            schwartz = psychology_profile.get('schwartz_values', [])
            if schwartz:
                present_values = len([v for v in schwartz if v.get('is_present', False)])
                confidence_factors.append(min(present_values / 3.0, 1.0))  # At least 3 values identified
            
            # Oblicz średnią confidence
            if confidence_factors:
                avg_confidence = sum(confidence_factors) / len(confidence_factors)
                return max(int(avg_confidence * 100), 10)  # Minimum 10%
            else:
                return 10
                
        except Exception as e:
            logger.error(f"❌ Błąd obliczania confidence: {e}")
            return 10
    
    def _create_minimal_psychology_fallback(self) -> Dict[str, Any]:
        """Tworzy minimalny fallback profil psychologiczny"""
        return {
            "big_five": {
                "openness": {"score": 5, "rationale": "Brak wystarczających danych", "strategy": "Zbieraj więcej informacji o preferencjach"},
                "conscientiousness": {"score": 5, "rationale": "Brak wystarczających danych", "strategy": "Przedstaw systematyczne korzyści"},
                "extraversion": {"score": 5, "rationale": "Brak wystarczających danych", "strategy": "Dostosuj styl komunikacji"},
                "agreeableness": {"score": 5, "rationale": "Brak wystarczających danych", "strategy": "Buduj relacje ostrożnie"},
                "neuroticism": {"score": 5, "rationale": "Brak wystarczących danych", "strategy": "Zapewnij o bezpieczeństwie"}
            },
            "disc": {
                "dominance": {"score": 5, "rationale": "Brak wystarczających danych", "strategy": "Prezentuj fakty jasno"},
                "influence": {"score": 5, "rationale": "Brak wystarczających danych", "strategy": "Używaj storytelling"},
                "steadiness": {"score": 5, "rationale": "Brak wystarczających danych", "strategy": "Zapewnij stabilność"},
                "compliance": {"score": 5, "rationale": "Brak wystarczających danych", "strategy": "Dostarczaj dowody"}
            },
            "schwartz_values": [
                {"value_name": "Bezpieczeństwo", "is_present": True, "rationale": "Uniwersalna wartość", "strategy": "Podkreśl bezpieczeństwo Tesla"}
            ],
            "confidence": 10,
            "is_fallback": True,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _create_psychology_error_fallback(self, error_message: str) -> Dict[str, Any]:
        """Tworzy fallback w przypadku błędu"""
        fallback = self._create_minimal_psychology_fallback()
        fallback.update({
            'error_occurred': True,
            'error_message': error_message,
            'confidence': 5
        })
        return fallback
    
    def _create_archetype_fallback(self) -> Dict[str, Any]:
        """Tworzy fallback archetyp klienta"""
        return {
            'archetype_name': 'Niezdecydowany Odkrywca',
            'archetype_description': 'Klient w fazie zbierania informacji',
            'confidence_score': 10,
            'dominant_traits': ['Ostrożność', 'Analityczność'],
            'sales_strategies': ['Dostarczaj fakty', 'Buduj zaufanie stopniowo'],
            'communication_style': 'Profesjonalny i cierpliwy',
            'motivators': ['Bezpieczeństwo', 'Wartość'],
            'red_flags': ['Presja czasowa', 'Niejasne korzyści'],
            'is_fallback': True,
            'generated_at': datetime.now().isoformat()
        }
    
    # Placeholder methods for future implementation
    async def _update_psychology_profile(self, user_input: str, session_context: Dict[str, Any], previous_psychology: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Aktualizuje profil psychologiczny - do implementacji"""
        return previous_psychology or self._create_minimal_psychology_fallback()
    
    async def _generate_clarifying_questions(self, psychology_profile: Dict[str, Any], user_input: str) -> List[Dict[str, Any]]:
        """Generuje pytania pomocnicze - do implementacji"""
        return []
    
    def _analyze_dominant_traits(self, psychology_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analizuje dominujące cechy - do implementacji"""
        return {'confidence': 50, 'dominant_traits': ['Analityczność']}
    
    def _determine_primary_archetype(self, archetype_data: Dict[str, Any]) -> Dict[str, Any]:
        """Określa główny archetyp - do implementacji"""  
        return {
            'name': 'Niezdecydowany Odkrywca',
            'description': 'Klient zbierający informacje',
            'communication_preferences': 'Profesjonalny',
            'key_motivators': ['Bezpieczeństwo'],
            'potential_objections': ['Cena']
        }
    
    def _generate_archetype_strategies(self, archetype: Dict[str, Any], psychology_profile: Dict[str, Any]) -> List[str]:
        """Generuje strategie dla archetypu - do implementacji"""
        return ['Przedstaw fakty systematycznie', 'Buduj zaufanie stopniowo']
