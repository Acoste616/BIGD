/**
 * AI Dojo API Service - Komunikacja z backendem AI Dojo
 * 
 * Moduł 3: Interaktywne AI Dojo "Sparing z Mistrzem"
 * 
 * Funkcjonalności:
 * - Chat z AI w trybie treningowym
 * - Potwierdzanie zapisu strukturalnej wiedzy
 * - Zarządzanie sesjami treningowymi
 * - Analityka i statystyki AI Dojo
 */
import apiClient from './api';

/**
 * CORE FUNCTIONS - Główne funkcje komunikacji
 */

/**
 * Wyślij wiadomość do AI w trybie treningowym
 * 
 * @param {Object} payload - Dane wiadomości
 * @param {string} payload.message - Tekst wiadomości eksperta
 * @param {string} [payload.training_mode='knowledge_update'] - Tryb treningu
 * @param {Array} [payload.conversation_history=[]] - Historia konwersacji
 * @param {Object} [payload.client_context=null] - Kontekst klienta
 * @param {string} [sessionId] - ID sesji treningowej
 * @param {string} [expertName='Administrator'] - Nazwa eksperta
 * @returns {Promise<Object>} Odpowiedź AI z strukturą DojoMessageResponse
 * 
 * @example
 * const response = await sendDojoMessage({
 *   message: "Tesla Model Y ma nową opcję kolorystyczną - szary metalik",
 *   training_mode: "knowledge_update"
 * });
 * 
 * if (response.response_type === "confirmation") {
 *   // AI przygotował dane do zapisu
 *   console.log("Structured data:", response.structured_data);
 * }
 */
export const sendDojoMessage = async (payload, sessionId = null, expertName = 'Administrator') => {
  try {
    // Walidacja podstawowa
    if (!payload || !payload.message) {
      throw new Error('Message is required');
    }

    if (payload.message.length > 5000) {
      throw new Error('Message too long (max 5000 characters)');
    }

    // Przygotuj parametry URL
    const params = new URLSearchParams();
    if (sessionId) params.append('session_id', sessionId);
    if (expertName && expertName !== 'Administrator') {
      params.append('expert_name', expertName);
    }

    const url = `/dojo/chat${params.toString() ? `?${params.toString()}` : ''}`;

    // Wyślij żądanie
    const response = await apiClient.post(url, payload);

    // Log sukcesu
    console.log('✅ AI Dojo: Wiadomość wysłana', {
      responseType: response.response_type,
      confidence: response.confidence_level,
      processingTime: response.processing_time_ms
    });

    return response;

  } catch (error) {
    console.error('❌ AI Dojo API Error:', error);
    
    // Sformatuj błąd dla UI
    const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
    
    throw {
      code: 'DOJO_MESSAGE_ERROR',
      message: `Błąd podczas wysyłania wiadomości: ${errorMessage}`,
      statusCode: error.response?.status || 500,
      originalError: error
    };
  }
};

/**
 * Potwierdź i zapisz strukturalną wiedzę do bazy Qdrant
 * 
 * @param {string} sessionId - ID sesji treningowej
 * @param {Object} structuredData - Dane do zapisu
 * @param {string} structuredData.title - Tytuł wiedzy
 * @param {string} structuredData.content - Treść wiedzy
 * @param {string} structuredData.knowledge_type - Typ wiedzy
 * @param {string} [structuredData.archetype] - Docelowy archetyp
 * @param {Array} [structuredData.tags] - Tagi
 * @param {string} [structuredData.source] - Źródło
 * @param {boolean} [confirmed=true] - Czy zatwierdzić zapis
 * @returns {Promise<Object>} Status operacji zapisu
 * 
 * @example
 * const result = await confirmKnowledgeWrite(sessionId, {
 *   title: "Nowy kolor Model Y",
 *   content: "Midnight Silver Metallic dostępny dla Long Range i Performance",
 *   knowledge_type: "product",
 *   archetype: null,
 *   tags: ["model-y", "kolory", "opcje"],
 *   source: "Expert Product Team"
 * }, true);
 * 
 * console.log("Zapisano:", result.response);
 */
