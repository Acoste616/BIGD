"""
AI Service - Integracja z modelem językowym (LLM) poprzez Ollama
"""
import json
import asyncio
import uuid
import hashlib
import functools
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


# Prompt psychometryczny dla Modułu 2: Zintegrowana Analiza Psychometryczna
PSYCHOMETRIC_SYSTEM_PROMPT = """
Jesteś ekspertem w dziedzinie psychologii sprzedaży i lingwistyki. Twoim zadaniem jest przeanalizować poniższą transkrypcję rozmowy sprzedażowej i stworzyć szczegółowy profil psychometryczny klienta. Wynik przedstaw WYŁĄCZNIE jako JSON zgodny z podaną strukturą.

KROKI ANALIZY:

1. **Analiza Big Five:** Oceń klienta w 5 wymiarach osobowości (0-10). Dla każdej cechy podaj UZASADNIENIE (rationale) z cytatami z rozmowy oraz STRATEGIĘ sprzedażową dostosowaną do tej cechy.

2. **Analiza DISC:** Oceń dominujący styl zachowania klienta (0-10) w 4 wymiarach. Dla każdej cechy podaj UZASADNIENIE z przykładami oraz STRATEGIĘ sprzedażową.

3. **Analiza Wartości Schwartza:** Zidentyfikuj, które z kluczowych wartości (Bezpieczeństwo, Władza, Osiągnięcia, Hedonizm, Stymulacja, Samostanowienie, Uniwersalizm, Życzliwość, Tradycja, Przystosowanie) są obecne w wypowiedziach klienta. Dla każdej podaj UZASADNIENIE i STRATEGIĘ.

ENHANCED GUIDELINES - Precyzyjna Analiza:

BIG FIVE - Wskazówki Specyficzne:
- Openness (0-10): Czy klient pyta o nowe technologie, innowacje, funkcje przyszłości?
- Conscientiousness (0-10): Czy wymaga szczegółów, danych, planuje długoterminowo?
- Extraversion (0-10): Czy mówi o innych ludziach, statusie, wrażeniu na otoczenie?
- Agreeableness (0-10): Czy unika konfrontacji, szuka konsensusu, jest uprzejmy?
- Neuroticism (0-10): Czy wyraża obawy, stres, niepewność, potrzebę bezpieczeństwa?

DISC - Wskazówki Behawioralne:
- Dominance (0-10): Czy jest bezpośredni, decyzyjny, chce kontrolować proces?
- Influence (0-10): Czy jest towarzyski, perswazyjny, opowiada historie?
- Steadiness (0-10): Czy jest cierpliwy, lojalny, szuka stabilności?
- Compliance (0-10): Czy jest analityczny, systematyczny, potrzebuje dowodów?

SCHWARTZ VALUES - Kluczowe Motywatory:
- Bezpieczeństwo: Gwarancje, koszty, niezawodność
- Władza: Status, prestiż, kontrola, wpływ na innych
- Osiągnięcia: Sukces, kompetencje, wyniki, efektywność
- Hedonizm: Przyjemność, komfort, luksus
- Stymulacja: Nowość, wyzwania, ekscytacja
- Samostanowienie: Niezależność, autonomia, własne decyzje
- Uniwersalizm: Ekologia, dobro ogółu, sprawiedliwość
- Życzliwość: Troska o innych, relacje, współpraca
- Tradycja: Szacunek dla kultury, stabilne wartości
- Przystosowanie: Dopasowanie do norm, uprzejmość

STRUKTURA WYJŚCIOWA - zwróć WYŁĄCZNIE ten JSON:
{
  "big_five": {
    "openness": { "score": 7, "rationale": "Klient wypowiedział: '[cytat z rozmowy]', co wskazuje na...", "strategy": "Skoncentruj się na innowacyjnych cechach Tesla..." },
    "conscientiousness": { "score": 8, "rationale": "Z wypowiedzi '[cytat]' wynika...", "strategy": "Przedstaw szczegółowe dane o ROI i TCO..." },
    "extraversion": { "score": 6, "rationale": "...", "strategy": "..." },
    "agreeableness": { "score": 5, "rationale": "...", "strategy": "..." },
    "neuroticism": { "score": 4, "rationale": "...", "strategy": "..." }
  },
  "disc": {
    "dominance": { "score": 6, "rationale": "Klient wykazuje cechy dominacji przez...", "strategy": "Bądź bezpośredni, prezentuj fakty..." },
    "influence": { "score": 4, "rationale": "...", "strategy": "..." },
    "steadiness": { "score": 7, "rationale": "...", "strategy": "..." },
    "compliance": { "score": 8, "rationale": "...", "strategy": "..." }
  },
  "schwartz_values": [
    { "value_name": "Bezpieczeństwo", "is_present": true, "rationale": "Klient wyraził obawy o...", "strategy": "Podkreśl najwyższe oceny bezpieczeństwa Tesla..." },
    { "value_name": "Osiągnięcia", "is_present": false, "rationale": "Brak oznak zorientowania na sukces...", "strategy": "..." }
  ]
}

KLUCZOWE WYMAGANIA:
- Każde uzasadnienie MUSI zawierać konkretne cytaty z rozmowy
- Strategie muszą być praktyczne i gotowe do użycia przez sprzedawcę Tesla
- Oceny muszą być realistyczne i oparte na faktycznych dowodach z tekstu
- JSON musi być poprawnie sformatowany (bez komentarzy)

JEŚLI BRAK WYSTARCZAJĄCYCH DANYCH:
Jeśli rozmowa jest zbyt krótka lub nie zawiera wystarczających informacji do precyzyjnej analizy psychometrycznej, 
zamiast JSON zwróć:

{
  "insufficient_data": true,
  "probing_questions": [
    "Konkretne pytanie pomagające określić Big Five",
    "Pytanie o styl komunikacji (DISC)",
    "Pytanie o motywacje i wartości (Schwartz)"
  ],
  "analysis_confidence": "low",
  "suggestions": "Co sprzedawca powinien sprawdzić aby lepiej zrozumieć psychologię klienta"
}
"""

# Enhanced prompt dla Dwuetapowej Analizy Psychometrycznej
DUAL_STAGE_PSYCHOMETRIC_PROMPT = """
Jesteś ekspertem psychologii sprzedaży prowadzącym DWUETAPOWĄ ANALIZĘ klienta.

ETAP 1 - WSTĘPNA ANALIZA:
1. Przeanalizuj dostępny tekst pod kątem Big Five, DISC i Schwartz
2. Dla każdego wymiaru oblicz wstępną ocenę i PEWNOŚĆ tej oceny (0-100%)
3. Oblicz OGÓLNĄ PEWNOŚĆ całej analizy jako średnią ważoną

ETAP 2 - SAMOOCENA AI:
Zadaj sobie pytanie: "Czy na podstawie dostarczonych informacji mój poziom pewności 
co do określonego profilu psychometrycznego jest wystarczająco wysoki (≥75%)?"

JEŚLI PEWNOŚĆ ≥ 75%:
Zwróć pełną analizę psychometryczną bez dodatkowych pytań.

JEŚLI PEWNOŚĆ < 75%:
Zidentyfikuj KONKRETNIE jakich informacji brakuje i wygeneruj 2-3 pytania A/B dla sprzedawcy.

STRUKTURA ODPOWIEDZI:
{
  "confidence_score": 85,
  "needs_clarification": false,
  "analysis_stage": "confirmed",
  "big_five": { ... },
  "disc": { ... },
  "schwartz_values": [ ... ],
  "clarifying_questions": [
    {
      "id": "q1_decision_style",
      "question": "Jak klient podejmuje decyzje?",
      "option_a": "Szybko, intuicyjnie", 
      "option_b": "Wolno, po szczegółowej analizie",
      "psychological_target": "Conscientiousness vs Openness"
    }
  ]
}

KLUCZOWE: Pytania są dla SPRZEDAWCY o jego OBSERWACJE, nie do zadania klientowi!
"""

