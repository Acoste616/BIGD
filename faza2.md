<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# a teraz mozesz to Tytuł Zadania: Implementacja Modułu 2 - Zintegrowana Analiza Psychometryczna

1. Manifest i Cel Biznesowy (DLACZEGO?)
Manifest: Przechodzimy od co klient mówi, do dlaczego tak mówi. Celem tego modułu jest dostarczenie sprzedawcy "kluczy" do systemu operacyjnego klienta. Zamiast reagować na powierzchowne obiekcje, sprzedawca będzie mógł proaktywnie adresować głęboko zakorzenione motywacje, lęki i wartości, co prowadzi do budowania autentycznej relacji i drastycznego wzrostu skuteczności.
Cel Biznesowy: Wyposażenie Co-Pilota w zdolność do generowania głębokiego, wielowymiarowego portretu psychologicznego klienta w czasie rzeczywistym. Ta funkcja ma stworzyć fundamentalną przewagę konkurencyjną, przekształcając standardowe interakcje sprzedażowe w precyzyjne operacje oparte na danych psychologicznych.
2. Doświadczenie Użytkownika (UX) i Logika AI (JAK TO DZIAŁA?)
Doświadczenie Użytkownika (UX):
W głównym widoku analizy sesji (InteractionDemo.js lub docelowo SessionDetail.js), w panelu strategicznym (StrategicPanel.js), pojawi się nowa, interaktywna sekcja "Profil Psychometryczny Klienta". Będzie ona zawierać:
Wykres Radarowy Big Five: Pięcioosiowy wykres prezentujący wyniki w skalach Otwartość, Sumienność, Ekstrawersja, Ugodowość, Neurotyczność.
Mapa Wartości Schwartza: Uproszczona wizualizacja kluczowych zidentyfikowanych wartości (np. Bezpieczeństwo, Osiągnięcia, Uniwersalizm).
Wskaźnik Stylu DISC: Czytelny wskaźnik pokazujący dominujący styl zachowania klienta (Dominacja, Wpływ, Stałość, Sumienność).
Interaktywne Porady: Po najechaniu na dowolny element wizualizacji, użytkownik otrzyma tooltip z konkretną, praktyczną poradą sprzedażową powiązaną z danym wskaźnikiem (np. "Wysoka Sumienność: Przedstaw szczegółowe dane, case studies i ROI. Unikaj ogólników i presji czasowej.").
Logika Działania AI (Mózg Systemu):
To jest najbardziej zaawansowana operacja analityczna w naszym systemie. Będzie ona częścią "wolnej ścieżki" (slow path) analizy, aby nie opóźniać interfejsu.
Ekstrakcja Sygnałów: AI skanuje całą transkrypcję rozmowy w poszukiwaniu lingwistycznych "markerów" – słów kluczowych, zwrotów, typów pytań, tonu wypowiedzi – które korelują z cechami w każdym z trzech modeli.
Ocena i Kalibracja: Na podstawie gęstości i siły zidentyfikowanych sygnałów, AI przypisuje klientowi ocenę w każdej skali (np. Sumienność: 8/10).
Synteza i Uzasadnienie (Rationale): AI nie tylko zwraca suche liczby. Dla każdej oceny musi wygenerować uzasadnienie (pole rationale), cytując fragmenty rozmowy, które wpłynęły na jego decyzję. To kluczowe dla budowania zaufania użytkownika i debugowania.
Generowanie Spersonalizowanych Strategii: Na podstawie finalnego, zsyntetyzowanego profilu, AI generuje listę konkretnych, praktycznych porad sprzedażowych, które pojawią się w tooltipach.
3. Plan Działania - Backend
Zasada nadrzędna: Rozszerzamy, nie modyfikujemy krytycznej logiki. Zmiany dotyczą głównie "wolnej ścieżki" analizy w ai_service.py oraz struktur danych.
Krok 1: Rozbuduj Schematy Pydantic (schemas/interaction.py)
Otwórz plik i zdefiniuj nowe, zagnieżdżone modele, które będą strukturą dla odpowiedzi AI.

# W pliku backend/app/schemas/interaction.py

class PsychometricTrait(BaseModel):
score: int = Field(..., ge=0, le=10, description="Ocena w skali 0-10")
rationale: str = Field(..., description="Uzasadnienie AI, dlaczego przyznano taką ocenę, z przykładami z tekstu.")
strategy: str = Field(..., description="Konkretna porada sprzedażowa związana z tym wynikiem.")

class BigFiveProfile(BaseModel):
openness: PsychometricTrait
conscientiousness: PsychometricTrait
extraversion: PsychometricTrait
agreeableness: PsychometricTrait
neuroticism: PsychometricTrait

