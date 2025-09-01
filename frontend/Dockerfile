# Etap budowania
FROM node:20-alpine as builder

# Ustawienie etykiety wersji
LABEL version="v4.2.1"
LABEL description="Sales Copilot Frontend with Ultra Brain v4.2.1 and UI Data Flow Fixes"

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików package
COPY package*.json ./

# Instalacja zależności
RUN npm ci

# Kopiowanie kodu źródłowego
COPY . .

# Ustawienie zmiennych środowiskowych dla build
ENV REACT_APP_VERSION=v4.2.1
ENV REACT_APP_FRONTEND_ARCHITECTURE=ultra_brain_v4.2.1
ENV REACT_APP_ENABLE_ULTRA_BRAIN=true
ENV REACT_APP_ENABLE_UI_FIXES=true
ENV REACT_APP_DEBUG_DATA_FLOW=true

# Budowanie aplikacji
RUN npm run build

# Etap produkcyjny
FROM nginx:alpine

# Ustawienie etykiety wersji
LABEL version="v4.2.1"
LABEL maintainer="Sales Copilot Team"

# Kopiowanie zbudowanej aplikacji
COPY --from=builder /app/build /usr/share/nginx/html

# Kopiowanie pliku test-data-flow.html do katalogu publicznego
COPY --from=builder /app/test-data-flow.html /usr/share/nginx/html/

# Konfiguracja nginx dla React Router z ulepszonymi ustawieniami
RUN echo 'server { \
    listen 3000; \
    server_name localhost; \
    \
    # Security headers \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
    \
    # Gzip compression \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 1024; \
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json; \
    \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
        \
        # Cache static assets \
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg)$ { \
            expires 1y; \
            add_header Cache-Control "public, immutable"; \
        } \
    } \
    \
    # Test page for debugging \
    location /test-data-flow.html { \
        root /usr/share/nginx/html; \
        add_header Cache-Control "no-cache"; \
    } \
    \
    location /api { \
        proxy_pass http://backend:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        proxy_connect_timeout 60s; \
        proxy_send_timeout 60s; \
        proxy_read_timeout 60s; \
    } \
    \
    location /ws { \
        proxy_pass http://backend:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_connect_timeout 60s; \
        proxy_send_timeout 60s; \
        proxy_read_timeout 60s; \
    } \
    \
    # Health check endpoint \
    location /health { \
        access_log off; \
        return 200 "healthy\\n"; \
        add_header Content-Type text/plain; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Zmienne środowiskowe
ENV NGINX_VERSION=alpine
ENV APP_VERSION=v4.2.1
ENV FRONTEND_ARCHITECTURE=ultra_brain_v4.2.1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
