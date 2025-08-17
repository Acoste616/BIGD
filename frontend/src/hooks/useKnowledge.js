/**
 * Custom React Hooks dla Knowledge Management
 * Zarządzanie stanem i operacjami na bazie wiedzy
 */
import { useState, useEffect, useCallback } from 'react';
import {
  getKnowledgeList,
  getKnowledgeById,
  createKnowledge,
  deleteKnowledge,
  searchKnowledge,
  getKnowledgeStats,
  bulkCreateKnowledge,
  getQdrantHealth,
  formatKnowledgeData,
  validateKnowledgeData,
  validateSearchData,
  formatSearchResults
} from '../services/knowledgeApi';

/**
 * Hook do zarządzania listą wskazówek z paginacją i filtrowaniem
 * @param {Object} options - Opcje hooka
 * @returns {Object} Stan i funkcje do zarządzania listą
 */
export const useKnowledgeList = (options = {}) => {
  const {
    initialPage = 1,
    initialSize = 10,
    autoFetch = true
  } = options;

  const [knowledge, setKnowledge] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(initialPage);
  const [size, setSize] = useState(initialSize);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(0);

  // Filtry
  const [filters, setFilters] = useState({
    knowledge_type: null,
    archetype: null,
    search: null
  });

  // Funkcja pobierania listy
  const fetchKnowledge = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);

    try {
      const requestParams = {
        page: params.page || page,
        size: params.size || size,
        ...filters,
        ...params
      };

      const response = await getKnowledgeList(requestParams);
      
      // Formatuj dane
      const formattedItems = response.items.map(formatKnowledgeData);
      
      setKnowledge(formattedItems);
      setTotal(response.total);
      setPages(response.pages);
      
      // Aktualizuj stan paginacji jeśli przyszły nowe parametry
      if (params.page !== undefined) setPage(params.page);
      if (params.size !== undefined) setSize(params.size);

    } catch (err) {
      setError(err.message || 'Nie udało się pobrać listy wskazówek');
      setKnowledge([]);
    } finally {
      setLoading(false);
    }
  }, [page, size, filters]);

  // Funkcja zmiany strony
  const changePage = useCallback((newPage) => {
    setPage(newPage);
    fetchKnowledge({ page: newPage });
  }, [fetchKnowledge]);

  // Funkcja zmiany rozmiaru strony
  const changeSize = useCallback((newSize) => {
    setSize(newSize);
    setPage(1); // Reset do pierwszej strony
    fetchKnowledge({ page: 1, size: newSize });
  }, [fetchKnowledge]);

  // Funkcja aktualizacji filtrów
  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPage(1); // Reset do pierwszej strony
    
    // Fetch z nowymi filtrami
    const requestParams = {
      page: 1,
      size,
      ...filters,
      ...newFilters
    };
    fetchKnowledge(requestParams);
  }, [fetchKnowledge, size, filters]);

  // Funkcja czyszczenia filtrów
  const clearFilters = useCallback(() => {
    setFilters({
      knowledge_type: null,
      archetype: null,
      search: null
    });
    setPage(1);
    fetchKnowledge({ page: 1, size, knowledge_type: null, archetype: null, search: null });
  }, [fetchKnowledge, size]);

  // Auto-fetch przy inicjalizacji
  useEffect(() => {
    if (autoFetch) {
      fetchKnowledge();
    }
  }, []); // Tylko przy mount

  return {
    // Stan
    knowledge,
    loading,
    error,
    page,
    size,
    total,
    pages,
    filters,
    
    // Funkcje
    fetchKnowledge,
    changePage,
    changeSize,
    updateFilters,
    clearFilters,
    
    // Computed properties
    hasItems: knowledge.length > 0,
    isEmpty: !loading && knowledge.length === 0,
    hasNextPage: page < pages,
    hasPrevPage: page > 1,
    isFiltered: Object.values(filters).some(v => v !== null && v !== ''),
    totalPages: pages,
    startIndex: (page - 1) * size + 1,
    endIndex: Math.min(page * size, total)
  };
};

/**
 * Hook do tworzenia nowej wskazówki
 * @returns {Object} Stan i funkcja do tworzenia
 */
