/**
 * API Client dla modułu Analytics
 * Komunikacja z backend endpoints dla zaawansowanych wskaźników analitycznych
 */
import apiClient from './api';

/**
 * Pobiera wskaźniki analityczne dla konkretnej sesji
 * @param {number} sessionId - ID sesji
 * @returns {Promise<Object>} Dane analityczne (PRL, FDS, summary, dominant_traits)
 */
export const getSessionAnalytics = async (sessionId) => {
    if (!sessionId) {
        throw new Error("Session ID is required to fetch analytics.");
    }
    const response = await apiClient.get(`/sessions/${sessionId}/analytics`);
    return response.data;
};
