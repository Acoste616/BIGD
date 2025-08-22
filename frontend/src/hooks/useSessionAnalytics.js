/**
 * Custom React Hook do zarządzania analityką sesji
 * Zapewnia łatwą integrację z Analytics API w komponentach
 */
import { useState, useCallback, useEffect } from 'react';
import { getSessionAnalytics } from '../services';

/**
 * Hook do pobierania i zarządzania danymi analitycznymi sesji
 * @param {number} sessionId - ID sesji
 * @returns {Object} Stan i funkcje do zarządzania analityką
 */
export const useSessionAnalytics = (sessionId) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        if (!sessionId) return;
        setLoading(true);
        setError(null);
        try {
            const analyticsData = await getSessionAnalytics(sessionId);
            setData(analyticsData);
        } catch (err) {
            setError(err.message || 'Failed to fetch session analytics.');
        } finally {
            setLoading(false);
        }
    }, [sessionId]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return { data, loading, error, refresh: fetchData };
};
