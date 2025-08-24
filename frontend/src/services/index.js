/**
 * Główny punkt eksportu dla wszystkich modułów API
 * Importuj stąd wszystkie funkcje API w komponentach
 */

// Eksport głównego klienta API
export { default as apiClient, buildQueryString, API_BASE_URL, API_TIMEOUT } from './api';

// Eksport funkcji modułu Klientów
export {
  getClients,
  getClientById,
  createClient,
  updateClient,
  deleteClient,
  getClientStatistics,
  searchClients,
  getClientsByArchetype,
  getAvailableArchetypes,
  formatClientData,
  validateClientData
} from './clientsApi';

// Eksport funkcji modułu Sesji
export {
  getClientSessions,
  getSessionById,
  createSession,
  updateSession,
  endSession,
  deleteSession,
  getSessionStatistics,
  getRecentSessions,
  getClientEngagement,
  formatSessionData,
  validateSessionData,
  getAvailableSessionTypes,
  getAvailableOutcomes
} from './sessionsApi';

// Eksport funkcji modułu Interakcji
export {
  getSessionInteractions,
  getInteractionById,
  createInteraction,
  updateInteraction,
  deleteInteraction,
  getInteractionStatistics,
  getConversationAnalysis,
  getRecentInteractions,
  formatInteractionData,
  validateInteractionData,
  getAvailableInteractionTypes,
  sendClarifyingAnswer,  // DEPRECATED: Interactive Psychometric Flow
  sendSessionQuestionAnswer  // NOWY v3.0: Session-level question answering
} from './interactionsApi';

// Eksport funkcji modułu Knowledge Management
export {
  getKnowledgeList,
  getKnowledgeById,
  createKnowledge,
  deleteKnowledge,
  searchKnowledge,
  getKnowledgeStats,
  bulkCreateKnowledge,
  bulkImportFromJSON,
  getQdrantHealth,
  getAvailableKnowledgeTypes,
  deleteAllKnowledge,
  formatKnowledgeData,
  validateKnowledgeData,
  validateSearchData,
  getLocalKnowledgeTypes,
  getAvailableKnowledgeArchetypes,
  formatSearchResults
} from './knowledgeApi';

// Eksport funkcji modułu Feedback (Blueprint Granularny System Ocen)
export {
  createFeedback,
  formatFeedbackData,
  isSuggestionRated,
  getFeedbackStats
} from './feedbackApi';

// Eksport funkcji modułu AI Dojo (Moduł 3: Sparing z Mistrzem)
export {
  sendDojoMessage,
  confirmKnowledgeWrite,
  getSessionSummary,
  getDojoAnalytics,
  getDojoHealth,
  validateDojoMessage,
  validateStructuredData,
  formatDojoResponse,
  generateSessionId,
  TRAINING_MODES,
  RESPONSE_TYPES,
  KNOWLEDGE_TYPES
} from './dojoApi';

// Przyszłe moduły API (placeholder)
// export * from './authApi';

/**
 * Pomocnicze funkcje do obsługi stanów ładowania i błędów
 */

// Stan początkowy dla danych listowych
export const initialListState = {
  data: [],
  loading: false,
  error: null,
  pagination: {
    total: 0,
    page: 1,
    size: 10,
    pages: 0
  }
};

// Stan początkowy dla pojedynczych obiektów
export const initialItemState = {
  data: null,
  loading: false,
  error: null
};

/**
 * Helper do obsługi błędów API w komponentach
 * @param {Error} error - Błąd z API
 * @param {Function} setError - Setter stanu błędu
 * @param {Function} showNotification - Opcjonalna funkcja do pokazania notyfikacji
 */
export const handleApiError = (error, setError, showNotification = null) => {
  const errorMessage = error.message || 'Wystąpił nieoczekiwany błąd';
  
  setError(errorMessage);
  
  if (showNotification) {
    showNotification({
      type: 'error',
      message: errorMessage,
      duration: 5000
    });
  }
  
  console.error('API Error handled:', error);
};

/**
 * Helper do resetowania błędów po określonym czasie
 * @param {Function} setError - Setter stanu błędu
 * @param {number} delay - Opóźnienie w ms (domyślnie 5000)
 */
export const clearErrorAfterDelay = (setError, delay = 5000) => {
  setTimeout(() => {
    setError(null);
  }, delay);
};

/**
 * Wrapper do wykonywania operacji API z obsługą stanów
 * @param {Function} apiCall - Funkcja API do wywołania
 * @param {Function} setLoading - Setter stanu ładowania
 * @param {Function} setError - Setter stanu błędu
 * @param {Function} onSuccess - Callback po sukcesie
 * @param {Function} onError - Opcjonalny callback po błędzie
 */
export const executeApiCall = async (
  apiCall,
  setLoading,
  setError,
  onSuccess,
  onError = null
) => {
  setLoading(true);
  setError(null);
  
  try {
    const result = await apiCall();
    onSuccess(result);
    return result;
  } catch (error) {
    handleApiError(error, setError);
    if (onError) {
      onError(error);
    }
    throw error;
  } finally {
    setLoading(false);
  }
};

/**
 * Pomocnicza funkcja do debounce (opóźnienia) wywołań API
 * Przydatna np. przy wyszukiwaniu w czasie rzeczywistym
 * @param {Function} func - Funkcja do opóźnienia
 * @param {number} delay - Opóźnienie w ms
 * @returns {Function} Opóźniona funkcja
 */
export const debounce = (func, delay) => {
  let timeoutId;
  
  return (...args) => {
    clearTimeout(timeoutId);
    
    return new Promise((resolve) => {
      timeoutId = setTimeout(async () => {
        const result = await func(...args);
        resolve(result);
      }, delay);
    });
  };
};

/**
 * Helper do cache'owania wyników API w sessionStorage
 * @param {string} key - Klucz cache
 * @param {any} data - Dane do zapisania
 * @param {number} ttl - Czas życia w minutach (domyślnie 5)
 */
export const cacheApiResponse = (key, data, ttl = 5) => {
  const cacheData = {
    data,
    timestamp: Date.now(),
    ttl: ttl * 60 * 1000 // Konwersja na milisekundy
  };
  
  try {
    sessionStorage.setItem(`api_cache_${key}`, JSON.stringify(cacheData));
  } catch (e) {
    console.warn('Failed to cache API response:', e);
  }
};

/**
 * Helper do pobierania danych z cache
 * @param {string} key - Klucz cache
 * @returns {any|null} Dane z cache lub null jeśli wygasły/nie istnieją
 */
export const getCachedApiResponse = (key) => {
  try {
    const cached = sessionStorage.getItem(`api_cache_${key}`);
    if (!cached) return null;
    
    const { data, timestamp, ttl } = JSON.parse(cached);
    
    if (Date.now() - timestamp > ttl) {
      sessionStorage.removeItem(`api_cache_${key}`);
      return null;
    }
    
    return data;
  } catch (e) {
    console.warn('Failed to get cached API response:', e);
    return null;
  }
};

/**
 * Helper do czyszczenia cache API
 * @param {string} prefix - Opcjonalny prefix kluczy do wyczyszczenia
 */
export const clearApiCache = (prefix = null) => {
  const keys = Object.keys(sessionStorage);
  
  keys.forEach(key => {
    if (key.startsWith('api_cache_')) {
      if (!prefix || key.includes(prefix)) {
        sessionStorage.removeItem(key);
      }
    }
  });
};

// Eksport feedback API (Blueprint Granularny System Ocen)
export * as feedbackApi from './feedbackApi';