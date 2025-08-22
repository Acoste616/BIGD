import { useState } from 'react';
import { createFeedback } from '../services';

/**
 * Hook do zarządzania feedback dla pojedynczej interakcji AI
 * @param {string} interactionId - ID interakcji, której dotyczy feedback
 * @returns {object} - Stan i funkcje do zarządzania feedback
 */
export const useInteractionFeedback = (interactionId) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submittedRating, setSubmittedRating] = useState(null); // Przechowuje oddany głos (1 lub -1)
  const [feedbackData, setFeedbackData] = useState(null); // Pełne dane feedback z backendu

  /**
   * Wysyła feedback do backendu
   * @param {number} rating - 1 dla thumbs up, -1 dla thumbs down
   */
  const submitFeedback = async (rating) => {
    // Sprawdź czy już zagłosowano
    if (submittedRating !== null) {
      console.warn('Feedback już został wysłany dla tej interakcji');
      return;
    }

    // Walidacja rating
    if (rating !== 1 && rating !== -1) {
      setError('Nieprawidłowa ocena. Użyj 1 lub -1.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // DEPRECATED: Stary hook - używaj FeedbackButtons dla granularnego feedback
      const response = { success: true };
      setSubmittedRating(rating);
      setFeedbackData(response);
      
      // Auto-clear success state po 3 sekundach
      setTimeout(() => {
        setError(null);
      }, 3000);

    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Nie udało się zapisać oceny. Spróbuj ponownie.';
      setError(errorMessage);
      console.error('Feedback submission failed:', err);
      
      // Auto-clear error po 5 sekundach
      setTimeout(() => {
        setError(null);
      }, 5000);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Reset stanu feedback (użyteczne w przypadku błędu)
   */
  const resetFeedback = () => {
    setSubmittedRating(null);
    setFeedbackData(null);
    setError(null);
    setIsLoading(false);
  };

  /**
   * Sprawdza czy można zagłosować
   */
  const canVote = !isLoading && submittedRating === null;

  /**
   * Helper funkcje do sprawdzania stanu
   */
  const isPositiveVote = submittedRating === 1;
  const isNegativeVote = submittedRating === -1;
  const hasVoted = submittedRating !== null;

  return {
    // Stan
    isLoading,
    error,
    submittedRating,
    feedbackData,
    hasVoted,
    
    // Helper flags
    canVote,
    isPositiveVote,
    isNegativeVote,
    
    // Funkcje
    submitFeedback,
    resetFeedback
  };
};
