/**
 * API functions dla granularnego systemu feedback (Blueprint Feedback Loop)
 */
import apiClient from './api';

/**
 * Wysyła ocenę konkretnej sugestii AI
 * Zgodnie z Blueprint - granularny feedback dla każdej sugestii z unikalnym ID
 */
export const createFeedback = async (interactionId, feedbackData) => {
  const endpoint = `/interactions/${interactionId}/feedback/`;
  
  console.log(`📊 Wysyłanie feedback dla sugestii ${feedbackData.suggestion_id} (${feedbackData.suggestion_type}):`, {
    interaction_id: feedbackData.interaction_id,
    suggestion_id: feedbackData.suggestion_id,
    suggestion_type: feedbackData.suggestion_type,
    score: feedbackData.score
  });
  
  try {
    const response = await apiClient.post(endpoint, feedbackData);
    
    console.log(`✅ Feedback wysłany pomyślnie dla sugestii ${feedbackData.suggestion_id}`);
    return response.data;
    
  } catch (error) {
    console.error(`❌ Błąd przy wysyłaniu feedback dla sugestii ${feedbackData.suggestion_id}:`, error);
    throw error;
  }
};

/**
 * Formatuje dane feedback do wyświetlenia
 */
export const formatFeedbackData = (interaction) => {
  if (!interaction.feedback_data || !Array.isArray(interaction.feedback_data)) {
    return [];
  }
  
  return interaction.feedback_data.map(feedback => ({
    ...feedback,
    scoreLabel: feedback.score === 1 ? 'Pozytywna' : 'Negatywna',
    timestamp: new Date().toISOString() // Placeholder - w przyszłości z bazy
  }));
};

/**
 * Sprawdza czy sugestia została już oceniona
 */
export const isSuggestionRated = (interaction, suggestionId) => {
  if (!interaction.feedback_data || !Array.isArray(interaction.feedback_data)) {
    return null;
  }
  
  const feedback = interaction.feedback_data.find(f => f.suggestion_id === suggestionId);
  return feedback ? feedback.score : null;
};

/**
 * Pobiera statystyki feedback dla interakcji
 */
export const getFeedbackStats = (interaction) => {
  if (!interaction.feedback_data || !Array.isArray(interaction.feedback_data)) {
    return { total: 0, positive: 0, negative: 0 };
  }
  
  const total = interaction.feedback_data.length;
  const positive = interaction.feedback_data.filter(f => f.score === 1).length;
  const negative = interaction.feedback_data.filter(f => f.score === -1).length;
  
  return { total, positive, negative };
};