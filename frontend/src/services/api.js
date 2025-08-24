/**
 * Główny klient API do komunikacji z backendem
 * Zawiera konfigurację axios i podstawowe interceptory
 */
import axios from 'axios';

// Domyślna konfiguracja - używamy zmiennych środowiskowych React
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api/v1';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT) || 45000; // 45s dla Ultra Mózgu

// Tworzymy główną instancję axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor - możemy tu dodać autoryzację w przyszłości
apiClient.interceptors.request.use(
  (config) => {
    // Logowanie requestów w trybie debug
    if (process.env.REACT_APP_DEBUG === 'true') {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }

    // Tu w przyszłości dodamy token autoryzacji
    // const token = localStorage.getItem('authToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }

    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - obsługa błędów i transformacja odpowiedzi
apiClient.interceptors.response.use(
  (response) => {
    // Logowanie odpowiedzi w trybie debug
    if (process.env.REACT_APP_DEBUG === 'true') {
      console.log(`API Response: ${response.config.url}`, response.data);
    }

    // Zwracamy tylko dane, bez całego obiektu response
    return response.data;
  },
  (error) => {
    // Zunifikowana obsługa błędów
    let errorMessage = 'Wystąpił nieoczekiwany błąd';
    let errorCode = 'UNKNOWN_ERROR';
    let statusCode = null;

    if (error.response) {
      // Błąd z odpowiedzią serwera
      statusCode = error.response.status;
      errorMessage = error.response.data?.detail || error.response.data?.message || errorMessage;
      
      switch (statusCode) {
        case 400:
          errorCode = 'BAD_REQUEST';
          break;
        case 401:
          errorCode = 'UNAUTHORIZED';
          // Tu możemy przekierować do logowania
          break;
        case 403:
          errorCode = 'FORBIDDEN';
          break;
        case 404:
          errorCode = 'NOT_FOUND';
          errorMessage = 'Zasób nie został znaleziony';
          break;
        case 422:
          errorCode = 'VALIDATION_ERROR';
          // FastAPI zwraca szczegóły walidacji
          if (error.response.data?.detail && Array.isArray(error.response.data.detail)) {
            errorMessage = error.response.data.detail
              .map(err => `${err.loc.join('.')}: ${err.msg}`)
              .join(', ');
          }
          break;
        case 500:
          errorCode = 'SERVER_ERROR';
          errorMessage = 'Błąd serwera. Spróbuj ponownie później';
          break;
      }
    } else if (error.request) {
      // Brak odpowiedzi od serwera
      errorCode = 'NETWORK_ERROR';
      errorMessage = 'Nie można połączyć się z serwerem';
    } else {
      // Błąd konfiguracji żądania
      errorCode = 'REQUEST_ERROR';
      errorMessage = error.message;
    }

    // Zwracamy ustandaryzowany obiekt błędu
    const standardError = {
      code: errorCode,
      message: errorMessage,
      statusCode,
      originalError: error,
    };

    console.error('API Error:', standardError);
    return Promise.reject(standardError);
  }
);

// Helper do budowania query params
export const buildQueryString = (params) => {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(v => searchParams.append(key, v));
      } else {
        searchParams.append(key, value);
      }
    }
  });
  
  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
};

// Eksportujemy instancję klienta jako domyślną
export default apiClient;

// Eksportujemy też pomocnicze funkcje
export { API_BASE_URL, API_TIMEOUT };