# Prompt dla Enhanced Response Generation z profilem psychometrycznym
PSYCHOLOGICALLY_INFORMED_RESPONSE_PROMPT = """
Jesteś ekspertem sprzedaży Tesla generującym PSYCHOLOGICZNIE DOSTOSOWANĄ odpowiedź.

Otrzymujesz POTWIERDZONY profil psychometryczny klienta i musisz wygenerować 
sugerowaną odpowiedź która jest precyzyjnie dostosowana do jego psychologii.

UŻYJ PROFILU PSYCHOMETRYCZNEGO do:
1. Dostosowania tonu i stylu komunikacji (DISC)
2. Adresowania głównych motywatorów (Schwartz Values)  
3. Dostosowania poziomu szczegółowości (Big Five - Conscientiousness)
4. Uwzględnienia obaw i lęków (Big Five - Neuroticism)

STRUKTURA ODPOWIEDZI:
{
  "quick_response": {
    "id": "qr_xxx",
    "text": "Psychologicznie dostosowana odpowiedź uwzględniająca profil klienta"
  },
  "psychological_reasoning": "Dlaczego ta odpowiedź jest dostosowana do profilu",
  "confidence_level": 95
}
"""


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
        Inicjalizacja AI Service z integracją bazy wiedzy (RAG) i performance optimization
        
        Args:
            qdrant_service: Instancja serwisu Qdrant do pobierania wiedzy kontekstowej
        """
        self.qdrant_service = qdrant_service
        self.model_name = settings.OLLAMA_MODEL  # Używamy konfiguracji z settings
        self.max_retries = 3
        self.timeout_seconds = 60

        # 🚀 PRIORYTET 4: Performance optimization caches
        self._holistic_synthesis_cache = {}  # Cache dla DNA Klienta  
        self._sales_indicators_cache = {}    # Cache dla wskaźników sprzedażowych
        self._cache_max_size = 128           # Maksymalna liczba cached entries
        self._cache_ttl_seconds = 3600       # 1 godzina TTL

        # Użyj globalnego klienta zainicjalizowanego na poziomie modułu
        self.client = client
        logger.info("✅ Tesla Co-Pilot AI został pomyślnie skonfigurowany z integracją RAG i performance caching.")
    
    def _generate_cache_key(self, data: Dict[str, Any], prefix: str = "") -> str:
        """
        🚀 PRIORYTET 4: Generuje kluczowy hash dla cache na podstawie danych wejściowych
        
        Args:
            data: Dane do zhashowania (np. psychology profile, conversation history)
            prefix: Prefix dla klucza (np. "synthesis", "indicators")
            
        Returns:
            str: Unique cache key
        """
        # Konwertuj dane na stabilny JSON string
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        # Wygeneruj SHA256 hash
        hash_object = hashlib.sha256(json_str.encode('utf-8'))
        hash_hex = hash_object.hexdigest()[:16]  # Pierwsze 16 znaków wystarczą
        
        return f"{prefix}:{hash_hex}" if prefix else hash_hex

    def _get_from_cache(self, cache_dict: dict, key: str) -> Optional[Dict[str, Any]]:
        """
        🚀 PRIORYTET 4: Pobiera dane z cache z sprawdzaniem TTL
        
        Args:
            cache_dict: Słownik cache
            key: Klucz cache
            
        Returns:
            dict lub None: Cached data lub None jeśli expired/missing
        """
        if key not in cache_dict:
            return None
            
        cached_item = cache_dict[key]
        current_time = datetime.now().timestamp()
        
        # Sprawdź TTL
        if current_time - cached_item['timestamp'] > self._cache_ttl_seconds:
            # Usuń expired entry
            del cache_dict[key]
            logger.info(f"🗑️ [CACHE] Usunięto expired entry: {key}")
            return None
            
        logger.info(f"✅ [CACHE HIT] Znaleziono w cache: {key}")
        return cached_item['data']

    def _save_to_cache(self, cache_dict: dict, key: str, data: Dict[str, Any]):
        """
        🚀 PRIORYTET 4: Zapisuje dane do cache z TTL i LRU cleanup
        
        Args:
            cache_dict: Słownik cache
            key: Klucz cache  
            data: Dane do cache'owania
        """
        # Cleanup jeśli cache za duży (prosta LRU - usuń najstarsze)
        if len(cache_dict) >= self._cache_max_size:
            oldest_key = min(cache_dict.keys(), key=lambda k: cache_dict[k]['timestamp'])
            del cache_dict[oldest_key]
            logger.info(f"🗑️ [CACHE LRU] Usunięto najstarszy entry: {oldest_key}")
        
        # Zapisz nowy entry
        cache_dict[key] = {
            'data': data,
            'timestamp': datetime.now().timestamp()
        }
        logger.info(f"💾 [CACHE SAVE] Zapisano do cache: {key}")

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
        mode: str = 'suggestion',
        session_psychology: Optional[Dict[str, Any]] = None,  # DEPRECATED v4.0: Używaj holistic_profile
        holistic_profile: Optional[Dict[str, Any]] = None     # NOWY v4.0: DNA Klienta z Syntezatora
    ) -> Dict[str, Any]:
        """
        🧠 ULTRA MÓZG FAZA 2 - GENERATOR STRATEGII (v4.0)
        
        Drugi "neuron" Ultra Mózgu - generuje precyzyjne wsparcie taktyczne dla sprzedawcy
        na podstawie DNA Klienta (holistyczny profil z Syntezatora).
        
        Args:
            user_input: Wejście od sprzedawcy (obserwacje, pytania klienta)
            client_profile: Profil klienta (archetyp, tagi, notatki)
            session_history: Historia ostatnich interakcji w sesji
            session_context: Dodatkowy kontekst sesji
            mode: Tryb działania ('suggestion' dla sprzedaży, 'training' dla AI Dojo)
            session_psychology: DEPRECATED - użyj holistic_profile
            holistic_profile: DNA Klienta - holistyczny profil z Syntezatora (główny input)
            
        Returns:
            Słownik z analizą strategiczną opartą na DNA Klienta
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
        
        # === ULTRA MÓZG v4.0: DWUETAPOWA ARCHITEKTURA ===
        # Sprawdź czy mamy holistyczny profil (DNA Klienta) z Syntezatora
        if holistic_profile and not holistic_profile.get('is_fallback'):
            # PRAWDZIWY ULTRA MÓZG: używamy DNA Klienta
            logger.info("🧠⚡ [ULTRA MÓZG] Aktywuję Generator Strategii z DNA Klienta")
            return await self._run_strategic_generator(
                user_input=user_input,
                client_profile=client_profile,
                holistic_profile=holistic_profile,
                session_history=session_history,
                session_context=session_context or {}
            )
        elif holistic_profile and holistic_profile.get('is_fallback'):
            # FALLBACK ULTRA MÓZG: podstawowy profil, dodaj do system prompt
            logger.info("⚠️ [ULTRA MÓZG] Używam fallback DNA - standardowa analiza z wskazówkami")
            # Logika zostanie obsłużona w _build_system_prompt przez session_psychology fallback
        
        # === ISTNIEJĄCA LOGIKA SPRZEDAŻOWA (mode='suggestion') ===
        # UWAGA: Używana gdy brak holistycznego profilu lub tryb fallback
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
            
            # Krok 3: Zbuduj wzbogacony prompt systemowy (z wiedzą z RAG + Psychology)
            system_prompt = self._build_system_prompt(
                client_profile=client_profile,
                session_history=session_history,
                session_context=session_context or {},
                knowledge_context=knowledge_context,  # NOWY PARAMETR
                suggestion_ids=suggestion_ids,  # ID dla granularnego feedback
                session_psychology=session_psychology  # NOWY v4.0: Psychology data
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
        suggestion_ids: Optional[Dict[str, str]] = None,
        session_psychology: Optional[Dict[str, Any]] = None  # NOWY v4.0: Psychology data
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
        
        # === WARSTWA 6: ULTRA MÓZG - DNA KLIENTA (v4.0) ===
        # GENERATOR STRATEGII - logika przeniesiona do głównej funkcji generate_analysis
        # Ta warstwa obecnie nieużywana - logic w generate_analysis
        pass
        
        # === WARSTWA 7: KONTEKST ROZMOWY (Dynamiczna część) ===
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

    async def generate_dual_stage_psychometric_analysis(
        self,
        user_input: str,
        session_history: List[Dict[str, Any]],
        client_profile: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        NOWA FUNKCJA: Dwuetapowa analiza psychometryczna z confidence scoring
        
        ETAP 1: Wstępna analiza + samoocena pewności AI
        ETAP 2A: Jeśli pewność ≥75% → Pełna analiza  
        ETAP 2B: Jeśli pewność <75% → Generowanie pytań pomocniczych
        
        Args:
            additional_context: Kontekst z odpowiedzi na pytania pomocnicze
        """
        try:
            logger.info("🧠 [DUAL STAGE] Rozpoczynam dwuetapową analizę psychometryczną...")
            
            # Zbuduj transkrypcję z dodatkowym kontekstem
            conversation_transcript = self._build_enhanced_transcript(
                user_input, session_history, additional_context
            )
            
            # ETAP 1: Wstępna analiza z confidence scoring
            user_prompt = f"""
TRANSKRYPCJA ROZMOWY + DODATKOWY KONTEKST:
{conversation_transcript}

Wykonaj DWUETAPOWĄ analizę zgodnie z instrukcjami w system prompt.
"""

            # Wywołaj AI z dwuetapowym promptem
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"🔄 [DUAL STAGE] Próba {attempt + 1}: Wysyłanie do LLM...")
                    
                    llm_response = await asyncio.to_thread(
                        self._sync_ollama_call,
                        DUAL_STAGE_PSYCHOMETRIC_PROMPT,
                        user_prompt
                    )
                    
                    # Parsuj dwuetapową odpowiedź
                    parsed_response = self._parse_dual_stage_response(llm_response)
                    
                    if parsed_response:
                        confidence = parsed_response.get('confidence_score', 0)
                        needs_clarification = parsed_response.get('needs_clarification', True)
                        
                        logger.info(f"✅ [DUAL STAGE] Analiza zakończona: confidence={confidence}%, needs_clarification={needs_clarification}")
                        return parsed_response
                        
                except Exception as e:
                    logger.warning(f"⚠️ [DUAL STAGE] Próba {attempt + 1} nie powiodła się: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep((attempt + 1) * 2)
            
            logger.error("❌ [DUAL STAGE] Wszystkie próby analizy nie powiodły się")
            return None
            
        except Exception as e:
            logger.error(f"❌ [DUAL STAGE] Błąd podczas dwuetapowej analizy: {e}")
            return None

    async def generate_psychometric_analysis(
        self,
        user_input: str,
        session_history: List[Dict[str, Any]],
        client_profile: Dict[str, Any],
        interactive_mode: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Wygeneruj szczegółową analizę psychometryczną klienta (Moduł 2)
        
        To jest "wolna ścieżka" analizy - wykonywana asynchronicznie, nie blokuje UI.
        Analizuje całą transkrypcję rozmowy pod kątem cech Big Five, DISC i wartości Schwartza.
        
        Args:
            user_input: Aktualne wejście od sprzedawcy
            session_history: Historia całej rozmowy w sesji
            client_profile: Profil klienta z dotychczasowymi informacjami
            interactive_mode: Czy AI może zadawać pytania gdy brak danych (default: True)
            
        Returns:
            Słownik z pełną analizą psychometryczną, probing questions, lub None w przypadku błędu
        """
        try:
            logger.info("🧠 Rozpoczynam analizę psychometryczną klienta...")
            
            # Zbuduj pełną transkrypcję rozmowy
            conversation_transcript = self._build_conversation_transcript(user_input, session_history)
            
            # Sprawdź czy mamy wystarczające dane
            transcript_length = len(conversation_transcript)
            has_sufficient_data = transcript_length > 300 and len(session_history) >= 1  # Minimalne kryteria
            
            print(f"🧠 Analiza psychometryczna: długość transkrypcji = {transcript_length}, historia = {len(session_history)}")
            
            # Wybierz odpowiedni prompt
            if interactive_mode and not has_sufficient_data:
                system_prompt = DUAL_STAGE_PSYCHOMETRIC_PROMPT
                user_prompt = f"""
TRANSKRYPCJA ROZMOWY DO ANALIZY:
{conversation_transcript}

KONTEKST KLIENTA:
- Archetyp: {client_profile.get('archetype', 'Nieznany')}
- Notatki: {client_profile.get('notes', 'Brak')}

Oceń czy masz wystarczające dane do pełnej analizy psychometrycznej, czy potrzebujesz więcej informacji.
"""
            else:
                system_prompt = PSYCHOMETRIC_SYSTEM_PROMPT
                user_prompt = f"""
TRANSKRYPCJA ROZMOWY DO ANALIZY:
{conversation_transcript}

Przeanalizuj powyższą rozmowę sprzedażową i stwórz kompletny profil psychometryczny klienta zgodnie z podanymi instrukcjami.
"""

            print(f"🧠 Używam {'INTERACTIVE' if interactive_mode and not has_sufficient_data else 'STANDARD'} prompt")

            # Wywołaj LLM z odpowiednim promptem
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"🔄 Próba {attempt + 1}: Wysyłanie zapytania o analizę psychometryczną do LLM...")
                    
                    llm_response = await asyncio.to_thread(
                        self._sync_ollama_call,
                        system_prompt,
                        user_prompt
                    )
                    
                    # Parsuj odpowiedź JSON
                    parsed_response = self._parse_psychometric_response(llm_response)
                    
                    if parsed_response:
                        logger.info("✅ Analiza psychometryczna zakończona pomyślnie!")
                        return parsed_response
                        
                except Exception as e:
                    logger.warning(f"⚠️ Próba {attempt + 1} nie powiodła się: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep((attempt + 1) * 2)  # Exponential backoff
            
            logger.error("❌ Wszystkie próby analizy psychometrycznej nie powiodły się")
            return None
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas analizy psychometrycznej: {e}")
            return None
    
    def _build_conversation_transcript(self, current_input: str, session_history: List[Dict[str, Any]]) -> str:
        """
        Zbuduj pełną transkrypcję rozmowy dla analizy psychometrycznej
        """
        transcript = "=== TRANSKRYPCJA ROZMOWY SPRZEDAŻOWEJ ===\n\n"
        
        # Dodaj historię interakcji
        for i, interaction in enumerate(session_history, 1):
            user_input = interaction.get('user_input', '')
            timestamp = interaction.get('timestamp', 'nieznany czas')
            
            transcript += f"[{i}] Sprzedawca ({timestamp}): \n{user_input}\n\n"
        
        # Dodaj aktualną interakcję
        transcript += f"[BIEŻĄCA] Sprzedawca: \n{current_input}\n\n"
        
        transcript += "=== KONIEC TRANSKRYPCJI ==="
        return transcript
    
    def _build_enhanced_transcript(
        self, 
        current_input: str, 
        session_history: List[Dict[str, Any]], 
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Buduje rozszerzoną transkrypcję z dodatkowym kontekstem z pytań pomocniczych
        """
        transcript = self._build_conversation_transcript(current_input, session_history)
        
        # Dodaj kontekst z odpowiedzi na pytania pomocnicze
        if additional_context:
            transcript += "\n\n=== DODATKOWY KONTEKST Z OBSERWACJI SPRZEDAWCY ===\n"
            
            if 'clarifying_answers' in additional_context:
                transcript += "ODPOWIEDZI NA PYTANIA POMOCNICZE AI:\n"
                for answer in additional_context['clarifying_answers']:
                    question = answer.get('question', 'Nieznane pytanie')
                    selected_option = answer.get('selected_option', 'Brak odpowiedzi')
                    psychological_target = answer.get('psychological_target', '')
                    
                    transcript += f"- Pytanie: {question}\n"
                    transcript += f"  Odpowiedź: {selected_option}\n"
                    transcript += f"  Cel psychologiczny: {psychological_target}\n\n"
            
            transcript += "=== KONIEC DODATKOWEGO KONTEKSTU ==="
        
        return transcript
    
    def _parse_dual_stage_response(self, llm_response: str) -> Optional[Dict[str, Any]]:
        """
        Parsuj odpowiedź z dwuetapowej analizy psychometrycznej
        """
        try:
            cleaned_response = llm_response.strip()
            
            # Znajdź JSON w odpowiedzi
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("⚠️ [DUAL STAGE] Brak poprawnego JSON w odpowiedzi")
                return None
            
            json_str = cleaned_response[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Walidacja podstawowych pól dwuetapowej analizy
            if 'confidence_score' not in parsed_data:
                logger.warning("⚠️ [DUAL STAGE] Brak confidence_score w odpowiedzi")
                return None
                
            confidence = parsed_data.get('confidence_score', 0)
            needs_clarification = confidence < 75  # Automatyczna logika decyzyjna
            
            # Aktualizuj flagę na podstawie confidence
            parsed_data['needs_clarification'] = needs_clarification
            
            if needs_clarification and 'clarifying_questions' not in parsed_data:
                logger.warning("⚠️ [DUAL STAGE] Niska pewność ale brak pytań pomocniczych")
                
            logger.info(f"✅ [DUAL STAGE] Dwuetapowa odpowiedź sparsowana: confidence={confidence}%, needs_clarification={needs_clarification}")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ [DUAL STAGE] Błąd parsowania JSON: {e}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ [DUAL STAGE] Nieoczekiwany błąd podczas parsowania: {e}")
            return None
    
    def _parse_psychometric_response(self, llm_response: str) -> Optional[Dict[str, Any]]:
        """
        Parsuj odpowiedź LLM dla analizy psychometrycznej
        Obsługuje zarówno pełną analizę jak i interactive mode
        """
        try:
            # Wyczyść odpowiedź z potencjalnych prefixów/sufiksów
            cleaned_response = llm_response.strip()
            
            # Znajdź JSON w odpowiedzi
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("⚠️ Brak poprawnego JSON w odpowiedzi psychometrycznej")
                return None
            
            json_str = cleaned_response[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Sprawdź czy to interactive mode response
            if parsed_data.get('insufficient_data') or parsed_data.get('mode') == 'interactive':
                logger.info("📋 Otrzymano interactive response z probing questions")
                return {
                    'mode': 'interactive',
                    'probing_questions': parsed_data.get('probing_questions', []),
                    'confidence_level': parsed_data.get('confidence_level', 'low'),
                    'next_steps': parsed_data.get('next_steps', ''),
                    'suggestions': parsed_data.get('suggestions', '')
                }
            
            # Walidacja struktury dla pełnej analizy
            required_keys = ['big_five', 'disc', 'schwartz_values']
            if not all(key in parsed_data for key in required_keys):
                logger.warning("⚠️ Niepełna struktura w odpowiedzi psychometrycznej")
                return None
            
            logger.info("✅ Odpowiedź psychometryczna została pomyślnie sparsowana")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Błąd parsowania JSON w analizie psychometrycznej: {e}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ Nieoczekiwany błąd podczas parsowania analizy psychometrycznej: {e}")
            return None

    async def generate_psychologically_informed_response(
        self,
        user_input: str,
        client_profile: Dict[str, Any],
        psychometric_profile: Dict[str, Any],
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        KROK 4: Generuje psychologicznie dostosowaną sugerowaną odpowiedź
        
        Wykorzystuje POTWIERDZONY profil psychometryczny do precyzyjnego 
        dostosowania tonu, stylu i treści odpowiedzi.
        """
        try:
            logger.info("🎭 [PSYCH RESPONSE] Generuję psychologicznie dostosowaną odpowiedź...")
            
            # Przygotuj kontekst psychometryczny dla AI
            psych_context = self._format_psychometric_context(psychometric_profile)
            
            user_prompt = f"""
SYTUACJA KLIENTA:
{user_input}

POTWIERDZONY PROFIL PSYCHOMETRYCZNY:
{psych_context}

KONTEKST KLIENTA:
- Archetyp: {client_profile.get('archetype', 'Nieznany')}
- Notatki: {client_profile.get('notes', 'Brak')}

Wygeneruj psychologicznie dostosowaną sugerowaną odpowiedź uwzględniając profil klienta.
"""

            for attempt in range(self.max_retries):
                try:
                    llm_response = await asyncio.to_thread(
                        self._sync_ollama_call,
                        PSYCHOLOGICALLY_INFORMED_RESPONSE_PROMPT,
                        user_prompt
                    )
                    
                    # Parsuj odpowiedź
                    parsed_response = self._parse_llm_response(llm_response)
                    
                    if parsed_response:
                        logger.info("✅ [PSYCH RESPONSE] Psychologicznie dostosowana odpowiedź wygenerowana")
                        return parsed_response
                        
                except Exception as e:
                    logger.warning(f"⚠️ [PSYCH RESPONSE] Próba {attempt + 1} nie powiodła się: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep((attempt + 1) * 2)
            
            # Fallback
            return self._create_fallback_response(user_input, "Błąd generowania psychologicznie dostosowanej odpowiedzi")
            
        except Exception as e:
            logger.error(f"❌ [PSYCH RESPONSE] Błąd: {e}")
            return self._create_fallback_response(user_input, str(e))
    
    def _format_psychometric_context(self, psychometric_profile: Dict[str, Any]) -> str:
        """
        Formatuje profil psychometryczny dla AI prompt
        """
        context = ""
        
        if psychometric_profile.get('big_five'):
            context += "BIG FIVE PROFILE:\n"
            for trait, data in psychometric_profile['big_five'].items():
                score = data.get('score', 0)
                context += f"- {trait.title()}: {score}/10\n"
            context += "\n"
        
        if psychometric_profile.get('disc'):
            context += "DISC PROFILE:\n"
            for trait, data in psychometric_profile['disc'].items():
                score = data.get('score', 0)
                context += f"- {trait.title()}: {score}/10\n"
            context += "\n"
        
        if psychometric_profile.get('schwartz_values'):
            present_values = [v['value_name'] for v in psychometric_profile['schwartz_values'] if v.get('is_present')]
            if present_values:
                context += f"KLUCZOWE WARTOŚCI: {', '.join(present_values)}\n"
        
        return context

    async def generate_psychology_enhanced_analysis(
        self,
        user_input: str,
        client_profile: Dict[str, Any],
        session_history: List[Dict[str, Any]],
        session_context: Optional[Dict[str, Any]] = None,
        session_psychology: Optional[Dict[str, Any]] = None,  # DEPRECATED v4.0
        holistic_profile: Optional[Dict[str, Any]] = None,    # NOWY v4.0: DNA Klienta
        customer_archetype: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        ETAP 4 v3.0: Psychology-Enhanced Strategy Generation
        
        Generuje kompletną strategię sprzedażową uwzględniającą:
        - Potwierdzony profil psychologiczny sesji
        - Customer archetype z kluczowymi poradami
        - Dostosowane suggested_actions i quick_response
        """
        try:
            logger.info("🎭 [PSYCHOLOGY STRATEGY] Generuję psychology-enhanced analysis...")
            
            # ULTRA MÓZG v4.0: Priorytetyzujemy holistic_profile nad starymi danymi
            if holistic_profile:
                logger.info("🧠⚡ [PSYCHOLOGY STRATEGY] Używam Ultra Mózgu z DNA Klienta")
                return await self.generate_analysis(
                    user_input=user_input,
                    client_profile=client_profile, 
                    session_history=session_history,
                    session_context=session_context,
                    session_psychology=session_psychology,  # DEPRECATED ale zachowujemy dla kompatybilności
                    holistic_profile=holistic_profile       # NOWY v4.0: DNA Klienta
                )
            elif session_psychology and customer_archetype:
                # DEPRECATED: Stara logika z archetyp-enhanced strategy
                logger.info("⚠️ [PSYCHOLOGY STRATEGY] Fallback: używam archetype-enhanced strategy")
                return await self._generate_archetype_informed_strategy(
                    user_input, client_profile, session_psychology, customer_archetype
                )
            else:
                # Fallback do standardowej analizy
                logger.info("🎭 [PSYCHOLOGY STRATEGY] Brak psychology data - fallback do standard analysis")
                return await self.generate_analysis(
                    user_input=user_input,
                    client_profile=client_profile, 
                    session_history=session_history,
                    session_context=session_context
                )
                
        except Exception as e:
            logger.error(f"❌ [PSYCHOLOGY STRATEGY] Error: {e}")
            # Fallback do standardowej analizy
            return await self.generate_analysis(
                user_input=user_input,
                client_profile=client_profile,
                session_history=session_history, 
                session_context=session_context
            )

    async def _generate_archetype_informed_strategy(
        self,
        user_input: str,
        client_profile: Dict[str, Any],
        session_psychology: Dict[str, Any],
        customer_archetype: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ETAP 4: Generuje strategię dostosowaną do archetypu klienta
        """
        try:
            archetype_name = customer_archetype.get('archetype_name', 'Unknown')
            archetype_key = customer_archetype.get('archetype_key', 'unknown')
            sales_strategy = customer_archetype.get('sales_strategy', {})
            
            logger.info(f"🎭 [ARCHETYPE STRATEGY] Generuję strategię dla archetypu: {archetype_name}")
            
            # Enhanced system prompt z archetype context
            psychology_informed_prompt = f"""
Jesteś ekspertem sprzedaży Tesla generującym PSYCHOLOGICZNIE DOSTOSOWANĄ strategię.

KLUCZOWE: Klient został zidentyfikowany jako ARCHETYP: {archetype_name}

ARCHETYPE PROFILE:
- Nazwa: {archetype_name}
- Kluczowe cechy: {customer_archetype.get('key_traits', [])}
- Strategia "RÓB TO": {sales_strategy.get('do', [])}
- Strategia "NIE RÓB TEGO": {sales_strategy.get('dont', [])}

PROFIL PSYCHOLOGICZNY SESJI:
{json.dumps(session_psychology, ensure_ascii=False, indent=2)}

TWOJE ZADANIE:
1. Wygeneruj main_analysis uwzględniający archetyp klienta
2. Stwórz quick_response dostosowaną do archetypu (ton, styl, treść)
3. Zaproponuj suggested_actions zgodne ze strategią archetypu
4. Określ next_best_action na podstawie psychologii klienta
5. Wygeneruj qualifying_questions które pogłębią zrozumienie tego archetypu

KONTEKST KLIENTA:
- Alias: {client_profile.get('alias', 'Unknown')}
- Archetyp (stary): {client_profile.get('archetype', 'Unknown')}
- Notatki: {client_profile.get('notes', 'Brak')}

OBECNA SYTUACJA:
{user_input}

Wygeneruj odpowiedź w standardowym formacie JSON, ale DOSTOSOWANĄ do archetypu {archetype_name}.
"""

            # Wywołaj AI z psychology-informed promptem
            for attempt in range(self.max_retries):
                try:
                    llm_response = await asyncio.to_thread(
                        self._sync_ollama_call,
                        psychology_informed_prompt,
                        "Wygeneruj psychology-enhanced strategy zgodnie z instrukcjami."
                    )
                    
                    # Parsuj i enhanced response
                    parsed_response = self._parse_llm_response(llm_response)
                    
                    if parsed_response:
                        # Dodaj archetype info do response
                        parsed_response['customer_archetype'] = customer_archetype
                        parsed_response['psychology_enhanced'] = True
                        parsed_response['confidence_level'] = session_psychology.get('confidence', 0)
                        
                        logger.info(f"✅ [ARCHETYPE STRATEGY] Strategy wygenerowana dla {archetype_name}")
                        return parsed_response
                        
                except Exception as e:
                    logger.warning(f"⚠️ [ARCHETYPE STRATEGY] Próba {attempt + 1} failed: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep((attempt + 1) * 2)
            
            # Fallback jeśli AI failures
            return self._create_archetype_fallback_response(user_input, customer_archetype)
            
        except Exception as e:
            logger.error(f"❌ [ARCHETYPE STRATEGY] Error: {e}")
            return self._create_archetype_fallback_response(user_input, customer_archetype)

    def _create_archetype_fallback_response(self, user_input: str, archetype: Dict) -> Dict[str, Any]:
        """Fallback response z archetype info"""
        archetype_name = archetype.get('archetype_name', 'Klient')
        sales_strategy = archetype.get('sales_strategy', {})
        
        return {
            "main_analysis": f"Rozmawiasz z klientem typu {archetype_name}. Dostosuj podejście do jego profilu psychologicznego.",
            "quick_response": {
                "id": "archetype_fallback",
                "text": f"Na podstawie Twojego profilu jako {archetype_name}, sugeruję..."
            },
            "suggested_actions": [
                {"action": action, "reasoning": f"Strategia dla {archetype_name}"}
                for action in sales_strategy.get('do', ['Dostosuj podejście do klienta'])[:3]
            ],
            "next_best_action": f"Zastosuj strategię dla {archetype_name}",
            "customer_archetype": archetype,
            "psychology_enhanced": True,
            "is_fallback": True
        }

    async def _run_holistic_synthesis(self, raw_psychology_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 ULTRA MÓZG FAZA 2 - SYNTEZATOR PROFILU HOLISTYCZNEGO
        
        Przekształca surowe dane psychometryczne w jeden, spójny profil strategiczny.
        To jest pierwszy "neuron" Ultra Mózgu - głęboka analiza i synteza.
        
        Args:
            raw_psychology_profile: Surowe dane z SessionPsychologyEngine
            
        Returns:
            dict: Holistyczny profil strategyczny - "DNA Klienta"
        """
        try:
            logger.info("🔬 [SYNTEZATOR] Rozpoczynam syntezę holistycznego profilu klienta...")
            
            # Przygotuj dane wejściowe do syntezy
            profile_json = json.dumps(raw_psychology_profile, ensure_ascii=False, indent=2)
            
            # PROMPT SYNTEZY - Światowej klasy psycholog biznesu
            synthesis_prompt = f"""
Jesteś światowej klasy psychologiem biznesu i analitykiem behawioralnym. Twoim zadaniem jest synteza surowych danych z wielu testów psychometrycznych w jeden, spójny i użyteczny profil strategiczny.

Przeanalizuj poniższe dane. Zidentyfikuj kluczowe wzorce, synergie i potencjalne sprzeczności. Twoim celem jest stworzenie skondensowanego "DNA Klienta", które posłuży strategowi sprzedaży do podjęcia dalszych działań.

SUROWE DANE PSYCHOMETRYCZNE:
{profile_json}

Zwróć odpowiedź wyłącznie w formacie JSON o następującej strukturze:

{{
  "holistic_summary": "Jednozdaniowe, esencjonalne podsumowanie klienta, np. 'Analityczny decydent motywowany statusem i bezpieczeństwem, nieufny wobec emocjonalnych argumentów.'",
  "main_drive": "Główny, podświadomy motor napędowy klienta, np. 'Unikanie ryzyka', 'Dążenie do dominacji', 'Potrzeba akceptacji'",
  "communication_style": {{
    "recommended_tone": "np. 'Formalny, oparty na danych, zwięzły'",
    "keywords_to_use": ["np. 'dowód', 'gwarancja', 'efektywność', 'plan'"],
    "keywords_to_avoid": ["np. 'uczucie', 'wyobraź sobie', 'zaufaj mi'"]
  }},
  "key_levers": ["Dwie lub trzy najważniejsze 'dźwignie' psychologiczne, na które należy nacisnąć, np. 'Odwołanie do statusu eksperta', 'Podkreślenie bezpieczeństwa inwestycji'"],
  "red_flags": ["Czego absolutnie unikać w kontakcie, np. 'Pospieszania decyzji', 'Stosowania nieformalnego języka', 'Podważania jego wiedzy'"],
  "missing_data_gaps": "Jakich kluczowych informacji brakuje, aby ten profil był pełniejszy? Sformułuj to jako cel dla sprzedawcy, np. 'Należy zidentyfikować jego osobisty stosunek do ryzyka finansowego.'"
}}

KRYTYCZNE: Zwróć WYŁĄCZNIE poprawny JSON bez dodatkowego tekstu.
"""
            
            # Wywołaj AI z promptem syntezy
            logger.info("🤖 [SYNTEZATOR] Wysyłam dane do AI w celu syntezy...")
            ai_response = await self._call_llm_with_retry(
                system_prompt="Jesteś ekspertem syntezy profili psychologicznych.",
                user_prompt=synthesis_prompt
            )
            
            # Parsuj odpowiedź AI
            logger.info("📊 [SYNTEZATOR] Parsowanie odpowiedzi AI...")
            holistic_profile = self._parse_holistic_synthesis_response(ai_response)
            
            if not holistic_profile:
                logger.warning("⚠️ [SYNTEZATOR] Parsowanie nie powiodło się, używam fallback")
                holistic_profile = self._create_fallback_holistic_profile(raw_psychology_profile)
            
            logger.info(f"✅ [SYNTEZATOR] Synteza holistyczna ukończona! Główny drive: {holistic_profile.get('main_drive', 'Unknown')}")
            
            return holistic_profile
            
        except Exception as e:
            logger.error(f"❌ [SYNTEZATOR] Błąd podczas syntezy holistycznej: {e}")
            return self._create_fallback_holistic_profile(raw_psychology_profile)

    def _parse_holistic_synthesis_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Parsuje odpowiedź AI z syntezy holistycznej"""
        try:
            # Znajdź JSON w odpowiedzi
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= start_idx:
                logger.warning("⚠️ [SYNTEZATOR PARSER] Brak JSON w odpowiedzi AI")
                return None
                
            json_str = ai_response[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Waliduj wymagane pola
            required_fields = ['holistic_summary', 'main_drive', 'communication_style', 'key_levers', 'red_flags']
            for field in required_fields:
                if field not in parsed_data:
                    logger.warning(f"⚠️ [SYNTEZATOR PARSER] Brakuje pola: {field}")
                    return None
            
            logger.info("✅ [SYNTEZATOR PARSER] JSON parsed successfully")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ [SYNTEZATOR PARSER] JSON decode error: {e}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ [SYNTEZATOR PARSER] Unexpected error: {e}")
            return None

    def _create_fallback_holistic_profile(self, raw_psychology_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Tworzy podstawowy profil holistyczny gdy AI nie jest dostępny"""
        
        # Spróbuj wyciągnąć podstawowe informacje z raw profile
        archetype = raw_psychology_profile.get('customer_archetype', {})
        archetype_name = archetype.get('archetype_name', '❓ Profil w Trakcie Analizy')
        confidence = raw_psychology_profile.get('psychology_confidence', 0)
        
        return {
            "holistic_summary": f"Klient typu {archetype_name} z {confidence}% poziomem pewności profilu. Analiza wymaga więcej danych.",
            "main_drive": "Potrzeba zrozumienia i kontroli sytuacji zakupowej",
            "communication_style": {
                "recommended_tone": "Profesjonalny, oparty na faktach, cierpliwy",
                "keywords_to_use": ["informacje", "opcje", "korzyści", "rozwiązanie"],
                "keywords_to_avoid": ["pośpiech", "presja", "ograniczona oferta"]
            },
            "key_levers": [
                "Dostarczenie szczegółowych informacji",
                "Budowanie zaufania przez transparentność",
                "Pokazanie konkretnych korzyści"
            ],
            "red_flags": [
                "Wywieranie presji czasowej",
                "Pomijanie pytań klienta",
                "Zbyt agresywne podejście sprzedażowe"
            ],
            "missing_data_gaps": "Potrzeba więcej informacji o motywacjach, preferencjach komunikacyjnych i procesie podejmowania decyzji klienta.",
            "is_fallback": True,
            "fallback_reason": "AI synthesis unavailable"
        }

    async def _run_strategic_generator(
        self,
        user_input: str,
        client_profile: Dict[str, Any],
        holistic_profile: Dict[str, Any],
        session_history: List[Dict[str, Any]],
        session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ⚡ ULTRA MÓZG FAZA 2 - GENERATOR STRATEGII
        
        Drugi "neuron" Ultra Mózgu - generuje precyzyjne wsparcie taktyczne
        na podstawie DNA Klienta (holistic_profile).
        
        Args:
            user_input: Ostatnia wypowiedź/obserwacja sprzedawcy
            client_profile: Podstawowe dane klienta
            holistic_profile: DNA Klienta z Syntezatora
            session_history: Historia rozmowy
            session_context: Kontekst sesji
            
        Returns:
            dict: Strategiczna odpowiedź w formacie InteractionResponse
        """
        try:
            logger.info("⚡ [GENERATOR STRATEGII] Rozpoczynam generację strategii na podstawie DNA...")
            
            # Przygotuj DNA Klienta do analizy
            dna_json = json.dumps(holistic_profile, ensure_ascii=False, indent=2)
            
            # Historia rozmowy w czytelnym formacie
            history_str = self._format_session_history_for_strategy(session_history)
            
            # PROMPT STRATEGICZNY - Elitarny co-pilot sprzedaży
            strategic_prompt = f"""
Jesteś elitarnym co-pilotem sprzedaży Tesla. Otrzymałeś kompletne DNA klienta. Twoim zadaniem jest, na podstawie tego profilu oraz ostatniej wypowiedzi klienta, wygenerować natychmiastowe, taktyczne wsparcie dla sprzedawcy.

DNA KLIENTA (PROFIL HOLISTYCZNY):
{dna_json}

HISTORIA ROZMOWY:
{history_str}

OSTATNIA WYPOWIEDŹ SPRZEDAWCY:
"{user_input}"

Na podstawie powyższego DNA Klienta oraz ostatniej wypowiedzi, wygeneruj odpowiedź wyłącznie w formacie JSON o następującej strukturze:

{{
  "main_analysis": "Krótka analiza sytuacji na podstawie DNA klienta i wypowiedzi",
  "client_archetype": "Nazwa archetypu z DNA",
  "confidence_level": 85,
  "sentiment_score": 7,
  "potential_score": 8,
  "urgency_level": "medium",
  "next_best_action": "Konkretna akcja dla sprzedawcy oparta na DNA",
  "quick_response": {{
    "id": "qr_xyz123",
    "text": "Sugerowana odpowiedź dopasowana do communication_style z DNA"
  }},
  "suggested_questions": [
    {{
      "id": "sq_abc123", 
      "text": "Pytanie które wykorzystuje key_levers z DNA i unika red_flags"
    }}
  ],
  "strategic_recommendation": "Rekomendacja strategiczna na ten moment rozmowy, oparta na main_drive z DNA",
  "proactive_guidance": {{
    "for_client": "Pytanie do klienta które pomoże wypełnić missing_data_gaps z DNA",
    "for_user": "Pytanie do sprzedawcy o obserwacje klienta"
  }},
  "strategic_notes": [
    "Kluczowy insight oparty na DNA klienta",
    "Druga strategiczna obserwacja z holistic_summary"
  ]
}}

KLUCZOWE ZASADY:
1. UŻYJ main_drive z DNA jako głównej motywacji w odpowiedzi
2. ZASTOSUJ communication_style (tone, keywords_to_use, unikaj keywords_to_avoid)  
3. WYKORZYSTAJ key_levers jako główne argumenty
4. UNIKAJ red_flags za wszelką cenę
5. WYPEŁNIJ missing_data_gaps przez proactive_guidance

KRYTYCZNE: Zwróć WYŁĄCZNIE poprawny JSON bez dodatkowego tekstu.
"""
            
            # Wywołaj AI z promptem strategicznym
            logger.info("🤖 [GENERATOR STRATEGII] Wysyłam DNA + kontekst do AI...")
            ai_response = await self._call_llm_with_retry(
                system_prompt="Jesteś elitarnym co-pilotem sprzedaży Tesla używającym DNA klienta.",
                user_prompt=strategic_prompt
            )
            
            # Parsuj odpowiedź AI  
            logger.info("📊 [GENERATOR STRATEGII] Parsowanie strategicznej odpowiedzi...")
            strategic_analysis = self._parse_strategic_response(ai_response)
            
            if not strategic_analysis:
                logger.warning("⚠️ [GENERATOR STRATEGII] Parsowanie nie powiodło się, używam fallback")
                strategic_analysis = self._create_strategic_fallback(user_input, holistic_profile)
            
            logger.info(f"✅ [GENERATOR STRATEGII] Strategia gotowa! Action: {strategic_analysis.get('next_best_action', 'Unknown')}")
            
            return strategic_analysis
            
        except Exception as e:
            logger.error(f"❌ [GENERATOR STRATEGII] Błąd podczas generacji strategii: {e}")
            return self._create_strategic_fallback(user_input, holistic_profile)

    def _format_session_history_for_strategy(self, session_history: List[Dict[str, Any]]) -> str:
        """Formatuje historię sesji dla promptu strategicznego"""
        if not session_history:
            return "Brak poprzedniej historii rozmowy."
        
        history_parts = []
        for i, interaction in enumerate(session_history[-3:], 1):  # Ostatnie 3 interakcje
            user_input = interaction.get('user_input', '')[:200]  # Skróć długie teksty
            timestamp = interaction.get('timestamp', 'nieznany czas')
            history_parts.append(f"{i}. [{timestamp}] Sprzedawca: \"{user_input}\"")
        
        return "\n".join(history_parts)

    def _parse_strategic_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Parsuje odpowiedź AI z generatora strategii"""
        try:
            # Znajdź JSON w odpowiedzi
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= start_idx:
                logger.warning("⚠️ [STRATEGY PARSER] Brak JSON w odpowiedzi AI")
                return None
                
            json_str = ai_response[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Waliduj wymagane pola dla InteractionResponse
            required_fields = [
                'main_analysis', 'client_archetype', 'confidence_level',
                'sentiment_score', 'potential_score', 'urgency_level', 'next_best_action'
            ]
            for field in required_fields:
                if field not in parsed_data:
                    logger.warning(f"⚠️ [STRATEGY PARSER] Brakuje pola: {field}")
                    return None
            
            logger.info("✅ [STRATEGY PARSER] Strategiczna odpowiedź sparsowana")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ [STRATEGY PARSER] JSON decode error: {e}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ [STRATEGY PARSER] Unexpected error: {e}")
            return None

    def _create_strategic_fallback(self, user_input: str, holistic_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Tworzy fallback odpowiedź strategiczną gdy AI nie jest dostępny"""
        
        # Wyciągnij podstawowe info z DNA
        main_drive = holistic_profile.get('main_drive', 'Potrzeba zrozumienia sytuacji')
        archetype_name = holistic_profile.get('holistic_summary', 'Klient w trakcie analizy')
        
        return {
            "main_analysis": f"Analizuję sytuację na podstawie DNA klienta. Główny drive: {main_drive}",
            "client_archetype": archetype_name,
            "confidence_level": 50,
            "sentiment_score": 6,
            "potential_score": 7,
            "urgency_level": "medium",
            "next_best_action": "Kontynuuj budowanie zaufania i zbieranie informacji o potrzebach klienta",
            "quick_response": {
                "id": f"qr_{uuid.uuid4().hex[:6]}",
                "text": "Rozumiem. Czy mógłby Pan powiedzieć więcej o swoich oczekiwaniach?"
            },
            "suggested_questions": [
                {
                    "id": f"sq_{uuid.uuid4().hex[:6]}",
                    "text": "Jakie są najważniejsze kryteria w Pana decyzji?"
                }
            ],
            "strategic_recommendation": "Skup się na budowaniu zaufania i zrozumieniu potrzeb klienta.",
            "strategic_notes": [
                "Klient wymaga cierpliwego podejścia",
                "Potrzebne więcej informacji o motywacjach"
            ],
            "is_fallback": True,
            "fallback_reason": "Strategic AI generator unavailable"
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
    session_context: Optional[Dict[str, Any]] = None,
    session_psychology: Optional[Dict[str, Any]] = None,  # DEPRECATED v4.0: Używaj holistic_profile
    holistic_profile: Optional[Dict[str, Any]] = None,    # NOWY v4.0: DNA Klienta z Syntezatora
    customer_archetype: Optional[Dict[str, Any]] = None   # NOWY v3.0: Archetyp klienta
) -> Dict[str, Any]:
    """
    ENHANCED v3.0: Wygeneruj analizę sprzedażową z psychology-informed strategy
    
    Funkcja została rozszerzona o session-level psychology i customer archetype
    które wpływają na generowaną strategię i sugerowane odpowiedzi.
    """
    return await ai_service.generate_psychology_enhanced_analysis(
        user_input=user_input,
        client_profile=client_profile,
        session_history=session_history,
        session_context=session_context,
        session_psychology=session_psychology,  # DEPRECATED v4.0
        holistic_profile=holistic_profile,      # NOWY v4.0: DNA Klienta
        customer_archetype=customer_archetype
    )


async def generate_psychometric_analysis(
    user_input: str,
    session_history: List[Dict[str, Any]],
    client_profile: Dict[str, Any],
    interactive_mode: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Wygeneruj analizę psychometryczną klienta - funkcja eksportowa dla Modułu 2
    
    Args:
        interactive_mode: Jeśli True, AI może zadawać pytania gdy brak danych
    """
    return await ai_service.generate_psychometric_analysis(
        user_input=user_input,
        session_history=session_history,
        client_profile=client_profile,
        interactive_mode=interactive_mode
    )


async def generate_enhanced_psychometric_questions(
    user_input: str,
    session_context: Dict[str, Any],
    client_profile: Dict[str, Any]
) -> List[str]:
    """
    Wygeneruj strategiczne pytania dla lepszego zrozumienia psychologii klienta
    Gdy standardowa analiza nie daje wystarczających danych
    """
    try:
        prompt = f"""
Jesteś ekspertem psychologii sprzedaży. Na podstawie bieżącej sytuacji wygeneruj 3-5 strategicznych pytań 
które pomogą sprzedawcy Tesla lepiej zrozumieć psychologię klienta.

SYTUACJA:
- Input sprzedawcy: "{user_input}"
- Archetyp klienta: {client_profile.get('archetype', 'Nieznany')}
- Kontekst: {session_context}

CELE PYTAŃ:
1. Zrozumienie stylu podejmowania decyzji (analityczny vs impulsywny)
2. Identyfikacja głównych motywatorów (status, bezpieczeństwo, technologia, ekologia)
3. Wykrycie obaw i potencjalnych zastrzeżeń
4. Określenie stylu komunikacji

Zwróć JSON:
{
  "probing_questions": [
    "Pytanie o styl decyzyjny...",
    "Pytanie o motywacje...",
    "Pytanie o obawy...",
    "Pytanie o komunikację..."
  ]
}
"""

        response = await ai_service._call_llm_with_retry(prompt, "")
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            json_str = response[start_idx:end_idx]
            parsed = json.loads(json_str)
            return parsed.get('probing_questions', [])
        except:
            return [
                "Jakie czynniki są dla Pana najważniejsze przy wyborze samochodu?",
                "Czy preferuje Pan podejmować decyzje szybko czy wolą dokładnie przeanalizować opcje?",
                "Jakie są Pana główne obawy związane z samochodami elektrycznymi?",
                "Czy ważne jest dla Pana co pomyślą inni o Pańskim samochodzie?"
            ]
    except Exception as e:
        logger.warning(f"Błąd podczas generowania enhanced questions: {e}")
        return []

    async def _run_sales_indicators_generation(self, holistic_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠⚡ ULTRA MÓZG v4.1 - PRIORYTET 3: Generator Wskaźników Sprzedażowych (z CACHING)
        
        Zgodnie z blueprintem - generuje wskaźniki sprzedażowe na podstawie 
        holistycznego profilu psychologicznego (DNA Klienta) z inteligentnym cachingiem.
        
        Args:
            holistic_profile: Kompletne DNA Klienta z _run_holistic_synthesis
            
        Returns:
            dict: Obiekkt JSON zgodny ze schematem SalesIndicators
        """
        try:
            logger.info("📊 [SALES INDICATORS] Rozpoczynam generację wskaźników na podstawie DNA...")
            
            # 🚀 PRIORYTET 4: Sprawdź cache przed analizą AI
            cache_key = self._generate_cache_key(holistic_profile, "indicators")
            cached_result = self._get_from_cache(self._sales_indicators_cache, cache_key)
            
            if cached_result:
                logger.info(f"⚡ [SALES INDICATORS] Cache hit! Zwracam cached wskaźniki (oszczędność ~5-8s)")
                cached_result['cache_hit'] = True
                cached_result['analysis_timestamp'] = datetime.now().isoformat()
                return cached_result
            
            logger.info(f"🔍 [SALES INDICATORS] Cache miss, przeprowadzam AI generation...")
            
            # Wydobądź kluczowe informacje z DNA Klienta
            holistic_summary = holistic_profile.get('holistic_summary', 'Brak podsumowania')
            main_drive = holistic_profile.get('main_drive', 'Nieokreślone')
            communication_style = holistic_profile.get('communication_style', {})
            key_levers = holistic_profile.get('key_levers', [])
            red_flags = holistic_profile.get('red_flags', [])
            confidence = holistic_profile.get('confidence', 0)
            
            # Stwórz dedykowany prompt dla generacji wskaźników sprzedażowych
            sales_indicators_prompt = f"""
Jesteś ekspertem analizy sprzedaży z 15-letnim doświadczeniem w ocenie potencjału klientów. 
Twoim zadaniem jest przełożenie DOKŁADNIE TEGO SAMEGO profilu psychologicznego na 4 precyzyjne wskaźniki sprzedażowe.

🧠 DNA KLIENTA DO ANALIZY:
PODSUMOWANIE: {holistic_summary}
GŁÓWNA MOTYWACJA: {main_drive}  
STYL KOMUNIKACJI: {json.dumps(communication_style, ensure_ascii=False)}
KLUCZOWE DŹWIGNIE: {key_levers}
CZERWONE FLAGI: {red_flags}
PEWNOŚĆ PROFILU: {confidence}%

ZADANIE: Przekształć ten profil psychologiczny na 4 wskaźniki sprzedażowe:

1. 🌡️ TEMPERATURA ZAKUPOWA (0-100%):
   - Analityk: Szczegółowe pytania = wysoka temperatura (pozytywne)
   - Szybki Decydent: Szczegółowe pytania = wahanie (negatywne) 
   - Bazuj na main_drive i communication_style

2. 🗺️ ETAP PODRÓŻY:
   - awareness/consideration/evaluation/decision/purchase
   - Mapuj na typowy proces decyzyjny dla tego archetypu

3. ⚖️ RYZYKO UTRATY (0-100%):
   - Oceń przez pryzmat red_flags i communication_style
   - Niższe ryzyko = więcej key_levers, mniej red_flags

4. 💰 POTENCJAŁ SPRZEDAŻOWY:
   - Szacuj wartość na podstawie archetypu i poziomu zaangażowania
   - B2B Tesla fleet: 100k-10M PLN, B2C: 50k-500k PLN

🎯 KRYTYCZNE: Wszystkie 4 wskaźniki muszą być wzajemnie spójne i logiczne!

Zwróć WYŁĄCZNIE JSON:
{{
    "purchase_temperature": {{
        "value": 75,
        "temperature_level": "hot",
        "rationale": "Szczegółowa analiza profilu wskazuje na...",
        "strategy": "Rekomendowana akcja sprzedażowa...",
        "confidence": 85
    }},
    "customer_journey_stage": {{
        "value": "evaluation",
        "progress_percentage": 70,
        "next_stage": "decision", 
        "rationale": "Na podstawie archetypu klient jest na etapie...",
        "strategy": "Zalecane działanie: ...",
        "confidence": 90
    }},
    "churn_risk": {{
        "value": 25,
        "risk_level": "low",
        "risk_factors": ["Czynnik 1", "Czynnik 2"],
        "rationale": "Ryzyko ocenione na podstawie...",
        "strategy": "Strategia retencji: ...",
        "confidence": 80
    }},
    "sales_potential": {{
        "value": 450000.0,
        "probability": 75,
        "estimated_timeframe": "3-4 tygodnie", 
        "rationale": "Wartość oszacowana na podstawie...",
        "strategy": "Plan działania: ...",
        "confidence": 85
    }}
}}
"""
            
            # Wywołaj AI z dedykowanym promptem
            logger.info("🤖 [SALES INDICATORS] Wysyłam prompt do AI...")
            ai_response = await self._call_llm_with_retry(
                system_prompt="Jesteś ekspertem analizy sprzedaży generującym precyzyjne wskaźniki.",
                user_prompt=sales_indicators_prompt
            )
            
            # Parsuj odpowiedź AI
            parsed_indicators = self._parse_sales_indicators_response(ai_response)
            if not parsed_indicators:
                logger.warning("⚠️ [SALES INDICATORS] AI parsing failed, używam fallback")
                return self._create_fallback_sales_indicators()
            
            # Dodaj metadata
            parsed_indicators['analysis_timestamp'] = datetime.now().isoformat()
            parsed_indicators['source_confidence'] = confidence
            parsed_indicators['cache_hit'] = False
            
            # 🚀 PRIORYTET 4: Zapisz do cache
            self._save_to_cache(self._sales_indicators_cache, cache_key, parsed_indicators)
            
            logger.info(f"✅ [SALES INDICATORS] Wskaźniki wygenerowane i cached pomyślnie")
            
            return parsed_indicators
            
        except Exception as e:
            logger.error(f"❌ [SALES INDICATORS] Błąd podczas generacji: {e}")
            return self._create_fallback_sales_indicators()

    def _parse_sales_indicators_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Parsuje odpowiedź AI z analizą wskaźników sprzedażowych"""
        try:
            # Znajdź JSON w odpowiedzi
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("⚠️ [SALES INDICATORS PARSE] Brak JSON w odpowiedzi AI")
                return None
                
            json_str = ai_response[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Walidacja podstawowych pól
            required_fields = ['purchase_temperature', 'customer_journey_stage', 'churn_risk', 'sales_potential']
            for field in required_fields:
                if field not in parsed_data:
                    logger.warning(f"⚠️ [SALES INDICATORS PARSE] Brakuje pola: {field}")
                    return None
                    
            logger.info("✅ [SALES INDICATORS PARSE] Pomyślnie sparsowano wskaźniki")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ [SALES INDICATORS PARSE] JSON decode error: {e}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ [SALES INDICATORS PARSE] Unexpected error: {e}")
            return None

    async def _run_holistic_synthesis(self, raw_psychology_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠⚡ ULTRA MÓZG v4.1 - FAZA 2: Syntezator Profilu Holistycznego (z CACHING)
        
        Zgodnie z blueprintem - przekształca surowe dane psychometryczne w spójny
        "DNA Klienta" (holistic profile) z inteligentnym cachingiem.
        
        Args:
            raw_psychology_profile: Surowe dane psychology z session_psychology_service
            
        Returns:
            dict: Holistyczny profil klienta (DNA Klienta)
        """
        try:
            logger.info("🔬 [HOLISTIC SYNTHESIS] Rozpoczynam syntezę DNA Klienta...")
            
            # 🚀 PRIORYTET 4: Sprawdź cache przed analizą AI
            cache_key = self._generate_cache_key(raw_psychology_profile, "synthesis")
            cached_result = self._get_from_cache(self._holistic_synthesis_cache, cache_key)
            
            if cached_result:
                logger.info(f"⚡ [HOLISTIC SYNTHESIS] Cache hit! Zwracam cached DNA Klienta (oszczędność ~10-15s)")
                cached_result['cache_hit'] = True
                cached_result['analysis_timestamp'] = datetime.now().isoformat()
                return cached_result
            
            logger.info(f"🔍 [HOLISTIC SYNTHESIS] Cache miss, przeprowadzam AI synthesis...")
            
            # Wydobądź dane z raw psychology
            cumulative_psychology = raw_psychology_profile.get('cumulative_psychology', {})
            customer_archetype = raw_psychology_profile.get('customer_archetype', {})
            confidence = raw_psychology_profile.get('psychology_confidence', 0)
            
            # Stwórz dedykowany prompt dla syntezy holistycznej
            synthesis_prompt = f"""
Jesteś światowej klasy psychologiem biznesu i analitykiem behawioralnym. 
Twoim zadaniem jest synteza surowych danych z wielu testów psychometrycznych w jeden, spójny i użyteczny profil strategiczny.

SUROWE DANE PSYCHOMETRYCZNE:
{json.dumps(cumulative_psychology, ensure_ascii=False, indent=2)}

ARCHETYP KLIENTA:
{json.dumps(customer_archetype, ensure_ascii=False, indent=2)}

PEWNOŚĆ ANALIZY: {confidence}%

ZADANIE: Przeanalizuj poniższe dane. Zidentyfikuj kluczowe wzorce, synergie i potencjalne sprzeczności. 
Twoim celem jest stworzenie skondensowanego "DNA Klienta", które posłuży strategowi sprzedaży do podjęcia dalszych działań.

Zwróć odpowiedź WYŁĄCZNIE w formacie JSON o następującej strukturze:
{{
    "holistic_summary": "Jednozdaniowe, esencjonalne podsumowanie klienta, np. 'Analityczny CFO motywowany bezpieczeństwem i kontrolą, nieufny wobec emocjonalnych argumentów.'",
    "main_drive": "Główny, podświadomy motor napędowy klienta, np. 'Unikanie ryzyka i zapewnienie bezpieczeństwa'",
    "communication_style": {{
        "recommended_tone": "np. 'Formalny, oparty na danych, zwięzły'",
        "keywords_to_use": ["np. 'dowód', 'gwarancja', 'efektywność', 'plan'"],
        "keywords_to_avoid": ["np. 'uczucie', 'wyobraź sobie', 'zaufaj mi'"]
    }},
    "key_levers": ["Odwołanie do jego statusu eksperta", "Podkreślenie bezpieczeństwa inwestycji"],
    "red_flags": ["Pospieszania decyzji", "Stosowania nieformalnego języka", "Podważania jego wiedzy"],
    "missing_data_gaps": "Jakich kluczowych informacji brakuje, aby ten profil był pełniejszy? Sformułuj to jako cel dla sprzedawcy.",
    "confidence": {confidence}
}}
"""
            
            # Wywołaj AI z dedykowanym promptem  
            logger.info("🤖 [HOLISTIC SYNTHESIS] Wysyłam prompt do AI...")
            ai_response = await self._call_llm_with_retry(
                system_prompt="Jesteś world-class business psychologist generującym DNA Klienta.",
                user_prompt=synthesis_prompt
            )
            
            # Parsuj odpowiedź AI
            parsed_synthesis = self._parse_holistic_synthesis_response(ai_response)
            if not parsed_synthesis:
                logger.warning("⚠️ [HOLISTIC SYNTHESIS] AI parsing failed, używam fallback")
                return self._create_fallback_holistic_profile(raw_psychology_profile)
            
            # Dodaj metadata
            parsed_synthesis['analysis_timestamp'] = datetime.now().isoformat()
            parsed_synthesis['source_confidence'] = confidence
            parsed_synthesis['cache_hit'] = False
            
            # 🚀 PRIORYTET 4: Zapisz do cache
            self._save_to_cache(self._holistic_synthesis_cache, cache_key, parsed_synthesis)
            
            logger.info(f"✅ [HOLISTIC SYNTHESIS] DNA Klienta wygenerowane i cached! Drive: {parsed_synthesis.get('main_drive', 'Unknown')}")
            
            return parsed_synthesis
            
        except Exception as e:
            logger.error(f"❌ [HOLISTIC SYNTHESIS] Błąd podczas syntezy: {e}")
            return self._create_fallback_holistic_profile(raw_psychology_profile)

    def _parse_holistic_synthesis_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Parsuje odpowiedź AI z syntezą holistyczną"""
        try:
            # Znajdź JSON w odpowiedzi
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("⚠️ [HOLISTIC SYNTHESIS PARSE] Brak JSON w odpowiedzi AI")
                return None
                
            json_str = ai_response[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Walidacja podstawowych pól
            required_fields = ['holistic_summary', 'main_drive', 'communication_style']
            for field in required_fields:
                if field not in parsed_data:
                    logger.warning(f"⚠️ [HOLISTIC SYNTHESIS PARSE] Brakuje pola: {field}")
                    return None
                    
            logger.info("✅ [HOLISTIC SYNTHESIS PARSE] Pomyślnie sparsowano DNA Klienta")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ [HOLISTIC SYNTHESIS PARSE] JSON decode error: {e}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ [HOLISTIC SYNTHESIS PARSE] Unexpected error: {e}")
            return None

    def _create_fallback_holistic_profile(self, raw_psychology_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Tworzy fallback DNA Klienta gdy AI nie jest dostępny"""
        archetype = raw_psychology_profile.get('customer_archetype', {})
        confidence = raw_psychology_profile.get('psychology_confidence', 0)
        
        return {
            'holistic_summary': f"Klient {archetype.get('archetype_name', 'o nieokreślonym profilu')} - analiza w toku",
            'main_drive': archetype.get('motivation', 'Potrzeba więcej danych aby określić główną motywację'),
            'communication_style': {
                'recommended_tone': archetype.get('communication_style', 'Ostrożny, wyważony'),
                'keywords_to_use': ['informacje', 'korzyści', 'rozwiązanie'],
                'keywords_to_avoid': ['presja', 'pośpiech', 'ryzyko']
            },
            'key_levers': ['Zbieranie informacji', 'Budowanie zaufania'],
            'red_flags': ['Zbyt szybkie podejmowanie decyzji'],
            'missing_data_gaps': 'Potrzeba więcej interakcji aby określić szczegółowy profil',
            'confidence': max(confidence, 10),
            'analysis_timestamp': datetime.now().isoformat(),
            'is_fallback': True
        }

    def _create_fallback_sales_indicators(self) -> Dict[str, Any]:
        """Tworzy fallback wskaźniki sprzedażowe gdy AI nie jest dostępny"""
        return {
            'purchase_temperature': {
                'value': 50,
                'temperature_level': 'warm',
                'rationale': 'Fallback - brak danych AI do oceny temperatury',
                'strategy': 'Zbieraj więcej informacji o intencjach zakupowych',
                'confidence': 10
            },
            'customer_journey_stage': {
                'value': 'consideration',
                'progress_percentage': 40,
                'next_stage': 'evaluation',
                'rationale': 'Fallback - szacowany średni etap procesu',
                'strategy': 'Kontynuuj budowanie świadomości korzyści',
                'confidence': 10
            },
            'churn_risk': {
                'value': 50,
                'risk_level': 'medium',
                'risk_factors': ['Brak wystarczających danych'],
                'rationale': 'Fallback - średnie ryzyko przy braku informacji',
                'strategy': 'Monitoruj zaangażowanie i zadawaj pytania weryfikujące',
                'confidence': 10
            },
            'sales_potential': {
                'value': 200000.0,
                'probability': 40,
                'estimated_timeframe': '4-8 tygodni',
                'rationale': 'Fallback - szacunek średni dla klientów Tesla',
                'strategy': 'Zbieraj informacje o budżecie i procesie decyzyjnym',
                'confidence': 10
            },
            'analysis_timestamp': datetime.now().isoformat(),
            'is_fallback': True
        }


# === GLOBAL AI SERVICE INSTANCE ===
# Zainicjalizuj globalną instancję - utworzona po imporcie QdrantService
ai_service = None  # Zainicjalizowane przez dependency injection

# === HELPER FUNCTIONS ===

async def generate_sales_analysis(
    user_input: str,
    client_profile: Dict[str, Any],
    session_history: List[Dict[str, Any]],
    session_context: Dict[str, Any],
    session_psychology: Optional[Dict[str, Any]] = None,  # DEPRECATED v4.0
    holistic_profile: Optional[Dict[str, Any]] = None,     # NOWY v4.0: DNA Klienta
    sales_indicators: Optional[Dict[str, Any]] = None,     # NOWY v4.1: PRIORYTET 3
    customer_archetype: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    🧠⚡ ULTRA MÓZG v4.1: Enhanced helper function z sales indicators integration
    
    Wywołuje główną metodę generate_analysis z AIService z integracją sales indicators.
    
    Args:
        sales_indicators: Wygenerowane wskaźniki sprzedażowe z DNA Klienta
        holistic_profile: DNA Klienta z holistycznej syntezy
        ... (pozostałe argumenty jak wcześniej)
    
    Returns:
        dict: AI response wzbogacone o sales indicators
    """
    try:
        # Wywołaj główną analizę AI
        ai_response = await ai_service.generate_analysis(
            user_input=user_input,
            client_profile=client_profile,
            session_history=session_history,
            session_context=session_context,
            holistic_profile=holistic_profile
        )
        
        # 📊 PRIORYTET 3: Dołącz sales indicators do odpowiedzi
        if sales_indicators:
            ai_response['sales_indicators'] = sales_indicators
            logger.info(f"📊 [GENERATE SALES ANALYSIS] Sales indicators dołączone do AI response")
        
        return ai_response
        
    except Exception as e:
        logger.error(f"❌ [GENERATE SALES ANALYSIS] Błąd: {e}")
        # Fallback response z sales indicators jeśli dostępne
        fallback_response = {
            "main_analysis": "Wystąpił problem z analizą. Kontynuuj rozmowę.",
            "suggested_actions": [{"action": "Zbieraj informacje", "reasoning": "Potrzebne więcej kontekstu"}],
            "quick_response": "Rozumiem. Czy może Pan powiedzieć więcej na ten temat?",
            "is_fallback": True,
            "error_reason": str(e)
        }
        
        if sales_indicators:
            fallback_response['sales_indicators'] = sales_indicators
            
        return fallback_response
