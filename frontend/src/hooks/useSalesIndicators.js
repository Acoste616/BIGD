import { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Custom hook for fetching and managing sales indicators data
 * 
 * @param {string|number} sessionId - The ID of the session to fetch indicators for
 * @param {Object} options - Configuration options
 * @param {boolean} options.autoFetch - Whether to automatically fetch data on mount and when sessionId changes
 * @returns {Object} indicatorsData, loading, error, and refetch function
 */
export const useSalesIndicators = (sessionId, options = {}) => {
  const { autoFetch = true } = options;
  const [indicatorsData, setIndicatorsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Fetch sales indicators data from the API
   */
  const fetchIndicators = useCallback(async () => {
    if (!sessionId) {
      setError('Session ID is required');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/indicators`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Session not found');
        }
        throw new Error(`Failed to fetch sales indicators: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      setIndicatorsData(data);
    } catch (err) {
      console.error('Error fetching sales indicators:', err);
      setError(err.message || 'Failed to fetch sales indicators');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  /**
   * Refetch function to manually trigger data fetching
   */
  const refetch = useCallback(() => {
    fetchIndicators();
  }, [fetchIndicators]);

  // Automatically fetch data when sessionId changes (if autoFetch is enabled)
  useEffect(() => {
    if (autoFetch && sessionId) {
      fetchIndicators();
    } else if (!sessionId) {
      // Clear data when sessionId is null/undefined
      setIndicatorsData(null);
      setError(null);
    }
  }, [sessionId, autoFetch, fetchIndicators]);

  return {
    indicatorsData,
    loading,
    error,
    refetch
  };
};

export default useSalesIndicators;