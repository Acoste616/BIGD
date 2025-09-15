/**
 * Custom React Hook do zarządzania sesjami i analityką
 * Zapewnia łatwą integrację z Sessions API w komponentach
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../services/api';

/**
 * Hook do pobierania listy wszystkich sesji
 * @param {Object} options - Opcje hooka
 * @returns {Object} Stan i funkcje do zarządzania sesjami
 */
export const useSessions = (options = {}) => {
  const {
    autoFetch = true,
    pageSize = 10,
    onError = null
  } = options;

  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    size: pageSize,
    pages: 0
  });

  // Funkcja do pobierania wszystkich sesji
  const fetchSessions = useCallback(async (page = 1, size = pageSize) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        skip: ((page - 1) * size).toString(),
        limit: size.toString()
      });

      const response = await apiClient.get(`/sessions/?${params}`);
      
      // Format response based on backend structure
      const formattedSessions = (response || []).map(session => ({
        ...session,
        displayStartTime: new Date(session.start_timestamp).toLocaleDateString('pl-PL', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }),
        displayEndTime: session.end_timestamp 
          ? new Date(session.end_timestamp).toLocaleDateString('pl-PL', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })
          : null,
        isActive: session.status === 'active',
        statusLabel: session.status === 'active' ? 'Aktywna' : 'Zakończona',
      }));
      
      setSessions(formattedSessions);
      // For now, we'll assume all sessions are returned (no pagination from backend)
      setPagination({
        total: formattedSessions.length,
        page: page,
        size: size,
        pages: 1
      });
    } catch (err) {
      const errorMessage = err.message || 'Nie udało się pobrać sesji';
      setError(errorMessage);
      setSessions([]);
      
      if (onError) {
        onError(err);
      }
    } finally {
      setLoading(false);
    }
  }, [pageSize, onError]);

  // Automatyczne pobieranie przy montażu
  useEffect(() => {
    if (autoFetch) {
      fetchSessions();
    }
  }, [fetchSessions, autoFetch]);

  // Funkcja do odświeżania listy
  const refresh = useCallback(() => {
    fetchSessions(pagination.page, pagination.size);
  }, [fetchSessions, pagination.page, pagination.size]);

  // Funkcja do zmiany strony
  const changePage = useCallback((newPage) => {
    fetchSessions(newPage, pagination.size);
  }, [fetchSessions, pagination.size]);

  // Funkcja do zmiany rozmiaru strony
  const changePageSize = useCallback((newSize) => {
    fetchSessions(1, newSize);
  }, [fetchSessions]);

  return {
    sessions,
    loading,
    error,
    pagination,
    fetchSessions,
    refresh,
    changePage,
    changePageSize,
    // Dodatkowe dane
    hasActiveSessions: sessions.some(s => s.isActive),
    totalSessions: sessions.length,
    activeSessions: sessions.filter(s => s.isActive),
    completedSessions: sessions.filter(s => !s.isActive)
  };
};

/**
 * Hook do finalizacji sesji
 * @param {Object} options - Opcje hooka
 * @returns {Object} Stan i funkcje do finalizacji sesji
 */
export const useConcludeSession = (options = {}) => {
  const { onSuccess = null, onError = null } = options;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Funkcja do finalizacji sesji
  const concludeSession = async (sessionId, conclusionData) => {
    if (!sessionId) {
      throw new Error('Session ID is required');
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await apiClient.post(`/sessions/${sessionId}/conclude`, conclusionData);
      
      setSuccess(true);
      
      if (onSuccess) {
        onSuccess(response);
      }
      
      // Auto-clear success after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
      
      return { success: true, data: response };
    } catch (err) {
      const errorMessage = err.message || 'Nie udało się zakończyć sesji';
      setError(errorMessage);
      
      if (onError) {
        onError(err);
      }
      
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Funkcja do resetowania stanów
  const resetState = () => {
    setError(null);
    setSuccess(false);
  };

  return {
    concludeSession,
    loading,
    error,
    success,
    resetState
  };
};