export const confirmKnowledgeWrite = async (sessionId, structuredData, confirmed = true) => {
  try {
    // Walidacja parametrów
    if (!sessionId) {
      throw new Error('Session ID is required');
    }

    if (confirmed && (!structuredData || !structuredData.title || !structuredData.content)) {
      throw new Error('Title and content are required when confirming');
    }

    // Wyślij żądanie potwierdzenia
    const response = await apiClient.post('/dojo/confirm', structuredData, {
      params: {
        session_id: sessionId,
        confirmed: confirmed
      }
    });

    console.log(`✅ AI Dojo: Knowledge ${confirmed ? 'zapisana' : 'anulowana'}`, {
      sessionId,
      responseType: response.response_type
    });

    return response;

  } catch (error) {
    console.error('❌ AI Dojo Confirm Error:', error);
    
    const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
    
    throw {
      code: 'DOJO_CONFIRM_ERROR', 
      message: `Błąd podczas ${confirmed ? 'zapisu' : 'anulowania'}: ${errorMessage}`,
      statusCode: error.response?.status || 500,
      originalError: error
    };
  }
};

/**
 * SESSION MANAGEMENT - Zarządzanie sesjami treningowymi
 */

/**
 * Pobierz podsumowanie sesji treningowej
 * 
 * @param {string} sessionId - ID sesji
 * @returns {Promise<Object>} Podsumowanie sesji
 * 
 * @example
 * const summary = await getSessionSummary('dojo_abc12345_1629123456');
 * console.log(`Sesja: ${summary.duration_minutes} min, ${summary.knowledge_items_added} dodanych`);
 */
export const getSessionSummary = async (sessionId) => {
  try {
    if (!sessionId) {
      throw new Error('Session ID is required');
    }

    const response = await apiClient.get(`/dojo/session/${sessionId}`);
    
    console.log('✅ AI Dojo: Session summary retrieved', {
      sessionId,
      messages: response.total_messages,
      knowledgeItems: response.knowledge_items_added
    });

    return response;

  } catch (error) {
    console.error('❌ AI Dojo Session Error:', error);
    
    if (error.response?.status === 404) {
      throw {
        code: 'SESSION_NOT_FOUND',
        message: `Sesja ${sessionId} nie została znaleziona`,
        statusCode: 404,
        originalError: error
      };
    }
    
    const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
    
    throw {
      code: 'SESSION_ERROR',
      message: `Błąd podczas pobierania sesji: ${errorMessage}`,
      statusCode: error.response?.status || 500,
      originalError: error
    };
  }
};

/**
 * ANALYTICS - Statystyki i analityka
 */

/**
 * Pobierz analitykę systemu AI Dojo
 * 
 * @returns {Promise<Object>} Statystyki globalne
 * 
 * @example
 * const analytics = await getDojoAnalytics();
 * console.log(`Aktywne sesje: ${analytics.active_sessions}`);
 */
export const getDojoAnalytics = async () => {
  try {
    const response = await apiClient.get('/dojo/analytics');
    
    console.log('✅ AI Dojo: Analytics retrieved', {
      activeSessions: response.active_sessions,
      totalSessions: response.total_sessions
    });

    return response;

  } catch (error) {
    console.error('❌ AI Dojo Analytics Error:', error);
    
    const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
    
    throw {
      code: 'ANALYTICS_ERROR',
      message: `Błąd podczas pobierania statystyk: ${errorMessage}`,
      statusCode: error.response?.status || 500,
      originalError: error
    };
  }
};

/**
 * Sprawdź status systemu AI Dojo
 * 
 * @returns {Promise<Object>} Status health check
 */