export const useCreateKnowledge = () => {
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const createKnowledgeItem = useCallback(async (knowledgeData) => {
    // Walidacja lokalna
    const validation = validateKnowledgeData(knowledgeData);
    if (!validation.isValid) {
      setError(Object.values(validation.errors)[0]);
      return null;
    }

    setCreating(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await createKnowledge(knowledgeData);
      setSuccess(true);
      
      // Auto-clear success po 3 sekundach
      setTimeout(() => setSuccess(false), 3000);
      
      return response;
    } catch (err) {
      setError(err.message || 'Nie udało się dodać wskazówki');
      return null;
    } finally {
      setCreating(false);
    }
  }, []);

  const resetState = useCallback(() => {
    setError(null);
    setSuccess(false);
  }, []);

  return {
    creating,
    error,
    success,
    createKnowledgeItem,
    resetState
  };
};

/**
 * Hook do usuwania wskazówki
 * @returns {Object} Stan i funkcja do usuwania
 */
export const useDeleteKnowledge = () => {
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const deleteKnowledgeItem = useCallback(async (knowledgeId) => {
    if (!knowledgeId) {
      setError('ID wskazówki jest wymagane');
      return false;
    }

    setDeleting(true);
    setError(null);
    setSuccess(false);

    try {
      await deleteKnowledge(knowledgeId);
      setSuccess(true);
      
      // Auto-clear success po 2 sekundach
      setTimeout(() => setSuccess(false), 2000);
      
      return true;
    } catch (err) {
      setError(err.message || 'Nie udało się usunąć wskazówki');
      return false;
    } finally {
      setDeleting(false);
    }
  }, []);

  const resetState = useCallback(() => {
    setError(null);
    setSuccess(false);
  }, []);

  return {
    deleting,
    error,
    success,
    deleteKnowledgeItem,
    resetState
  };
};

/**
 * Hook do wyszukiwania wektorowego
 * @returns {Object} Stan i funkcja do wyszukiwania
 */
