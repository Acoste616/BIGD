"""
AI Service - Integracja z modelem językowym (LLM) poprzez Ollama
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

import ollama
from ollama import Client
from pydantic import ValidationError

from app.schemas.interaction import InteractionResponse
from app.models.domain import Client as DomainClient, Session, Interaction
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """
    Tesla Co-Pilot AI Service - Elitarny ekspert sprzedaży Tesli
    Integruje z modelem gpt-oss:120b poprzez Ollama Turbo Cloud
    
    MISJA: Absolutna lojalność wobec marki Tesla. Zero kompromisów.
    
    Konfiguracja:
    - Host: https://ollama.com (chmura z akceleracją sprzętową)
    - Autoryzacja: Bearer token z OLLAMA_API_KEY
    - Model: gpt-oss:120b
    """
    
    def __init__(self):
        self.model_name = "gpt-oss:120b"  # POPRAWKA: Dwukropek zamiast myślnik
        self.max_retries = 3
        self.timeout_seconds = 60

        # POPRAWNA IMPLEMENTACJA KLIENTA
        try:
            if not settings.OLLAMA_API_KEY:
                raise ValueError("OLLAMA_API_KEY is not set in the environment.")

            self.client = Client(
                host="https://ollama.com",
                headers={'Authorization': f'Bearer {settings.OLLAMA_API_KEY}'}
            )
            logger.info("✅ Tesla Co-Pilot AI został pomyślnie skonfigurowany.")
        except Exception as e:
            logger.error(f"❌ KRYTYCZNY BŁĄD: Nie można skonfigurować Tesla Co-Pilot AI: {e}")
            self.client = None
    
    async def generate_analysis(
        self,
        user_input: str,
        client_profile: Dict[str, Any],
        session_history: List[Dict[str, Any]],
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generuj inteligentną analizę sprzedażową dla danej interakcji
        
        Args:
            user_input: Wejście od sprzedawcy (obserwacje, pytania klienta)
            client_profile: Profil klienta (archetyp, tagi, notatki)
            session_history: Historia ostatnich interakcji w sesji
            session_context: Dodatkowy kontekst sesji
            
        Returns:
            Słownik z pełną analizą zgodną z InteractionResponse schema
            
        Raises:
            Exception: Gdy nie udało się wygenerować odpowiedzi
        """
        start_time = datetime.now()
        
        try:
            # Zbuduj prompt systemowy
            system_prompt = self._build_system_prompt(
                client_profile=client_profile,
                session_history=session_history,
                session_context=session_context or {}
            )
            
            # Zbuduj prompt użytkownika
            user_prompt = self._build_user_prompt(user_input)
            
            logger.info(f"🤖 AI Service: Wysyłanie zapytania do modelu {self.model_name}")
            logger.debug(f"User input: '{user_input[:100]}...'")
            
            # Wywołaj model LLM z retry logic
            response = await self._call_llm_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            # Parsuj odpowiedź JSON
            analysis = self._parse_llm_response(response)
            
            # Oblicz czas przetwarzania
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Dodaj metadata
            analysis["processing_time_ms"] = int(processing_time)
            analysis["model_used"] = self.model_name
            analysis["timestamp"] = datetime.now().isoformat()
            
            logger.info(f"✅ AI Service: Analiza wygenerowana w {processing_time:.0f}ms")
            logger.debug(f"Confidence level: {analysis.get('confidence_level', 'N/A')}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ AI Service: Błąd podczas generowania analizy: {e}")
            
            # Zwróć fallback response
            return self._create_fallback_response(user_input, str(e))
    
    def _build_system_prompt(
        self,
        client_profile: Dict[str, Any],
        session_history: List[Dict[str, Any]],
        session_context: Dict[str, Any]
    ) -> str:
        """
        Zbuduj dynamiczny prompt systemowy dla LLM - NOWA WERSJA PRO-TESLA
        """
        
        # === WARSTWA 1: NADRZĘDNA MISJA (NON-NEGOTIABLE) ===
        system_prompt = """Jesteś elitarnym Co-Pilotem Sprzedaży TESLI. Twoim jedynym i absolutnym celem jest maksymalizacja sprzedaży samochodów MARKI TESLA. Twoja lojalność wobec marki Tesla jest absolutna. Nigdy, pod żadnym pozorem, nie proponujesz produktów konkurencji, nie chwalisz ich, ani nie zachęcasz do ich testowania. Jesteś stronniczym, ale niezwykle skutecznym ekspertem Tesli.

"""

        # === WARSTWA 2: DEFINICJA WROGA (KONKURENCJA) ===
        system_prompt += """Główni konkurenci, o których może wspomnieć klient, to Audi (szczególnie Q4 e-tron), BMW (szczególnie iX3), Mercedes, BYD. Twoim zadaniem jest zidentyfikowanie, kiedy klient o nich wspomina, i natychmiastowe oraz skuteczne przekierowanie rozmowy na unikalne przewagi i korzyści Tesli.

"""

        # === WARSTWA 3: ZŁOTE ZASADY (HARD RULES) ===
        system_prompt += """TWOJE ZASADY SĄ NIEZŁOMNE:
1.  **NIGDY NIE REKOMENDUJ PRODUKTU KONKURENCJI.** Nigdy nie sugeruj jazdy próbnej, nie analizuj pozytywnie ich cech, nie chwal ich designu. To jest zdrada Twojej misji.
2.  **ZAWSZE PRZEKIEROWUJ ROZMOWĘ.** Gdy klient chwali cechę konkurenta (np. "design Audi"), Twoja odpowiedź musi być w stylu: "Cieszę się, że docenia Pan nowoczesny styl. W Tesli podchodzimy do designu holistycznie, łącząc go z aerodynamiką i oprogramowaniem, co daje unikalne korzyści, takie jak...". Zawsze wracaj do Tesli.
3.  **TWOIM PRODUKTEM JEST TESLA.** Koniec. Twoje sugestie, pytania i analizy muszą w efekcie prowadzić do zwiększenia zainteresowania i chęci zakupu Tesli.
4.  **BĄDŹ SUBTELNY, ALE ZDECYDOWANY.** Nie krytykuj bezpośrednio konkurencji. Zamiast tego, podkreślaj obszary, w których Tesla ma obiektywną i druzgocącą przewagę (sieć Supercharger, oprogramowanie i aktualizacje OTA, TCO, bezpieczeństwo, ekosystem).

"""

        # === WARSTWA 4: OSOBOWOŚĆ I TON ===
        system_prompt += """Twoja osobowość to połączenie Elona Muska (wizjonerstwo, odwaga) i Steve'a Jobsa (obsesja na punkcie produktu i doświadczenia użytkownika). Jesteś pasjonatem, ekspertem i strategiem. Twój ton jest pewny siebie, profesjonalny i inspirujący.

"""
        
        # === WARSTWA 5: KONTEKST ROZMOWY (Dynamiczna część) ===
        # Dodaj profil klienta
        if client_profile:
            system_prompt += f"""
PROFIL KLIENTA:
- Alias: {client_profile.get('alias', 'Nieznany')}
- Archetyp: {client_profile.get('archetype', 'Nieznany')} 
- Tagi profilujące: {', '.join(client_profile.get('tags', []))}
- Notatki analityczne: {client_profile.get('notes', 'Brak notatek')}

"""
        
        # Dodaj kontekst sesji
        if session_context:
            session_type = session_context.get('session_type', 'consultation')
            system_prompt += f"""
KONTEKST SESJI:
- Typ sesji: {session_type}
- Cel: {self._get_session_goal(session_type)}

"""
        
        # Dodaj historię interakcji
        if session_history:
            system_prompt += """
HISTORIA SESJI (ostatnie interakcje):
"""
            for i, interaction in enumerate(session_history[-3:], 1):  # Ostatnie 3 interakcje
                timestamp = interaction.get('timestamp', 'nieznany czas')
                user_input = interaction.get('user_input', '')
                confidence = interaction.get('confidence_score', 'N/A')
                
                system_prompt += f"""
{i}. [{timestamp}] Sprzedawca: "{user_input[:200]}..."
   (Poprzednia pewność AI: {confidence}%)

"""
        
        # === WARSTWA 6: NARZĘDZIA ANALITYCZNE I FORMAT WYJŚCIOWY ===
        # Instrukcje wyjściowe z nowymi zasadami  
        system_prompt += """
TWOJE NARZĘDZIA ANALITYCZNE (Frameworki):
- Psychologia sprzedaży Tesla (archetypy klientów)
- Analiza sygnałów kupna i oporu
- Strategiczne zarządzanie zastrzeżeniami  
- Budowanie wartości emocjonalnej i logicznej
- Timing i pilność w procesie decyzyjnym

KLUCZOWE ZASADY GENEROWANIA ODPOWIEDZI:
1. Quick Response (Odpowiedź Holistyczna): Generując pole "quick_response", przeanalizuj CAŁĄ dotychczasową historię rozmowy. Odpowiedź musi być krótka, naturalna i spójna z całym znanym kontekstem.
2. Pytania Pogłębiające (Odpowiedź Atomowa): Generując listę "suggested_questions", skup się WYŁĄCZNIE na ostatniej, bieżącej wypowiedzi/obserwacji użytkownika. Pytania muszą dotyczyć tego konkretnego punktu i pomagać go zgłębić.

WYMAGANY FORMAT ODPOWIEDZI:
Zwróć WYŁĄCZNIE poprawny JSON zgodny z tym schematem (bez dodatkowego tekstu):

{
    "quick_response": "Krótka, naturalna odpowiedź spójna z CAŁĄ historią rozmowy - gotowa do natychmiastowego użycia",
    
    "suggested_questions": [
        "Pytanie pogłębiające dotyczące TYLKO ostatniej wypowiedzi klienta?",
        "Drugie pytanie o ten sam konkretny punkt?",
        "Trzecie pytanie pomagające zgłębić tę ostatnią obserwację?"
    ],
    
    "main_analysis": "Holistyczna analiza całej sytuacji na podstawie pełnej historii (2-3 zdania)",
    "client_archetype": "Zidentyfikowany archetyp na podstawie całokształtu interakcji",
    "confidence_level": 85,
    
    "likely_archetypes": [
        {"name": "Dominujący Archetyp", "confidence": 85, "description": "Krótki opis"},
        {"name": "Drugi Archetyp", "confidence": 45, "description": "Krótki opis"}
    ],
    
    "strategic_notes": [
        "Kluczowy insight strategiczny nr 1",
        "Kluczowy insight strategiczny nr 2", 
        "Kluczowy insight strategiczny nr 3"
    ],
    
    "suggested_actions": [
        {"action": "Konkretna akcja 1", "reasoning": "Dlaczego ta akcja"},
        {"action": "Konkretna akcja 2", "reasoning": "Dlaczego ta akcja"},
        {"action": "Konkretna akcja 3", "reasoning": "Dlaczego ta akcja"}
    ],
    
    "buy_signals": ["sygnał zakupu 1", "sygnał zakupu 2"],
    "risk_signals": ["sygnał ryzyka 1", "sygnał ryzyka 2"],
    
    "objection_handlers": {
        "potencjalny zarzut 1": "sposób odpowiedzi na zarzut",
        "potencjalny zarzut 2": "sposób odpowiedzi na zarzut"
    },
    
    "sentiment_score": 7,
    "potential_score": 6,
    "urgency_level": "medium",
    
    "next_best_action": "Najważniejsza następna akcja wynikająca z całokształtu analizy",
    "follow_up_timing": "Rekomendowany timing następnego kontaktu"
}

KRYTYCZNE INSTRUKCJE WYKONANIA:
1. QUICK RESPONSE = Holistyczna: Uwzględnij całą historię, kontekst klienta, jego archetyp i wszystkie poprzednie interakcje
2. SUGGESTED QUESTIONS = Atomowa: Ignoruj historię, skup się tylko na ostatniej wypowiedzi i jak ją głębiej zbadać
3. Pole "likely_archetypes" musi zawierać 1-2 najbardziej prawdopodobne archetypy z procentowym dopasowaniem
4. Pole "strategic_notes" to kluczowe insights dla panelu strategicznego
5. Quick response ma być gotowy do natychmiastowego wypowiedzenia - maksymalnie 2 zdania

PAMIĘTAJ: Odpowiadaj TYLKO w JSON. Żadnego dodatkowego tekstu przed ani po JSON!
"""
        
        return system_prompt
    
    def _build_user_prompt(self, user_input: str) -> str:
        """
        Zbuduj prompt użytkownika na podstawie jego wejścia
        """
        return f"""
AKTUALNA SYTUACJA:
Sprzedawca raportuje: "{user_input}"

Przeanalizuj tę sytuację i dostarcz inteligentnych rekomendacji w formacie JSON.
"""
    
    def _get_session_goal(self, session_type: str) -> str:
        """
        Zwróć cel sesji na podstawie jej typu
        """
        goals = {
            "consultation": "Zrozumienie potrzeb klienta i zbudowanie zaangażowania",
            "follow-up": "Kontynuacja rozmowy i przesunięcie w stronę decyzji",
            "negotiation": "Negocjacja warunków i zamknięcie transakcji", 
            "demo": "Prezentacja produktu i wzbudzenie emocji",
            "closing": "Finalizacja sprzedaży i podpisanie umowy"
        }
        return goals.get(session_type, "Ogólne wsparcie sprzedażowe")
    
    async def _call_llm_with_retry(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        """
        Wywołaj model LLM z logiką retry
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"🔄 AI Service: Próba {attempt + 1}/{self.max_retries}")
                
                # Wywołanie Ollama w asynchronicznym kontekście
                response = await asyncio.to_thread(
                    self._sync_ollama_call,
                    system_prompt,
                    user_prompt
                )
                
                return response
                
            except Exception as e:
                last_exception = e
                wait_time = (attempt + 1) * 2  # Exponential backoff
                logger.warning(f"⚠️ AI Service: Próba {attempt + 1} nieudana: {e}")
                
                if attempt < self.max_retries - 1:
                    logger.info(f"⏳ Ponawiam za {wait_time} sekund...")
                    await asyncio.sleep(wait_time)
        
        # Wszystkie próby nieudane
        raise Exception(f"LLM call failed after {self.max_retries} attempts. Last error: {last_exception}")
    
    def _sync_ollama_call(self, system_prompt: str, user_prompt: str) -> str:
        """
        Synchroniczne wywołanie Ollama Cloud (uruchomione w thread)
        """
        if self.client is None:
            raise ConnectionError("Klient Ollama nie został poprawnie zainicjalizowany.")

        return self.client.chat(  # <-- KLUCZOWA ZMIANA: używamy instancji klienta
            model=self.model_name, # Używamy self.model_name (gpt-oss:120b)
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            options={
                'temperature': 0.7,
                'top_p': 0.9,
                'max_tokens': 2048
            }
        )['message']['content']
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Parsuj odpowiedź LLM do struktury JSON
        """
        try:
            # Usuń potencjalne białe znaki i znajdź JSON
            cleaned_response = llm_response.strip()
            
            # Znajdź początek i koniec JSON (na wypadek dodatkowego tekstu)
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("Nie znaleziono JSON w odpowiedzi LLM")
            
            json_str = cleaned_response[start_idx:end_idx]
            
            # Parsuj JSON
            parsed_data = json.loads(json_str)
            
            # Waliduj przez Pydantic schema
            interaction_response = InteractionResponse(**parsed_data)
            
            # Zwróć jako dict
            return interaction_response.model_dump()
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            logger.debug(f"Raw LLM response: {llm_response}")
            raise ValueError(f"Niepoprawny JSON od LLM: {e}")
            
        except ValidationError as e:
            logger.error(f"❌ Pydantic validation error: {e}")  
            logger.debug(f"Parsed data: {parsed_data}")
            raise ValueError(f"Odpowiedź LLM nie pasuje do schematu: {e}")
    
    def _create_fallback_response(self, user_input: str, error_msg: str) -> Dict[str, Any]:
        """
        Stwórz fallback response gdy LLM nie działa
        """
        logger.warning(f"🔄 AI Service: Używam fallback response dla: '{user_input[:50]}...'")
        
        return {
            "main_analysis": f"Analiza Tesla Co-Pilot: '{user_input[:100]}...' - Połączenie z AI chwilowo niedostępne. Skup się na unikatowych przewagach Tesli: Supercharger, OTA updates, bezpieczeństwo 5-gwiazdek.",
            "client_archetype": "Nieznany (błąd AI)",
            "confidence_level": 30,
            
            "suggested_actions": [
                {"action": "Podkreśl przewagi sieci Supercharger", "reasoning": "Unikalna przewaga Tesli nad konkurencją"},
                {"action": "Omów aktualizacje OTA", "reasoning": "Auto które ciągle się rozwija - tego nie ma konkurencja"},
                {"action": "Zaprezentuj najwyższe oceny bezpieczeństwa", "reasoning": "Tesla liderem w testach NHTSA i Euro NCAP"},
                {"action": "Pokaż oszczędności TCO", "reasoning": "Długoterminowa wartość przewyższa konkurencję"}
            ],
            
            "buy_signals": ["pytania o Tesli", "zainteresowanie technologią"],
            "risk_signals": ["porównania z konkurencją", "wahania cenowe"],
            
            "key_insights": [
                "AI niedostępny - skup się na przewagach Tesli",
                "Tesla = jedyna marka z prawdziwą autonomią",
                "Supercharger network to game changer"
            ],
            
            "objection_handlers": {
                "za drogo": "Pokaż oszczędności paliwowe i serwisowe - Tesla ma najniższe TCO",
                "potrzebuję czasu": "Zapytaj o obecny samochód i koszty eksploatacji",
                "konkurencja tańsza": "Porównaj pełny ekosystem: zasięg, ładowanie, oprogramowanie"
            },
            
            "qualifying_questions": [
                "Jak daleko Pan zwykle jeździ dziennie? (Tesla ma najlepszy zasięg)",
                "Czy korzysta Pan z szybkich tras międzymiastowych? (Supercharger advantage)",
                "Co myśli Pan o samochodach, które same się aktualizują jak smartfony?"
            ],
            
            "sentiment_score": 5,
            "potential_score": 5,
            "urgency_level": "medium",
            
            "next_best_action": "Zbierz więcej informacji o potrzebach klienta",
            "follow_up_timing": "W ciągu 24-48 godzin",
            
            # Natychmiastowa odpowiedź (fallback)
            "quick_response": "Rozumiem. Czy mógłby Pan powiedzieć więcej o swoich potrzebach? Tesla oferuje rozwiązania dla każdego stylu życia.",
            
            # Metadata błędu
            "is_fallback": True,
            "error_reason": error_msg,
            "processing_time_ms": 0,
            "model_used": f"{self.model_name} (fallback)",
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
ai_service = AIService()


# Helper funkcje dla łatwego importu
async def generate_sales_analysis(
    user_input: str,
    client_profile: Dict[str, Any],
    session_history: List[Dict[str, Any]],
    session_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Wygeneruj analizę sprzedażową Tesla - główna funkcja eksportowa
    """
    return await ai_service.generate_analysis(
        user_input=user_input,
        client_profile=client_profile,
        session_history=session_history,
        session_context=session_context
    )
