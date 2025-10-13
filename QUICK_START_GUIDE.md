# 🚀 ULTRABIGDECODER - QUICK START GUIDE

**System gotowy do uruchomienia w 5 minut!**

---

## 📋 WYMAGANIA WSTĘPNE

### 1. Ollama Turbo API Key (WYMAGANE)

**Gdzie zdobyć:**
- Odwiedź: https://ollama.ai/
- Zarejestruj konto
- Przejdź do sekcji API Keys
- Wygeneruj nowy klucz API

**Format klucza:**
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. Oprogramowanie

- **Docker & Docker Compose** (zalecane)
  - Docker Desktop (Windows/Mac)
  - Docker Engine + Docker Compose (Linux)

**LUB**

- **Python 3.11+** (dla lokalnego dev)
- **PostgreSQL 16**
- **Qdrant Vector DB**

---

## ⚡ SZYBKI START (Docker - Zalecane)

### Krok 1: Konfiguracja API Key

```bash
# Otwórz plik .env w katalogu głównym
nano .env

# Zamień linię:
OLLAMA_API_KEY=YOUR_OLLAMA_API_KEY_HERE

# Na swoją API Key:
OLLAMA_API_KEY=sk-twoj-klucz-tutaj
```

**WAŻNE:** Bez prawidłowego klucza API system NIE BĘDZIE DZIAŁAĆ!

### Krok 2: Uruchomienie Systemu

```bash
# Windows
start_docker_v4.2.1.bat

# Linux/Mac
./start_docker_v4.2.1.sh

# Lub manualnie:
docker-compose up --build
```

### Krok 3: Weryfikacja

Po 30-60 sekundach otwórz w przeglądarce:

```
Frontend: http://localhost:3000
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs
```

**Health Checks:**
```bash
# Sprawdź status wszystkich komponentów
curl http://localhost:8000/health

# Sprawdź status bazy danych
curl http://localhost:8000/health/db

# Sprawdź połączenie z Ollama Turbo API
curl http://localhost:8000/health/ollama
```

---

## 🔧 KONFIGURACJA ZAAWANSOWANA

### Zmiana Modelu AI

W pliku `.env`:

```bash
# Dostępne modele (przykłady):
OLLAMA_MODEL=gpt-4-turbo          # Najlepszy (droższy)
OLLAMA_MODEL=gpt-3.5-turbo        # Szybki (tańszy)
OLLAMA_MODEL=gpt-4                # Balans
```

### Zmiana Limitów API

```bash
# Maksymalna liczba tokenów na request
MAX_TOKENS_PER_REQUEST=4000

# Maksymalna długość kontekstu
MAX_CONTEXT_LENGTH=8000

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600
```

### Tryb Produkcyjny

```bash
# W pliku .env zmień:
ENVIRONMENT=production
DEBUG=false

# Wygeneruj nowe, bezpieczne klucze:
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

---

## 🧪 TESTOWANIE SYSTEMU

### Test 1: Połączenie z Ollama API

```bash
cd backend
python test_ollama_turbo.py
```

**Oczekiwany output:**
```
🧪 OLLAMA TURBO API - CONNECTION TEST
================================================================================
📋 Step 1: Checking Configuration...
API Key: sk-abc12...xyz9 ✅
✅ BaseAIService initialized successfully
✅ Ollama Turbo API is reachable and authenticated
✅ Chat completion test PASSED
🎉 ALL TESTS PASSED - OLLAMA TURBO API IS WORKING!
```

### Test 2: Analiza End-to-End

```bash
cd backend
pytest tests/test_e2e_workflow.py -v
```

### Test 3: Ręczny Test UI

1. Otwórz http://localhost:3000
2. Kliknij "Nowa Sesja Sprzedażowa"
3. Wprowadź dane klienta
4. Dodaj pierwszą interakcję
5. Sprawdź czy pojawia się analiza AI

---

## 🐛 TROUBLESHOOTING

### Problem: "OLLAMA_API_KEY not configured"

**Rozwiązanie:**
```bash
# Upewnij się, że plik .env istnieje w katalogu głównym
ls -la .env

# Jeśli nie istnieje, skopiuj z template:
cp .env.fixed .env

# Edytuj i dodaj swój klucz:
nano .env
```

### Problem: "401 Unauthorized" przy wywołaniu API

**Przyczyny:**
- Nieprawidłowy klucz API
- Klucz wygasł
- Brak uprawnień

**Rozwiązanie:**
1. Sprawdź klucz na https://ollama.ai/
2. Wygeneruj nowy klucz jeśli potrzeba
3. Zaktualizuj `.env`
4. Zrestartuj kontenery: `docker-compose restart`

### Problem: "429 Rate Limit Exceeded"

**Rozwiązanie:**
- Poczekaj kilka minut
- Rozważ upgrade planu API
- Zmień model na tańszy (np. gpt-3.5-turbo)

### Problem: Backend nie startuje

**Sprawdź logi:**
```bash
docker-compose logs backend
```

**Najczęstsze przyczyny:**
- Brak połączenia z PostgreSQL
- Brak połączenia z Qdrant
- Błąd w migracji bazy danych

**Rozwiązanie:**
```bash
# Restart całego stack'u
docker-compose down --volumes
docker-compose up --build
```

### Problem: Frontend pokazuje błędy

**Sprawdź:**
1. Czy backend działa: http://localhost:8000/health
2. Czy jest połączenie z backendem
3. Sprawdź Console w DevTools (F12)

**Rozwiązanie:**
```bash
# Przebuduj frontend
docker-compose up --build frontend
```

---

## 📊 MONITORING WYDAJNOŚCI

### Sprawdzanie Statusu Systemu

```bash
# Status wszystkich komponentów
curl http://localhost:8000/health | jq

