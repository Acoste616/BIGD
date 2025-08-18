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
 * Import wiedzy z pliku JSON (knowledge_base_pl.json format)
 * @param {File} jsonFile - Plik JSON do importu
 * @param {Function} progressCallback - Callback do raportowania postępu
 * @returns {Promise<Object>} Wynik operacji importu z estatystykami
 */
export const bulkImportFromJSON = async (jsonFile, progressCallback = null) => {
  try {
    // Sprawdź czy to plik JSON
    if (!jsonFile.name.toLowerCase().endsWith('.json')) {
      throw new Error('Plik musi mieć rozszerzenie .json');
    }
    
    if (jsonFile.size > 10 * 1024 * 1024) { // 10MB limit
      throw new Error('Plik nie może przekraczać 10MB');
    }
    
    // Wczytaj zawartość pliku
    const fileContent = await readFileAsText(jsonFile);
    let jsonData;
    
    try {
      jsonData = JSON.parse(fileContent);
    } catch (parseError) {
      throw new Error('Nieprawidłowy format JSON: ' + parseError.message);
    }
    
    // Konwertuj różne formaty JSON do standardowego formatu
    const normalizedItems = normalizeJSONData(jsonData);
    
    if (normalizedItems.length === 0) {
      throw new Error('Plik nie zawiera żadnych prawidłowych wpisów');
    }
    
    // Raportuj postęp
    if (progressCallback) {
      progressCallback({
        phase: 'parsing',
        message: `Znaleziono ${normalizedItems.length} wpisów do importu`,
        itemsFound: normalizedItems.length
      });
    }
    
    // Podziel na batche (max 50 na raz)
    const batchSize = 50;
    const batches = [];
    for (let i = 0; i < normalizedItems.length; i += batchSize) {
      batches.push(normalizedItems.slice(i, i + batchSize));
    }
    
    // Importuj batch po batch
    let totalImported = 0;
    let totalErrors = 0;
    const results = [];
    
    for (let i = 0; i < batches.length; i++) {
      const batch = batches[i];
      
      if (progressCallback) {
        progressCallback({
          phase: 'importing',
          message: `Importuję batch ${i + 1}/${batches.length} (${batch.length} elementów)`,
          currentBatch: i + 1,
          totalBatches: batches.length,
          itemsProcessed: totalImported
        });
      }
      
      try {
        const result = await bulkCreateKnowledge(batch);
        results.push(result);
        totalImported += batch.length;
        
        // Krótkia przerwa między batchami żeby nie przeciążać serwera
        if (i < batches.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
        
      } catch (batchError) {
        totalErrors += batch.length;
        console.error(`Błąd w batch ${i + 1}:`, batchError);
        results.push({ 
          error: batchError.message,
          batch: i + 1,
          itemsInBatch: batch.length
        });
      }
    }
    
    // Finalne raportowanie
    if (progressCallback) {
      progressCallback({
        phase: 'completed',
        message: `Import zakończony. Zaimportowano: ${totalImported}, błędy: ${totalErrors}`,
        totalImported,
        totalErrors,
        totalItems: normalizedItems.length
      });
    }
    
    return {
      success: true,
      totalItems: normalizedItems.length,
      totalImported,
      totalErrors,
      results,
      summary: `Pomyślnie zaimportowano ${totalImported} z ${normalizedItems.length} elementów. Błędów: ${totalErrors}`
    };
    
  } catch (error) {
    if (progressCallback) {
      progressCallback({
        phase: 'error',
        message: `Błąd importu: ${error.message}`,
        error: error.message
      });
    }
    throw error;
  }
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

/**
 * Czyta plik jako tekst (Promise wrapper dla FileReader)
 * @param {File} file - Plik do wczytania
 * @returns {Promise<string>} Zawartość pliku jako tekst
 */
const readFileAsText = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = (e) => reject(new Error('Błąd podczas wczytywania pliku: ' + e.target.error));
    reader.readAsText(file, 'utf-8');
  });
};

/**
 * Normalizuje różne formaty JSON do standardowego formatu API
 * @param {any} jsonData - Surowe dane JSON
 * @returns {Array} Tablica znormalizowanych obiektów wiedzy
 */
