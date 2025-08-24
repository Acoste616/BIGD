"""
SessionPsychologyEngine v3.0 - Fundamentalna Refaktoryzacja
MÓZG systemu psychometrycznego na poziomie sesji

Filozofia: Jeden, ewoluujący profil psychologiczny per sesja
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.core.database import engine  # KRYTYCZNA NAPRAWA: Fresh session dla background task

from app.models.domain import Session, Interaction, Client
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

class SessionPsychologyEngine:
    """
    CORE ENGINE: Silnik Psychologiczny na Poziomie Sesji
    
    Odpowiada za:
    1. Ciągłe budowanie profilu psychologicznego przez całą sesję
    2. Konwersję suggested_questions na interaktywne pytania
    3. Syntezę profilu w Customer Archetype
    4. Zarządzanie confidence levels
    """
    
    # ETAP 5: Predefiniowane Archetypy Klientów
    CUSTOMER_ARCHETYPES = {
        "analityk": {
            "name": "🔬 Analityk",
            "description": "Wysoka Sumienność, Compliance (DISC), Wartość: Bezpieczeństwo",
            "psychological_profile": {
                "big_five": {"conscientiousness": "high", "openness": "medium"},
                "disc": {"compliance": "high", "steadiness": "medium"}, 
                "schwartz": ["security", "conformity"]
            },
            "sales_strategy": {
                "do": ["Dostarczaj twarde dane i statystyki", "Prezentuj TCO i ROI", "Dawaj czas na przemyślenie"],
                "dont": ["Nie naciskaj na szybką decyzję", "Nie pomijaj szczegółów technicznych", "Nie używaj emocjonalnych argumentów"]
            }
        },
        "wizjoner": {
            "name": "🚀 Wizjoner", 
            "description": "Wysoka Otwartość, Dominance + Influence (DISC), Wartość: Osiągnięcia",
            "psychological_profile": {
                "big_five": {"openness": "high", "extraversion": "high"},
                "disc": {"dominance": "high", "influence": "high"},
                "schwartz": ["achievement", "self_direction"]
            },
            "sales_strategy": {
                "do": ["Podkreślaj innowacyjność i przyszłość", "Mów o statusie i prestiżu", "Prezentuj wizję długoterminową"],
                "dont": ["Nie skupiaj się tylko na kosztach", "Nie wdawaj w nadmierne szczegóły", "Nie ograniczaj do obecnych potrzeb"]
            }
        },
        "relacyjny_budowniczy": {
            "name": "🤝 Relacyjny Budowniczy",
            "description": "Wysoka Ugodowość, Steadiness (DISC), Wartość: Życzliwość", 
            "psychological_profile": {
                "big_five": {"agreeableness": "high", "conscientiousness": "medium"},
                "disc": {"steadiness": "high", "influence": "medium"},
                "schwartz": ["benevolence", "tradition"]
            },
            "sales_strategy": {
                "do": ["Buduj osobistą relację", "Podkreślaj korzyści dla zespołu/rodziny", "Używaj referencji i opinii"],
                "dont": ["Nie bądź zbyt agresywny", "Nie ignoruj emocji i relacji", "Nie podejmuj za niego decyzji"]
            }
        },
        "szybki_decydent": {
            "name": "⚡ Szybki Decydent",
            "description": "Wysoka Ekstrawersja, Dominance (DISC), Wartość: Władza",
            "psychological_profile": {
                "big_five": {"extraversion": "high", "conscientiousness": "low"},
                "disc": {"dominance": "high", "compliance": "low"},
                "schwartz": ["power", "achievement"]
            },
            "sales_strategy": {
                "do": ["Prezentuj kluczowe korzyści szybko", "Podkreślaj przewagę konkurencyjną", "Oferuj natychmiastowe działanie"],
                "dont": ["Nie przeciągaj prezentacji", "Nie wdawaj się w szczegóły techniczne", "Nie zwlekaj z ofertą"]
            }
        }
    }

    async def update_cumulative_profile(self, session_id: int, old_db: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        GŁÓWNA FUNKCJA LOGIKI - Uruchamiana po każdej nowej interakcji
        
        KRYTYCZNA NAPRAWA v3.0: Tworzy świeżą sesję DB dla background task
        
        1. Pobiera sesję i CAŁĄ historię interakcji
        2. Pobiera obecny cumulative_psychology 
        3. Tworzy potężny prompt dla AI z całą historią + obecnym profilem
        4. AI zwraca: zaktualizowany profil + confidence + suggested_questions + archetyp
        5. Zapisuje wyniki w session
        """
        # KRYTYCZNA NAPRAWA: Stwórz świeżą, dedykowaną sesję dla background task
        async with AsyncSession(engine) as fresh_db:
            try:
                logger.info(f"🧠 [SESSION ENGINE FRESH] Rozpoczynam update cumulative profile dla sesji {session_id}")
                
                # 1. Pobierz sesję z całą historią interakcji
                query = (
                    select(Session)
                    .options(selectinload(Session.interactions))
                    .where(Session.id == session_id)
                )
                result = await fresh_db.execute(query)
                session = result.scalar_one_or_none()
                
                if not session:
                    raise ValueError(f"Sesja {session_id} nie została znaleziona")
                
                # 2. Zbuduj pełną historię rozmowy
                conversation_history = self._build_session_conversation_history(session.interactions)
                current_profile = session.cumulative_psychology if session.cumulative_psychology else {}
                current_confidence = int(session.psychology_confidence) if session.psychology_confidence else 0
                
                logger.info(f"🧠 [SESSION ENGINE] Historia: {len(session.interactions)} interakcji, obecny confidence: {current_confidence}%")
                
                # 3. Stwórz enhanced prompt dla AI z całym kontekstem
                psychology_prompt = self._build_cumulative_psychology_prompt(
                    conversation_history, 
                    current_profile, 
                    current_confidence
                )
                
                # 4. Wywołaj AI service
                ai_response = await asyncio.to_thread(
                    ai_service._sync_ollama_call,
                    psychology_prompt,
                    "Wykonaj analizę psychometryczną zgodnie z instrukcjami w system prompt."
                )
                
                # 5. Parsuj odpowiedź AI
                parsed_result = self._parse_psychology_ai_response(ai_response)
                
                if parsed_result:
                    # 6. Konwertuj suggested_questions na interactive format
                    interactive_questions = self._convert_to_interactive_questions(
                        parsed_result.get('suggested_questions', [])
                    )
                    
                    # 7. Zaktualizuj sesję
                    await self._update_session_psychology(
                        fresh_db, session_id, parsed_result, interactive_questions
                    )
                    
                    logger.info(f"✅ [SESSION ENGINE] Profile updated: confidence={parsed_result.get('psychology_confidence', 0)}%")
                    return parsed_result
                else:
                    logger.warning(f"⚠️ [SESSION ENGINE] Brak parsowanych wyników dla sesji {session_id}")
                    return {}
                
            except Exception as e:
                logger.error(f"❌ [SESSION ENGINE FRESH] Błąd podczas update profile sesji {session_id}: {e}")
                await fresh_db.rollback()
                return {}

    async def answer_clarifying_question(self, session_id: int, question_id: str, answer: str, db: AsyncSession):
        """
        Uruchamiana gdy sprzedawca kliknie odpowiedź na pytanie pomocnicze
        
        1. Tworzy "sztuczną" interakcję z odpowiedzią sprzedawcy
        2. Usuwa odpowiedziane pytanie z active_clarifying_questions  
        3. Ponownie uruchamia full cycle update_cumulative_profile
        """
        try:
            logger.info(f"🎯 [CLARIFYING] Przetwarzam odpowiedź na pytanie {question_id}: {answer}")
            
            # 1. Pobierz sesję
            query = select(Session).where(Session.id == session_id)
            result = await db.execute(query)
            session = result.scalar_one_or_none()
            
            if not session:
                raise ValueError(f"Sesja {session_id} nie została znaleziona")
                
            # 2. Znajdź pytanie w active_clarifying_questions
            active_questions = list(session.active_clarifying_questions) if session.active_clarifying_questions else []
            answered_question = None
            remaining_questions = []
            
            for q in active_questions:
                if q.get('id') == question_id:
                    answered_question = q
                else:
                    remaining_questions.append(q)
            
            if not answered_question:
                raise ValueError(f"Pytanie {question_id} nie zostało znalezione w aktywnych pytaniach")
            
            # 3. Stwórz "sztuczną" interakcję z odpowiedzią sprzedawcy
            observation_text = f"Sprzedawca zaobserwował: {answered_question.get('question', '')} - Odpowiedź: {answer}"
            
            # Dodaj observation do psychological context (nie tworzymy fizycznej interakcji)
            current_profile = dict(session.cumulative_psychology) if session.cumulative_psychology else {}
            if 'observations' not in current_profile:
                current_profile['observations'] = []
            
            current_profile['observations'].append({
                'question': answered_question.get('question', ''),
                'answer': answer,
                'timestamp': datetime.now().isoformat(),
                'psychological_target': answered_question.get('psychological_target', 'general')
            })
            
            # 4. Usuń odpowiedziane pytanie
            await db.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(
                    active_clarifying_questions=remaining_questions,
                    cumulative_psychology=current_profile
                )
            )
            await db.commit()
            
            # 5. Uruchom full cycle update
            updated_profile = await self.update_cumulative_profile(session_id, db)
            
            logger.info(f"✅ [CLARIFYING] Pytanie {question_id} processed, pozostało {len(remaining_questions)} pytań")
            return updated_profile
            
        except Exception as e:
            logger.error(f"❌ [CLARIFYING] Błąd podczas answer_clarifying_question: {e}")
            raise

    def _build_session_conversation_history(self, interactions: List[Interaction]) -> str:
        """Buduje pełną historię konwersacji sesji dla AI"""
        if not interactions:
            return "BRAK HISTORII ROZMOWY"
            
        history_parts = ["=== HISTORIA CAŁEJ SESJI ==="]
        
        # Sortuj interactions po timestamp (convert Column to datetime)
        sorted_interactions = sorted(interactions, key=lambda x: x.timestamp.timestamp() if hasattr(x.timestamp, 'timestamp') else x.timestamp)
        
        for i, interaction in enumerate(sorted_interactions):
            timestamp = interaction.timestamp.strftime("%H:%M:%S")
            history_parts.append(f"[{i+1}] {timestamp} - Sprzedawca: {interaction.user_input}")
            
            # Dodaj insights z AI response jeśli są
            if interaction.ai_response_json:
                insights = interaction.ai_response_json.get('main_analysis', '')
                if insights:
                    history_parts.append(f"    AI Insight: {insights[:200]}...")
        
        history_parts.append("=== KONIEC HISTORII ===")
        return "\n".join(history_parts)

    def _build_cumulative_psychology_prompt(self, history: str, current_profile: Dict, confidence: int) -> str:
        """
        Tworzy enhanced prompt dla AI z full context
        """
        archetyp_definitions = "\n".join([
            f"- {archetype['name']}: {archetype['description']}" 
            for archetype in self.CUSTOMER_ARCHETYPES.values()
        ])
        
        return f"""
Jesteś ekspertem psychologii sprzedaży prowadzącym CIĄGŁĄ, EWOLUUJĄCĄ analizę klienta na poziomie CAŁEJ SESJI.

TWOJE ZADANIE - 4 KROKI:

KROK 1 - AKTUALIZACJA PROFILU:
Na podstawie pełnej historii sesji i obecnego profilu, zaktualizuj i rozwiń profil psychometryczny klienta.
Uwzględnij WSZYSTKIE interakcje i obserwacje sprzedawcy.

KROK 2 - OCENA PEWNOŚCI:
Oblicz nowy poziom pewności analizy (0-100%) na podstawie ilości i jakości dostępnych danych.

KROK 3 - SUGGESTED QUESTIONS:
Jeśli pewność < 80%, wygeneruj 2-4 konkretne pytania które sprzedawca może zadać klientowi lub zaobserwować.

KROK 4 - SYNTEZA ARCHETYPU (KLUCZOWE!):
Jeśli pewność >= 70%, wykonaj natychmiastową syntezę:
1. Przeanalizuj cały profil psychologiczny (Big Five + DISC + Wartości Schwartza)
2. Przypisz klienta do najlepiej pasującego archetypu:
{archetyp_definitions}
3. Wygeneruj 3 konkretne porady "Rób to / Nie rób tego" specyficzne dla tego archetypu i tego konkretnego klienta

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
  }}
}}
"""

    def _parse_psychology_ai_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Parsuje odpowiedź AI z analizą psychometryczną"""
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
            
            logger.info(f"🧠 [DEBUG BIG FIVE] {big_five}")
            logger.info(f"🎯 [DEBUG DISC] {disc}")  
            logger.info(f"👤 [DEBUG ARCHETYPE] {archetype}")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ [PSYCHOLOGY PARSE] JSON decode error: {e}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ [PSYCHOLOGY PARSE] Unexpected error: {e}")
            return None

    def _convert_to_interactive_questions(self, suggested_questions: List[Dict]) -> List[Dict]:
        """
        ETAP 3: Konwertuje suggested_questions na format interaktywnych pytań dla UI
        
        Z: {"question": "Czy klient pyta o TCO?", "psychological_target": "conscientiousness"}
        Do: {"id": "q1", "question": "Czy klient pyta o TCO?", "option_a": "Tak, pyta", "option_b": "Nie, nie pyta"}
        """
        interactive_questions = []
        
        for i, sq in enumerate(suggested_questions):
            question_text = sq.get('question', '')
            psychological_target = sq.get('psychological_target', 'general assessment')
            
            # Generate sensible A/B options based on question type
            if any(word in question_text.lower() for word in ['czy', 'jak często', 'jakie']):
                option_a = "Tak, potwierdza"
                option_b = "Nie, zaprzecza"
            elif 'jak' in question_text.lower():
                option_a = "Szybko, bezpośrednio" 
                option_b = "Powoli, szczegółowo"
            elif 'co' in question_text.lower():
                option_a = "Korzyści ogólne"
                option_b = "Szczegóły techniczne"
            else:
                option_a = "Potwierdza"
                option_b = "Zaprzecza"
            
            interactive_questions.append({
                "id": f"sq_{i+1}",
                "question": question_text,
                "option_a": option_a,
                "option_b": option_b,
                "psychological_target": psychological_target
            })
        
        return interactive_questions

    async def _update_session_psychology(
        self, 
        db: AsyncSession, 
        session_id: int, 
        ai_result: Dict[str, Any], 
        interactive_questions: List[Dict]
    ):
        """Zapisuje wyniki analizy w sesji"""
        try:
            update_data = {
                'cumulative_psychology': ai_result.get('cumulative_psychology'),
                'psychology_confidence': ai_result.get('psychology_confidence', 0),
                'active_clarifying_questions': interactive_questions,
                'customer_archetype': ai_result.get('customer_archetype'),
                'psychology_updated_at': datetime.now()
            }
            
            await db.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(**update_data)
            )
            await db.commit()
            
            logger.info(f"✅ [SESSION UPDATE] Psychology data saved for session {session_id}")
            
        except Exception as e:
            logger.error(f"❌ [SESSION UPDATE] Error updating session {session_id}: {e}")
            raise

# Singleton instance
session_psychology_engine = SessionPsychologyEngine()
