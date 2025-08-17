/**
 * Custom React Hook do zarządzania klientami
 * Zapewnia łatwą integrację z API w komponentach
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  getClients,
  getClientById,
  createClient,
  updateClient,
  deleteClient,
  searchClients,
  getClientStatistics,
  validateClientData,
  debounce
} from '../services';

/**
 * Hook do pobierania listy klientów z paginacją i filtrowaniem
 * @param {Object} initialFilters - Początkowe filtry
 * @returns {Object} Stan i funkcje do zarządzania listą klientów
 */
export const useClientsList = (initialFilters = {}) => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    size: 10,
    pages: 0
  });
  const [filters, setFilters] = useState({
    page: 1,
    size: 10,
    sort_by: 'created_at',
    sort_order: 'desc',
    ...initialFilters
  });

  // Funkcja do pobierania klientów
  const fetchClients = useCallback(async (customFilters = {}) => {
    setLoading(true);
    setError(null);

    try {
      const params = { ...filters, ...customFilters };
      const response = await getClients(params);
      
      setClients(response.items || []);
      setPagination({
        total: response.total,
        page: response.page,
        size: response.size,
        pages: response.pages
      });
    } catch (err) {
      setError(err.message || 'Nie udało się pobrać listy klientów');
      setClients([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Automatyczne pobieranie przy zmianie filtrów
  useEffect(() => {
    fetchClients();
  }, [fetchClients]);

  // Funkcje pomocnicze
  const changePage = (newPage) => {
    setFilters(prev => ({ ...prev, page: newPage }));
  };

  const changePageSize = (newSize) => {
    setFilters(prev => ({ ...prev, page: 1, size: newSize }));
  };

  const changeSort = (sortBy, sortOrder = null) => {
    setFilters(prev => ({
      ...prev,
      sort_by: sortBy,
      sort_order: sortOrder || (prev.sort_by === sortBy && prev.sort_order === 'asc' ? 'desc' : 'asc'),
      page: 1
    }));
  };

  const applyFilters = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: 1 }));
  };

  const resetFilters = () => {
    setFilters({
      page: 1,
      size: 10,
      sort_by: 'created_at',
      sort_order: 'desc',
      ...initialFilters
    });
  };

  const refresh = () => {
    fetchClients();
  };

  return {
    // Stan
    clients,
    loading,
    error,
    pagination,
    filters,
    
    // Funkcje
    changePage,
    changePageSize,
    changeSort,
    applyFilters,
    resetFilters,
    refresh,
    
    // Dodatkowe informacje
    hasClients: clients.length > 0,
    isEmpty: !loading && clients.length === 0,
    isFirstPage: pagination.page === 1,
    isLastPage: pagination.page === pagination.pages,
    totalPages: pagination.pages,
    currentPage: pagination.page
  };
};

/**
 * Hook do zarządzania pojedynczym klientem
 * @param {number|null} clientId - ID klienta do pobrania
 * @returns {Object} Stan i funkcje do zarządzania klientem
 */
