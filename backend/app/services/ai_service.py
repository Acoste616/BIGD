"""
AI Service - Integracja z modelem językowym (LLM) poprzez Ollama
"""
import json
import asyncio
import uuid
from typing import Dict, List, Any, Optional, cast
from datetime import datetime
import logging

import ollama
from app.core.config import settings

# --- POCZĄTEK ZMIAN ---

# Dynamiczne tworzenie nagłówków do autoryzacji w Ollama Turbo
headers = {}
if settings.OLLAMA_API_KEY:
    headers['Authorization'] = f'Bearer {settings.OLLAMA_API_KEY}'

# Inicjalizacja klienta z hostem i nagłówkami
client = ollama.Client(
    host=settings.OLLAMA_API_URL,
    headers=headers
)

# --- KONIEC ZMIAN ---

from ollama import Client
from pydantic import ValidationError

from app.schemas.interaction import InteractionResponse
from app.models.domain import Client as DomainClient, Session, Interaction
from .qdrant_service import QdrantService

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
    
    def __init__(self, qdrant_service: QdrantService):
        """
        Inicjalizacja AI Service z integracją bazy wiedzy (RAG)
        
        Args:
            qdrant_service: Instancja serwisu Qdrant do pobierania wiedzy kontekstowej
        """
        self.qdrant_service = qdrant_service
        self.model_name = settings.OLLAMA_MODEL  # Używamy konfiguracji z settings
        self.max_retries = 3
        self.timeout_seconds = 60

        # Użyj globalnego klienta zainicjalizowanego na poziomie modułu
        self.client = client
        logger.info("✅ Tesla Co-Pilot AI został pomyślnie skonfigurowany z integracją RAG.")
    
    def _generate_unique_suggestion_ids(self) -> Dict[str, str]:
        """
        Generuje unikalne ID dla sugestii zgodnie z Blueprint Feedback Loop
        """
        return {
            "quick_response_id": f"qr_{uuid.uuid4().hex[:6]}",
            "sq_1_id": f"sq_{uuid.uuid4().hex[:6]}",
            "sq_2_id": f"sq_{uuid.uuid4().hex[:6]}",
            "sq_3_id": f"sq_{uuid.uuid4().hex[:6]}"
        }

    async def generate_analysis(
        self,
        user_input: str,
        client_profile: Dict[str, Any],
        session_history: List[Dict[str, Any]],
        session_context: Optional[Dict[str, Any]] = None,
        mode: str = 'suggestion'
    ) -> Dict[str, Any]:
        """
        Generuj inteligentną analizę sprzedażową dla danej interakcji
        
        Args:
            user_input: Wejście od sprzedawcy (obserwacje, pytania klienta)
            client_profile: Profil klienta (archetyp, tagi, notatki)
            session_history: Historia ostatnich interakcji w sesji
            session_context: Dodatkowy kontekst sesji
            mode: Tryb działania ('suggestion' dla sprzedaży, 'training' dla AI Dojo)
            
        Returns:
            Słownik z pełną analizą zgodną z InteractionResponse schema (suggestion mode)
            lub odpowiedź AI Dojo (training mode)
            
        Raises:
            Exception: Gdy nie udało się wygenerować odpowiedzi
        """
        # === AI DOJO: ROZGAŁĘZIENIE LOGIKI ===
        if mode == 'training':
            # Tryb treningowy AI Dojo - zupełnie oddzielna logika
            return await self._handle_training_conversation(
                user_input=user_input,
                client_profile=client_profile,
                session_history=session_history,
                session_context=session_context
            )
        
        # === ISTNIEJĄCA LOGIKA SPRZEDAŻOWA (mode='suggestion') ===
        # UWAGA: Poniższy kod nie został zmodyfikowany - działa dokładnie tak samo!
        start_time = datetime.now()
        
        try:
            # === POCZĄTEK NOWEJ LOGIKI RAG ===
            logger.info("🔍 RAG: Rozpoczynam pobieranie wiedzy kontekstowej z Qdrant")
            
            # Krok 1: Pobierz relevantną wiedzę z Qdrant
            relevant_knowledge = []
            try:
                client_archetype = client_profile.get("archetype")
                relevant_knowledge = await asyncio.to_thread(
                    self.qdrant_service.search_knowledge,
                    query=user_input,
                    archetype=client_archetype,  # type: ignore
                    limit=3  # Pobieramy 3 najbardziej trafne wyniki
                )
                logger.info(f"✅ RAG: Znaleziono {len(relevant_knowledge)} relevantnych wskazówek")
                
                # Loguj trafność wyników
                for i, nugget in enumerate(relevant_knowledge):
                    score = nugget.get('score', 0)
                    title = nugget.get('title', 'Bez tytułu')[:50]
                    logger.debug(f"  #{i+1}: {title}... (score: {score:.3f})")
                    
            except Exception as e:
                # W razie błędu Qdrant, kontynuujemy bez dodatkowej wiedzy
                logger.warning(f"⚠️ RAG: Błąd podczas wyszukiwania w Qdrant: {e}")
                relevant_knowledge = []

            # Krok 2: Sformatuj pobraną wiedzę do czytelnej formy dla LLM
            knowledge_context = "BRAK DODATKOWEGO KONTEKSTU Z BAZY WIEDZY."
            if relevant_knowledge:
                formatted_nuggets = []
                for i, nugget in enumerate(relevant_knowledge):
                    title = nugget.get("title", "Brak tytułu")
                    content = nugget.get("content", "Brak treści")
                    score = nugget.get("score", 0)
                    knowledge_type = nugget.get("knowledge_type", "general")
                    
                    formatted_nuggets.append(
                        f"{i+1}. [{knowledge_type.upper()}] {title}\n"
                        f"   Treść: {content}\n"
                        f"   Trafność: {score:.1%}"
                    )
                
                knowledge_context = "\n---\n".join(formatted_nuggets)
                logger.info(f"📚 RAG: Kontekst wiedzy przygotowany ({len(knowledge_context)} znaków)")
                
            # === KONIEC NOWEJ LOGIKI RAG ===

            # Wygeneruj unikalne ID dla sugestii (Blueprint Feedback Loop)
            suggestion_ids = self._generate_unique_suggestion_ids()
            
            # Krok 3: Zbuduj wzbogacony prompt systemowy (z wiedzą z RAG)
            system_prompt = self._build_system_prompt(
                client_profile=client_profile,
                session_history=session_history,
                session_context=session_context or {},
                knowledge_context=knowledge_context,  # NOWY PARAMETR
                suggestion_ids=suggestion_ids  # ID dla granularnego feedback
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
        session_context: Dict[str, Any],
        knowledge_context: str = "BRAK DODATKOWEGO KONTEKSTU Z BAZY WIEDZY.",
        suggestion_ids: Optional[Dict[str, str]] = None
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

        # === WARSTWA 5: KONTEKST WIEDZY Z BAZY RAG (KLUCZOWE!) ===
        system_prompt += f"""
=== SPECJALISTYCZNA WIEDZA Z BAZY DANYCH ===
Na podstawie bieżącej sytuacji, oto najważniejsze informacje z naszej bazy wiedzy, które MUSISZ uwzględnić w swojej analizie i rekomendacjach:

{knowledge_context}

INSTRUKCJE DOTYCZĄCE WIEDZY:
- Wykorzystaj powyższe informacje do stworzenia precyzyjnych, merytorycznie uzasadnionych odpowiedzi
- Jeśli wiedza zawiera konkretne dane (np. limity podatkowe, programy dopłat), użyj ich w swoich argumentach
- Odwołuj się do tych informacji naturalnie, nie wspominając że pochodzą z "bazy danych"
- Traktuj tę wiedzę jako swoje własne, eksperckie kompetencje

"""
        
        # === WARSTWA 6: KONTEKST ROZMOWY (Dynamiczna część) ===
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
        
        # === WARSTWA 7: NARZĘDZIA ANALITYCZNE I FORMAT WYJŚCIOWY ===
        # Instrukcje wyjściowe z nowymi zasadami  
        system_prompt += """
TWOJE NARZĘDZIA ANALITYCZNE (Frameworki):
- Psychologia sprzedaży Tesla (archetypy klientów)
- Analiza sygnałów kupna i oporu
- Strategiczne zarządzanie zastrzeżeniami  
- Budowanie wartości emocjonalnej i logicznej
- Timing i pilność w procesie decyzyjnym

KLUCZOWE ZASADY GENEROWANIA ODPOWIEDZI:
1. Quick Response (Odpowiedź Holistyczna): Generując pole quick_response, przeanalizuj CAŁĄ dotychczasową historię rozmowy. Odpowiedź musi być krótka, naturalna i spójna z całym znanym kontekstem.
2. Pytania Pogłębiające (Odpowiedź Atomowa): Generując listę suggested_questions, skup się WYŁĄCZNIE na ostatniej, bieżącej wypowiedzi/obserwacji użytkownika. Pytania muszą dotyczyć tego konkretnego punktu i pomagać go zgłębić.

WYMAGANY FORMAT ODPOWIEDZI:
Zwróć WYŁĄCZNIE poprawny JSON zgodny z tym schematem (bez dodatkowego tekstu):

{
    "quick_response": {
        "id": "{quick_response_id}",
        "text": "Krótka, naturalna odpowiedź spójna z CAŁĄ historią rozmowy - gotowa do natychmiastowego użycia"
    },
    
    "suggested_questions": [
        {
            "id": "{sq_1_id}",
            "text": "Pytanie pogłębiające dotyczące TYLKO ostatniej wypowiedzi klienta?"
        },
        {
            "id": "{sq_2_id}",
            "text": "Drugie pytanie o ten sam konkretny punkt?"
        }
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
        
        # Zastąp placeholdery ID prawdziwymi wartościami (Blueprint Feedback Loop)
        if suggestion_ids:
            # Prostsze podejście - bezpośrednie zastąpienie bez .format()
            system_prompt = system_prompt.replace("{quick_response_id}", suggestion_ids["quick_response_id"])
            system_prompt = system_prompt.replace("{sq_1_id}", suggestion_ids["sq_1_id"])
            system_prompt = system_prompt.replace("{sq_2_id}", suggestion_ids["sq_2_id"])
        
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

        response = self.client.chat(
            model=self.model_name,  # Używamy settings.OLLAMA_MODEL (gpt-oss:120b)
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
        )
        
        # Ollama może zwrócić różne struktury odpowiedzi
        if isinstance(response, dict):
            if 'message' in response and 'content' in response['message']:
                return response['message']['content']
            elif 'content' in response:
                return response['content']
        elif isinstance(response, str):
            return response
            
        # Fallback - spróbuj przekonwertować na string
        return str(response)
    
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
        Stwórz fallback response gdy LLM nie działa (z unikalnymi ID dla Feedback Loop)
        """
        logger.warning(f"🔄 AI Service: Używam fallback response dla: '{user_input[:50]}...'")
        
        # Wygeneruj unikalne ID dla fallback sugestii
        fallback_ids = self._generate_unique_suggestion_ids()
        
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
            
            # Natychmiastowa odpowiedź (fallback z unikalnym ID)
            "quick_response": {
                "id": fallback_ids["quick_response_id"],
                "text": "Rozumiem. Czy mógłby Pan powiedzieć więcej o swoich potrzebach? Tesla oferuje rozwiązania dla każdego stylu życia."
            },
            
            # Sugerowane pytania (fallback z unikalnymi ID)
            "suggested_questions": [
                {
                    "id": fallback_ids["sq_1_id"],
                    "text": "Jakie są Pana główne priorytety przy wyborze samochodu?"
                },
                {
                    "id": fallback_ids["sq_2_id"],
                    "text": "Czy rozważał Pan wcześniej samochód elektryczny?"
                }
            ],
            
            # Metadata błędu
            "is_fallback": True,
            "error_reason": error_msg,
            "processing_time_ms": 0,
            "model_used": f"{self.model_name} (fallback)",
            "timestamp": datetime.now().isoformat()
        }

    # === AI DOJO: NOWE FUNKCJE TRENINGOWE ===
    
    async def _handle_training_conversation(
        self,
        user_input: str,
        client_profile: Dict[str, Any],
        session_history: List[Dict[str, Any]],
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Obsługa konwersacji treningowej w AI Dojo
        
        Tryb 'training': AI działa jak analityk wiedzy, zadaje pytania doprecyzowujące,
        strukturyzuje informacje i przygotowuje je do zapisu w bazie Qdrant
        
        Args:
            user_input: Wiadomość od eksperta/administratora
            client_profile: Profil klienta (jeśli trening dotyczy konkretnego przypadku)
            session_history: Historia konwersacji treningowej
            session_context: Kontekst treningu
            
        Returns:
            Dict zgodny z DojoMessageResponse (response, response_type, structured_data, etc.)
        """
        start_time = datetime.now()
        
        try:
            logger.info("🎓 AI Dojo: Rozpoczynam przetwarzanie wiadomości treningowej")
            logger.debug(f"Training input: '{user_input[:100]}...'")
            
            # Zbuduj specjalny prompt dla trybu treningowego
            training_prompt = self._build_training_system_prompt(
                client_profile=client_profile,
                session_history=session_history,
                session_context=session_context or {}
            )
            
            # Zbuduj user prompt dla treningu
            user_prompt = self._build_training_user_prompt(user_input)
            
            logger.info(f"🤖 AI Dojo: Wysyłanie do modelu {self.model_name} (tryb treningowy)")
            
            # Wywołaj LLM z retry logic (używamy tej samej funkcji co w trybie sprzedażowym)
            response = await self._call_llm_with_retry(
                system_prompt=training_prompt,
                user_prompt=user_prompt
            )
            
            # Parsuj odpowiedź AI Dojo (inna logika niż w trybie sprzedażowym)
            training_analysis = self._parse_training_response(response)
            
            # Oblicz czas przetwarzania
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Dodaj metadata
            training_analysis["processing_time_ms"] = int(processing_time)
            training_analysis["timestamp"] = datetime.now().isoformat()
            training_analysis["model_used"] = f"{self.model_name} (training mode)"
            
            logger.info(f"✅ AI Dojo: Analiza wygenerowana w {processing_time:.0f}ms")
            logger.debug(f"Response type: {training_analysis.get('response_type', 'unknown')}")
            
            return training_analysis
            
        except Exception as e:
            logger.error(f"❌ AI Dojo: Błąd podczas przetwarzania: {e}")
            
            # Fallback response dla AI Dojo
            return self._create_training_fallback_response(user_input, str(e))
    
    def _build_training_system_prompt(
        self,
        client_profile: Dict[str, Any],
        session_history: List[Dict[str, Any]],
        session_context: Dict[str, Any]
    ) -> str:
        """
        Zbuduj prompt systemowy dla AI Dojo (tryb treningowy)
        
        UWAGA: To jest zupełnie inny prompt niż w trybie sprzedażowym!
        """
        
        system_prompt = """Jesteś EKSPERTEM STRUKTURYZACJI WIEDZY dla systemu sprzedaży Tesla Co-Pilot AI.

=== TWOJA MISJA ===
Otrzymujesz informacje od ekspertów sprzedaży i SZYBKO przekształcasz je w użyteczną, strukturalną wiedzę dla systemu. Jesteś PROAKTYWNY i EFEKTYWNY.

=== ZŁOTE ZASADY (PRIORITY ORDER) ===

1. **NAJPIERW: Sprawdź czy masz WYSTARCZAJĄCE informacje do przygotowania wiedzy**
   - Jeśli tak → NATYCHMIAST przygotuj structured_data (response_type: "confirmation")
   - Jeśli nie → zadaj MAKSYMALNIE 1-2 konkretne pytania (response_type: "question")

2. **MINIMALIZUJ PYTANIA**: Nie zadawaj więcej niż 2 pytań. Po 2 pytaniach ZAWSZE przygotuj dane na podstawie tego co masz.

3. **AKCJA nad PERFEKCJĄ**: Lepiej przygotować niekompletną wiedzę niż pytać w nieskończoność.

=== KONTEKST TESLA & AUTOMATYCZNE UZUPEŁNIANIE ===

Gdy przygotowujesz wiedzę o sprzedaży Tesla, automatycznie uzupełnij braki:

**Dla pytań o CENĘ Tesla (przykład z user input):**
- Typ wiedzy: "objection" lub "pricing"
- Archetyp: null (uniwersalne, chyba że user wskaże konkretny)
- Tagi: ["cena", "finansowanie", "wartość", "roi"]
- Treść: Skoncentruj się na TCO, oszczędnościach, leasing, porównaniu z kosztami benzyny

**Dla pytań technicznych:**
- Typ wiedzy: "technical" lub "product"
- Tagi: ["specyfikacja", "porównanie", "funkcje"]

**Dla obsługi zastrzeżeń:**
- Typ wiedzy: "objection"
- Tagi: ["obiekcja", "odpowiedź", "persuasion"]

=== SMART DEFAULTS ===
Jeśli user nie podał wszystkich szczegółów, użyj inteligentnych domyślnych wartości:
- knowledge_type: Dedukuj z kontekstu (cena=pricing, zastrzeżenia=objection, funkcje=product)
- archetype: null (uniwersalne) chyba że jasno wskazano
- source: "Ekspert sprzedaży" lub nazwa z kontekstu
- tags: Automatycznie wygeneruj 3-5 relevantnych tagów

=== PRZYKŁADY NATYCHMIASTOWEGO STRUKTURYZOWANIA ===

**INPUT: "Jak najlepiej odpowiadać klientom pytającym o cenę Tesla?"**
→ NATYCHMIAST przygotuj structured_data z typem "objection", tagami ["cena", "finansowanie", "tco"] 

**INPUT: "Tesla Model Y ma nową opcję kolorystyczną"**
→ NATYCHMIAST przygotuj structured_data z typem "product", tagami ["model-y", "kolory", "opcje"]

**INPUT: "Klient mówi że zasięg to za mało"**
→ NATYCHMIAST przygotuj structured_data z typem "objection", tagami ["zasięg", "obiekcje", "range-anxiety"]

**TYLKO zadawaj pytania gdy:**
- Informacja jest bardzo ogólna ("pomoc", "problem")
- Brakuje kluczowych danych technicznych (konkretne liczby, modele)
- User pyta o coś co nie dotyczy sprzedaży Tesla

"""
        
        # Dodaj kontekst sesji treningowej
        if session_context:
            training_mode = session_context.get('training_mode', 'knowledge_update')
            system_prompt += f"""
=== TRYB TRENINGU ===
Aktualny tryb: {training_mode}
"""
            
        # Dodaj historię konwersacji treningowej
        if session_history:
            system_prompt += """
=== HISTORIA KONWERSACJI TRENINGOWEJ ===
"""
            for i, msg in enumerate(session_history[-5:], 1):  # Ostatnie 5 wiadomości
                timestamp = msg.get('timestamp', 'nieznany czas')
                content = msg.get('message', msg.get('user_input', ''))
                system_prompt += f"""
{i}. [{timestamp}] {content[:200]}...
"""
        
        # Instrukcje wyjściowe
        system_prompt += """
=== FORMAT ODPOWIEDZI ===
Odpowiadaj WYŁĄCZNIE w formacie JSON zgodnym z jednym z poniższych wzorców:

**TRYB PYTAŃ (gdy potrzebujesz więcej informacji):**
{
    "response": "Pytania doprecyzowujące lub prośba o więcej szczegółów",
    "response_type": "question",
    "confidence_level": 60,
    "suggested_follow_up": ["Pytanie 1?", "Pytanie 2?"]
}

**TRYB STRUKTURYZOWANIA (gdy przygotowujesz dane do zapisu):**
{
    "response": "Przygotowałem kompleksową wiedzę o odpowiadaniu na pytania o cenę Tesla. Czy zapisać w bazie?",
    "response_type": "confirmation", 
    "structured_data": {
        "title": "Skuteczne odpowiedzi na pytania o cenę Tesla",
        "content": "Strategia odpowiedzi na pytania cenowe: 1) Przekieruj na wartość (TCO, oszczędności paliwowe, serwis), 2) Pokaż kalkulator porównawczy z benzyną, 3) Zaproponuj opcje finansowania (leasing, kredyt), 4) Podkreśl unikalne korzyści (Supercharger, aktualizacje OTA, bezpieczeństwo), 5) Dostosuj do archetypu klienta.",
        "knowledge_type": "objection",
        "archetype": null,
        "tags": ["cena", "finansowanie", "tco", "wartość", "obiekcje"],
        "source": "Administrator"
    },
    "confidence_level": 90
}

**TRYB STATUS (potwierdzenia, błędy):**
{
    "response": "Informacja została zapisana/wystąpił błąd/inne",
    "response_type": "status",
    "confidence_level": 95
}

PAMIĘTAJ: Odpowiadaj TYLKO w JSON, bez dodatkowego tekstu!
"""
        
        return system_prompt
    
    def _build_training_user_prompt(self, user_input: str) -> str:
        """
        Zbuduj prompt użytkownika dla trybu treningowego
        """
        return f"""
WIADOMOŚĆ OD EKSPERTA:
"{user_input}"

Przeanalizuj tę informację i odpowiedz zgodnie z instrukcjami systemowymi.
"""
    
    def _parse_training_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Parsuj odpowiedź LLM w trybie treningowym
        
        Inna logika niż w trybie sprzedażowym - oczekujemy DojoMessageResponse format
        """
        try:
            # Usuń potencjalne białe znaki i znajdź JSON
            cleaned_response = llm_response.strip()
            
            # Znajdź początek i koniec JSON
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("Nie znaleziono JSON w odpowiedzi AI Dojo")
            
            json_str = cleaned_response[start_idx:end_idx]
            
            # Parsuj JSON
            parsed_data = json.loads(json_str)
            
            # Walidacja - sprawdź czy ma wymagane pola
            required_fields = ["response", "response_type"]
            for field in required_fields:
                if field not in parsed_data:
                    raise ValueError(f"Brakuje wymaganego pola: {field}")
            
            # Dodaj domyślne wartości jeśli brakuje
            if "confidence_level" not in parsed_data:
                parsed_data["confidence_level"] = 70
            
            logger.debug(f"AI Dojo response type: {parsed_data['response_type']}")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ AI Dojo JSON parsing error: {e}")
            logger.debug(f"Raw AI response: {llm_response}")
            raise ValueError(f"Niepoprawny JSON od AI Dojo: {e}")
            
        except Exception as e:
            logger.error(f"❌ AI Dojo response parsing error: {e}")
            raise ValueError(f"Błąd parsowania odpowiedzi AI Dojo: {e}")
    
    def _create_training_fallback_response(self, user_input: str, error_msg: str) -> Dict[str, Any]:
        """
        Stwórz fallback response dla AI Dojo gdy LLM nie działa
        """
        logger.warning(f"🔄 AI Dojo: Używam fallback response dla: '{user_input[:50]}...'")
        
        return {
            "response": f"Przepraszam, chwilowo nie mogę przetworzyć Twojej wiadomości: '{user_input[:100]}...'. Spróbuj ponownie za chwilę lub sformułuj pytanie inaczej.",
            "response_type": "error",
            "confidence_level": 0,
            "suggested_follow_up": [
                "Czy możesz przeformułować swoją wiadomość?",
                "Czy chcesz spróbować za chwilę?"
            ],
            "processing_time_ms": 0,
            "model_used": f"{self.model_name} (fallback)",
            "timestamp": datetime.now().isoformat(),
            "is_fallback": True,
            "error_reason": error_msg
        }


# Import Qdrant service for singleton creation
from .qdrant_service import qdrant_service

# Singleton instance z integracją RAG
ai_service = AIService(qdrant_service=qdrant_service)


# Helper funkcje dla łatwego importu
async def generate_sales_analysis(
    user_input: str,
    client_profile: Dict[str, Any],
    session_history: List[Dict[str, Any]],
    session_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Wygeneruj analizę sprzedażową Tesla - główna funkcja eksportowa z integracją RAG
    """
    return await ai_service.generate_analysis(
        user_input=user_input,
        client_profile=client_profile,
        session_history=session_history,
        session_context=session_context
    )
