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
    
    # ETAP 5: Predefiniowane Archetypy Klientów - OGÓLNE
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

    # ETAP 6: Strategiczne Archetypy Klientów Tesli - ULTRA MÓZG v4.1
    TESLA_CUSTOMER_ARCHETYPES = {
        "zdobywca_statusu": {
            "name": "🏆 Zdobywca Statusu",
            "description": "Percepcja Tesli jako symbolu sukcesu i prestiżu. Klient, który postrzega zakup Tesli jako inwestycję w swój wizerunek i pozycję społeczną.",
            "dominant_traits": ["extraversion", "dominance_disc"],
            "psychological_profile": {
                "big_five": {"extraversion": "high", "conscientiousness": "medium"},
                "disc": {"dominance": "high", "influence": "high"},
                "schwartz": ["achievement", "power"]
            },
            "sales_strategy": {
                "do": [
                    "Podkreślaj ekskluzywność i prestiż marki Tesla",
                    "Mów o statusie właściciela Tesli w społeczeństwie",
                    "Prezentuj Teslę jako symbol sukcesu i innowacyjności",
                    "Używaj języka sukcesu i przywództwa",
                    "Podkreślaj unikalność - 'nie każdy może mieć Teslę'"
                ],
                "dont": [
                    "Nie skupiaj się tylko na aspektach technicznych",
                    "Nie pomniejszaj znaczenia wizerunku i statusu",
                    "Nie używaj argumentów czysto ekonomicznych",
                    "Nie porównuj z konkurencją w kategoriach ceny"
                ]
            },
            "motivation": "Status społeczny i prestiż",
            "communication_style": "Entuzjastyczny, skoncentrowany na korzyściach wizerunkowych"
        },
        "straznik_rodziny": {
            "name": "👨‍👩‍👧‍👦 Strażnik Rodziny",
            "description": "Priorytetem jest bezpieczeństwo i ochrona najbliższych. Tesla postrzegana jako najbezpieczniejszy wybór dla rodziny.",
            "dominant_traits": ["conscientiousness", "steadiness_disc"],
            "psychological_profile": {
                "big_five": {"conscientiousness": "high", "agreeableness": "high"},
                "disc": {"steadiness": "high", "compliance": "high"},
                "schwartz": ["security", "benevolence"]
            },
            "sales_strategy": {
                "do": [
                    "Podkreślaj bezpieczeństwo - najwyższe oceny NHTSA",
                    "Mów o ochronie rodziny i dzieci",
                    "Prezentuj technologię Autopilot jako opiekuna",
                    "Używaj języka bezpieczeństwa i zaufania",
                    "Podkreślaj niezawodność i trwałość Tesli"
                ],
                "dont": [
                    "Nie ignoruj aspektów bezpieczeństwa",
                    "Nie bagatelizuj obaw o rodzinę",
                    "Nie skupiaj się wyłącznie na osiągach",
                    "Nie używa języka ryzykanckiego"
                ]
            },
            "motivation": "Bezpieczeństwo i ochrona rodziny",
            "communication_style": "Spokojny, skoncentrowany na bezpieczeństwie"
        },
        "pragmatyczny_analityk": {
            "name": "📊 Pragmatyczny Analityk",
            "description": "Kieruje się danymi, TCO i ROI. Dokładnie analizuje koszty, zasięg, efektywność energetyczną.",
            "dominant_traits": ["conscientiousness", "compliance_disc"],
            "psychological_profile": {
                "big_five": {"conscientiousness": "high", "openness": "medium"},
                "disc": {"compliance": "high", "steadiness": "medium"},
                "schwartz": ["security", "conformity"]
            },
            "sales_strategy": {
                "do": [
                    "Dostarczaj szczegółowe dane TCO i ROI",
                    "Porównuj koszty z konkurentami (na korzyść Tesli)",
                    "Prezentuj fakty o zasięgu i efektywności",
                    "Używaj wykresów, tabel i konkretnych liczb",
                    "Podkreślaj ekonomiczne korzyści długoterminowe"
                ],
                "dont": [
                    "Nie pomijaj aspektów ekonomicznych",
                    "Nie używaj emocjonalnych argumentów",
                    "Nie naciskaj na szybką decyzję",
                    "Nie bagatelizuj kosztów początkowych"
                ]
            },
            "motivation": "Ekonomiczna efektywność i dane",
            "communication_style": "Faktyczny, analityczny, skoncentrowany na liczbach"
        },
        "wizjoner_przyszlosci": {
            "name": "🔮 Wizjoner Przyszłości",
            "description": "Entuzjasta technologii i innowacji. Widzi w Tesli przyszłość transportu i chce być częścią rewolucji.",
            "dominant_traits": ["openness", "influence_disc"],
            "psychological_profile": {
                "big_five": {"openness": "high", "extraversion": "high"},
                "disc": {"influence": "high", "dominance": "medium"},
                "schwartz": ["self_direction", "universalism"]
            },
            "sales_strategy": {
                "do": [
                    "Podkreślaj rewolucyjne technologie Tesli",
                    "Mów o wizji przyszłości transportu elektrycznego",
                    "Prezentuj Autopilot, FSD i przyszłe funkcje",
                    "Używaj języka innowacji i przyszłości",
                    "Podkreślaj rolę Tesli w zrównoważonym rozwoju"
                ],
                "dont": [
                    "Nie skupiaj się tylko na kosztach",
                    "Nie ignoruj aspektów technologicznych",
                    "Nie używa języka konserwatywnego",
                    "Nie porównuj z tradycyjnymi samochodami"
                ]
            },
            "motivation": "Innowacja i przyszłość technologii",
            "communication_style": "Entuzjastyczny, wizjonerski, technologiczny"
        },
        "ekologiczny_aktywista": {
            "name": "🌱 Ekologiczny Aktywista",
            "description": "Świadomy ekologicznie klient, który widzi w Tesli narzędzie do walki ze zmianami klimatu.",
            "dominant_traits": ["agreeableness", "openness"],
            "psychological_profile": {
                "big_five": {"agreeableness": "high", "openness": "high"},
                "disc": {"steadiness": "high", "influence": "medium"},
                "schwartz": ["universalism", "benevolence"]
            },
            "sales_strategy": {
                "do": [
                    "Podkreślaj ekologiczne korzyści Tesli",
                    "Mów o redukcji emisji CO2",
                    "Prezentuj zrównoważony rozwój Gigafactory",
                    "Używaj języka środowiska i przyszłości planety",
                    "Podkreślaj wpływ na przyszłe pokolenia"
                ],
                "dont": [
                    "Nie ignoruj aspektów środowiskowych",
                    "Nie używa języka destrukcyjnego",
                    "Nie skupiaj się wyłącznie na osiągach",
                    "Nie porównuj z tradycyjnymi samochodami bez kontekstu ekologicznego"
                ]
            },
            "motivation": "Środowisko i zrównoważony rozwój",
            "communication_style": "Idealistyczny, skoncentrowany na środowisku"
        },
        "fleet_manager": {
            "name": "🏢 Fleet Manager",
            "description": "Zarządca floty pojazdów, skupia się na efektywności kosztowej, niezawodności i skalowalności.",
            "dominant_traits": ["conscientiousness", "compliance_disc"],
            "psychological_profile": {
                "big_five": {"conscientiousness": "high", "extraversion": "low"},
                "disc": {"compliance": "high", "steadiness": "high"},
                "schwartz": ["security", "conformity"]
            },
            "sales_strategy": {
                "do": [
                    "Podkreślaj korzyści flotowe (TCO, serwis, zarządzanie)",
                    "Prezentuj skalowalność rozwiązań Tesli",
                    "Mów o niezawodności i minimalizacji przestojów",
                    "Używaj języka biznesowego i efektywności",
                    "Podkreślaj korzyści dla całej organizacji"
                ],
                "dont": [
                    "Nie ignoruj aspektów biznesowych",
                    "Nie skupiaj się tylko na indywidualnych korzyściach",
                    "Nie używaj języka emocjonalnego",
                    "Nie pomniejszaj znaczenia kosztów operacyjnych"
                ]
            },
            "motivation": "Efektywność biznesowa i zarządzanie ryzykiem",
            "communication_style": "Profesjonalny, skoncentrowany na biznesie"
        }
    }



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
            active_questions = session.active_clarifying_questions if session.active_clarifying_questions else []
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
            current_profile = dict(session.cumulative_psychology or {})
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
        sorted_interactions = sorted(interactions, key=lambda x: x.timestamp if hasattr(x.timestamp, 'timestamp') else x.timestamp)
        
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
        🧠⚡ ULTRA MÓZG v4.1 - Enhanced prompt z few-shot learning i Zero Null Policy
        """
        archetyp_definitions = "\n".join([
            f"- {archetype['name']}: {archetype['description']}" 
            for archetype in self.CUSTOMER_ARCHETYPES.values()
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
            
            # 🔧 NOWA WARSTWA WALIDACJI - zgodnie z blueprintem
            validated_data = self._validate_and_repair_psychology(parsed_data, None)
            
            # DEBUG: Log szczegółowych danych psychology
            cumulative = validated_data.get('cumulative_psychology', {})
            big_five = cumulative.get('big_five', {})
            disc = cumulative.get('disc', {})
            archetype = validated_data.get('customer_archetype', {})
            
            logger.info(f"🧠 [DEBUG BIG FIVE] {len([k for k,v in big_five.items() if v.get('score')])} traits validated")
            logger.info(f"🎯 [DEBUG DISC] {len([k for k,v in disc.items() if v.get('score')])} traits validated")  
            logger.info(f"👤 [DEBUG ARCHETYPE] {archetype.get('archetype_key', 'none')} confidence={archetype.get('confidence', 0)}%")
            
            # MODUŁ 4: Debug sales indicators
            sales_indicators = validated_data.get('sales_indicators', {})
            logger.info(f"📊 [DEBUG INDICATORS] {len(sales_indicators)} indicators present")
            
            return validated_data
            
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
                'psychology_updated_at': datetime.now(),
                # MODUŁ 4: Wskaźniki Sprzedażowe
                'sales_indicators': ai_result.get('sales_indicators')
            }
            
            await db.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(**update_data)
            )
            
            logger.info(f"✅ [SESSION UPDATE] Psychology data saved for session {session_id}")
            
        except Exception as e:
            logger.error(f"❌ [SESSION UPDATE] Error updating session {session_id}: {e}")
            raise

    async def update_and_get_psychology(self, session_id: int, db: AsyncSession, ai_service) -> Dict[str, Any]:
        """
        NOWA FUNKCJA v4.0: Synchroniczna analiza psychology - fundament Ultra Mózgu
        
        Cel: Przekształcenie asynchronicznego zadania w tle w synchroniczną, blokującą funkcję,
        która zwraca kompletny profil psychometryczny przed generowaniem AI response.
        
        Args:
            session_id: ID sesji do analizy
            db: Aktywna sesja bazy danych
            ai_service: Instancja AIService do wywołania analiz
            
        Returns:
            dict: Kompletny profil psychometryczny gotowy do użycia przez AI response
            
        Raises:
            Exception: Gdy nie można wygenerować profilu
        """
        try:
            logger.info(f"🧠 [ULTRA BRAIN] Rozpoczynam synchroniczną analizę psychology dla sesji {session_id}")
            
            # KROK 1: Pobierz z bazy danych pełną historię interakcji dla danej sesji
            query = (
                select(Session)
                .options(selectinload(Session.interactions))
                .where(Session.id == session_id)
            )
            result = await db.execute(query)
            session = result.scalar_one_or_none()
            
            if not session:
                logger.error(f"❌ [ULTRA BRAIN] Session {session_id} not found")
                return {}
            
                        # KROK 2: Sformatuj historię rozmowy w jeden, spójny tekst
            conversation_history = self._build_session_history(session.interactions)
            interaction_count = len(session.interactions) if session.interactions else 0
            logger.info(f"📚 [ULTRA BRAIN] Historia sesji przygotowana ({len(conversation_history)} znaków)")
            logger.info(f"🔍 [ULTRA BRAIN] Ilość interakcji: {interaction_count}")
            logger.info(f"🔍 [ULTRA BRAIN] Szczegóły historii: '{conversation_history[:200]}...'")

            # KROK 3: Pobierz obecny profil z sesji (jeśli istnieje)
            current_profile = dict(session.cumulative_psychology or {})
            current_confidence = int(session.psychology_confidence or 0)

            logger.info(f"🔍 [ULTRA BRAIN] Obecny confidence: {current_confidence}%")
            logger.info(f"🔍 [ULTRA BRAIN] Obecny profil istnieje: {bool(current_profile)}")

            # KALIBRACJA: Zawsze próbuj przeprowadzić analizę, nawet przy jednej interakcji
            logger.info(f"🚀 [ULTRA BRAIN] KALIBRACJA: Zawsze wykonuję analizę - interakcje: {interaction_count}")

            # KROK 4: Sekwencyjnie wywołaj analizę AI - jeden wielki prompt zamiast osobnych wywołań
            ai_prompt = self._build_cumulative_psychology_prompt(
                history=conversation_history,
                current_profile=current_profile,
                confidence=current_confidence
            )
            
            logger.info(f"🤖 [ULTRA BRAIN] Wysyłam prompt do AI ({len(ai_prompt)} znaków)")
            
            # Wywołaj AI z pełnym promptem (wszystkie analizy w jednym wywołaniu)
            ai_response = await ai_service._call_llm_with_retry(
                system_prompt="Jesteś ekspertem psychologii sprzedaży generującym kompletny profil klienta.",
                user_prompt=ai_prompt
            )

            # KROK 5: Ekstraktuj content z odpowiedzi AI (jest to dict z kluczem 'content')
            ai_response_content = ai_response.get('content', '') if isinstance(ai_response, dict) else str(ai_response)

            # KROK 5: Parsuj odpowiedź AI
            logger.info(f"🔍 [ULTRA BRAIN] Odpowiedź AI: '{ai_response_content[:500]}...'")
            parsed_result = self._parse_psychology_ai_response(ai_response_content)
            if not parsed_result:
                logger.warning(f"⚠️ [ULTRA BRAIN] AI parsing failed, używam fallback")
                logger.warning(f"🔍 [ULTRA BRAIN] Cała odpowiedź AI: {ai_response_content}")
                return self._create_fallback_psychology_profile(interaction_count)
            
            # KROK 6: 🚀 ULTRA MÓZG v4.1 - SYNTEZA ARCHETYPU TESLI
            cumulative_psychology = parsed_result.get('cumulative_psychology', {})

            # Wywołaj naszego "dyrygenta" archetypów
            tesla_archetype = await self._map_profile_to_tesla_archetype(cumulative_psychology)

            # Zaktualizuj wynik AI o nowy archetyp Tesli
            parsed_result['customer_archetype'] = tesla_archetype
            parsed_result['tesla_archetype_mapped'] = True

            # KROK 7: Zapisz kompletny profil w bazie danych
            interactive_questions = self._convert_to_interactive_questions(
                parsed_result.get('suggested_questions', [])
            )

            await self._update_session_psychology(
                db=db,
                session_id=session_id,
                ai_result=parsed_result,
                interactive_questions=interactive_questions
            )

            # KALIBRACJA: Określ poziom analizy na podstawie ilości interakcji
            analysis_level = "pełna" if interaction_count >= 3 else "wstępna"
            logger.info(f"🎯 [ULTRA BRAIN] KALIBRACJA: Poziom analizy = {analysis_level} (interakcje: {interaction_count})")

            # KROK 8: Zwróć kompletny profil z archetypem Tesli i poziomem analizy
            complete_profile = {
                'cumulative_psychology': cumulative_psychology,
                'customer_archetype': tesla_archetype,  # NOWY: Archetyp Tesli zamiast ogólnego
                'psychology_confidence': parsed_result.get('psychology_confidence', 0),
                'sales_indicators': parsed_result.get('sales_indicators', {}),
                'active_clarifying_questions': interactive_questions,
                'analysis_timestamp': datetime.now().isoformat(),
                'tesla_archetype_active': True,  # Flaga wskazująca na aktywację ULTRA MÓZGU
                'analysis_level': analysis_level,  # NOWY: Poziom analizy
                'interaction_count': interaction_count  # Informacja o ilości interakcji
            }

            logger.info(f"✅ [ULTRA BRAIN] Profil kompletny! Confidence: {complete_profile['psychology_confidence']}%, Level: {analysis_level}")

            return complete_profile
            
        except Exception as e:
            logger.error(f"❌ [ULTRA BRAIN] Błąd podczas analizy sesji {session_id}: {e}")
            # W przypadku błędu, zwróć podstawowy profil z poziomem analizy
            return self._create_fallback_psychology_profile(interaction_count)

    def _create_fallback_psychology_profile(self, interaction_count: int = 0) -> Dict[str, Any]:
        """🔧 ULTRA MÓZG v4.1 - Enhanced fallback z Zero Null Policy i poziomem analizy"""
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
            'active_clarifying_questions': [],
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_level': analysis_level,  # KALIBRACJA: Zawsze podaj poziom analizy
            'interaction_count': interaction_count,  # KALIBRACJA: Informacja o ilości interakcji
            'tesla_archetype_active': False  # Fallback - nie ma archetypu Tesli
        }

    # DEPRECATED: Stara funkcja - zachowujemy dla backward compatibility
    async def update_cumulative_profile(self, session_id: int, old_db: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        @deprecated: Użyj update_and_get_psychology zamiast tej funkcji.
        
        STARA FUNKCJA - Background task approach. 
        Zostaje tylko dla backward compatibility, ale nie jest już wywoływana.
        """
        logger.warning("⚠️ [DEPRECATED] update_cumulative_profile jest deprecated. Użyj update_and_get_psychology.")
        
        # Zwróć pusty wynik - ta funkcja nie powinna być już używana
        return {}

    async def _map_profile_to_tesla_archetype(self, cumulative_psychology: dict) -> dict:
        """
        🧠⚡ ULTRA MÓZG v4.1 - "DYRYGENT" Archetypów Tesli

        Inteligentny mapper, który na podstawie surowych danych psychologicznych
        wybiera najbardziej pasujący Archetyp Klienta Tesli.

        Args:
            cumulative_psychology: Kompletny profil psychologiczny klienta

        Returns:
            dict: Wybrany archetyp Tesli z pełnymi danymi strategicznymi
        """
        try:
            logger.info("🎯 [ARCHETYPE MAPPER] Rozpoczynam mapowanie na archetyp Tesli...")

            # ETAP 1: Ekstrakcja kluczowych wskaźników psychologicznych
            big_five = cumulative_psychology.get('big_five', {})
            disc = cumulative_psychology.get('disc', {})

            # Pobierz wyniki jako liczby (domyślnie 5 jeśli brak)
            scores = {
                'extraversion': big_five.get('extraversion', {}).get('score', 5),
                'conscientiousness': big_five.get('conscientiousness', {}).get('score', 5),
                'openness': big_five.get('openness', {}).get('score', 5),
                'agreeableness': big_five.get('agreeableness', {}).get('score', 5),
                'dominance_disc': disc.get('dominance', {}).get('score', 5),
                'influence_disc': disc.get('influence', {}).get('score', 5),
                'steadiness_disc': disc.get('steadiness', {}).get('score', 5),
                'compliance_disc': disc.get('compliance', {}).get('score', 5)
            }

            # ETAP 2: Algorytm decyzyjny - reguły mapowania
            selected_archetype = None
            max_score = 0

            # Zdobywca Statusu: Wysoka ekstrawersja + dominacja
            status_score = (scores['extraversion'] + scores['dominance_disc'] + scores['influence_disc']) / 3
            if status_score > max_score:
                max_score = status_score
                selected_archetype = "zdobywca_statusu"

            # Strażnik Rodziny: Wysoka sumienność + stabilność
            family_score = (scores['conscientiousness'] + scores['steadiness_disc'] + scores['compliance_disc']) / 3
            if family_score > max_score:
                max_score = family_score
                selected_archetype = "straznik_rodziny"

            # Pragmatyczny Analityk: Wysoka sumienność + zgodność
            analyst_score = (scores['conscientiousness'] + scores['compliance_disc']) / 2
            if analyst_score > max_score:
                max_score = analyst_score
                selected_archetype = "pragmatyczny_analityk"

            # Wizjoner Przyszłości: Wysoka otwartość + wpływy
            visionary_score = (scores['openness'] + scores['influence_disc']) / 2
            if visionary_score > max_score:
                max_score = visionary_score
                selected_archetype = "wizjoner_przyszlosci"

            # Ekologiczny Aktywista: Wysoka ugodowość + otwartość
            eco_score = (scores['agreeableness'] + scores['openness']) / 2
            if eco_score > max_score:
                max_score = eco_score
                selected_archetype = "ekologiczny_aktywista"

            # Fleet Manager: Niska ekstrawersja + wysoka zgodność (fallback dla biznesowych)
            if scores['extraversion'] < 4 and scores['compliance_disc'] > 6:
                selected_archetype = "fleet_manager"

            # ETAP 3: Jeśli nie udało się jednoznacznie wybrać - fallback na analityka
            if not selected_archetype:
                selected_archetype = "pragmatyczny_analityk"
                logger.info("⚠️ [ARCHETYPE MAPPER] Fallback na Pragmatycznego Analityka")

            # ETAP 4: Pobierz pełny archetyp z bazy
            archetype_data = self.TESLA_CUSTOMER_ARCHETYPES[selected_archetype].copy()

            # ETAP 5: Oblicz confidence na podstawie dopasowania
            confidence = min(95, max(60, int(max_score * 10)))  # 60-95%

            # ETAP 6: Przygotuj finalny obiekt archetypu
            final_archetype = {
                "archetype_key": selected_archetype,
                "archetype_name": archetype_data["name"],
                "description": archetype_data["description"],
                "dominant_traits": archetype_data["dominant_traits"],
                "confidence": confidence,
                "key_traits": archetype_data["dominant_traits"],
                "sales_strategy": archetype_data["sales_strategy"],
                "motivation": archetype_data["motivation"],
                "communication_style": archetype_data["communication_style"],
                "psychological_match": {
                    "big_five_alignment": f"{max_score:.1f}/10",
                    "primary_drivers": archetype_data["dominant_traits"],
                    "secondary_traits": [k for k, v in scores.items() if v >= 7]
                }
            }

            logger.info(f"✅ [ARCHETYPE MAPPER] Wybrany archetyp: {archetype_data['name']} (confidence: {confidence}%)")
            return final_archetype

        except Exception as e:
            logger.error(f"❌ [ARCHETYPE MAPPER] Błąd podczas mapowania archetypu: {e}")
            # Fallback na bezpieczny archetyp
            return {
                "archetype_key": "pragmatyczny_analityk",
                "archetype_name": "📊 Pragmatyczny Analityk",
                "description": "Fallback - bezpieczny wybór archetypu",
                "confidence": 50,
                "key_traits": ["conscientiousness", "compliance_disc"],
                "sales_strategy": {
                    "do": ["Dostarczaj dane i fakty", "Bądź cierpliwy", "Używaj języka profesjonalnego"],
                    "dont": ["Nie naciskaj", "Nie używaj emocji", "Nie przyspieszaj decyzji"]
                },
                "motivation": "Bezpieczeństwo decyzji",
                "communication_style": "Profesjonalny i rzeczowy"
            }

    def _build_session_history(self, interactions) -> str:
        """
        Formatuje historię sesji w jeden, spójny tekst dla AI

        Args:
            interactions: Lista interakcji z sesji

        Returns:
            str: Sformatowana historia rozmowy
        """
        if not interactions:
            return "Brak poprzedniej historii rozmowy."

        history_parts = []
        for i, interaction in enumerate(interactions, 1):
            user_input = interaction.user_input or ""
            timestamp = interaction.timestamp.strftime("%H:%M") if interaction.timestamp else "unknown"

            # Skróć bardzo długie wypowiedzi
            if len(user_input) > 500:
                user_input = user_input[:500] + "..."

            history_parts.append(f"{i}. [{timestamp}] Sprzedawca: \"{user_input}\"")
        
        return "\n".join(history_parts)

# Singleton instance
session_psychology_engine = SessionPsychologyEngine()
