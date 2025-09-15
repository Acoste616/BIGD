"""SemanticValidatorService - Walidacja semantyczna i logiczna odpowiedzi AI

Odpowiedzialny za:
- Walidację spójności profili psychometrycznych
- Sprawdzanie logiczności porad komunikacyjnych
- Wykrywanie halucynacji i niespójności w danych AI
- Zabezpieczenie przed zapisem niepoprawnych analiz
"""
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SemanticValidatorService:
    """
    Serwis odpowiedzialny za walidację semantyczną i logiczną
    odpowiedzi generowanych przez AI.
    
    Funkcjonalności:
    - Walidacja spójności profili DISC
    - Sprawdzanie kompletności kluczowych pól
    - Walidacja logiczności porad komunikacyjnych
    - Wykrywanie halucynacji w analizach
    """
    
    def __init__(self):
        # W przyszłości ten serwis może potrzebować dostępu do bazy
        # lub innych zasobów, ale na razie jest bezstanowy.
        logger.info("✅ SemanticValidatorService initialized")
        
        # Mapowanie profili DISC na oczekiwane słowa kluczowe w poradach
        self.disc_keywords = {
            'D': ['wynik', 'cel', 'rezultat', 'efekt', 'osiągnięcie', 'sukces', 'bezpośredni', 'szybki', 'decyzyjny'],
            'I': ['ludzie', 'relacje', 'entuzjazm', 'motywacja', 'inspiracja', 'towarzyski', 'pozytywny', 'energia'],
            'S': ['stabilność', 'bezpieczeństwo', 'cierpliwość', 'wsparcie', 'zespół', 'współpraca', 'spokój', 'metodyczny'],
            'C': ['dane', 'fakty', 'analiza', 'szczegóły', 'precyzja', 'jakość', 'dokładność', 'systematyczny']
        }
        
        # Wymagane pola w różnych typach analiz
        self.required_fields = {
            'holistic_synthesis': [
                'holistic_summary',
                'main_drive',
                'communication_style',
                'key_levers',
                'red_flags'
            ],
            'archetype_analysis': [
                'primary_archetype',
                'confidence'
            ],
            'disc_profile': [
                'dominant_factor',
                'communication_style_advice'
            ]
        }
    
    def validate_holistic_synthesis(self, analysis_data: dict) -> Tuple[bool, str]:
        """
        Waliduje spójność w holistycznej syntezie psychometrycznej.
        
        Args:
            analysis_data: Dane analizy holistycznej do walidacji
            
        Returns:
            Tuple[bool, str]: (isValid, errorMessage)
        """
        try:
            logger.info("🔍 Rozpoczynam walidację semantyczną holistycznej syntezy...")
            
            # Walidacja 1: Sprawdzenie obecności kluczowych pól
            validation_result = self._validate_required_fields(
                analysis_data, 
                self.required_fields['holistic_synthesis'],
                'holistic_synthesis'
            )
            if not validation_result[0]:
                return validation_result
            
            # Walidacja 2: Spójność profilu DISC (jeśli dostępny)
            if 'disc_profile' in analysis_data:
                disc_validation = self._validate_disc_consistency(analysis_data['disc_profile'])
                if not disc_validation[0]:
                    return disc_validation
            
            # Walidacja 3: Spójność archetypu (jeśli dostępny)
            if 'archetype_analysis' in analysis_data:
                archetype_validation = self._validate_archetype_analysis(analysis_data['archetype_analysis'])
                if not archetype_validation[0]:
                    return archetype_validation
            
            # Walidacja 4: Logiczność key_levers i red_flags
            levers_validation = self._validate_strategic_elements(analysis_data)
            if not levers_validation[0]:
                return levers_validation
            
            # Walidacja 5: Sprawdzenie confidence score
            confidence_validation = self._validate_confidence_score(analysis_data)
            if not confidence_validation[0]:
                return confidence_validation
            
            logger.info("✅ Walidacja semantyczna przeszła pomyślnie")
            return True, ""
            
        except Exception as e:
            error_msg = f"Błąd podczas walidacji semantycznej: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def _validate_required_fields(self, data: dict, required_fields: List[str], context: str) -> Tuple[bool, str]:
        """
        Sprawdza obecność wymaganych pól w analizie.
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Brak wymaganych pól w {context}: {', '.join(missing_fields)}"
            logger.warning(f"⚠️ {error_msg}")
            return False, error_msg
        
        return True, ""
    
    def _validate_disc_consistency(self, disc_profile: dict) -> Tuple[bool, str]:
        """
        Waliduje spójność profilu DISC z poradami komunikacyjnymi.
        """
        dominant_factor = disc_profile.get("dominant_factor")
        advice = disc_profile.get("communication_style_advice", "").lower()
        
        if not dominant_factor or not advice:
            return False, "Brak kluczowych danych w profilu DISC"
        
        # Sprawdź czy porada zawiera odpowiednie słowa kluczowe dla danego profilu
        expected_keywords = self.disc_keywords.get(dominant_factor, [])
        
        if expected_keywords:
            found_keywords = [keyword for keyword in expected_keywords if keyword in advice]
            
            if not found_keywords:
                error_msg = f"Porada dla profilu DISC '{dominant_factor}' nie zawiera oczekiwanych słów kluczowych: {expected_keywords[:3]}"
                logger.warning(f"⚠️ {error_msg}")
                return False, error_msg
        
        # Specyficzne walidacje dla każdego typu DISC
        if dominant_factor == "D" and not any(word in advice for word in ['wynik', 'cel', 'rezultat', 'bezpośredni']):
            return False, "Porada dla profilu 'D' nie skupia się na wynikach i bezpośredniości."
        
        if dominant_factor == "I" and not any(word in advice for word in ['ludzie', 'relacje', 'entuzjazm', 'motywacja']):
            return False, "Porada dla profilu 'I' nie skupia się na relacjach i motywacji."
        
        if dominant_factor == "S" and not any(word in advice for word in ['stabilność', 'wsparcie', 'cierpliwość', 'zespół']):
            return False, "Porada dla profilu 'S' nie skupia się na stabilności i wsparciu."
        
        if dominant_factor == "C" and not any(word in advice for word in ['dane', 'fakty', 'analiza', 'szczegóły']):
            return False, "Porada dla profilu 'C' nie skupia się na danych i faktach."
        
        return True, ""
    
    def _validate_archetype_analysis(self, archetype_analysis: dict) -> Tuple[bool, str]:
        """
        Waliduje analizę archetypu klienta.
        """
        primary_archetype = archetype_analysis.get("primary_archetype")
        
        if not primary_archetype or len(primary_archetype.strip()) < 3:
            return False, "Brak lub niepoprawny 'primary_archetype' w analizie archetypu."
        
        # Sprawdź czy confidence jest w rozsądnym zakresie
        confidence = archetype_analysis.get("confidence")
        if confidence is not None:
            try:
                conf_value = float(confidence)
                if conf_value < 0 or conf_value > 100:
                    return False, f"Confidence archetypu poza zakresem 0-100: {conf_value}"
            except (ValueError, TypeError):
                return False, f"Niepoprawny format confidence archetypu: {confidence}"
        
        return True, ""
    
    def _validate_strategic_elements(self, analysis_data: dict) -> Tuple[bool, str]:
        """
        Waliduje logiczność elementów strategicznych (key_levers, red_flags).
        """
        key_levers = analysis_data.get('key_levers', [])
        red_flags = analysis_data.get('red_flags', [])
        
        # Sprawdź czy key_levers nie są puste i mają sens
        if isinstance(key_levers, list):
            for i, lever in enumerate(key_levers):
                if not isinstance(lever, str) or len(lever.strip()) < 5:
                    return False, f"Key lever #{i+1} jest zbyt krótki lub niepoprawny: '{lever}'"
        
        # Sprawdź czy red_flags nie są puste i mają sens
        if isinstance(red_flags, list):
            for i, flag in enumerate(red_flags):
                if not isinstance(flag, str) or len(flag.strip()) < 5:
                    return False, f"Red flag #{i+1} jest zbyt krótki lub niepoprawny: '{flag}'"
        
        # Sprawdź czy nie ma duplikatów między key_levers a red_flags
        if key_levers and red_flags:
            levers_lower = [lever.lower() for lever in key_levers if isinstance(lever, str)]
            flags_lower = [flag.lower() for flag in red_flags if isinstance(flag, str)]
            
            for lever in levers_lower:
                for flag in flags_lower:
                    # Sprawdź podobieństwo (proste sprawdzenie)
                    if len(lever) > 10 and len(flag) > 10 and lever in flag:
                        return False, f"Wykryto podobieństwo między key_lever i red_flag: '{lever}' vs '{flag}'"
        
        return True, ""
    
    def _validate_confidence_score(self, analysis_data: dict) -> Tuple[bool, str]:
        """
        Waliduje poprawność confidence score.
        """
        confidence = analysis_data.get('confidence')
        
        if confidence is not None:
            try:
                conf_value = float(confidence)
                if conf_value < 0 or conf_value > 100:
                    return False, f"Confidence score poza zakresem 0-100: {conf_value}"
                
                # Sprawdź czy confidence nie jest podejrzanie wysoki przy małej ilości danych
                if conf_value > 90:
                    # Można dodać dodatkowe sprawdzenia, np. czy analiza ma wystarczająco danych
                    holistic_summary = analysis_data.get('holistic_summary', '')
                    if len(holistic_summary) < 50:
                        return False, f"Confidence {conf_value}% zbyt wysoki dla krótkiej analizy"
                
            except (ValueError, TypeError):
                return False, f"Niepoprawny format confidence score: {confidence}"
        
        return True, ""
    
    def validate_sales_strategy(self, strategy_data: dict) -> Tuple[bool, str]:
        """
        Waliduje strategię sprzedażową (do implementacji w przyszłości).
        
        Args:
            strategy_data: Dane strategii sprzedażowej
            
        Returns:
            Tuple[bool, str]: (isValid, errorMessage)
        """
        # Placeholder dla przyszłej implementacji
        logger.info("🔍 Walidacja strategii sprzedażowej - w trakcie implementacji")
        return True, ""
    
    def validate_psychology_profile(self, psychology_data: dict) -> Tuple[bool, str]:
        """
        Waliduje profil psychometryczny (Big Five, DISC, Schwartz).
        
        Args:
            psychology_data: Dane profilu psychometrycznego
            
        Returns:
            Tuple[bool, str]: (isValid, errorMessage)
        """
        try:
            logger.info("🔍 Rozpoczynam walidację profilu psychometrycznego...")
            
            # Walidacja Big Five
            if 'big_five' in psychology_data:
                big_five_validation = self._validate_big_five(psychology_data['big_five'])
                if not big_five_validation[0]:
                    return big_five_validation
            
            # Walidacja DISC
            if 'disc' in psychology_data:
                disc_validation = self._validate_disc_scores(psychology_data['disc'])
                if not disc_validation[0]:
                    return disc_validation
            
            # Walidacja Schwartz Values
            if 'schwartz_values' in psychology_data:
                schwartz_validation = self._validate_schwartz_values(psychology_data['schwartz_values'])
                if not schwartz_validation[0]:
                    return schwartz_validation
            
            logger.info("✅ Walidacja profilu psychometrycznego przeszła pomyślnie")
            return True, ""
            
        except Exception as e:
            error_msg = f"Błąd podczas walidacji profilu psychometrycznego: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def _validate_big_five(self, big_five_data: dict) -> Tuple[bool, str]:
        """
        Waliduje dane Big Five.
        """
        required_traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in required_traits:
            if trait not in big_five_data:
                return False, f"Brak cechy Big Five: {trait}"
            
            trait_data = big_five_data[trait]
            if not isinstance(trait_data, dict):
                return False, f"Niepoprawny format danych dla cechy {trait}"
            
            # Sprawdź score
            score = trait_data.get('score')
            if score is None or not isinstance(score, (int, float)) or score < 0 or score > 10:
                return False, f"Niepoprawny score dla cechy {trait}: {score}"
            
            # Sprawdź rationale
            rationale = trait_data.get('rationale', '')
            if not rationale or len(rationale.strip()) < 10:
                return False, f"Zbyt krótkie lub brakujące uzasadnienie dla cechy {trait}"
        
        return True, ""
    
    def _validate_disc_scores(self, disc_data: dict) -> Tuple[bool, str]:
        """
        Waliduje dane DISC.
        """
        required_factors = ['dominance', 'influence', 'steadiness', 'compliance']
        
        for factor in required_factors:
            if factor not in disc_data:
                return False, f"Brak czynnika DISC: {factor}"
            
            factor_data = disc_data[factor]
            if not isinstance(factor_data, dict):
                return False, f"Niepoprawny format danych dla czynnika {factor}"
            
            # Sprawdź score
            score = factor_data.get('score')
            if score is None or not isinstance(score, (int, float)) or score < 0 or score > 10:
                return False, f"Niepoprawny score dla czynnika DISC {factor}: {score}"
        
        return True, ""
    
    def _validate_schwartz_values(self, schwartz_data: list) -> Tuple[bool, str]:
        """
        Waliduje wartości Schwartza.
        """
        if not isinstance(schwartz_data, list):
            return False, "Schwartz values muszą być listą"
        
        expected_values = [
            'Bezpieczeństwo', 'Władza', 'Osiągnięcia', 'Hedonizm', 'Stymulacja',
            'Samostanowienie', 'Uniwersalizm', 'Życzliwość', 'Tradycja', 'Przystosowanie'
        ]
        
        for item in schwartz_data:
            if not isinstance(item, dict):
                return False, "Każda wartość Schwartza musi być obiektem"
            
            value_name = item.get('value_name')
            if not value_name or value_name not in expected_values:
                return False, f"Niepoprawna nazwa wartości Schwartza: {value_name}"
            
            is_present = item.get('is_present')
            if not isinstance(is_present, bool):
                return False, f"Pole 'is_present' musi być boolean dla wartości {value_name}"
        
        return True, ""