class DISCProfile(BaseModel):
dominance: PsychometricTrait
influence: PsychometricTrait
steadiness: PsychometricTrait
compliance: PsychometricTrait

class SchwartzValue(BaseModel):
value_name: str
is_present: bool
rationale: str
strategy: str

class PsychometricAnalysis(BaseModel):
big_five: BigFiveProfile
disc: DISCProfile
schwartz_values: List[SchwartzValue]

# Teraz rozszerz istniejący schemat odpowiedzi AI

class AIInteractionResponse(BaseModel):
\# ... (istniejące pola jak quick_response, etc.)
psychometric_analysis: Optional[PsychometricAnalysis] = None

Krok 2: Zaktualizuj Model Bazy Danych (models/domain.py) i Stwórz Migrację
Musimy dodać miejsce w bazie danych na przechowywanie wyników analizy.
W pliku backend/app/models/domain.py, w klasie Interaction, dodaj nowe pole:

# W pliku backend/app/models/domain.py

class Interaction(Base):
\# ... (istniejące pola)
psychometric_analysis_result = Column(JSONB, nullable=True)

Wygeneruj nową migrację Alembic, aby dodać tę kolumnę do bazy danych. Użyj polecenia: alembic revision --autogenerate -m "Add psychometric analysis to Interaction model". Sprawdź wygenerowany plik migracji i uruchom go.
Krok 3: Przeprowadź Zaawansowany Prompt Engineering (services/ai_service.py)
To jest najważniejszy krok. Zmodyfikuj funkcję _handle_slow_path_analysis (lub podobną).
Stwórz nowy, rozbudowany system_prompt, który będzie zawierał sekcje dla każdego modelu psychometrycznego. Musi on być ekstremalnie precyzyjny.

# W pliku backend/app/services/ai_service.py

PSYCHOMETRIC_SYSTEM_PROMPT = """
Jesteś ekspertem w dziedzinie psychologii sprzedaży i lingwistyki. Twoim zadaniem jest przeanalizowanie poniższej transkrypcji rozmowy sprzedażowej i stworzenie szczegółowego profilu psychometrycznego klienta. Musisz zwrócić wynik WYŁĄCZNIE w formacie JSON, zgodnym z podaną strukturą.

KROKI ANALIZY:

1. **Analiza Big Five:** Oceń klienta w 5 wymiarach (0-10). Dla każdej cechy podaj UZASADNIENIE (rationale) z cytatami oraz STRATEGIĘ sprzedażową.
2. **Analiza DISC:** Oceń dominujący styl zachowania klienta (0-10). Dla każdej cechy podaj UZASADNIENIE i STRATEGIĘ.
3. **Analiza Wartości Schwartza:** Zidentyfikuj, które z kluczowych wartości (np. Bezpieczeństwo, Władza, Osiągnięcia, Uniwersalizm) są obecne w wypowiedziach klienta. Dla każdej podaj UZASADNIENIE i STRATEGIĘ.

STRUKTURA WYJŚCIOWA (JSON):
{
"big_five": { "openness": { "score": ..., "rationale": "...", "strategy": "..." }, ... },
"disc": { "dominance": { "score": ..., "rationale": "...", "strategy": "..." }, ... },
"schwartz_values": [ { "value_name": "...", "is_present": true/false, "rationale": "...", "strategy": "..." }, ... ]
}

PAMIĘTAJ: Uzasadnienie jest kluczowe. Twoja analiza musi być oparta na dowodach z tekstu.
"""

