# Etap budowania
FROM python:3.12-slim as builder

# Ustawienie etykiety wersji
LABEL version="v4.2.1"
LABEL description="Sales Copilot Backend with Session Orchestrator Service and Frontend UI Fixes"

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalacja Poetry
RUN pip install poetry==1.7.1

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików konfiguracyjnych Poetry
COPY pyproject.toml poetry.lock* ./

# Instalacja zależności
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Etap produkcyjny
FROM python:3.12-slim

# Ustawienie etykiety wersji
LABEL version="v4.2.1"
LABEL maintainer="Sales Copilot Team"

# Instalacja zależności systemowych dla runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie zainstalowanych pakietów z etapu budowania
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie kodu aplikacji
COPY . .

# Tworzenie katalogu na logi
RUN mkdir -p /app/logs

# Utworzenie użytkownika nieroot
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Zmienne środowiskowe
ENV PYTHONPATH=/app
ENV APP_VERSION=v4.2.1
ENV BACKEND_ARCHITECTURE=modular_session_orchestrator

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Komenda startowa
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
