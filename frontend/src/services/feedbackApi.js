import apiClient from './api';

/**
 * Wysyła ocenę dla konkretnej interakcji AI.
 * @param {string} interactionId ID interakcji, która jest oceniana.
 * @param {number} rating Ocena: 1 dla pozytywnej, -1 dla negatywnej.
 * @returns {Promise<object>} Obiekt utworzonego feedbacku.
 */
export const submitInteractionFeedback = async (interactionId, rating) => {
  if (!interactionId) {
    throw new Error('ID interakcji jest wymagane');
  }
  
  if (rating !== 1 && rating !== -1) {
    throw new Error('Ocena musi być równa 1 (pozytywna) lub -1 (negatywna)');
  }

  const payload = {
    rating: rating,
    feedback_type: 'suggestion_rating'
  };

  try {
    const response = await apiClient.post(`/interactions/${interactionId}/feedback/`, payload);
    return response.data;
  } catch (error) {
    console.error('Błąd podczas wysyłania feedback:', error);
    throw error;
  }
};

/**
 * Helper function do walidacji feedback payload
 * @param {number} rating 
 * @returns {boolean}
 */
export const validateFeedbackRating = (rating) => {
  return rating === 1 || rating === -1;
};

/**
 * Formatuje feedback data do wyświetlenia w UI
 * @param {object} feedback 
 * @returns {object}
 */
export const formatFeedbackData = (feedback) => {
  if (!feedback) return null;
  
  return {
    ...feedback,
    isPositive: feedback.rating === 1,
    isNegative: feedback.rating === -1,
    displayRating: feedback.rating === 1 ? 'Pozytywna' : 'Negatywna',
    displayType: feedback.feedback_type === 'suggestion_rating' ? 'Ocena sugestii' : feedback.feedback_type
  };
};
