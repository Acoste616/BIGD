# Plan Projektowy v2.2 (Kompletny Blueprint): Osobisty Co-Pilot Sprzedaży AI

Wersja dokumentu: 2.2

Data: 21.08.2025

Status: Aktywny - Nadrzędne i Jedyne Źródło Prawdy

## Część I: Manifest, Filozofia i Architektura

### 1. Manifest Projektu: Od Narzędzia do Partnera

Wersja 1.0 stworzyła nam doskonałego, reaktywnego Asystenta. Wersja 2.0 ma za zadanie powołać do życia proaktywnego, uczącego się Partnera Strategicznego. Różnica jest fundamentalna:

Asystent odpowiada na pytania.

Partner przewiduje pytania, których jeszcze nie zadałeś, rozumie głębszy kontekst i aktywnie dąży do samodoskonalenia.

Celem v2.0 jest stworzenie systemu, który staje się prawdziwym rozszerzeniem intuicji i wiedzy eksperckiej sprzedawcy.

### 2. Fundament Niezmienności: Nasza Działająca Baza v1.0

Prace nad v2.0 opierają się na nienaruszalności stabilnej i w pełni funkcjonalnej architektury v1.0. Poniższe elementy są naszym punktem wyjścia i nie podlegają modyfikacji, a jedynie rozszerzeniu:

Architektura Ogólna: W pełni skonteneryzowana (docker-compose.yml) z usługami: Backend (FastAPI), Frontend (React), Baza Danych (PostgreSQL), Baza Wektorowa (Qdrant).

Backend (FastAPI):

Warstwowa Struktura: W pełni działająca logika w podziale na routers, services, repositories, models, schemas.

Core API: Stabilne i przetestowane endpointy do zarządzania Klientami, Sesjami i Interakcjami.

Integracja z AI (Ollama): Działająca komunikacja z modelem gpt-oss:120b.

Architektura "Fast Path / Slow Path": Zaimplementowany mechanizm dwuetapowej analizy zapewniający natychmiastową odpowiedź UI (<4s) oraz głęboką analizę w tle.

Baza Danych (PostgreSQL): Stabilny schemat relacyjny przechowujący dane o klientach, sesjach i interakcjach.

Baza Wektorowa (Qdrant): Zainicjalizowana i gotowa do przyjmowania oraz przeszukiwania "bryłek wiedzy" (knowledge nuggets).

Frontend (React): Działający interfejs użytkownika z podstawowymi widokami do zarządzania sesjami i prowadzenia interakcji.

### 3. Architektura Techniczna v2.0: Ewolucja na Stabilnym Fundamencie

Nowe moduły będą zintegrowane jako rozszerzenia istniejącej logiki.

Diagram Interakcji Modułów v2.0:

[Użytkownik] <--> [Frontend (React)] <--> [Backend API (FastAPI)]
     |                                             |
     |                                             +------> [Baza Danych (PostgreSQL)]
     |                                             |        (Przechowuje dane o sesjach, interakcjach, feedbacku)
     |                                             |
     +---------------------------------------------> [Moduł 1: Feedback API]
     |                                             |
     |                                             +------> [Moduł 2 & 4: AI Service (Analiza)]
     |                                             |        (Generuje analizę psychometryczną i wskaźniki)
     |                                             |
[AI Dojo] <----------------------------------------+------> [Moduł 3: AI Service (Dialog)]
     (Użytkownik jako Mentor)                      |        (Prowadzi dialog, uczy się, aktualizuje wiedzę)
                                                   |
                                                   +------> [Baza Wektorowa (Qdrant)]
                                                            (Przechowuje wiedzę produktową i "metazasady")

### 4. Sposób Pracy: Dyscyplina i Przejrzystość

Pracujemy według ustalonych zasad: jeden cel na raz, kompletne zadania, ciągłość kontekstu i nadrzędność tego dokumentu. Każde zadanie będzie miało jasno zdefiniowane kryteria ukończenia.

## Część II: Szczegółowa Specyfikacja Modułów v2.0

### Moduł 1: Granularna Pętla Uczenia się (Feedback Loop)

