/**
 * API Client dla modułu Knowledge Management
 * Komunikacja z backend endpoints dla zarządzania bazą wiedzy Qdrant
 */
import apiClient from './api';

/**
 * Pobiera listę wszystkich wskazówek z możliwością filtrowania
 * @param {Object} params - Parametry zapytania
 * @returns {Promise<Object>} Lista wskazówek z paginacją
 */
export const getKnowledgeList = async (params = {}) => {
  const {
    page = 1,
    size = 10,
    knowledge_type = null,
    archetype = null,
    search = null
  } = params;
  
  const queryParams = new URLSearchParams({
    page: page.toString(),
    size: size.toString()
  });
  
  if (knowledge_type) queryParams.append('knowledge_type', knowledge_type);
  if (archetype) queryParams.append('archetype', archetype);
  if (search) queryParams.append('search', search);
  
  return await apiClient.get(`/knowledge/?${queryParams}`);
};

/**
 * Pobiera szczegóły pojedynczej wskazówki
 * @param {string} knowledgeId - ID wskazówki
 * @returns {Promise<Object>} Szczegóły wskazówki
 */
export const getKnowledgeById = async (knowledgeId) => {
  if (!knowledgeId) {
    throw new Error('Knowledge ID is required');
  }
  return await apiClient.get(`/knowledge/${knowledgeId}`);
};

/**
 * Tworzy nową wskazówkę w bazie wiedzy
 * @param {Object} knowledgeData - Dane wskazówki
 * @returns {Promise<Object>} Utworzona wskazówka z ID
 */
export const createKnowledge = async (knowledgeData) => {
  if (!knowledgeData.content) {
    throw new Error('Content is required');
  }
  
  const requestData = {
    content: knowledgeData.content.trim(),
    title: knowledgeData.title?.trim() || null,
    knowledge_type: knowledgeData.knowledge_type || 'general',
    archetype: knowledgeData.archetype || null,
    tags: knowledgeData.tags || [],
    source: knowledgeData.source || 'manual'
  };
  
  return await apiClient.post('/knowledge/', requestData);
};

/**
 * Usuwa wskazówkę z bazy wiedzy
 * @param {string} knowledgeId - ID wskazówki do usunięcia
 * @returns {Promise<Object>} Potwierdzenie usunięcia
 */
export const deleteKnowledge = async (knowledgeId) => {
  if (!knowledgeId) {
    throw new Error('Knowledge ID is required');
  }
  return await apiClient.delete(`/knowledge/${knowledgeId}`);
};

/**
 * Wyszukuje wskazówki podobne do zapytania (vector search)
 * @param {Object} searchData - Parametry wyszukiwania
 * @returns {Promise<Array>} Lista podobnych wskazówek z score
 */
export const searchKnowledge = async (searchData) => {
  if (!searchData.query) {
    throw new Error('Search query is required');
  }
  
  const requestData = {
    query: searchData.query.trim(),
    limit: searchData.limit || 5,
    knowledge_type: searchData.knowledge_type || null,
    archetype: searchData.archetype || null
  };
  
  return await apiClient.post('/knowledge/search', requestData);
};

/**
 * Pobiera statystyki bazy wiedzy
 * @returns {Promise<Object>} Szczegółowe statystyki
 */
export const getKnowledgeStats = async () => {
  return await apiClient.get('/knowledge/stats/summary');
};

/**
 * Masowe dodawanie wskazówek (batch import)
 * @param {Array} knowledgeItems - Lista wskazówek do dodania
 * @returns {Promise<Object>} Wynik operacji batch
 */
export const bulkCreateKnowledge = async (knowledgeItems) => {
  if (!Array.isArray(knowledgeItems) || knowledgeItems.length === 0) {
    throw new Error('Knowledge items array is required');
  }
  
  if (knowledgeItems.length > 50) {
    throw new Error('Maximum 50 items per batch');
  }
  
  const requestData = {
    items: knowledgeItems.map(item => ({
      content: item.content.trim(),
      title: item.title?.trim() || null,
      knowledge_type: item.knowledge_type || 'general',
      archetype: item.archetype || null,
      tags: item.tags || [],
      source: item.source || 'manual'
    }))
  };
  
  return await apiClient.post('/knowledge/bulk', requestData);
};