export const useKnowledgeSearch = () => {
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState([]);
  const [lastQuery, setLastQuery] = useState('');

  const searchKnowledgeItems = useCallback(async (searchData) => {
    // Walidacja lokalna
    const validation = validateSearchData(searchData);
    if (!validation.isValid) {
      setError(Object.values(validation.errors)[0]);
      return [];
    }

    setSearching(true);
    setError(null);
    setLastQuery(searchData.query);

    try {
      const response = await searchKnowledge(searchData);
      const formattedResults = formatSearchResults(response);
      setResults(formattedResults);
      return formattedResults;
    } catch (err) {
      setError(err.message || 'Nie udało się wykonać wyszukiwania');
      setResults([]);
      return [];
    } finally {
      setSearching(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setResults([]);
    setLastQuery('');
    setError(null);
  }, []);

  return {
    searching,
    error,
    results,
    lastQuery,
    searchKnowledgeItems,
    clearResults,
    hasResults: results.length > 0,
    isEmpty: !searching && results.length === 0 && lastQuery !== ''
  };
};

/**
 * Hook do pobierania statystyk bazy wiedzy
 * @param {boolean} autoFetch - Czy automatycznie pobrać przy inicjalizacji
 * @returns {Object} Stan i funkcja do pobierania statystyk
 */
export const useKnowledgeStats = (autoFetch = true) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getKnowledgeStats();
      setStats(response);
    } catch (err) {
      setError(err.message || 'Nie udało się pobrać statystyk');
      setStats(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-fetch przy inicjalizacji
  useEffect(() => {
    if (autoFetch) {
      fetchStats();
    }
  }, [autoFetch, fetchStats]);

  return {
    stats,
    loading,
    error,
    fetchStats,
    hasStats: !!stats,
    totalItems: stats?.total_items || 0
  };
};

/**
 * Hook do masowego dodawania wskazówek
 * @returns {Object} Stan i funkcja do bulk import
 */
export const useBulkCreateKnowledge = () => {
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const bulkImport = useCallback(async (knowledgeItems) => {
    if (!Array.isArray(knowledgeItems) || knowledgeItems.length === 0) {
      setError('Lista wskazówek jest wymagana');
      return null;
    }

    setImporting(true);
    setError(null);
    setResult(null);

    try {
      const response = await bulkCreateKnowledge(knowledgeItems);
      setResult(response);
      return response;
    } catch (err) {
      setError(err.message || 'Nie udało się wykonać importu');
      return null;
    } finally {
      setImporting(false);
    }
  }, []);

  const resetState = useCallback(() => {
    setError(null);
    setResult(null);
  }, []);

  return {
    importing,
    error,
    result,
    bulkImport,
    resetState,
    hasResult: !!result,
    successCount: result?.success_count || 0,
    errorCount: result?.error_count || 0
  };
};

/**
 * Hook do sprawdzania statusu Qdrant
 * @param {boolean} autoCheck - Czy automatycznie sprawdzić przy inicjalizacji
 * @returns {Object} Stan i funkcja do health check
 */
export const useQdrantHealth = (autoCheck = true) => {
  const [health, setHealth] = useState(null);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState(null);

  const checkHealth = useCallback(async () => {
    setChecking(true);
    setError(null);

    try {
      const response = await getQdrantHealth();
      setHealth(response);
    } catch (err) {
      setError(err.message || 'Nie udało się sprawdzić statusu Qdrant');
      setHealth(null);
    } finally {
      setChecking(false);
    }
  }, []);

  // Auto-check przy inicjalizacji
  useEffect(() => {
    if (autoCheck) {
      checkHealth();
    }
  }, [autoCheck, checkHealth]);

  return {
    health,
    checking,
    error,
    checkHealth,
    isHealthy: health?.status === 'healthy',
    isUnhealthy: health?.status === 'unhealthy',
    collectionExists: health?.collection_exists || false
  };
};

/**
 * Hook do pobierania pojedynczej wskazówki
 * @param {string} knowledgeId - ID wskazówki
 * @param {boolean} autoFetch - Czy automatycznie pobrać
 * @returns {Object} Stan i funkcja do pobierania
 */
export const useKnowledge = (knowledgeId, autoFetch = true) => {
  const [knowledge, setKnowledge] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchKnowledge = useCallback(async (id = knowledgeId) => {
    if (!id) {
      setKnowledge(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await getKnowledgeById(id);
      const formattedKnowledge = formatKnowledgeData(response);
      setKnowledge(formattedKnowledge);
    } catch (err) {
      setError(err.message || 'Nie udało się pobrać wskazówki');
      setKnowledge(null);
    } finally {
      setLoading(false);
    }
  }, [knowledgeId]);

  // Auto-fetch przy zmianie ID
  useEffect(() => {
    if (autoFetch && knowledgeId) {
      fetchKnowledge();
    }
  }, [knowledgeId, autoFetch, fetchKnowledge]);

  return {
    knowledge,
    loading,
    error,
    fetchKnowledge,
    hasKnowledge: !!knowledge
  };
};

/**
 * Hook pomocniczy do zarządzania formularzem wskazówki
 * @param {Object} initialValues - Początkowe wartości formularza
 * @returns {Object} Stan i funkcje formularza
 */
export const useKnowledgeForm = (initialValues = {}) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    knowledge_type: 'general',
    archetype: '',
    tags: [],
    source: 'manual',
    ...initialValues
  });

  const [errors, setErrors] = useState({});

  const updateField = useCallback((field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  }, [errors]);

  const updateMultipleFields = useCallback((fields) => {
    setFormData(prev => ({ ...prev, ...fields }));
  }, []);

  const validateForm = useCallback(() => {
    const validation = validateKnowledgeData(formData);
    setErrors(validation.errors);
    return validation.isValid;
  }, [formData]);

  const resetForm = useCallback(() => {
    setFormData({
      title: '',
      content: '',
      knowledge_type: 'general',
      archetype: '',
      tags: [],
      source: 'manual',
      ...initialValues
    });
    setErrors({});
  }, [initialValues]);

  const isValid = useCallback(() => {
    return validateKnowledgeData(formData).isValid;
  }, [formData]);

  return {
    formData,
    errors,
    updateField,
    updateMultipleFields,
    validateForm,
    resetForm,
    isValid: isValid(),
    hasErrors: Object.keys(errors).length > 0
  };
};