Wizja Biznesowa: Stworzenie silnika samodoskonalenia. Każde "👍" i "👎" to mikrolekcja dla AI, która z czasem przekształci system w narzędzie o precyzji niedostępnej dla konkurencji. To inwestycja w długoterminową przewagę rynkową.

Doświadczenie Użytkownika (UX): Przy każdej kluczowej sugestii AI (odpowiedź, pytanie, akcja) użytkownik widzi proste ikony 👍/👎. Kliknięcie jest natychmiastowe. Po kliknięciu ikony stają się nieaktywne, dając wizualne potwierdzenie, że feedback został zarejestrowany. Interfejs jest dyskretny, ale zawsze dostępny, zachęcając do ciągłej interakcji.

Logika Działania AI (Mózg Systemu): Na tym etapie AI nie reaguje jeszcze aktywnie na feedback w czasie rzeczywistym. Logika polega na pedantycznym gromadzeniu danych. System zapisuje nie tylko ocenę (+1/-1), ale cały kontekst: jaka była sugestia, jaki był stan rozmowy, jaki był profil klienta. Te dane stają się "paliwem" dla Modułu 3.

Specyfikacja Techniczna:

Backend:

Model SQLAlchemy (models/domain.py): W klasie Interaction dodajemy pole: feedback_data = Column(JSONB, nullable=True, default=lambda: []). Będzie to lista obiektów JSON.

Schemat Pydantic (schemas/feedback.py): Tworzymy nowy schemat FeedbackCreate(BaseModel) z polami: interaction_id: int, suggestion_id: str, suggestion_type: str, score: int.

Router (routers/feedback.py): Tworzymy nowy plik z endpointem POST /feedback, który przyjmuje schemat FeedbackCreate.

Repozytorium (repositories/feedback_repository.py): Tworzymy nową klasę z metodą add_feedback, która w sposób bezpieczny (obsługa współbieżności) dołącza nowy obiekt feedbacku do tablicy JSON w bazie danych dla danej interakcji.

Frontend:

AI Service (services/ai_service.py): Modyfikujemy logikę generowania odpowiedzi, aby każda sugestia (quick_response, follow_up_questions, etc.) była obiektem zawierającym text oraz unikalne id (wygenerowane np. przez uuid.uuid4()).

Komponent (InteractionCard.js): Renderuje przyciski 👍/👎 obok każdej sugestii, przekazując suggestion.id do funkcji obsługi.

Hook (hooks/useInteractionFeedback.js): Tworzymy nowy hook, który zarządza stanem wysyłania feedbacku (loading, error) i wywołuje odpowiednią funkcję z feedbackApi.js.

### Moduł 2: Zintegrowana Analiza Psychometryczna

Wizja Biznesowa: Zrozumienie "systemu operacyjnego" klienta. Zamiast sprzedawać produkt, sprzedajemy rozwiązanie dla konkretnego typu osobowości i systemu wartości. To pozwala na budowanie głębszej relacji i omijanie standardowych obiekcji.

Doświadczenie Użytkownika (UX): W panelu analizy sesji pojawia się nowy, interaktywny dashboard. Użytkownik widzi wykres radarowy dla Big Five, listę kluczowych wartości Schwartza i pozycję klienta na mapie DISC. Po najechaniu na każdy element, pojawia się tooltip z wyjaśnieniem i konkretną poradą sprzedażową, np. "Wysoka Neurotyczność: Skup się na gwarancji i bezpieczeństwie, aby zredukować jego lęk przed złą decyzją".

Logika Działania AI (Mózg Systemu): To jest kluczowy skok w zaawansowaniu. AI wykonuje analizę wieloetapową:

Ekstrakcja Sygnałów: AI skanuje całą rozmowę w poszukiwaniu fraz, pytań i stwierdzeń, które są wskaźnikami dla poszczególnych modeli (np. pytanie o dane i ROI -> wysoka Sumienność; pytanie o ekologię -> wartość Uniwersalizmu).

Ocena i Kalibracja: Na podstawie zebranych sygnałów, AI ocenia klienta w każdym modelu.

