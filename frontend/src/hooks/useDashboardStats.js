/**
 * Custom React Hook do pobierania statystyk dashboardu v4.2.0
 * Zapewnia łatwą integrację z API w komponencie Dashboard
 * Zgodność z nową architekturą backendu v4.2.0
 */
import { useState, useEffect, useCallback } from 'react';
import { getRecentSessions } from '../services/sessionsApi';
import { getClientSessions } from '../services/sessionsApi';

/**
 * Hook do pobierania statystyk dashboardu v4.2.0
 * @returns {Object} Stan i funkcje do zarządzania statystykami
 */
export const useDashboardStats = () => {
  const [stats, setStats] = useState({
    totalClients: 0,
    activeSessions: 0,
    completedAnalyses: 0,
    recentSessions: [],
    loading: true,
    error: null
  });

  const fetchStats = useCallback(async () => {
    setStats(prev => ({ ...prev, loading: true, error: null }));

    try {
      // Pobierz ostatnie sesje (wszystkich klientów) v4.2.0
      const recentSessionsResponse = await getRecentSessions(20);
      const recentSessions = recentSessionsResponse || [];

      // Oblicz statystyki na podstawie sesji v4.2.0
      const activeSessions = recentSessions.filter(session => !session.end_time).length;
      const completedAnalyses = recentSessions.filter(session => session.end_time && session.outcome).length;

      // Pobierz liczbę klientów (zakładamy, że każda sesja ma client_id)
      const uniqueClientIds = new Set(recentSessions.map(session => session.client_id));
      const totalClients = uniqueClientIds.size;

      setStats({
        totalClients,
        activeSessions,
        completedAnalyses,
        recentSessions,
        loading: false,
        error: null
      });

    } catch (error) {
      console.error('Błąd podczas pobierania statystyk dashboardu v4.2.0:', error);
      setStats(prev => ({
        ...prev,
        loading: false,
        error: error.message || 'Nie udało się pobrać statystyk v4.2.0'
      }));
    }
  }, []);

  // Automatyczne pobieranie przy montowaniu komponentu
  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // Funkcja do odświeżania statystyk
  const refreshStats = useCallback(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    ...stats,
    refreshStats
  };
};