# Cache statistics
curl http://localhost:8000/service/health | jq

# Statystyki bazy danych
curl http://localhost:8000/health/db | jq
```

### Sprawdzanie Zużycia Tokenów

Token usage jest logowany w każdej odpowiedzi AI:

```bash
# Sprawdź logi backendu
docker-compose logs backend | grep "Token Usage"
```

---

## 🎯 PIERWSZE KROKI PO URUCHOMIENIU

### 1. Zasilenie Bazy Wiedzy (Qdrant)

```bash
cd backend
python scripts/seed_qdrant.py
```

To dodaje "bryłki wiedzy" (knowledge nuggets) do systemu RAG.

### 2. Utwórz Pierwszego Klienta

**Przez UI:**
1. Przejdź do http://localhost:3000
2. Kliknij "Dashboard" → "Dodaj Klienta"
3. Wypełnij formularz

**Przez API:**
```bash
curl -X POST http://localhost:8000/api/v1/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "alias": "Jan Kowalski",
    "demographic_data": {
      "age_range": "35-45",
      "occupation": "Menedżer IT",
      "family_status": "Rodzina z dziećmi"
    }
  }'
```

### 3. Utwórz Pierwszą Sesję Sprzedażową

```bash
curl -X POST http://localhost:8000/api/v1/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "session_type": "initial_contact"
  }'
```

### 4. Dodaj Pierwszą Interakcję (z AI Analysis!)

```bash
curl -X POST http://localhost:8000/api/v1/sessions/1/interactions/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Klient powiedział: Szukam samochodu elektrycznego dla rodziny, ważne jest bezpieczeństwo.",
    "interaction_type": "customer_statement"
  }'
```

**Odpowiedź zawiera:**
- Analizę psychometryczną (Big Five, DISC, Schwartz)
- Archetyp klienta
- Strategię sprzedażową
- Sugerowane pytania
- Rekomendacje następnych kroków

---

## 📚 DODATKOWE ZASOBY

### Dokumentacja API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Przykłady API Calls

Zobacz pliki w `backend/api_examples/`:
- `clients.http` - Operacje na klientach
- `sessions.http` - Zarządzanie sesjami
- `interactions.http` - Tworzenie interakcji
- `feedback.http` - System feedback

### Architektura Systemu

Zobacz `ULTRABIGDECODER_DIAGNOSTIC_REPORT.md` dla szczegółowej analizy architektury.

---

## 🆘 WSPARCIE

### Problemy?

1. Sprawdź logi: `docker-compose logs backend`
2. Sprawdź health checks: http://localhost:8000/health
3. Uruchom test: `python backend/test_ollama_turbo.py`

### Najczęstsze Pytania

**Q: Jak długo trwa analiza AI?**
A: Zwykle 3-8 sekund dla pierwszej analizy, <1s dla kolejnych (cache).

**Q: Czy mogę używać lokalnego Ollama zamiast Cloud API?**
A: Tak, zmień `OLLAMA_API_URL` na `http://localhost:11434` i usuń `OLLAMA_API_KEY`.

**Q: Jak resetować system?**
A: `docker-compose down --volumes && docker-compose up --build`

**Q: Gdzie są zapisane dane?**
A: PostgreSQL (dane strukturalne) + Qdrant (embeddings) w Docker volumes.

---

## ✅ CHECKLIST GOTOWOŚCI

Przed użyciem w produkcji upewnij się:

- [ ] OLLAMA_API_KEY jest poprawnie skonfigurowany
- [ ] Wszystkie health checks zwracają "healthy"
- [ ] Test `test_ollama_turbo.py` przechodzi pomyślnie
- [ ] SECRET_KEY i JWT_SECRET_KEY zostały zmienione
- [ ] Baza wiedzy Qdrant została zasilona
- [ ] Frontend działa i komunikuje się z backendem
- [ ] Przetestowano pełny flow: klient → sesja → interakcja → AI analysis

---

**SUKCES!** 🎉

System ULTRABIGDECODER jest gotowy do rewolucjonizowania Twojej sprzedaży!

Każda interakcja z klientem to teraz głęboka analiza psychologiczna i strategia sprzedażowa oparta na AI.

**Powodzenia w sprzedaży!** 🚀
