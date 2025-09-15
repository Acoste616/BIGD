#!/usr/bin/env python3
"""
Skrypt do dodawania dodatkowych promptów do bazy danych
Poprawiona wersja kodu użytkownika z właściwymi importami
"""
import asyncio
import sys
import os

# Dodaj ścieżkę do modułów aplikacji
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

# Poprawne importy z istniejącej struktury
from app.core.database import AsyncSessionLocal
from app.models.domain import PromptTemplate, PromptStatus

@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# Słownik z promptami do dodania
PROMPTS_TO_SEED = {
    "holistic_synthesis_v2": """
System Prompt:
Jesteś ekspertem w dziedzinie psychologii sprzedaży i analizy behawioralnej. Twoim zadaniem jest stworzenie kompleksowego, holistycznego profilu psychometrycznego klienta na podstawie dostarczonej pełnej historii interakcji. Analizuj język, używane zwroty, zadawane pytania i zgłaszane obiekcje. Zwróć odpowiedź WYŁĄCZNIE w formacie JSON, bez żadnych dodatkowych komentarzy.

User Prompt:
Przeanalizuj poniższą historię interakcji i wygeneruj profil psychometryczny.

Historia Interakcji:
{historia_interakcji_jako_string}

Format wyjściowy JSON:
{
  "archetype_analysis": {
    "primary_archetype": "Nazwa Głównego Archetypu (np. Mędrzec, Odkrywca)",
    "secondary_archetype": "Nazwa Drugiego Archetypu",
    "confidence": "Wartość_od_0_do_100",
    "rationale": "Krótkie uzasadnienie wyboru archetypów na podstawie interakcji."
  },
  "disc_profile": {
    "dominant_factor": "Jedna litera: D, I, S, lub C",
    "secondary_factor": "Druga w kolejności litera",
    "scores": {"D": "Wartość", "I": "Wartość", "S": "Wartość", "C": "Wartość"},
    "communication_style_advice": "Konkretne porady, jak komunikować się z tym profilem."
  }
}
""",
    "sales_strategy_generation_v2": """
System Prompt:
Jesteś światowej klasy strategiem sprzedaży i storytellerem. Na podstawie kompletnego profilu psychometrycznego klienta, jego kluczowych obaw i motywacji, stwórz dwie krótkie, potężne narracje (Bólu i Zysku) oraz 3 konkretne, następne kroki strategiczne. Używaj języka i argumentów, które najsilniej zarezonują z tym konkretnym profilem. Zwróć odpowiedź WYŁĄCZNIE w formacie JSON.

User Prompt:
Profil klienta:
{holistic_psychometric_profile_json}

Kluczowe obawy zidentyfikowane w rozmowie:
{lista_obaw}

Kluczowe motywacje zidentyfikowane w rozmowie:
{lista_motywacji}

Wygeneruj strategię.

Format wyjściowy JSON:
{
  "suggested_strategy": {
    "pain_narrative": "Krótka, emocjonalna historia opisująca przyszłość klienta bez Twojego rozwiązania, bazująca na jego obawach.",
    "gain_narrative": "Krótka, inspirująca historia opisująca przyszłość klienta z Twoim rozwiązaniem, bazująca na jego motywacjach.",
    "next_strategic_steps": [
      "Krok 1 (np. 'Zaproponuj spersonalizowane demo skupione na funkcji X')",
      "Krok 2 (np. 'Przygotuj analizę TCO do wysłania na maila')",
      "Krok 3 (np. 'Wprowadź do rozmowy temat Y, aby wzmocnić poczucie bezpieczeństwa')"
    ]
  }
}
""",
    "quick_response": """
System Prompt:
Jesteś błyskawicznym asystentem sprzedaży. Twoim zadaniem jest wygenerowanie 2-3 krótkich, taktycznych propozycji (pytania lub stwierdzenia) w odpowiedzi na ostatnią wypowiedź klienta. Wykorzystaj dostarczony kontekst z bazy wiedzy. Odpowiedzi muszą być w języku polskim. Zwróć odpowiedź WYŁĄCZNIE w formacie JSON, w formie listy stringów.

User Prompt:
Ostatnia wypowiedź klienta: "{user_input}"

Kontekst z bazy wiedzy (najbardziej trafne "bryłki wiedzy"):
1. {nugget_1_content}
2. {nugget_2_content}
3. {nugget_3_content}

Wygeneruj listę sugestii.

Format wyjściowy JSON:
{
  "quick_responses": [
    "Sugestia 1...",
    "Sugestia 2...",
    "Sugestia 3..."
  ]
}
"""
}

async def seed_additional_prompts():
    """
    Wypełnia bazę danych dodatkowymi szablonami promptów, jeśli jeszcze nie istnieją.
    """
    print("🚀 Rozpoczynam dodawanie dodatkowych promptów do bazy danych...")
    
    async with get_session() as session:
        try:
            added_count = 0
            for name, content in PROMPTS_TO_SEED.items():
                # Sprawdź, czy prompt o tej nazwie już istnieje
                existing_prompt_stmt = await session.execute(
                    select(PromptTemplate).where(PromptTemplate.name == name)
                )
                if not existing_prompt_stmt.scalars().first():
                    new_prompt = PromptTemplate(
                        name=name,
                        content=content.strip(),
                        version=1,
                        status=PromptStatus.ACTIVE
                    )
                    session.add(new_prompt)
                    print(f"✅ Dodano prompt '{name}' do bazy danych.")
                    added_count += 1
                else:
                    print(f"ℹ️ Prompt '{name}' już istnieje w bazie danych. Pomijam.")
            
            await session.commit()
            print(f"🎉 Zakończono dodawanie promptów. Dodano {added_count} nowych promptów.")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Błąd podczas dodawania promptów: {e}")
            raise
        finally:
            await session.close()

if __name__ == "__main__":
    print("📋 Skrypt dodawania dodatkowych promptów...")
    asyncio.run(seed_additional_prompts())