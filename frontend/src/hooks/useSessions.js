/**
 * Custom React Hook do zarządzania sesjami
 * Zapewnia łatwą integrację z Sessions API w komponentach
 */
import { useState, useEffect, useCallback } from 'react';
import {
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
  validateSessionData
} from '../services';

/**
 * Hook do pobierania listy sesji dla konkretnego klienta
 * @param {number} clientId - ID klienta
 * @param {Object} options - Opcje hooka
 * @returns {Object} Stan i funkcje do zarządzania sesjami klienta
 */
export const useClientSessions = (clientId, options = {}) => {
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

  // Funkcja do pobierania sesji klienta
  const fetchSessions = useCallback(async (page = 1) => {
    if (!clientId) {
      setSessions([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await getClientSessions(clientId, page, pageSize);
      
      // Format response based on backend structure
      const formattedSessions = (response.items || response.data || []).map(formatSessionData);
      
      setSessions(formattedSessions);
      setPagination({
        total: response.total || 0,
        page: response.page || page,
        size: response.size || pageSize,
        pages: response.pages || Math.ceil((response.total || 0) / pageSize)
      });
    } catch (err) {
      const errorMessage = err.message || 'Nie udało się pobrać sesji klienta';
      setError(errorMessage);
      setSessions([]);
      
      if (onError) {
        onError(err);
      }
    } finally {
      setLoading(false);
    }
  }, [clientId, pageSize, onError]);

  // Automatyczne pobieranie przy zmianach clientId
  useEffect(() => {
    if (autoFetch && clientId) {
      fetchSessions();
    }
  }, [fetchSessions, autoFetch, clientId]);

  // Funkcja do odświeżania listy
  const refresh = useCallback(() => {
    fetchSessions(pagination.page);
  }, [fetchSessions, pagination.page]);

  // Funkcja do zmiany strony
  const changePage = useCallback((newPage) => {
    fetchSessions(newPage);
  }, [fetchSessions]);

  return {
    sessions,
    loading,
    error,
    pagination,
    fetchSessions,
    refresh,
    changePage,
    // Dodatkowe dane
    hasActiveSessions: sessions.some(s => s.isActive),
    totalSessions: sessions.length,
    activeSessions: sessions.filter(s => s.isActive),
    completedSessions: sessions.filter(s => !s.isActive)
  };
};

/**
 * Hook do pobierania szczegółów pojedynczej sesji
 * @param {number} sessionId - ID sesji
 * @param {Object} options - Opcje hooka
 * @returns {Object} Stan i funkcje do zarządzania sesją
 */
export const useSession = (sessionId, options = {}) => {
  const {
    includeInteractions = false,
    autoFetch = true,
    onError = null
  } = options;

  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [interactions, setInteractions] = useState([]);

  // Pobieranie danych sesji
  const fetchSession = useCallback(async () => {
    if (!sessionId) {
      setSession(null);
      setInteractions([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getSessionById(sessionId, includeInteractions);
      const formattedSession = formatSessionData(data);
      setSession(formattedSession);
      
      // Jeśli response zawiera interakcje, zapisz je
      if (includeInteractions && data.interactions) {
        const { formatInteractionData } = await import('../services');
        const formattedInteractions = data.interactions.map(formatInteractionData);
        setInteractions(formattedInteractions);
      }
    } catch (err) {
      const errorMessage = err.message || 'Nie udało się pobrać danych sesji';
      setError(errorMessage);
      setSession(null);
      setInteractions([]);
      
      if (onError) {
        onError(err);
      }
    } finally {
      setLoading(false);
    }
  }, [sessionId, includeInteractions, onError]);

  // Pobieranie statystyk sesji
  const fetchStatistics = useCallback(async () => {
    if (!sessionId) return;

    setStatsLoading(true);

    try {
      const stats = await getSessionStatistics(sessionId);
      setStatistics(stats);
    } catch (err) {
      console.error('Failed to fetch session statistics:', err);
      setStatistics(null);
    } finally {
      setStatsLoading(false);
    }
  }, [sessionId]);

  // Aktualizacja sesji
  const updateSessionData = async (updateData) => {
    if (!sessionId) throw new Error('No session ID provided');

    setLoading(true);
    setError(null);

    try {
      const updated = await updateSession(sessionId, updateData);
      const formattedSession = formatSessionData(updated);
      setSession(formattedSession);
      return formattedSession;
    } catch (err) {
      setError(err.message || 'Nie udało się zaktualizować sesji');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Zakończenie sesji
  const endSessionData = async (endData = {}) => {
    if (!sessionId) throw new Error('No session ID provided');

    setLoading(true);
    setError(null);

    try {
      const ended = await endSession(sessionId, endData);
      const formattedSession = formatSessionData(ended);
      setSession(formattedSession);
      return formattedSession;
    } catch (err) {
      setError(err.message || 'Nie udało się zakończyć sesji');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Usunięcie sesji
  const deleteSessionData = async () => {
    if (!sessionId) throw new Error('No session ID provided');

    setLoading(true);
    setError(null);

    try {
      await deleteSession(sessionId);
      setSession(null);
      return true;
    } catch (err) {
      setError(err.message || 'Nie udało się usunąć sesji');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Automatyczne pobieranie przy zmianie sessionId
  useEffect(() => {
    if (autoFetch) {
      fetchSession();
    }
  }, [fetchSession, autoFetch]);

  return {
    session,
    loading,
    error,
    statistics,
    statsLoading,
    interactions,
    fetchSession,
    fetchStatistics,
    updateSessionData,
    endSessionData,
    deleteSessionData,
    // Helper properties
    isActive: session?.isActive || false,
    canEdit: session && session.isActive,
    hasInteractions: interactions.length > 0,
    interactionsCount: interactions.length
  };
};

/**
 * Hook do tworzenia nowej sesji
 * @param {Object} options - Opcje hooka
 * @returns {Object} Stan i funkcje do tworzenia sesji
 */
export const useCreateSession = (options = {}) => {
  const { onSuccess = null, onError = null } = options;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});
  const [success, setSuccess] = useState(false);

  // Funkcja do tworzenia sesji
  const createNewSession = async (clientId, sessionData = {}) => {
    if (!clientId) {
      throw new Error('Client ID is required');
    }

    // Walidacja danych
    const validation = validateSessionData(sessionData);
    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      return { success: false, errors: validation.errors };
    }

    setLoading(true);
    setError(null);
    setValidationErrors({});
    setSuccess(false);

    try {
      const newSession = await createSession(clientId, sessionData);
      const formattedSession = formatSessionData(newSession);
      
      setSuccess(true);
      
      if (onSuccess) {
        onSuccess(formattedSession);
      }
      
      // Auto-clear success after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
      
      return { success: true, data: formattedSession };
    } catch (err) {
      const errorMessage = err.message || 'Nie udało się utworzyć sesji';
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
    setValidationErrors({});
    setSuccess(false);
  };

  return {
    createNewSession,
    loading,
    error,
    validationErrors,
    success,
    resetState
  };
};

/**
 * Hook do pobierania ostatnich sesji (wszystkich klientów)
 * @param {number} limit - Maksymalna liczba sesji
 * @returns {Object} Stan i funkcje do zarządzania ostatnimi sesjami
 */
export const useRecentSessions = (limit = 10) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecentSessions = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getRecentSessions(limit);
      const formattedSessions = (data || []).map(formatSessionData);
      setSessions(formattedSessions);
    } catch (err) {
      setError(err.message || 'Nie udało się pobrać ostatnich sesji');
      setSessions([]);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchRecentSessions();
  }, [fetchRecentSessions]);

  return {
    sessions,
    loading,
    error,
    fetchRecentSessions,
    refresh: fetchRecentSessions
  };
};

/**
 * Hook do pobierania metryk zaangażowania klienta
 * @param {number} clientId - ID klienta
 * @returns {Object} Stan i funkcje do zarządzania metrykami
 */
export const useClientEngagement = (clientId) => {
  const [engagement, setEngagement] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchEngagement = useCallback(async () => {
    if (!clientId) {
      setEngagement(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getClientEngagement(clientId);
      setEngagement(data);
    } catch (err) {
      setError(err.message || 'Nie udało się pobrać metryk zaangażowania');
      setEngagement(null);
    } finally {
      setLoading(false);
    }
  }, [clientId]);

  useEffect(() => {
    fetchEngagement();
  }, [fetchEngagement]);

  return {
    engagement,
    loading,
    error,
    fetchEngagement,
    refresh: fetchEngagement
  };
};