/**
 * Sprawdza status połączenia z Qdrant
 * @returns {Promise<Object>} Status health check
 */
export const getQdrantHealth = async () => {
  return await apiClient.get('/knowledge/health/qdrant');
};

/**
 * Pobiera dostępne typy wiedzy
 * @returns {Promise<Array>} Lista dostępnych typów
 */
export const getAvailableKnowledgeTypes = async () => {
  return await apiClient.get('/knowledge/types/available');
};

/**
 * UWAGA: Usuwa całą bazę wiedzy (tylko dewelopersko)
 * @returns {Promise<Object>} Potwierdzenie usunięcia
 */
export const deleteAllKnowledge = async () => {
  return await apiClient.delete('/knowledge/all');
};

/**
 * Formatuje dane wskazówki do wyświetlenia
 * @param {Object} knowledge - Obiekt wskazówki z API
 * @returns {Object} Sformatowane dane wskazówki
 */
export const formatKnowledgeData = (knowledge) => {
  return {
    ...knowledge,
    displayCreatedAt: knowledge.created_at 
      ? new Date(knowledge.created_at).toLocaleDateString('pl-PL', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      : 'Nieznana data',
    displayTitle: knowledge.title || `Wskazówka ${knowledge.id?.substring(0, 8)}`,
    displayContent: knowledge.content?.length > 150 
      ? `${knowledge.content.substring(0, 150)}...`
      : knowledge.content,
    displayType: getKnowledgeTypeLabel(knowledge.knowledge_type),
    displayArchetype: knowledge.archetype || 'Ogólne',
    displayTags: knowledge.tags || [],
    displaySource: getSourceLabel(knowledge.source),
    hasArchetype: !!knowledge.archetype,
    hasTags: knowledge.tags && knowledge.tags.length > 0,
    isLongContent: knowledge.content_length > 500
  };
};

/**
 * Waliduje dane wskazówki przed wysłaniem
 * @param {Object} knowledgeData - Dane wskazówki do walidacji
 * @returns {Object} Wynik walidacji z błędami
 */
export const validateKnowledgeData = (knowledgeData) => {
  const errors = {};
  
  // Walidacja content (wymagane)
  if (!knowledgeData.content || !knowledgeData.content.trim()) {
    errors.content = 'Treść wskazówki jest wymagana';
  } else if (knowledgeData.content.trim().length < 10) {
    errors.content = 'Treść musi mieć co najmniej 10 znaków';
  } else if (knowledgeData.content.trim().length > 5000) {
    errors.content = 'Treść nie może przekraczać 5000 znaków';
  }
  
  // Walidacja title (opcjonalne)
  if (knowledgeData.title && knowledgeData.title.length > 200) {
    errors.title = 'Tytuł nie może przekraczać 200 znaków';
  }
  
  // Walidacja tags
  if (knowledgeData.tags && knowledgeData.tags.length > 10) {
    errors.tags = 'Maksymalnie 10 tagów';
  }
  
  // Walidacja typu wiedzy
  const validTypes = [
    'general', 'objection', 'closing', 'product', 'pricing', 
    'competition', 'demo', 'follow_up', 'technical'
  ];
  if (knowledgeData.knowledge_type && !validTypes.includes(knowledgeData.knowledge_type)) {
    errors.knowledge_type = 'Nieprawidłowy typ wiedzy';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Waliduje zapytanie wyszukiwania
 * @param {Object} searchData - Dane wyszukiwania
 * @returns {Object} Wynik walidacji
 */
export const validateSearchData = (searchData) => {
  const errors = {};
  
  if (!searchData.query || !searchData.query.trim()) {
    errors.query = 'Zapytanie wyszukiwania jest wymagane';
  } else if (searchData.query.trim().length < 3) {
    errors.query = 'Zapytanie musi mieć co najmniej 3 znaki';
  } else if (searchData.query.trim().length > 500) {
    errors.query = 'Zapytanie nie może przekraczać 500 znaków';
  }
  
  if (searchData.limit && (searchData.limit < 1 || searchData.limit > 20)) {
    errors.limit = 'Limit musi być między 1 a 20';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Pomocnicza funkcja do etykietowania typów wiedzy
 * @param {string} type - Typ wiedzy
 * @returns {string} Etykieta typu wiedzy
 */
const getKnowledgeTypeLabel = (type) => {
  const typeLabels = {
    'general': 'Ogólne',
    'objection': 'Zastrzeżenia',
    'closing': 'Zamknięcie',
    'product': 'Produkt',
    'pricing': 'Cennik',
    'competition': 'Konkurencja',
    'demo': 'Demonstracja',
    'follow_up': 'Kontakt',
    'technical': 'Techniczne'
  };
  
  return typeLabels[type] || 'Nieznany';
};

/**
 * Pomocnicza funkcja do etykietowania źródeł
 * @param {string} source - Źródło wiedzy
 * @returns {string} Etykieta źródła
 */
const getSourceLabel = (source) => {
  const sourceLabels = {
    'manual': 'Ręczne',
    'import': 'Import',
    'ai_generated': 'Wygenerowane AI',
    'feedback': 'Z feedbacku'
  };
  
  return sourceLabels[source] || 'Nieznane';
};

/**
 * Pobiera dostępne typy wiedzy (local data)
 * @returns {Array} Lista dostępnych typów wiedzy
 */
export const getLocalKnowledgeTypes = () => {
  return [
    { value: 'general', label: 'Ogólne', icon: 'info', color: 'primary' },
    { value: 'objection', label: 'Zastrzeżenia', icon: 'block', color: 'warning' },
    { value: 'closing', label: 'Zamknięcie', icon: 'handshake', color: 'success' },
    { value: 'product', label: 'Produkt', icon: 'inventory', color: 'info' },
    { value: 'pricing', label: 'Cennik', icon: 'attach_money', color: 'secondary' },
    { value: 'competition', label: 'Konkurencja', icon: 'trending_up', color: 'error' },
    { value: 'demo', label: 'Demonstracja', icon: 'play_circle', color: 'primary' },
    { value: 'follow_up', label: 'Kontakt', icon: 'phone', color: 'info' },
    { value: 'technical', label: 'Techniczne', icon: 'settings', color: 'default' }
  ];
};

/**
 * Pobiera dostępne archetypy klientów (synchronizowane z clientsApi)
 * @returns {Array} Lista dostępnych archetypów
 */
export const getAvailableKnowledgeArchetypes = () => {
  return [
    { value: 'analityk', label: 'Analityk', description: 'Potrzebuje danych i szczegółów' },
    { value: 'decydent', label: 'Decydent', description: 'Skupiony na wynikach biznesowych' },
    { value: 'relacyjny', label: 'Relacyjny', description: 'Buduje długotrwałe relacje' },
    { value: 'kierownik', label: 'Kierownik', description: 'Zarządza zespołem i budżetem' },
    { value: 'ekspert', label: 'Ekspert', description: 'Specjalista w swojej dziedzinie' },
    { value: 'konserwatywny', label: 'Konserwatywny', description: 'Ostrożny w podejmowaniu decyzji' },
    { value: 'innowator', label: 'Innowator', description: 'Chce być pierwszy z nowymi rozwiązaniami' },
    { value: 'pragmatyk', label: 'Pragmatyk', description: 'Szuka sprawdzonych rozwiązań' }
  ];
};

/**
 * Formatuje wyniki wyszukiwania z score
 * @param {Array} searchResults - Wyniki wyszukiwania z API
 * @returns {Array} Sformatowane wyniki z dodatkowymi informacjami
 */
export const formatSearchResults = (searchResults) => {
  return searchResults.map(result => ({
    ...formatKnowledgeData(result),
    score: result.score,
    displayScore: `${Math.round(result.score * 100)}%`,
    relevanceLevel: getRelevanceLevel(result.score),
    isHighlyRelevant: result.score >= 0.8,
    isModeratelyRelevant: result.score >= 0.6 && result.score < 0.8,
    isLowRelevant: result.score < 0.6
  }));
};

/**
 * Określa poziom relevancji na podstawie score
 * @param {number} score - Score podobieństwa (0-1)
 * @returns {string} Poziom relevancji
 */
const getRelevanceLevel = (score) => {
  if (score >= 0.9) return 'Bardzo wysokie';
  if (score >= 0.8) return 'Wysokie';
  if (score >= 0.6) return 'Średnie';
  if (score >= 0.4) return 'Niskie';
  return 'Bardzo niskie';
};