const normalizeJSONData = (jsonData) => {
  const normalizedItems = [];
  
  // Funkcja do przetwarzania pojedynczego elementu
  const processItem = (item) => {
    // Sprawdź czy ma wymagane pola
    if (!item.content || !item.title) {
      console.warn('Pominięto element bez content lub title:', item.id || 'unknown');
      return null;
    }
    
    // Konwertuj format z pliku JSON do formatu API
    const normalized = {
      content: String(item.content).trim(),
      title: String(item.title).trim(),
      knowledge_type: mapKnowledgeType(item.type),
      archetype: extractArchetype(item.archetype_filter),
      tags: Array.isArray(item.tags) ? item.tags : [],
      source: item.source || 'import'
    };
    
    return normalized;
  };
  
  // Obsłuż różne struktury JSON
  if (Array.isArray(jsonData)) {
    // Prosta tablica obiektów
    jsonData.forEach(item => {
      const normalized = processItem(item);
      if (normalized) normalizedItems.push(normalized);
    });
    
  } else if (jsonData && typeof jsonData === 'object') {
    // Obiekt z różnymi kluczami
    Object.values(jsonData).forEach(section => {
      if (Array.isArray(section)) {
        // Sekcja z tablicą elementów
        section.forEach(item => {
          const normalized = processItem(item);
          if (normalized) normalizedItems.push(normalized);
        });
      } else if (section && typeof section === 'object') {
        // Zagnieżdżony obiekt z facts/tactics/knowledge_entries
        if (section.facts && Array.isArray(section.facts)) {
          section.facts.forEach(item => {
            const normalized = processItem(item);
            if (normalized) normalizedItems.push(normalized);
          });
        }
        if (section.tactics && Array.isArray(section.tactics)) {
          section.tactics.forEach(item => {
            const normalized = processItem(item);
            if (normalized) normalizedItems.push(normalized);
          });
        }
        if (section.knowledge_entries && Array.isArray(section.knowledge_entries)) {
          section.knowledge_entries.forEach(item => {
            const normalized = processItem(item);
            if (normalized) normalizedItems.push(normalized);
          });
        }
      }
    });
  }
  
  return normalizedItems;
};

/**
 * Mapuje typ wiedzy z pliku JSON do typu API
 * @param {string} jsonType - Typ z pliku JSON
 * @returns {string} Typ API
 */
const mapKnowledgeType = (jsonType) => {
  const typeMapping = {
    'accounting': 'pricing',
    'sales_tactic': 'objection', 
    'pricing': 'pricing',
    'technical': 'technical',
    'product': 'product',
    'market': 'competition',
    'psychology': 'general',
    'psychometric_indicator': 'general',
    'behavioral_indicator': 'general',
    'question_pattern': 'general',
    'sales_narrative': 'closing'
  };
  
  return typeMapping[jsonType] || 'general';
};

/**
 * Ekstraktuje archetyp z tablicy archetype_filter
 * @param {Array} archetypeFilter - Tablica archetypów z pliku JSON
 * @returns {string|null} Pierwszy dopasowany archetyp lub null
 */
const extractArchetype = (archetypeFilter) => {
  if (!Array.isArray(archetypeFilter) || archetypeFilter.length === 0) {
    return null;
  }
  
  // Mapowanie archetypów z JSON do archetypów API
  const archetypeMapping = {
    'business_optimizer': 'analityk',
    'pragmatyczny_analityk': 'analityk',
    'data_driven_professional': 'analityk',
    'straznik_rodziny': 'relacyjny',
    'family_oriented': 'relacyjny',
    'dynamiczny_entuzjasta': 'innowator',
    'wizjoner': 'innowator',
    'techniczny_sceptyk': 'ekspert',
    'tech_enthusiast': 'ekspert',
    'eko_entuzjasta': 'pragmatyk',
    'eco_enthusiast': 'pragmatyk',
    'lowca_okazji': 'analityk',
    'niezdecydowany_odkrywca': 'konserwatywny'
  };
  
  // Znajdź pierwszy dopasowany archetyp
  for (const jsonArchetype of archetypeFilter) {
    const mappedArchetype = archetypeMapping[jsonArchetype];
    if (mappedArchetype) {
      return mappedArchetype;
    }
  }
  
  // Jeśli nie ma dopasowania, zwróć pierwszy jako fallback
  return archetypeFilter[0] || null;
};
