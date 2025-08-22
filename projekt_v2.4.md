# Plan Projektowy v2.4 (Kompletny Blueprint): Osobisty Co-Pilot Sprzedaży AI

Wersja dokumentu: 2.4

Data: 21.08.2025

Status: Aktywny - Nadrzędne i Jedyne Źródło Prawdy

## Część I: Manifest, Filozofia i Architektura

### 1. Manifest Projektu: Od Narzędzia do Partnera

Wersja 1.0 stworzyła nam doskonałego, reaktywnego Asystenta. Wersja 2.0 ma za zadanie powołać do życia proaktywnego, uczącego się Partnera Strategicznego. Różnica jest fundamentalna:

Asystent odpowiada na pytania.

Partner przewiduje pytania, których jeszcze nie zadałeś, rozumie głębszy kontekst i aktywnie dąży do samodoskonalenia.

Celem jest stworzenie systemu, który staje się prawdziwym rozszerzeniem intuicji i wiedzy eksperckiej sprzedawcy.

### 2. Fundament Niezmienności: Nasza Działająca Baza v1.0

Prace nad v2.0 opierają się na nienaruszalności stabilnej i w pełni funkcjonalnej architektury v1.0. Poniższe elementy są naszym punktem wyjścia i nie podlegają modyfikacji, a jedynie rozszerzeniu:

Architektura Ogólna: W pełni skonteneryzowana (docker-compose.yml) z usługami: Backend (FastAPI), Frontend (React), Baza Danych (PostgreSQL), Baza Wektorowa (Qdrant).

Backend (FastAPI):

Warstwowa Struktura: W pełni działająca logika w podziale na routers, services, repositories, models, schemas.

Core API: Stabilne i przetestowane endpointy do zarządzania Klientami, Sesjami i Interakcjami.

Integracja z AI (Ollama): Działająca komunikacja z modelem gpt-oss:120b przez turbo i chmure ollama !!!

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
     |                                             |        (Przechowuje stany sesji, wyniki, feedback)
     |                                             |
     +---------------------------------------------> [Moduł 1 & 5: Feedback & Session Lifecycle API]
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

Wizja Biznesowa: Stworzenie silnika samodoskonalenia. Każde "👍" i "👎" to mikrolekcja dla AI.

Specyfikacja Techniczna: Zgodna z poprzednią wersją planu (rozszerzenie modelu Interaction, dedykowany endpoint API).

### Moduł 2: Zintegrowana Analiza Psychometryczna

Wizja Biznesowa: Zrozumienie "systemu operacyjnego" klienta poprzez integrację modeli Big Five, Schwartz i DISC.

Specyfikacja Techniczna: Zgodna z poprzednią wersją planu (zaawansowany prompt engineering, rozbudowa schematów Pydantic, wizualizacje na frontendzie).

### Moduł 3: Centrum Uczenia i Dialogu (AI Dojo)

Wizja Biznesowa: Stworzenie skalowalnego mechanizmu transferu wiedzy eksperckiej i analizy błędów.

Specyfikacja Techniczna: Zgodna z poprzednią wersją planu (router intencji, dynamiczne scenariusze konwersacyjne, integracja z Qdrant).

### Moduł 4: Zaawansowane Wskaźniki Sprzedażowe

Wizja Biznesowa: Zastąpienie "przeczucia" sprzedawcy twardymi, opartymi na danych predykcjami.

Specyfikacja Techniczna: Zgodna z poprzednią wersją planu (rozszerzenie promptu AI, nowe schematy Pydantic, komponenty wizualizacyjne).

### Moduł 5: Cykl Życia Sesji i Persystencja Pracy (Zaktualizowano)

Wizja Biznesowa: Zapewnienie ciągłości pracy i stworzenie kompletnego repozytorium interakcji z klientem. System staje się centralnym miejscem, które śledzi cały cykl życia klienta od pierwszego zapytania do finalnej decyzji, a następnie wykorzystuje te dane do nauki.

Doświadczenie Użytkownika (UX) - Zaktualizowano:

Automatyczny Zapis: W momencie wygenerowania pierwszej analizy dla nowego klienta, sesja jest automatycznie tworzona w tle i otrzymuje unikalny numer (ID). Użytkownik nie musi niczego klikać, aby zapisać pracę.

Dashboard jako Centrum Dowodzenia: Główny widok aplikacji (Dashboard) staje się listą wszystkich zapisanych sesji. Każda pozycja na liście pokazuje: ID Sesji, Alias Klienta, Status (🟢 Aktywna / ✅ Zakończona) oraz datę ostatniej aktywności.

