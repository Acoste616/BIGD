/**
 * API Client dla modułu Sesji
 * Komunikacja z backend endpoints dla zarządzania sesjami klientów
 */
import apiClient from './api';

/**
 * Pobiera wszystkie sesje dla konkretnego klienta
 * @param {number} clientId - ID klienta
 * @param {number} page - Numer strony (domyślnie 1)
 * @param {number} size - Rozmiar strony (domyślnie 10)
 * @returns {Promise<Object>} Lista sesji z paginacją
 */
export const getClientSessions = async (clientId, page = 1, size = 10) => {
  if (!clientId) {
    throw new Error('Client ID is required');
  }
  
  const params = new URLSearchParams({
    page: page.toString(),
    size: size.toString()
  });
  
  return await apiClient.get(`/clients/${clientId}/sessions/?${params}`);
};

/**
 * Pobiera szczegóły pojedynczej sesji
 * @param {number} sessionId - ID sesji
 * @param {boolean} includeInteractions - Czy dołączyć listę interakcji
 * @returns {Promise<Object>} Szczegóły sesji
 */
export const getSessionById = async (sessionId, includeInteractions = false) => {
  if (!sessionId) {
    throw new Error('Session ID is required');
  }
  
  const params = includeInteractions ? '?include_interactions=true' : '';
  return await apiClient.get(`/sessions/${sessionId}${params}`);
};

/**
 * Creates a new session for a specific client.
 * @param {string} clientId - The ID of the client for whom to create the session.
 * @param {object} sessionData - The initial data for the session (e.g., notes, type).
 * @returns {Promise<object>} The newly created session object.
 */
export const createSession = async (clientId, sessionData) => {
  // CRITICAL FIX: Ensure clientId is provided.
  if (!clientId) {
    throw new Error("Client ID is required to create a session.");
  }
  try {
    // CRITICAL FIX: Use the correct, nested endpoint.
    const response = await apiClient.post(`/clients/${clientId}/sessions/`, sessionData);
    console.log('✅ Sesja utworzona pomyślnie:', response.data);
    return response.data;
  } catch (error) {
    console.error(`❌ Błąd podczas tworzenia sesji dla klienta ${clientId}:`, error.response?.data || error.message);
    // Re-throw the error to be handled by the component.
    throw new Error(error.response?.data?.detail || "Nie udało się utworzyć sesji.");
  }
};

/**
 * Aktualizuje sesję
 * @param {number} sessionId - ID sesji
 * @param {Object} updateData - Dane do aktualizacji
 * @returns {Promise<Object>} Zaktualizowana sesja
 */
export const updateSession = async (sessionId, updateData) => {
  if (!sessionId) {
    throw new Error('Session ID is required');
  }
  return await apiClient.put(`/sessions/${sessionId}`, updateData);
};

/**
 * Kończy sesję (ustawia end_time)
 * @param {number} sessionId - ID sesji
 * @param {Object} endData - Dane końcowe (summary, outcome, itp.)
 * @returns {Promise<Object>} Zakończona sesja
 */
export const endSession = async (sessionId, endData = {}) => {
  if (!sessionId) {
    throw new Error('Session ID is required');
  }
  return await apiClient.put(`/sessions/${sessionId}/end`, endData);
};

/**
 * Usuwa sesję
 * @param {number} sessionId - ID sesji
 * @returns {Promise<void>}
 */
export const deleteSession = async (sessionId) => {
  if (!sessionId) {
    throw new Error('Session ID is required');
  }
  return await apiClient.delete(`/sessions/${sessionId}`);
};

/**
 * Pobiera statystyki sesji
 * @param {number} sessionId - ID sesji
 * @returns {Promise<Object>} Statystyki sesji
 */
export const getSessionStatistics = async (sessionId) => {
  if (!sessionId) {
    throw new Error('Session ID is required');
  }
  return await apiClient.get(`/sessions/${sessionId}/statistics`);
};

/**
 * Pobiera ostatnie sesje (wszystkich klientów)
 * @param {number} limit - Maksymalna liczba sesji (domyślnie 10)
 * @returns {Promise<Array>} Lista ostatnich sesji
 */
export const getRecentSessions = async (limit = 10) => {
  const params = new URLSearchParams({
    limit: limit.toString()
  });
  
  return await apiClient.get(`/sessions/recent?${params}`);
};

/**
 * Pobiera metryki zaangażowania klienta
 * @param {number} clientId - ID klienta
 * @returns {Promise<Object>} Metryki zaangażowania
 */
