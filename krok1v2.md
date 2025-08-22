Tytuł Zadania: Implementacja Modułu 3 - Interaktywne AI Dojo ("Sparing z Mistrzem")
1. Kontekst i Cel (DLACZEGO?)
Kontekst: Projekt jest w wersji 0.3.0 - PRODUCTION READY. Wszystkie kluczowe systemy, w tym Ollama Turbo AI i Granularny System Ocen, są w pełni operacyjne i stabilne. Naszym następnym celem, zgodnie z roadmapą, jest budowa Modułu 3: AI Dojo, który wprowadzi do systemu zdolność samodoskonalenia.

Cel Biznesowy: Stworzenie interaktywnego mechanizmu treningowego "Sparing z Mistrzem". Umożliwi on administratorowi (ekspertowi) prowadzenie na żywo rozmowy z AI w celu błyskawicznego uczenia go, korygowania błędów i aktualizowania bazy wiedzy Qdrant. To drastycznie przyspieszy proces adaptacji AI do nowych informacji (np. zmiana oferty produktowej) i podniesie jego ogólną skuteczność.

2. Wymagania Architektoniczne (CO i JAK?)
Musimy rozbudować system o nową, odizolowaną ścieżkę komunikacji przeznaczoną wyłącznie do treningu. Kluczowe jest, aby nie modyfikować i nie naruszać istniejącej logiki generowania sugestii sprzedażowych.

Implementacja będzie wymagała:

Backend: Stworzenia nowego routera, serwisu i schematów Pydantic dedykowanych dla Dojo.

Frontend: Stworzenia nowego, re-używalnego komponentu chatu, nowego hooka do zarządzania jego stanem oraz nowego serwisu API, które zostaną zintegrowane z istniejącym panelem admina.

3. Plan Działania - Backend
Zasada nadrzędna: Nie modyfikuj plików interactions.py, sessions.py ani feedback.py. Twórz nowe, dedykowane pliki dla logiki Dojo.

Krok 1: Stwórz nowy Router (dojo.py)

W folderze backend/app/routers/ stwórz nowy plik dojo.py.

Zdefiniuj w nim nowy APIRouter z prefixem /dojo i tagiem Dojo.

Stwórz w nim jeden endpoint: POST /chat, który będzie przyjmował dane od administratora.

Zabezpiecz ten endpoint (na razie koncepcyjnie) jako dostępny tylko dla admina.

Ważne: Pamiętaj, aby zaimportować i zarejestrować ten nowy router w głównym pliku aplikacji backend/main.py, dodając app.include_router(dojo.router).

Krok 2: Stwórz nowe Schematy (schemas/dojo.py)

W backend/app/schemas/ stwórz plik dojo.py.

Zdefiniuj w nim modele Pydantic dla nowego endpointu:

DojoMessageRequest: powinien zawierać pole message: str oraz opcjonalnie conversation_history: List[Dict].

DojoMessageResponse: powinien zawierać pole response: str, response_type: str (np. 'question', 'confirmation', 'status') oraz opcjonalnie structured_data: Optional[Dict].

Krok 3: Stwórz nowy Serwis (dojo_service.py)

W folderze backend/app/services/ stwórz nowy plik dojo_service.py.

Stwórz w nim główną funkcję, np. async def handle_dojo_conversation(...).

To jest serce logiki:

Funkcja ta będzie wywoływana przez router /dojo/chat.

Będzie ona zarządzać stanem konwersacji treningowej.

Wywoła istniejący ai_service, ale w nowym, specjalnym trybie treningowym.

Krok 4: Zmodyfikuj ai_service.py w sposób bezpieczny

Otwórz backend/app/services/ai_service.py.

Dodaj do istniejącej funkcji generującej odpowiedź (np. get_ai_response) nowy, opcjonalny parametr, np. mode: str = 'suggestion'.

Wewnątrz tej funkcji zaimplementuj logikę warunkową:

if mode == 'suggestion': użyj istniejącego, sprawdzonego promptu do generowania sugestii sprzedażowych. Nie zmieniaj tej części kodu!

if mode == 'training': użyj nowego, zupełnie innego systemowego promptu. Ten prompt musi instruować Ollama Turbo AI, aby działał jak analityk wiedzy: "Twoim zadaniem jest analiza poniższego tekstu. Jeśli jest on dla Ciebie niejasny lub niekompletny, zadaj pytania doprecyzowujące. Gdy zrozumiesz kontekst, ustrukturyzuj tę wiedzę w formacie JSON i poproś o potwierdzenie przed zapisem."

dojo_service.py będzie zawsze wywoływał tę funkcję z parametrem mode='training'.

Krok 5: Wykorzystaj istniejący qdrant_service.py

dojo_service.py, po otrzymaniu od AI ustrukturyzowanych danych (JSON) i potwierdzeniu od administratora, ma wywołać istniejącą funkcję w qdrant_service.py do zapisu nowej "bryłki wiedzy". Nie powinno być potrzeby modyfikacji samego qdrant_service.py, a jedynie jego poprawnego użycia.

4. Plan Działania - Frontend
Zasada nadrzędna: Buduj nowe, odizolowane komponenty i hooki, aby nie wpływać na działanie istniejących widoków sesji sprzedażowej.

Krok 1: Stwórz nowy Serwis API (dojoApi.js)

W folderze frontend/src/services/ stwórz nowy plik dojoApi.js.

Zdefiniuj w nim asynchroniczną funkcję, np. export const sendDojoMessage = (payload) => api.post('/dojo/chat', payload);.

Pamiętaj o dodaniu eksportu do pliku frontend/src/services/index.js.

Krok 2: Stwórz nowy Hook (useDojoChat.js)

W folderze frontend/src/hooks/ stwórz nowy plik useDojoChat.js.

Hook ten powinien zarządzać stanem konwersacji: const [messages, setMessages] = useState([]);, const [isLoading, setIsLoading] = useState(false);.

Powinien eksponować jedną główną funkcję, np. sendMessage, która:

Dodaje wiadomość użytkownika do stanu messages.

Ustawia isLoading na true.

Wywołuje sendDojoMessage z dojoApi.js.

Po otrzymaniu odpowiedzi, dodaje ją do stanu messages i ustawia isLoading na false.

Krok 3: Stwórz nowy Komponent (DojoChat.js)

W folderze frontend/src/components/ stwórz nowy folder dojo a w nim plik DojoChat.js.

Komponent ten będzie renderował interfejs chatu.

Użyj w nim hooka useDojoChat do zarządzania logiką (const { messages, sendMessage, isLoading } = useDojoChat();).

Zaimplementuj logikę renderowania: mapuj tablicę messages do komponentów ChatMessage. Pokaż wskaźnik ładowania, gdy isLoading jest true.

Ważne: Zaimplementuj specjalne renderowanie dla wiadomości od AI typu confirmation. Jeśli wiadomość zawiera structured_data, wyświetl je w sformatowanym bloku <pre> i dodaj przyciski "Zatwierdź i zapisz w bazie wiedzy" oraz "Anuluj". Kliknięcie "Zatwierdź" powinno wysłać specjalną wiadomość do backendu.

Krok 4: Zintegruj DojoChat.js z Panelem Admina

Otwórz istniejący plik strony frontend/src/pages/AdminBrainInterface.js.

Zaimportuj nowo utworzony komponent DojoChat.

Dodaj w strukturze JSX tej strony nową, wyraźnie oznaczoną sekcję, np. w nowej zakładce (Tab) lub w osobnym kontenerze (Card) z tytułem "AI Dojo: Sparing z Mistrzem".

Umieść w tej sekcji komponent <DojoChat />.