Płynny Powrót do Pracy: Użytkownik może w dowolnym momencie kliknąć na dowolną Aktywną sesję na liście. System natychmiast przenosi go do widoku tej sesji, ładując całą historię rozmowy i ostatnią wygenerowaną analizę. Praca jest kontynuowana dokładnie w tym miejscu, w którym została przerwana.

Finalizacja Cyklu: Gdy cykl sprzedażowy dobiega końca, użytkownik w widoku sesji klika przycisk "Zakończ Sesję". Otwiera się modal, w którym wybiera ostateczny rezultat (np. "Klient kupił", "Klient nie kupił") i dodaje notatkę. Sesja zmienia status na Zakończona.

Logika Działania AI (Mózg Systemu): Kluczowe jest gromadzenie danych o rezultatach w powiązaniu z całą historią sesji. W AI Dojo, AI będzie mogło zadawać pytania typu: "Przeanalizowałem sesję #123, która zakończyła się sukcesem. Zauważyłem, że kluczowym momentem było użycie strategii X po tym, jak klient wyraził obawę Y. Czy to jest wzorzec, który powinniśmy stosować częściej?".

Specyfikacja Techniczna - Zaktualizowano:

Backend:

Model SQLAlchemy (models/domain.py): W klasie Session dodajemy pola: status: Column(String, default='active', nullable=False) oraz outcome_data: Column(JSONB, nullable=True).

Logika Tworzenia Sesji: Endpoint POST /interactions zostanie zmodyfikowany. Jeśli w zapytaniu session_id jest null, system najpierw automatycznie tworzy nową sesję w SessionRepository, a następnie przypisuje do niej nową interakcję. Zwraca pełny obiekt interakcji wraz z nowym session_id.

Router (routers/sessions.py): Rozbudowujemy router o:

GET /sessions: Pobiera listę wszystkich sesji dla widoku dashboardu.

GET /sessions/{session_id}: Pobiera szczegóły jednej sesji wraz ze wszystkimi powiązanymi interakcjami.

POST /sessions/{session_id}/conclude: Przyjmuje dane o rezultacie, aktualizuje outcome_data i zmienia status na 'closed'.

Frontend:

Główny Widok (Dashboard.js): Zostanie przebudowany, aby pobierać i wyświetlać listę sesji z endpointu GET /sessions.

Nawigacja: Kliknięcie sesji na liście nawiguje do SessionDetail.js, przekazując session_id w URL.

Ładowanie Stanu (SessionDetail.js): Komponent, po zamontowaniu, użyje session_id z URL, aby wywołać GET /sessions/{session_id} i załadować całą historię interakcji do stanu.

Komponent Modala (ConcludeSessionModal.js): Nowy komponent z formularzem do finalizacji sesji.

## Część III: Strategiczna Mapa Drogowa (Roadmap)

Aktualizujemy mapę drogową, aby odzwierciedlić priorytety.

Sprint 1: Moduł 1 (Feedback Loop)

Kryteria Ukończenia: Użytkownik może oceniać sugestie AI, a oceny są poprawnie zapisywane w bazie danych.

Sprint 2: Moduł 2 (Analiza Psychometryczna)

Kryteria Ukończenia: Nowy dashboard psychometryczny poprawnie wyświetla analizy generowane przez AI.

Sprint 3: Moduł 4 (Wskaźniki Sprzedażowe)

Kryteria Ukończenia: Nowy panel wskaźników poprawnie wyświetla predykcje generowane przez AI.

Sprint 4: Moduł 5 (Cykl Życia Sesji)

Kryteria Ukończenia: Sesje są automatycznie zapisywane. Użytkownik może pauzować, wznawiać i finalizować sesje z podaniem rezultatu. Dane są poprawnie zapisywane.

Sprint 5: Moduł 3 (AI Dojo)

Kryteria Ukończenia: Użytkownik może prowadzić dialog z AI w celu aktualizacji wiedzy i analizy feedbacku (z Modułu 1) oraz wyników sesji (z Modułu 5).

## Część IV: Zarządzanie Ryzykiem

Ryzyko 1: Złożoność Promptów:

Mitigacja: Rygorystyczne testy wydajności, optymalizacja architektury "Fast Path / Slow Path".

Ryzyko 2: "Halucynacje" AI:

Mitigacja: Moduł 1 (Feedback Loop) i pole rationale w odpowiedziach AI.

Ryzyko 3: Zależność Modułów:

Mitigacja: Ścisłe trzymanie się kolejności sprintów i rygorystyczne testy end-to-end.