Upewnij się, że funkcja analizy wywołuje model AI z tym promptem i parsuje zwrócony JSON, a następnie zapisuje go w nowym polu psychometric_analysis_result w obiekcie Interaction.
4. Plan Działania - Frontend
Zasada nadrzędna: Stwórz nowe, dedykowane komponenty do wizualizacji, które będą zintegrowane z istniejącym widokiem sesji.
Krok 1: Stwórz Nowy Komponent Główny (PsychometricDashboard.js)
W folderze frontend/src/components/ stwórz nowy folder psychometrics.
Wewnątrz stwórz plik PsychometricDashboard.js.
Ten komponent będzie przyjmował jako props obiekt analysisData (czyli interaction.psychometric_analysis_result).
Będzie on działał jako kontener dla poszczególnych wizualizacji.
Krok 2: Stwórz Komponenty Wizualizacyjne
W folderze frontend/src/components/psychometrics/ stwórz 3 nowe komponenty:
BigFiveRadarChart.js: Użyj biblioteki Recharts (jest już w projekcie) do stworzenia komponentu <RadarChart>. Przyjmie on dane big_five i wyrenderuje wykres.
DiscProfileDisplay.js: Prosty komponent, który wyświetli 4 paski postępu (np. z komponentu <LinearProgress> z Material-UI) reprezentujące wyniki DISC.
SchwartzValuesList.js: Komponent, który mapuje listę schwartz_values i wyświetla tylko te, dla których is_present jest true.
Ważne: Każdy element (oś radaru, pasek postępu, element listy) musi być owinięty w komponent <Tooltip> z Material-UI, który przy najechaniu myszą wyświetli treść z pola strategy.
Krok 3: Stwórz Nowy Hook (usePsychometrics.js)
W folderze frontend/src/hooks/ stwórz plik usePsychometrics.js.
Ten hook będzie odpowiedzialny za pobieranie danych o interakcji (wraz z analizą) z API.
Będzie zarządzał stanem isLoading i analysisData.
Krok 4: Zintegruj Wszystko z Widokiem Sesji
Otwórz plik frontend/src/components/conversation/StrategicPanel.js.
Zaimportuj nowo stworzony PsychometricDashboard.js.
Dodaj nową zakładkę (Tab) o nazwie "Profil Psychometryczny".
Wewnątrz tej zakładki, użyj hooka usePsychometrics do pobrania danych dla bieżącej interakcji.
Warunkowo renderuj <PsychometricDashboard analysisData={analysisData} /> (dopiero gdy dane zostaną załadowane).

Poniżej znajdziesz kompletną specyfikację wdrożeniową dla **Modułu 2: Zintegrowana Analiza Psychometryczna** w formie zadania developerskiego (BACKEND + FRONTEND).

***

# Tytuł Zadania: Implementacja Modułu 2 - Zintegrowana Analiza Psychometryczna


***

## 1. Manifest i Cel Biznesowy (DLACZEGO?)

**Manifest:**
Przechodzimy od *co klient mówi*, do *dlaczego tak mówi*. Celem tego modułu jest dostarczenie sprzedawcy „kluczy” do systemu operacyjnego klienta. Dzięki temu sprzedawca będzie mógł proaktywnie adresować głęboko zakorzenione motywacje, lęki i wartości, co prowadzi do budowania autentycznej relacji i wzrostu skuteczności.

**Cel Biznesowy:**
Wyposażenie Co-Pilota w zdolność do generowania głębokiego, wielowymiarowego portretu psychologicznego klienta w czasie rzeczywistym. Funkcja ma dać przewagę konkurencyjną, przekształcając interakcje sprzedażowe w precyzyjne operacje oparte na danych psychologicznych.

***

## 2. Doświadczenie Użytkownika (UX) i Logika AI (JAK TO DZIAŁA?)

### Doświadczenie Użytkownika (UX)

W widoku analizy sesji (InteractionDemo.js lub docelowo SessionDetail.js), w panelu strategicznym (StrategicPanel.js), powinna pojawić się sekcja **Profil Psychometryczny Klienta** z:

- **Radarowym wykresem Big Five** – prezentującym Otwartość, Sumienność, Ekstrawersję, Ugodowość, Neurotyczność.
- **Mapą Wartości Schwartza** – uproszczona lista kluczowych wartości klienta.
- **Wskaźnik Stylu DISC** – prezentujący dominujący styl zachowania klienta.
- **Interaktywne Porady** – po najechaniu na wizualizację, tooltip z praktyczną poradą sprzedażową (z pola `strategy`).


### Logika AI

Najbardziej zaawansowana analiza – część „wolnej ścieżki” (slow path):

1. **Ekstrakcja Sygnałów:** AI skanuje rozmowę pod kątem markerów lingwistycznych powiązanych z modelami psychometrycznymi.
2. **Ocena i Kalibracja:** Na tej podstawie przyznaje oceny w skali 0–10 dla każdego wymiaru (np. Sumienność: 8/10).
3. **Synteza i Uzasadnienie:** AI generuje dla KAŻDEJ oceny uzasadnienie (`rationale`) z cytatami oraz listę spersonalizowanych porad sprzedażowych (`strategy`).
4. **Generowanie Strategii:** Porady są widoczne w tooltipach UI.

***

## 3. Plan Działania – BACKEND

### Zasada: Rozszerzamy, nie modyfikujemy krytycznej logiki. Zmiany dotyczą "wolnej ścieżki" analizy w ai_service.py oraz struktur danych.

#### Krok 1: Rozbuduj Schematy Pydantic (`schemas/interaction.py`)