Synteza i Archetyp: AI używa archetypu jako "szablonu interpretacyjnego". Łączy wyniki, tworząc spójny portret, np. "To jest Pragmatyczny Analityk (archetyp), co jest napędzane przez jego wysoką Sumienność (Big Five) i potrzebę Kontroli (DISC). Jego główną wartością jest Bezpieczeństwo (Schwartz)".

Generowanie Strategii: Na podstawie tej syntezy, AI generuje hiper-spersonalizowane strategie.

Specyfikacja Techniczna:

Backend:

Prompt Engineering (services/ai_service.py): Całkowita przebudowa system_prompt dla "wolnej ścieżki". Będzie on zawierał szczegółowe instrukcje i przykłady dla każdego modelu psychometrycznego oraz wymóg zwrócenia wyniku w ściśle określonym formacie JSON.

Schematy Pydantic (schemas/interaction.py): Rozbudowa AIResponse o zagnieżdżone modele: BigFiveProfile, SchwartzValues, DISCProfile. Każdy z nich będzie zawierał nie tylko wynik, ale też pole rationale (uzasadnienie), w którym AI wyjaśni, na jakiej podstawie dokonało oceny.

Frontend:

Komponent (PsychometricDashboard.js): Nowy komponent wykorzystujący bibliotekę do wykresów (np. Chart.js lub Recharts) do renderowania wykresu radarowego i innych wizualizacji.

Logika: Komponent będzie pobierał dane z ostatniej pełnej analizy interakcji i dynamicznie je wyświetlał.

### Moduł 3: Centrum Uczenia i Dialogu (AI Dojo)

Wizja Biznesowa: Stworzenie skalowalnego mechanizmu transferu wiedzy eksperckiej. Zamiast kosztownych szkoleń, najlepszy sprzedawca może w trybie konwersacyjnym "uczyć" całą flotę AI, podnosząc kompetencje całego zespołu. To także system wczesnego ostrzegania o zmianach na rynku.

Doświadczenie Użytkownika (UX): Użytkownik wchodzi do dedykowanego interfejsu czatu. AI wita go i pyta, czym mogą się dzisiaj zająć. Użytkownik może swobodnie pisać, np. "Kia wprowadziła nowy model EV". AI natychmiast przechodzi w tryb "dociekliwego analityka", zadając serię pytań. Innym razem AI może samo zainicjować rozmowę: "Zauważyłem, że oceniłeś negatywnie moją sugestię dotyczącą rabatów dla klienta Z. Czy moglibyśmy to omówić?".

Logika Działania AI (Mózg Systemu): To najbardziej złożony moduł.

Router Intencji: Pierwszym krokiem AI po otrzymaniu wiadomości jest jej klasyfikacja: [Aktualizacja Wiedzy], [Analiza Feedbacku], [Pytanie Ogólne].

Dynamiczne Scenariusze: W zależności od intencji, AI uruchamia odpowiedni scenariusz konwersacyjny.

Dla [Aktualizacja Wiedzy], celem jest zebranie kompletnych, ustrukturyzowanych danych i zapisanie ich w Qdrant.

Dla [Analiza Feedbacku], celem jest zrozumienie przyczyny błędu i wygenerowanie nowej "metazasady" (np. "Nie proponuj rabatów klientom o profilu 'Wizjoner' na wczesnym etapie rozmowy").

Specyfikacja Techniczna:

Backend:

Router (routers/dojo.py): Nowy router z endpointem POST /dojo/conversation.

AI Service (services/ai_service.py): Nowa, złożona funkcja handle_dojo_conversation, która zarządza stanem rozmowy (pamięta poprzednie wiadomości) i dynamicznie generuje prompty w zależności od scenariusza.

Integracja z Qdrant: Funkcja ta będzie miała uprawnienia do zapisu i aktualizacji danych w kolekcji Qdrant.

Frontend:

Strona (AIDojoPage.js): Nowa strona z interfejsem czatu, zarządzająca stanem konwersacji (listą wiadomości) i komunikacją z API.

### Moduł 4: Zaawansowane Wskaźniki Sprzedażowe

Wizja Biznesowa: Zastąpienie "przeczucia" sprzedawcy twardymi, opartymi na danych predykcjami. Pozwala to na obiektywną ocenę lejka sprzedażowego, lepsze prognozowanie i efektywniejsze zarządzanie czasem – skupienie się na klientach o najwyższym potencjale.

