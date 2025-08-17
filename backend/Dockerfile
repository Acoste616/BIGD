# Etap budowania
FROM python:3.11-slim as builder

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
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
FROM python:3.11-slim

# Instalacja zależności systemowych dla runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie zainstalowanych pakietów z etapu budowania
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie kodu aplikacji
COPY . .

# Utworzenie użytkownika nieroot
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Komenda startowa
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