export const getDojoHealth = async () => {
  try {
    const response = await apiClient.get('/dojo/health');
    
    return response;

  } catch (error) {
    console.error('❌ AI Dojo Health Error:', error);
    
    // Dla health check zawsze zwracamy dane, nawet przy błędzie
    return {
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
};

/**
 * UTILITY FUNCTIONS - Funkcje pomocnicze
 */

/**
 * Waliduj dane wiadomości przed wysłaniem
 * 
 * @param {Object} messageData - Dane do walidacji
 * @returns {Object} { isValid: boolean, errors: Array }
 */
export const validateDojoMessage = (messageData) => {
  const errors = [];

  if (!messageData) {
    errors.push('Message data is required');
    return { isValid: false, errors };
  }

  if (!messageData.message || typeof messageData.message !== 'string') {
    errors.push('Message text is required and must be a string');
  } else {
    if (messageData.message.trim().length === 0) {
      errors.push('Message cannot be empty');
    }
    if (messageData.message.length > 5000) {
      errors.push('Message too long (max 5000 characters)');
    }
  }

  if (messageData.training_mode && !['knowledge_update', 'error_correction', 'general_chat'].includes(messageData.training_mode)) {
    errors.push('Invalid training mode');
  }

  if (messageData.conversation_history && !Array.isArray(messageData.conversation_history)) {
    errors.push('Conversation history must be an array');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Waliduj strukturalne dane przed zapisem
 * 
 * @param {Object} structuredData - Dane do walidacji
 * @returns {Object} { isValid: boolean, errors: Array }
 */
export const validateStructuredData = (structuredData) => {
  const errors = [];
  const requiredFields = ['title', 'content', 'knowledge_type'];

  if (!structuredData) {
    errors.push('Structured data is required');
    return { isValid: false, errors };
  }

  requiredFields.forEach(field => {
    if (!structuredData[field] || structuredData[field].trim().length === 0) {
      errors.push(`${field} is required and cannot be empty`);
    }
  });

  const validKnowledgeTypes = [
    'general', 'objection', 'closing', 'product', 
    'pricing', 'competition', 'demo', 'follow_up', 'technical'
  ];

  if (structuredData.knowledge_type && !validKnowledgeTypes.includes(structuredData.knowledge_type)) {
    errors.push('Invalid knowledge type');
  }

  if (structuredData.tags && !Array.isArray(structuredData.tags)) {
    errors.push('Tags must be an array');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Formatuj dane do wyświetlenia w UI
 * 
 * @param {Object} dojoResponse - Odpowiedź z API
 * @returns {Object} Sformatowane dane
 */
export const formatDojoResponse = (dojoResponse) => {
  if (!dojoResponse) return null;

  return {
    ...dojoResponse,
    displayResponseType: getDisplayResponseType(dojoResponse.response_type),
    isConfirmationRequired: dojoResponse.response_type === 'confirmation',
    isErrorResponse: dojoResponse.response_type === 'error',
    formattedProcessingTime: dojoResponse.processing_time_ms ? 
      `${(dojoResponse.processing_time_ms / 1000).toFixed(1)}s` : 'N/A',
    confidenceLabel: getConfidenceLabel(dojoResponse.confidence_level)
  };
};

/**
 * Pobierz przyjazną nazwę typu odpowiedzi
 */
const getDisplayResponseType = (responseType) => {
  const types = {
    question: 'Pytanie doprecyzowujące',
    confirmation: 'Potwierdzenie zapisu',
    status: 'Status operacji', 
    error: 'Błąd'
  };
  
  return types[responseType] || responseType;
};

/**
 * Pobierz etykietę poziomu pewności
 */
const getConfidenceLabel = (confidenceLevel) => {
  if (!confidenceLevel) return 'Nieznany';
  
  if (confidenceLevel >= 85) return 'Bardzo wysoki';
  if (confidenceLevel >= 70) return 'Wysoki'; 
  if (confidenceLevel >= 50) return 'Średni';
  if (confidenceLevel >= 30) return 'Niski';
  return 'Bardzo niski';
};

/**
 * Wygeneruj unikalny ID sesji treningowej (fallback)
 * 
 * @returns {string} Unikalny ID sesji
 */
export const generateSessionId = () => {
  const timestamp = Math.floor(Date.now() / 1000);
  const random = Math.random().toString(36).substring(2, 8);
  return `dojo_${random}_${timestamp}`;
};

/**
 * CONSTANTS - Stałe dla AI Dojo
 */

export const TRAINING_MODES = {
  KNOWLEDGE_UPDATE: 'knowledge_update',
  ERROR_CORRECTION: 'error_correction', 
  GENERAL_CHAT: 'general_chat'
};

export const RESPONSE_TYPES = {
  QUESTION: 'question',
  CONFIRMATION: 'confirmation',
  STATUS: 'status',
  ERROR: 'error'
};

export const KNOWLEDGE_TYPES = [
  'general', 'objection', 'closing', 'product',
  'pricing', 'competition', 'demo', 'follow_up', 'technical'
];

// Default export dla łatwego importowania
export default {
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
};