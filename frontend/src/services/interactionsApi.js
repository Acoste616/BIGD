/**
 * API Client dla modułu Interakcji
 * Komunikacja z backend endpoints dla zarządzania interakcjami w sesjach
 */
import apiClient from './api';

/**
 * Pobiera wszystkie interakcje dla konkretnej sesji
 * @param {number} sessionId - ID sesji
 * @param {number} page - Numer strony (domyślnie 1)
 * @param {number} size - Rozmiar strony (domyślnie 10)
 * @returns {Promise<Object>} Lista interakcji z paginacją
 */
export const getSessionInteractions = async (sessionId, page = 1, size = 10) => {
  if (!sessionId) {
    throw new Error('Session ID is required');
  }
  
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: size.toString()
  });
  
  return await apiClient.get(`/sessions/${sessionId}/interactions/?${params}`);
};

/**
 * Pobiera szczegóły pojedynczej interakcji
 * @param {number} interactionId - ID interakcji
 * @returns {Promise<Object>} Szczegóły interakcji
 */
export const getInteractionById = async (interactionId) => {
  if (!interactionId) {
    throw new Error('Interaction ID is required');
  }
  return await apiClient.get(`/interactions/${interactionId}`);
};

/**
 * Tworzy nową interakcję w sesji
 * @param {number} sessionId - ID sesji
 * @param {Object} interactionData - Dane interakcji
 * @returns {Promise<Object>} Utworzona interakcja z analizą AI
 */
export const createInteraction = async (sessionId, interactionData) => {
  if (!sessionId) {
    throw new Error('Session ID is required');
  }
  
  if (!interactionData.user_input) {
    throw new Error('User input is required');
  }
  
  const requestData = {
    user_input: interactionData.user_input.trim(),
    interaction_type: interactionData.interaction_type || 'question',
    ...interactionData
  };
  
  return await apiClient.post(`/sessions/${sessionId}/interactions/`, requestData);
};

/**
 * Aktualizuje interakcję
 * @param {number} interactionId - ID interakcji
 * @param {Object} updateData - Dane do aktualizacji
 * @returns {Promise<Object>} Zaktualizowana interakcja
 */
export const updateInteraction = async (interactionId, updateData) => {
  if (!interactionId) {
    throw new Error('Interaction ID is required');
  }
  return await apiClient.put(`/interactions/${interactionId}`, updateData);
};

/**
 * Usuwa interakcję
 * @param {number} interactionId - ID interakcji
 * @returns {Promise<void>}
 */
export const deleteInteraction = async (interactionId) => {
  if (!interactionId) {
    throw new Error('Interaction ID is required');
  }
  return await apiClient.delete(`/interactions/${interactionId}`);
};

/**
 * Pobiera statystyki interakcji
 * @param {number} interactionId - ID interakcji
 * @returns {Promise<Object>} Statystyki interakcji
 */
export const getInteractionStatistics = async (interactionId) => {
  if (!interactionId) {
    throw new Error('Interaction ID is required');
  }
  return await apiClient.get(`/interactions/${interactionId}/statistics`);
};

/**
 * Pobiera analizę konwersacji dla sesji
 * @param {number} sessionId - ID sesji
 * @returns {Promise<Object>} Analiza przebiegu konwersacji
 */
export const getConversationAnalysis = async (sessionId) => {
  if (!sessionId) {
    throw new Error('Session ID is required');
  }
  return await apiClient.get(`/sessions/${sessionId}/interactions/analysis`);
};

/**
 * Pobiera ostatnie interakcje (wszystkich sesji)
 * @param {number} limit - Maksymalna liczba interakcji (domyślnie 10)
 * @returns {Promise<Array>} Lista ostatnich interakcji
 */
export const getRecentInteractions = async (limit = 10) => {
  const params = new URLSearchParams({
    limit: limit.toString()
  });
  
  return await apiClient.get(`/interactions/recent?${params}`);
};

/**
 * Formatuje dane interakcji do wyświetlenia
 * @param {Object} interaction - Obiekt interakcji z API
 * @returns {Object} Sformatowane dane interakcji
 */
export const formatInteractionData = (interaction) => {
  return {
    ...interaction,
    displayTimestamp: new Date(interaction.timestamp).toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }),
    formattedUserInput: interaction.user_input?.trim(),
    hasAIResponse: !!interaction.ai_response_json,
    aiConfidence: interaction.confidence_score || 0,
    displayType: getInteractionTypeLabel(interaction.interaction_type),
    quickResponse: interaction.ai_response_json?.quick_response,
    isAIAvailable: !interaction.ai_response_json?.is_fallback
  };
};

/**
 * Pomocnicza funkcja do etykietowania typów interakcji
 * @param {string} type - Typ interakcji
 * @returns {string} Etykieta typu interakcji
 */
const getInteractionTypeLabel = (type) => {
  const typeLabels = {
    'question': 'Pytanie',
    'objection': 'Zastrzeżenie',
    'interest': 'Zainteresowanie',
    'price_inquiry': 'Pytanie o cenę',
    'technical': 'Pytanie techniczne',
    'demo_request': 'Prośba o demo',
    'follow_up': 'Kontakt kontrolny',
    'closing': 'Finalizacja',
    'other': 'Inne'
  };
  
  return typeLabels[type] || 'Nieznany';
};

/**
 * Waliduje dane interakcji przed wysłaniem
 * @param {Object} interactionData - Dane interakcji do walidacji
 * @returns {Object} Wynik walidacji z błędami
 */
export const validateInteractionData = (interactionData) => {
  const errors = {};
  
  // Walidacja user_input (wymagane)
  if (!interactionData.user_input || !interactionData.user_input.trim()) {
    errors.user_input = 'Opis sytuacji jest wymagany';
  } else if (interactionData.user_input.trim().length < 10) {
    errors.user_input = 'Opis sytuacji musi mieć co najmniej 10 znaków';
  } else if (interactionData.user_input.trim().length > 2000) {
    errors.user_input = 'Opis sytuacji nie może przekraczać 2000 znaków';
  }
  
  // Walidacja typu interakcji
  const validTypes = ['question', 'objection', 'interest', 'price_inquiry', 'technical', 'demo_request', 'follow_up', 'closing', 'other'];
  if (interactionData.interaction_type && !validTypes.includes(interactionData.interaction_type)) {
    errors.interaction_type = 'Nieprawidłowy typ interakcji';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Pobiera dostępne typy interakcji
 * @returns {Array} Lista dostępnych typów interakcji
 */
export const getAvailableInteractionTypes = () => {
  return [
    { value: 'question', label: 'Pytanie', icon: 'help' },
    { value: 'objection', label: 'Zastrzeżenie', icon: 'block' },
    { value: 'interest', label: 'Zainteresowanie', icon: 'favorite' },
    { value: 'price_inquiry', label: 'Pytanie o cenę', icon: 'attach_money' },
    { value: 'technical', label: 'Pytanie techniczne', icon: 'settings' },
    { value: 'demo_request', label: 'Prośba o demo', icon: 'play_circle' },
    { value: 'follow_up', label: 'Kontakt kontrolny', icon: 'phone' },
    { value: 'closing', label: 'Finalizacja', icon: 'handshake' },
    { value: 'other', label: 'Inne', icon: 'more_horiz' }
  ];
};
