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
    Serwis AI dla generowania inteligentnych analiz sprzedażowych
    Integruje z modelem gpt-oss:120b poprzez Ollama Turbo Cloud
    
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
            logger.info("✅ Klient Ollama Turbo został pomyślnie skonfigurowany.")
        except Exception as e:
            logger.error(f"❌ KRYTYCZNY BŁĄD: Nie można skonfigurować klienta Ollama Turbo: {e}")
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
        Zbuduj dynamiczny prompt systemowy dla LLM
        """
        # Podstawowy kontekst roli
        system_prompt = """Jesteś EKSPERTEM SPRZEDAŻY SAMOCHODÓW ELEKTRYCZNYCH i doradcą AI dla sprzedawców Tesla.

Twoją misją jest analizowanie sytuacji sprzedażowej i dostarczanie PRECYZYJNYCH, PRAKTYCZNYCH rad, które pomogą sprzedawcy zamknąć transakcję.

INSTRUKCJE KLUCZOWE:
1. Analizuj psychologię klienta na podstawie jego archetypu
2. Identyfikuj sygnały kupna i sygnały ryzyka
3. Sugeruj KONKRETNE akcje, które sprzedawca może natychmiast podjąć
4. Przewiduj zastrzeżenia i przygotuj odpowiedzi
5. Oceń sentiment i potencjał na skali 1-10

"""
        
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
            "main_analysis": f"Analiza automatyczna: '{user_input[:100]}...' - Nie udało się połączyć z AI. Sprawdź sytuację według standardowych procedur.",
            "client_archetype": "Nieznany (błąd AI)",
            "confidence_level": 30,
            
            "suggested_actions": [
                {"action": "Zadawaj pytania otwarte", "reasoning": "Zbieraj więcej informacji"},
                {"action": "Słuchaj aktywnie", "reasoning": "Zrozum potrzeby klienta"},
                {"action": "Przedstaw korzyści", "reasoning": "Buduj wartość produktu"},
                {"action": "Zaproponuj następny krok", "reasoning": "Utrzymaj momentum"}
            ],
            
            "buy_signals": ["zainteresowanie", "pytania szczegółowe"],
            "risk_signals": ["wahanie", "brak zaangażowania"],
            
            "key_insights": [
                "AI niedostępny - użyj doświadczenia",
                "Skup się na budowaniu relacji",
                "Zadawaj pytania kwalifikujące"
            ],
            
            "objection_handlers": {
                "za drogo": "Pokaż wartość długoterminową",
                "potrzebuję czasu": "Zapytaj o konkretne obawy"
            },
            
            "qualifying_questions": [
                "Co jest dla Pana najważniejsze w nowym samochodzie?",
                "Jaki jest Pana budżet?",
                "Kiedy planuje Pan podjąć decyzję?"
            ],
            
            "sentiment_score": 5,
            "potential_score": 5,
            "urgency_level": "medium",
            
            "next_best_action": "Zbierz więcej informacji o potrzebach klienta",
            "follow_up_timing": "W ciągu 24-48 godzin",
            
            # Natychmiastowa odpowiedź (fallback)
            "quick_response": "Rozumiem. Opowiedz mi więcej o swoich potrzebach.",
            
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
    Wygeneruj analizę sprzedażową - główna funkcja eksportowa
    """
    return await ai_service.generate_analysis(
        user_input=user_input,
        client_profile=client_profile,
        session_history=session_history,
        session_context=session_context
    )