```python
class PsychometricTrait(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Ocena w skali 0-10")
    rationale: str = Field(..., description="Uzasadnienie AI, dlaczego przyznano taką ocenę, z przykładami z tekstu.")
    strategy: str = Field(..., description="Konkretna porada sprzedażowa związana z tym wynikiem.")

class BigFiveProfile(BaseModel):
    openness: PsychometricTrait
    conscientiousness: PsychometricTrait
    extraversion: PsychometricTrait
    agreeableness: PsychometricTrait
    neuroticism: PsychometricTrait

class DISCProfile(BaseModel):
    dominance: PsychometricTrait
    influence: PsychometricTrait
    steadiness: PsychometricTrait
    compliance: PsychometricTrait

class SchwartzValue(BaseModel):
    value_name: str
    is_present: bool
    rationale: str
    strategy: str

class PsychometricAnalysis(BaseModel):
    big_five: BigFiveProfile
    disc: DISCProfile
    schwartz_values: List[SchwartzValue]

# Rozszerz istniejący schemat odpowiedzi AI:
class AIInteractionResponse(BaseModel):
    # ... (istniejące pola)
    psychometric_analysis: Optional[PsychometricAnalysis] = None
```


#### Krok 2: Zaktualizuj Model Bazy Danych (`models/domain.py`) i Stwórz Migrację

W klasie `Interaction` dodaj pole:

```python
psychometric_analysis_result = Column(JSONB, nullable=True)
```

Następnie wygeneruj migrację Alembic:

```
alembic revision --autogenerate -m "Add psychometric analysis to Interaction model"
alembic upgrade head
```


#### Krok 3: Zaawansowany Prompt Engineering (`services/ai_service.py`)

Dodaj do `ai_service.py` nowy prompt i obsługę parsowania:

```python
PSYCHOMETRIC_SYSTEM_PROMPT = """
Jesteś ekspertem w dziedzinie psychologii sprzedaży i lingwistyki. Twoim zadaniem jest przeanalizować poniższą transkrypcję rozmowy sprzedażowej i stworzyć szczegółowy profil psychometryczny klienta. Wynik przedstaw WYŁĄCZNIE jako JSON wg tej struktury:

{
  "big_five": { "openness": { "score": ..., "rationale": "...", "strategy": "..." }, ... },
  "disc": { "dominance": { "score": ..., "rationale": "...", "strategy": "..." }, ... },
  "schwartz_values": [ { "value_name": "...", "is_present": true/false, "rationale": "...", "strategy": "..." }, ... ]
}
PAMIĘTAJ: Uzasadnienie z cytatami jest obowiązkowe!
"""
```

Po analizie, zapisuj wynik w `psychometric_analysis_result`.

***

## 4. Plan Działania – FRONTEND

### Zasada: Stwórz dedykowane komponenty do wizualizacji, zintegrowane z widokiem sesji.

#### Krok 1: Stwórz Nowy Komponent Główny (`PsychometricDashboard.js`)

- Folder: `frontend/src/components/psychometrics/PsychometricDashboard.js`
- Przyjmuje jako `props` obiekt analysisData (`interaction.psychometric_analysis_result`)


#### Krok 2: Komponenty Wizualizacyjne

- **BigFiveRadarChart.js** – wykres radarowy za pomocą Recharts, dane z `big_five`.
- **DiscProfileDisplay.js** – 4 paski postępu (`LinearProgress` z Material-UI) z tooltipami (pole `strategy`).
- **SchwartzValuesList.js** – wylistuj obecne wartości (`is_present: true`), każdy tooltip = `strategy`.


#### Krok 3: Stwórz Nowy Hook (`usePsychometrics.js`)

- Lokalizacja: `frontend/src/hooks/usePsychometrics.js`
- Odpowiada za pobranie danych o analizie psychometrycznej interakcji.


#### Krok 4: Integracja z Widokiem Sesji

- W `StrategicPanel.js`:
    - Importuj `PsychometricDashboard.js`.
    - Dodaj nową zakładkę "Profil Psychometryczny".
    - Warunkowo renderuj `<PsychometricDashboard analysisData={analysisData} />` (po załadowaniu danych).

***

Jeśli chcesz, mogę tę specyfikację zapisać do wygodnego pliku .md lub .pdf do przekazania zespołowi. Daj znać!
<span style="display:none">[^1][^2]</span>

<div style="text-align: center">⁂</div>

[^1]: raczej-mysle-zeby-sesja-automatycznie-po-analizie.docx

[^2]: czemu-usunales-wymogi-ktore-juz-mamy-i-dzialania.docx