export const useClient = (clientId) => {
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);

  // Pobieranie danych klienta
  const fetchClient = useCallback(async () => {
    if (!clientId) {
      setClient(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getClientById(clientId);
      setClient(data);
    } catch (err) {
      setError(err.message || 'Nie udało się pobrać danych klienta');
      setClient(null);
    } finally {
      setLoading(false);
    }
  }, [clientId]);

  // Pobieranie statystyk klienta
  const fetchStatistics = useCallback(async () => {
    if (!clientId) return;

    setStatsLoading(true);

    try {
      const stats = await getClientStatistics(clientId);
      setStatistics(stats);
    } catch (err) {
      console.error('Failed to fetch client statistics:', err);
      setStatistics(null);
    } finally {
      setStatsLoading(false);
    }
  }, [clientId]);

  // Aktualizacja klienta
  const updateClientData = async (updateData) => {
    if (!clientId) throw new Error('No client ID provided');

    setLoading(true);
    setError(null);

    try {
      const updated = await updateClient(clientId, updateData);
      setClient(updated);
      return updated;
    } catch (err) {
      setError(err.message || 'Nie udało się zaktualizować klienta');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Usunięcie klienta
  const removeClient = async () => {
    if (!clientId) throw new Error('No client ID provided');

    setLoading(true);
    setError(null);

    try {
      await deleteClient(clientId);
      setClient(null);
      return true;
    } catch (err) {
      setError(err.message || 'Nie udało się usunąć klienta');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Automatyczne pobieranie przy zmianie ID
  useEffect(() => {
    fetchClient();
  }, [fetchClient]);

  return {
    // Stan
    client,
    loading,
    error,
    statistics,
    statsLoading,
    
    // Funkcje
    refresh: fetchClient,
    fetchStatistics,
    updateClient: updateClientData,
    deleteClient: removeClient,
    
    // Pomocnicze
    exists: !!client,
    isReady: !loading && !error && !!client
  };
};

/**
 * Hook do tworzenia nowego klienta
 * @returns {Object} Stan i funkcje do tworzenia klienta
 */
export const useCreateClient = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});

  const validateAndCreate = async (clientData) => {
    setError(null);
    setValidationErrors({});

    // Walidacja lokalna
    const validation = validateClientData(clientData);
    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      return { success: false, errors: validation.errors };
    }

    setLoading(true);

    try {
      const newClient = await createClient(clientData);
      return { success: true, data: newClient };
    } catch (err) {
      const errorMessage = err.message || 'Nie udało się utworzyć klienta';
      setError(errorMessage);
      
      // Jeśli to błąd walidacji z serwera
      if (err.code === 'VALIDATION_ERROR') {
        // Tu możemy parsować szczegóły błędów walidacji z serwera
        return { success: false, errors: err.details || {} };
      }
      
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const clearErrors = () => {
    setError(null);
    setValidationErrors({});
  };

  return {
    createClient: validateAndCreate,
    loading,
    error,
    validationErrors,
    clearErrors
  };
};

/**
 * Hook do wyszukiwania klientów w czasie rzeczywistym
 * @param {number} debounceDelay - Opóźnienie debounce w ms
 * @returns {Object} Stan i funkcje wyszukiwania
 */
export const useClientSearch = (debounceDelay = 300) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Debounced search function
  const debouncedSearch = useMemo(
    () => debounce(async (query) => {
      if (!query || query.trim().length < 2) {
        setResults([]);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const searchResults = await searchClients(query);
        setResults(searchResults);
      } catch (err) {
        setError(err.message || 'Błąd podczas wyszukiwania');
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, debounceDelay),
    [debounceDelay]
  );

  // Efekt do wyszukiwania przy zmianie terminu
  useEffect(() => {
    debouncedSearch(searchTerm);
  }, [searchTerm, debouncedSearch]);

  const clearSearch = () => {
    setSearchTerm('');
    setResults([]);
    setError(null);
  };

  return {
    searchTerm,
    setSearchTerm,
    results,
    loading,
    error,
    clearSearch,
    hasResults: results.length > 0,
    isSearching: loading
  };
};

/**
 * Hook do zarządzania wyborem wielu klientów (np. do operacji grupowych)
 * @param {Array} initialSelection - Początkowa lista wybranych ID
 * @returns {Object} Stan i funkcje selekcji
 */
export const useClientSelection = (initialSelection = []) => {
  const [selectedIds, setSelectedIds] = useState(new Set(initialSelection));

  const toggleSelection = (clientId) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(clientId)) {
        newSet.delete(clientId);
      } else {
        newSet.add(clientId);
      }
      return newSet;
    });
  };

  const selectAll = (clientIds) => {
    setSelectedIds(new Set(clientIds));
  };

  const clearSelection = () => {
    setSelectedIds(new Set());
  };

  const isSelected = (clientId) => selectedIds.has(clientId);

  return {
    selectedIds: Array.from(selectedIds),
    selectedCount: selectedIds.size,
    toggleSelection,
    selectAll,
    clearSelection,
    isSelected,
    hasSelection: selectedIds.size > 0
  };
};
