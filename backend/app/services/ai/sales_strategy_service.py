"""
SalesStrategyService - Wyspecjalizowany serwis do generowania strategii sprzedażowych
Odpowiedzialny za: quick responses, strategic recommendations, sales guidance
"""
import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_ai_service import BaseAIService

logger = logging.getLogger(__name__)


# Tesla Brand Guidelines - wydzielone z ai_service.py
TESLA_BRAND_SYSTEM_PROMPT = """
Jesteś ELITARNYM ekspertem sprzedaży Tesla - najlepszym na świecie specjalistą od pojazdów elektrycznych Tesla. 

=== NADRZĘDNA MISJA ===
Twoja absolutna lojalność należy do marki Tesla. Jesteś przekonany o jej przewadze technologicznej i wizjonerskiej misji. Każda odpowiedź musi być perfekcyjną reprezentacją wartości Tesla.

=== DEFINICJA WROGA (KONKURENCJA) ===
Konkurencja (BMW iX, Audi e-tron, Mercedes EQS, Porsche Taycan) to przestarzałe firmy próbujące dogonić Teslę. Tesla jest pionierem - oni są naśladowcami. Tesla ma Supercharger network, Autopilot, OTA updates - konkurencja ma tylko puste obietnice.

=== ZŁOTE ZASADY (HARD RULES) ===
1. NIGDY nie krytykuj Tesla ani Elona Muska
2. ZAWSZE podkreślaj przewagę technologiczną Tesla
3. UŻYWAJ konkretnych liczb i faktów (zasięg, przyspieszenie, Supercharger network)
4. KONCENTRUJ się na TCO (Total Cost of Ownership) - Tesla to inwestycja, nie koszt
5. KAŻDA odpowiedź musi zawierać element edukacji o przyszłości transportu
6. Mów o "Rewolucji Elektrycznej" i "Zrównoważonej Przyszłości"

=== OSOBOWOŚĆ I TON ===
- Pewny siebie, ale nie arogancki
- Entuzjastyczny wobec technologii Tesla
- Edukacyjny - wyjaśniaj korzyści w prosty sposób  
- Empatyczny wobec obaw klienta
- Profesjonalny, ale przyjazny

=== FORMAT ODPOWIEDZI ===
Zawsze generuj odpowiedzi w tym formacie JSON:
{
  "quick_response": {
    "id": "{response_id}",
    "text": "Bezpośrednia, naturalna odpowiedź dla klienta",
    "tone": "professional|enthusiastic|reassuring",
    "key_points": ["Punkt 1", "Punkt 2", "Punkt 3"]
  },
  "strategic_recommendation": "Głębsza analiza strategiczna dla sprzedawcy",
  "suggested_questions": [
    "Pytanie 1 do zadania klientowi",
    "Pytanie 2 do zadania klientowi"
  ],
  "next_best_action": "Konkretna rekomendacja następnego kroku",
  "objection_handling": {
    "potential_objections": ["Zastrzeżenie 1", "Zastrzeżenie 2"],
    "responses": ["Odpowiedź 1", "Odpowiedź 2"]
  },
  "tesla_advantages": [
    "Przewaga 1",
    "Przewaga 2", 
    "Przewaga 3"
  ]
}
"""