Doświadczenie Użytkownika (UX): W głównym widoku sesji, użytkownik widzi panel z czterema kluczowymi wskaźnikami. Są one przedstawione graficznie (wskaźniki zegarowe, paski postępu), co pozwala na błyskawiczną ocenę sytuacji. Kolory sygnalizują pilność (np. wysoki "Churn Risk" na czerwono).

Logika Działania AI (Mózg Systemu): AI działa jak analityk predykcyjny. Analizuje całą rozmowę pod kątem wzorców językowych, sentymentu, rodzaju zadawanych pytań i porównuje je z modelowymi zachowaniami na różnych etapach podróży zakupowej. Na przykład, częste pytania o konkurencję i szczegóły techniczne mogą wskazywać na etap "Porównywanie opcji", podczas gdy pytania o dostępność i finansowanie sygnalizują "Gotowość do zakupu".

Specyfikacja Techniczna:

Backend:

Prompt Engineering (services/ai_service.py): Rozszerzenie system_prompt o sekcję "Analiza Wskaźników Sprzedażowych" z rygorystycznym wymogiem zwrotu danych w formacie JSON.

Schematy Pydantic (schemas/interaction.py): Dodanie modelu SalesIndicators do AIResponse.

Frontend:

Komponent (SalesIndicatorsPanel.js): Nowy komponent do wizualizacji danych, prawdopodobnie z wykorzystaniem tej samej biblioteki co Moduł 2.

## Część III: Strategiczna Mapa Drogowa (Roadmap)

Kolejność wdrożenia jest zaprojektowana tak, aby każdy sprint budował wartość na poprzednim.

Sprint 1: Moduł 1 (Feedback Loop)

Zadania: Backend (Model, Schemat, Router, Repozytorium), Frontend (Modyfikacja AI Service, Komponent, Hook).

Kryteria Ukończenia: Użytkownik może oceniać sugestie AI, a oceny są poprawnie zapisywane w bazie danych.

Sprint 2: Moduł 2 (Analiza Psychometryczna)

Zadania: Backend (Prompt Engineering, Schematy), Frontend (Komponent wizualizacyjny).

Kryteria Ukończenia: Nowy dashboard psychometryczny poprawnie wyświetla analizy generowane przez AI dla każdej interakcji.

Sprint 3: Moduł 4 (Wskaźniki Sprzedażowe)

Zadania: Backend (Prompt Engineering, Schematy), Frontend (Komponent wizualizacyjny).

Kryteria Ukończenia: Nowy panel wskaźników poprawnie wyświetla predykcje generowane przez AI.

Sprint 4: Moduł 3 (AI Dojo)

Zadania: Backend (Router, złożona logika w AI Service, integracja z Qdrant), Frontend (Strona czatu).

Kryteria Ukończenia: Użytkownik może prowadzić dialog z AI w celu aktualizacji wiedzy i analizy feedbacku. Zmiany są odzwierciedlane w bazie wektorowej.

## Część IV: Zarządzanie Ryzykiem

Ryzyko 1: Złożoność Promptów: Rozbudowane prompty mogą spowolnić czas odpowiedzi AI.

Mitigacja: Rygorystyczne testy wydajności po każdym sprincie. Dalsza optymalizacja architektury "Fast Path / Slow Path", aby kluczowe elementy UI pojawiały się natychmiast, niezależnie od czasu pełnej analizy.

Ryzyko 2: "Halucynacje" AI: AI może generować analizy psychometryczne, które nie są w pełni zgodne z rzeczywistością.

Mitigacja: Moduł 1 (Feedback Loop) jest kluczowym narzędziem do kalibracji. Dodatkowo, w promptach będziemy kłaść nacisk na uzasadnianie odpowiedzi (rationale), co pozwoli na łatwiejszą weryfikację.

Ryzyko 3: Zależność Modułów: Błędy w implementacji Modułu 1 (zbieranie danych) bezpośrednio wpłyną na skuteczność Modułu 3 (uczenie się).

Mitigacja: Ścisłe trzymanie się kolejności sprintów i rygorystyczne testy end-to-end po każdym z nich.