export const getClientEngagement = async (clientId) => {
  if (!clientId) {
    throw new Error('Client ID is required');
  }
  return await apiClient.get(`/clients/${clientId}/engagement`);
};

/**
 * Formatuje dane sesji do wyświetlenia
 * @param {Object} session - Obiekt sesji z API
 * @returns {Object} Sformatowane dane sesji
 */
export const formatSessionData = (session) => {
  return {
    ...session,
    displayStartTime: new Date(session.start_time).toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }),
    displayEndTime: session.end_time 
      ? new Date(session.end_time).toLocaleDateString('pl-PL', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      : null,
    isActive: !session.end_time,
    status: !session.end_time ? 'Aktywna' : 'Zakończona',
    duration: session.end_time 
      ? Math.round((new Date(session.end_time) - new Date(session.start_time)) / (1000 * 60)) + ' min'
      : 'W trakcie',
    displayOutcome: session.outcome || 'Brak',
    displayType: session.session_type || 'Konsultacja',
    sentimentLabel: getSentimentLabel(session.sentiment_score),
    potentialLabel: getPotentialLabel(session.potential_score)
  };
};

/**
 * Pomocnicza funkcja do etykietowania sentymentu
 * @param {number} score - Wynik sentymentu (1-10)
 * @returns {string} Etykieta sentymentu
 */
const getSentimentLabel = (score) => {
  if (!score) return 'Nieznany';
  if (score >= 8) return 'Bardzo pozytywny';
  if (score >= 6) return 'Pozytywny';
  if (score >= 4) return 'Neutralny';
  if (score >= 2) return 'Negatywny';
  return 'Bardzo negatywny';
};

/**
 * Pomocnicza funkcja do etykietowania potencjału
 * @param {number} score - Wynik potencjału (1-10)
 * @returns {string} Etykieta potencjału
 */
const getPotentialLabel = (score) => {
  if (!score) return 'Nieznany';
  if (score >= 8) return 'Bardzo wysoki';
  if (score >= 6) return 'Wysoki';
  if (score >= 4) return 'Średni';
  if (score >= 2) return 'Niski';
  return 'Bardzo niski';
};

/**
 * Waliduje dane sesji przed wysłaniem
 * @param {Object} sessionData - Dane sesji do walidacji
 * @returns {Object} Wynik walidacji z błędami
 */
export const validateSessionData = (sessionData) => {
  const errors = {};
  
  // Walidacja typu sesji
  const validTypes = ['consultation', 'follow-up', 'negotiation', 'demo', 'closing'];
  if (sessionData.session_type && !validTypes.includes(sessionData.session_type)) {
    errors.session_type = 'Nieprawidłowy typ sesji';
  }
  
  // Walidacja outcome
  const validOutcomes = ['interested', 'needs_time', 'not_interested', 'closed_deal', 'follow_up_needed'];
  if (sessionData.outcome && !validOutcomes.includes(sessionData.outcome)) {
    errors.outcome = 'Nieprawidłowy wynik sesji';
  }
  
  // Walidacja wyników (1-10)
  if (sessionData.sentiment_score && (sessionData.sentiment_score < 1 || sessionData.sentiment_score > 10)) {
    errors.sentiment_score = 'Wynik sentymentu musi być między 1 a 10';
  }
  
  if (sessionData.potential_score && (sessionData.potential_score < 1 || sessionData.potential_score > 10)) {
    errors.potential_score = 'Wynik potencjału musi być między 1 a 10';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Pobiera dostępne typy sesji
 * @returns {Array} Lista dostępnych typów sesji
 */
export const getAvailableSessionTypes = () => {
  return [
    { value: 'consultation', label: 'Konsultacja', icon: 'chat' },
    { value: 'follow-up', label: 'Kontakt kontrolny', icon: 'phone' },
    { value: 'negotiation', label: 'Negocjacje', icon: 'handshake' },
    { value: 'demo', label: 'Prezentacja/Demo', icon: 'presentation' },
    { value: 'closing', label: 'Finalizacja', icon: 'check_circle' }
  ];
};

/**
 * Pobiera dostępne wyniki sesji
 * @returns {Array} Lista dostępnych wyników sesji
 */
export const getAvailableOutcomes = () => {
  return [
    { value: 'interested', label: 'Zainteresowany', color: 'success' },
    { value: 'needs_time', label: 'Potrzebuje czasu', color: 'warning' },
    { value: 'not_interested', label: 'Niezainteresowany', color: 'error' },
    { value: 'closed_deal', label: 'Transakcja zamknięta', color: 'primary' },
    { value: 'follow_up_needed', label: 'Wymaga kontaktu', color: 'info' }
  ];
};