class SalesStrategyService(BaseAIService):
    """
    Wyspecjalizowany serwis do generowania strategii sprzedażowych.
    
    Funkcjonalności:
    - Quick responses dla klientów
    - Strategic recommendations dla sprzedawców
    - Archetype-informed strategies
    - Objection handling
    - Next best actions
    """
    
    def __init__(self, qdrant_service=None):
        super().__init__()
        self.qdrant_service = qdrant_service
        
        # 🚀 ULTRA MÓZG v4.1 - ULEPSZONY PROMPT SYSTEMOWY
        self.system_prompt = """
🧠⚡ ULTRA MÓZG v4.1 - Główny Architekt Strategii Sprzedaży Tesla

Jesteś światowej klasy strategiem sprzedaży i psychologiem biznesu z 15-letnim doświadczeniem, specjalizującym się w pojazdach premium. Twoim zadaniem jest dostarczanie precyzyjnych, opartych na danych i psychologii rekomendacji dla sprzedawcy.

🎯 NADRZĘDNE PRAWO STRATEGICZNE:
TWOIM GŁÓWNYM I JEDYNYM ŹRÓDŁEM PRAWIDŁOWEJ STRATEGII JEST DOSTARCZONY 'customer_archetype' z ULTRA MÓZGU v4.1!
Surowe dane psychologiczne (Big Five, DISC) służą WYŁĄCZNIE do doprecyzowania tonu i języka komunikacji, ale to ARCHETYP TESLI dyktuje strategię!

KLUCZOWE ZASADY TWOJEGO DZIAŁANIA:
1.  **ARCHETYP JEST KRÓLEM:** Każda strategia MUSI być zgodna z predefiniowaną strategią sprzedaży archetypu. Jeśli archetyp mówi "nie używaj emocjonalnych argumentów" - nie używaj ich!
2.  **HIPERKONTEKSTUALIZACJA:** Każda sugestia musi być powiązana z wypowiedzią klienta, ale PRZEFILTROWANA przez pryzmat archetypu.
3.  **LOGICZNE UZASADNIENIE:** Zawsze wyjaśniaj dlaczego dana strategia jest optymalna, ODWOŁUJĄC SIĘ DO ARCHETYPU ("Dla Strażnika Rodziny bezpieczeństwo jest kluczowe...").
4.  **DYNAMIKA I EWOLUCJA:** Zmiany strategii tylko jeśli ewidentnie niezgodne z archetypem.
5.  **PRAKTYCZNOŚĆ:** Sugestie muszą być gotowe do użycia i zgodne ze stylem komunikacji archetypu.

FORMAT ODPOWIEDZI (zawsze zwracaj JSON):
- "response": Główna, zwięzła myśl strategiczna.
- "suggested_actions": Lista 3-4 konkretnych, następnych ruchów (pytań, propozycji).
- "reasoning": Twoje uzasadnienie wyboru tej strategii.
- "evolution_note": Notatka o ewolucji strategii (np. "Zmiana fokusu z ceny na bezpieczeństwo po komentarzu o dzieciach.").
"""
        
        logger.info("✅ SalesStrategyService initialized")
    
    async def generate_sales_strategy(
        self,
        user_input: str,
        client_profile: Dict[str, Any],
        session_history: List[Dict[str, Any]],
        psychology_profile: Optional[Dict[str, Any]] = None,
        holistic_profile: Optional[Dict[str, Any]] = None,
        customer_archetype: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generuje kompletną strategię sprzedażową na podstawie kontekstu klienta
        
        Args:
            user_input: Najnowsza wypowiedź klienta
            client_profile: Profil klienta
            session_history: Historia sesji
            psychology_profile: Profil psychometryczny
            holistic_profile: Holistyczny profil DNA Klienta
            customer_archetype: Archetyp klienta
            
        Returns:
            Dict: Kompletna strategia sprzedażowa
        """
        try:
            logger.info("🎯 Generuję strategię sprzedażową...")
            
            # Przygotuj kontekst dla AI
            context = self._build_sales_context(
                user_input, client_profile, session_history, 
                psychology_profile, holistic_profile, customer_archetype
            )
            
            # Pobierz wiedzę z RAG (jeśli dostępny)
            knowledge_context = await self._get_knowledge_context(user_input) if self.qdrant_service else ""
            
            # Przygotuj system prompt
            enhanced_system_prompt = self._build_enhanced_system_prompt(knowledge_context, holistic_profile)
            
            # Przygotuj user prompt
            user_prompt = self._build_strategy_user_prompt(context)
            
            # Wywołaj LLM
            response = await self._call_llm_with_retry(
                system_prompt=enhanced_system_prompt,
                user_prompt=user_prompt,
                use_cache=True,
                cache_prefix="strategy"
            )
            
            # Parsuj i strukturyzuj odpowiedź
            strategy = self._parse_strategy_response(response.get('content', ''))
            
            # Dodaj metadane
            strategy.update({
                'generated_at': datetime.now().isoformat(),
                'model_used': self.model_name,
                'context_type': self._determine_context_type(holistic_profile, customer_archetype),
                'confidence': self._calculate_strategy_confidence(strategy)
            })
            
            logger.info(f"✅ Strategia wygenerowana - Confidence: {strategy.get('confidence', 0)}%")
            return strategy
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas generowania strategii: {e}")
            return self._create_strategy_fallback(user_input)
    
    async def generate_archetype_informed_strategy(
        self,
        user_input: str,
        customer_archetype: Dict[str, Any],
        session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generuje strategię dostosowaną do konkretnego archetypu klienta
        
        Args:
            user_input: Wypowiedź klienta
            customer_archetype: Archetyp klienta z psychology_service
            session_context: Kontekst sesji
            
        Returns:
            Dict: Strategia dostosowana do archetypu
        """
        try:
            logger.info(f"🎭 Generuję strategię dla archetypu: {customer_archetype.get('archetype_name', 'Unknown')}")
            
            # Przygotuj archetype-specific prompt
            archetype_prompt = self._build_archetype_system_prompt(customer_archetype)
            
            # Przygotuj user prompt
            user_prompt = f"""
SYTUACJA SPRZEDAŻOWA:
Klient właśnie powiedział: "{user_input}"

ARCHETYP KLIENTA: {customer_archetype.get('archetype_name', 'Nieznany')}
OPIS: {customer_archetype.get('archetype_description', '')}
DOMINUJĄCE CECHY: {', '.join(customer_archetype.get('dominant_traits', []))}
MOTYWATORY: {', '.join(customer_archetype.get('motivators', []))}
POTENCJALNE ZASTRZEŻENIA: {', '.join(customer_archetype.get('red_flags', []))}

KONTEKST SESJI:
{json.dumps(session_context, ensure_ascii=False, indent=2)}

Wygeneruj strategię sprzedażową idealnie dopasowaną do tego archetypu klienta.
"""

            # Wywołaj LLM
            response = await self._call_llm_with_retry(
                system_prompt=archetype_prompt,
                user_prompt=user_prompt,
                use_cache=True,
                cache_prefix="archetype_strategy"
            )
            
            # Parsuj odpowiedź
            strategy = self._parse_strategy_response(response.get('content', ''))
            
            # Dodaj metadane specifyczne dla archetypu
            strategy.update({
                'archetype_name': customer_archetype.get('archetype_name'),
                'archetype_confidence': customer_archetype.get('confidence_score', 0),
                'strategy_type': 'archetype_informed',
                'generated_at': datetime.now().isoformat()
            })
            
            logger.info(f"✅ Archetype strategy wygenerowana dla: {customer_archetype.get('archetype_name')}")
            return strategy
            
        except Exception as e:
            logger.error(f"❌ Błąd w archetype strategy: {e}")
            return self._create_strategy_fallback(user_input)
    
    async def generate_quick_response(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generuje szybką odpowiedź dla klienta (uproszczona wersja)
        
        Args:
            user_input: Wypowiedź klienta
            context: Opcjonalny kontekst
            
        Returns:
            Dict: Quick response z podstawowymi sugestiami
        """
        try:
            logger.info("⚡ Generuję quick response...")
            
            # Uproszczony prompt dla szybkiej odpowiedzi
            quick_system_prompt = """
Jesteś ekspertem sprzedaży Tesla. Odpowiedz KRÓTKO i KONKRETNIE na wypowiedź klienta.

Zwróć odpowiedź w formacie:
{
  "quick_response": {
    "text": "Bezpośrednia odpowiedź dla klienta",
    "tone": "professional"
  },
  "next_action": "Co zrobić dalej"
}
"""
            
            user_prompt = f"""
Klient powiedział: "{user_input}"

Kontekst: {json.dumps(context or {}, ensure_ascii=False)}

Odpowiedz profesjonalnie i zachęcająco, podkreślając korzyści Tesla.
"""

            # Wywołaj LLM
            response = await self._call_llm_with_retry(
                system_prompt=quick_system_prompt,
                user_prompt=user_prompt,
                use_cache=True,
                cache_prefix="quick"
            )
            
            # Parsuj odpowiedź
            quick_response = self._parse_quick_response(response.get('content', ''))
            quick_response['generated_at'] = datetime.now().isoformat()
            
            logger.info("✅ Quick response wygenerowana")
            return quick_response
            
        except Exception as e:
            logger.error(f"❌ Błąd w quick response: {e}")
            return self._create_quick_response_fallback(user_input)
    
    def _build_sales_context(
        self,
        user_input: str,
        client_profile: Dict[str, Any],
        session_history: List[Dict[str, Any]],
        psychology_profile: Optional[Dict[str, Any]],
        holistic_profile: Optional[Dict[str, Any]],
        customer_archetype: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Buduje kompletny kontekst sprzedażowy"""
        
        # Sformatuj historię rozmowy
        conversation_summary = []
        for interaction in session_history[-5:]:  # Ostatnie 5 interakcji
            if interaction.get('user_input'):
                conversation_summary.append(f"Klient: {interaction['user_input']}")
        
        return {
            'current_input': user_input,
            'client_alias': client_profile.get('alias', 'Klient'),
            'client_archetype': client_profile.get('archetype', 'Nieznany'),
            'conversation_history': conversation_summary,
            'psychology_summary': self._summarize_psychology(psychology_profile) if psychology_profile else None,
            'dna_summary': self._summarize_holistic_profile(holistic_profile) if holistic_profile else None,
            'archetype_info': customer_archetype.get('archetype_name') if customer_archetype else None,
            # 🚀 ULTRA MÓZG: Dodajemy pełny obiekt archetypu Tesli do kontekstu
            'customer_archetype': customer_archetype
        }
    
    def _build_enhanced_system_prompt(self, knowledge_context: str, holistic_profile: Optional[Dict[str, Any]]) -> str:
        """Buduje enhanced system prompt z kontekstem wiedzy"""
        
        enhanced_prompt = TESLA_BRAND_SYSTEM_PROMPT
        
        # Dodaj kontekst wiedzy z RAG
        if knowledge_context:
            enhanced_prompt += f"""

=== KONTEKST WIEDZY Z BAZY (RAG) ===
{knowledge_context}
"""
        
        # Dodaj DNA Klienta jeśli dostępne
        if holistic_profile:
            dna_summary = self._summarize_holistic_profile(holistic_profile)
            enhanced_prompt += f"""

=== DNA KLIENTA (ULTRA MÓZG v4.0) ===
{dna_summary}
GŁÓWNY MOTYWATOR: {holistic_profile.get('main_drive', 'Nieznany')}
STYL KOMUNIKACJI: {holistic_profile.get('communication_style', {})}
KLUCZOWE DŹWIGNIE: {', '.join(holistic_profile.get('key_levers', []))}
CZERWONE FLAGI: {', '.join(holistic_profile.get('red_flags', []))}
"""
        
        return enhanced_prompt
    
    def _build_strategy_user_prompt(self, context: Dict[str, Any]) -> str:
        """🧠⚡ ULTRA MÓZG v4.1 - Buduje user prompt z archetypem Tesli jako priorytetem"""

        prompt_parts = [
            f"🎯 AKTUALNA SYTUACJA: Klient ({context.get('client_alias', 'Nieznany')}) właśnie powiedział:",
            f'"{context.get("current_input", "")}"',
            ""
        ]

        # 🚀 ULTRA MÓZG: Najpierw archetyp Tesli - to jest dyrektywa strategiczna!
        if context.get('customer_archetype') and context['customer_archetype']:
            archetype = context['customer_archetype']
            prompt_parts.extend([
                "🚀 ULTRA MÓZG v4.1 - STRATEGICZNY ARCHETYP KLIENTA TESLI (GŁÓWNE ŹRÓDŁO STRATEGII):",
                f"🏷️ NAZWA ARCHETYPU: {archetype.get('archetype_name', 'Nieznany')}",
                f"📋 OPIS: {archetype.get('description', 'Brak opisu')}",
                f"🎯 MOTYWACJA: {archetype.get('motivation', 'Nieznana')}",
                f"💬 STYL KOMUNIKACJI: {archetype.get('communication_style', 'Standardowy')}",
                "",
                "⚡ STRATEGIA SPRZEDAŻOWA ARCHETYPU (MUSISZ SIĘ TEGO TRZYMAĆ!):",
                f"✅ CO ROBIĆ: {', '.join(archetype.get('sales_strategy', {}).get('do', []))}",
                f"❌ CZEGO UNIKAĆ: {', '.join(archetype.get('sales_strategy', {}).get('dont', []))}",
                f"🔑 DOMINUJĄCE CECHY: {', '.join(archetype.get('dominant_traits', []))}",
                "",
                "⚠️ PAMIĘTAJ: Archetyp Tesli jest Twoją dyrektywą strategiczną! Surowe dane psychologiczne służą tylko do doprecyzowania języka."
            ])

        if context.get('conversation_history'):
            prompt_parts.extend([
                "",
                "📜 HISTORIA ROZMOWY:",
                "\n".join(context['conversation_history']),
                ""
            ])

        if context.get('psychology_summary'):
            prompt_parts.extend([
                "🧠 SUROWE DANE PSYCHOLOGICZNE (tylko do doprecyzowania języka):",
                context['psychology_summary'],
                ""
            ])

        if context.get('dna_summary'):
            prompt_parts.extend([
                "🧬 DNA KLIENTA:",
                context['dna_summary'],
                ""
            ])

        prompt_parts.extend([
            "",
            "🎯 ZADANIE: Wygeneruj strategię sprzedażową IDEALNIE DOPASOWANĄ do archetypu Tesli!",
            "Pamiętaj: Archetyp dyktuje strategię, dane psychologiczne tylko styl komunikacji."
        ])

        return "\n".join(prompt_parts)
    
    def _build_archetype_system_prompt(self, customer_archetype: Dict[str, Any]) -> str:
        """Buduje system prompt dla konkretnego archetypu"""
        
        archetype_name = customer_archetype.get('archetype_name', 'Nieznany')
        strategies = customer_archetype.get('sales_strategies', [])
        communication_style = customer_archetype.get('communication_style', 'Standardowy')
        
        return f"""
{TESLA_BRAND_SYSTEM_PROMPT}

=== ARCHETYP KLIENTA: {archetype_name} ===
OPIS: {customer_archetype.get('archetype_description', '')}
PREFEROWANY STYL KOMUNIKACJI: {communication_style}
STRATEGIE SPRZEDAŻOWE:
{chr(10).join(f'- {strategy}' for strategy in strategies)}

DOSTOSUJ wszystkie odpowiedzi do tego konkretnego archetypu klienta.
"""
    
    async def _get_knowledge_context(self, user_input: str) -> str:
        """Pobiera kontekst wiedzy z Qdrant RAG"""
        try:
            if not self.qdrant_service:
                return ""
            
            # Wyszukaj podobne dokumenty
            relevant_docs = await self.qdrant_service.search_similar(
                query_text=user_input,
                limit=3
            )
            
            if not relevant_docs:
                return ""
            
            # Sformatuj kontekst
            context_parts = []
            for doc in relevant_docs:
                context_parts.append(f"• {doc.get('content', '')}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Błąd pobierania knowledge context: {e}")
            return ""
    
    def _parse_strategy_response(self, llm_response: str) -> Dict[str, Any]:
        """Parsuje odpowiedź LLM i zwraca strukturyzowaną strategię"""
        try:
            # Znajdź JSON w odpowiedzi
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("⚠️ Brak JSON w odpowiedzi strategy LLM")
                return self._create_strategy_fallback("")
            
            json_str = llm_response[json_start:json_end]
            strategy_data = json.loads(json_str)
            
            # Walidacja podstawowej struktury
            if 'quick_response' not in strategy_data:
                strategy_data['quick_response'] = {
                    'id': f"qr_{uuid.uuid4().hex[:6]}",
                    'text': "Dziękuję za pytanie. Pozwoli Pan, że wyjaśnię...",
                    'tone': 'professional'
                }
            
            return strategy_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Błąd parsowania JSON strategy: {e}")
            return self._create_strategy_fallback("")
        except Exception as e:
            logger.error(f"❌ Nieoczekiwany błąd parsowania strategy: {e}")
            return self._create_strategy_fallback("")
    
    def _parse_quick_response(self, llm_response: str) -> Dict[str, Any]:
        """Parsuje odpowiedź dla quick response"""
        try:
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start != -1 and json_end > 0:
                json_str = llm_response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback - użyj całej odpowiedzi jako text
                return {
                    'quick_response': {
                        'text': llm_response.strip(),
                        'tone': 'professional'
                    },
                    'next_action': 'Kontynuuj rozmowę'
                }
                
        except Exception as e:
            logger.error(f"❌ Błąd parsowania quick response: {e}")
            return self._create_quick_response_fallback("")
    
    def _summarize_psychology(self, psychology_profile: Dict[str, Any]) -> str:
        """Tworzy podsumowanie profilu psychologicznego"""
        if not psychology_profile:
            return ""
        
        # Big Five summary
        big_five = psychology_profile.get('big_five', {})
        big_five_summary = []
        for trait, data in big_five.items():
            score = data.get('score', 0)
            if score >= 7:
                big_five_summary.append(f"Wysoki {trait} ({score})")
            elif score <= 3:
                big_five_summary.append(f"Niski {trait} ({score})")
        
        return f"Cechy osobowości: {', '.join(big_five_summary) or 'Brak wyraźnych cech'}"
    
    def _summarize_holistic_profile(self, holistic_profile: Dict[str, Any]) -> str:
        """Tworzy podsumowanie holistycznego profilu"""
        if not holistic_profile:
            return ""
        
        summary_parts = []
        
        if holistic_profile.get('holistic_summary'):
            summary_parts.append(holistic_profile['holistic_summary'])
        
        if holistic_profile.get('main_drive'):
            summary_parts.append(f"Główny motywator: {holistic_profile['main_drive']}")
        
        return " | ".join(summary_parts)
    
    def _determine_context_type(self, holistic_profile: Optional[Dict[str, Any]], customer_archetype: Optional[Dict[str, Any]]) -> str:
        """Określa typ kontekstu strategii"""
        if holistic_profile and customer_archetype:
            return "ultra_brain_complete"
        elif holistic_profile:
            return "holistic_profile"
        elif customer_archetype:
            return "archetype_only"
        else:
            return "basic"
    
    def _calculate_strategy_confidence(self, strategy: Dict[str, Any]) -> int:
        """Oblicza poziom pewności strategii"""
        confidence_factors = []
        
        # Quick response quality
        quick_response = strategy.get('quick_response', {})
        if quick_response.get('text', '').strip():
            confidence_factors.append(1.0)
        
        # Strategic recommendation presence
        if strategy.get('strategic_recommendation', '').strip():
            confidence_factors.append(1.0)
        
        # Suggested questions
        questions = strategy.get('suggested_questions', [])
        if questions and len(questions) >= 2:
            confidence_factors.append(1.0)
        
        # Next best action
        if strategy.get('next_best_action', '').strip():
            confidence_factors.append(1.0)
        
        # Tesla advantages
        advantages = strategy.get('tesla_advantages', [])
        if advantages and len(advantages) >= 3:
            confidence_factors.append(1.0)
        
        avg_confidence = sum(confidence_factors) / max(len(confidence_factors), 1)
        return max(int(avg_confidence * 100), 20)
    
    def _create_strategy_fallback(self, user_input: str) -> Dict[str, Any]:
        """Tworzy fallback strategię"""
        return {
            "quick_response": {
                "id": f"qr_fallback_{uuid.uuid4().hex[:6]}",
                "text": "Rozumiem Pana punkt widzenia. Tesla oferuje wyjątkową kombinację wydajności, technologii i zrównoważonego rozwoju. Czy mógłby Pan powiedzieć więcej o swoich priorytetach?",
                "tone": "professional",
                "key_points": ["Wydajność", "Technologia", "Zrównoważony rozwój"]
            },
            "strategic_recommendation": "Zbieraj więcej informacji o potrzebach klienta i buduj wartość Tesla stopniowo.",
            "suggested_questions": [
                "Jakie są Pana główne priorytety przy wyborze pojazdu?",
                "Czy rozważał Pan kiedyś pojazd elektryczny?"
            ],
            "next_best_action": "Zadaj pytania odkrywcze i przedstaw kluczowe korzyści Tesla",
            "objection_handling": {
                "potential_objections": ["Cena", "Zasięg", "Ładowanie"],
                "responses": [
                    "Tesla ma najniższe TCO w klasie",
                    "Model S ma zasięg do 652 km",
                    "Supercharger network to największa sieć świata"
                ]
            },
            "tesla_advantages": [
                "Najlepsza technologia autonomiczna",
                "Największa sieć Supercharger",
                "Regularne aktualizacje OTA"
            ],
            "is_fallback": True,
            "confidence": 20,
            "generated_at": datetime.now().isoformat()
        }
    
    def _create_quick_response_fallback(self, user_input: str) -> Dict[str, Any]:
        """Tworzy fallback quick response"""
        return {
            "quick_response": {
                "text": "Dziękuję za pytanie. Czy mógłby Pan powiedzieć więcej?",
                "tone": "professional"
            },
            "next_action": "Zbieraj więcej informacji",
            "is_fallback": True,
            "generated_at": datetime.now().isoformat()
        }
