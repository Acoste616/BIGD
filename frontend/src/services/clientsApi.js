/**
 * Moduł API dla zarządzania Klientami
 * Zawiera wszystkie funkcje do komunikacji z endpointami /clients
 */
import apiClient, { buildQueryString } from './api';

/**
 * Pobiera listę klientów z paginacją i filtrowaniem
 * @param {Object} params - Parametry zapytania
 * @param {number} params.page - Numer strony (domyślnie 1)
 * @param {number} params.size - Rozmiar strony (domyślnie 10)
 * @param {string} params.sort_by - Pole sortowania
 * @param {string} params.sort_order - Kierunek sortowania (asc/desc)
 * @param {string} params.search - Fraza wyszukiwania
 * @param {string} params.archetype - Filtr archetypu
 * @param {string[]} params.tags - Filtr tagów
 * @returns {Promise<Object>} Odpowiedź z listą klientów i metadanymi paginacji
 */
export const getClients = async (params = {}) => {
  const defaultParams = {
    page: 1,
    size: 10,
    sort_by: 'created_at',
    sort_order: 'desc',
    ...params
  };

  const queryString = buildQueryString(defaultParams);
  return await apiClient.get(`/clients/${queryString}`);
};

/**
 * Pobiera szczegóły pojedynczego klienta
 * @param {number} clientId - ID klienta
 * @returns {Promise<Object>} Dane klienta
 */
export const getClientById = async (clientId) => {
  if (!clientId) {
    throw new Error('Client ID is required');
  }
  return await apiClient.get(`/clients/${clientId}`);
};

/**
 * Tworzy nowego klienta (tylko dane profilujące - alias generowany automatycznie)
 * @param {Object} clientData - Dane nowego klienta
 * @param {string} clientData.notes - Notatki analityczne
 * @param {string} clientData.archetype - Archetyp klienta
 * @param {string[]} clientData.tags - Tagi profilujące
 * @returns {Promise<Object>} Utworzony klient z automatycznym aliasem
 */
export const createClient = async (clientData) => {
  // Czyścimy dane przed wysłaniem (tylko dane profilujące)
  const cleanedData = {
    notes: clientData.notes?.trim() || null,
    archetype: clientData.archetype || null,
    tags: Array.isArray(clientData.tags) ? clientData.tags : []
  };

  return await apiClient.post('/clients/', cleanedData);
};

/**
 * Aktualizuje dane istniejącego klienta
 * @param {number} clientId - ID klienta
 * @param {Object} updateData - Dane do aktualizacji (tylko zmienione pola)
 * @returns {Promise<Object>} Zaktualizowany klient
 */
export const updateClient = async (clientId, updateData) => {
  if (!clientId) {
    throw new Error('Client ID is required');
  }

  // Usuwamy puste wartości - wysyłamy tylko to, co ma być zaktualizowane
  const cleanedData = Object.entries(updateData).reduce((acc, [key, value]) => {
    if (value !== undefined && value !== '') {
      acc[key] = typeof value === 'string' ? value.trim() : value;
    }
    return acc;
  }, {});

  return await apiClient.put(`/clients/${clientId}`, cleanedData);
};

/**
 * Usuwa klienta
 * @param {number} clientId - ID klienta
 * @returns {Promise<void>}
 */
export const deleteClient = async (clientId) => {
  if (!clientId) {
    throw new Error('Client ID is required');
  }
  
  // API zwraca 204 No Content przy sukcesie
  await apiClient.delete(`/clients/${clientId}`);
  return { success: true, message: 'Klient został usunięty' };
};

/**
 * Pobiera statystyki klienta
 * @param {number} clientId - ID klienta
 * @returns {Promise<Object>} Statystyki klienta
 */
export const getClientStatistics = async (clientId) => {
  if (!clientId) {
    throw new Error('Client ID is required');
  }
  return await apiClient.get(`/clients/${clientId}/statistics`);
};

/**
 * Szybkie wyszukiwanie klientów
 * @param {string} query - Fraza wyszukiwania
 * @param {number} limit - Maksymalna liczba wyników
 * @returns {Promise<Array>} Lista dopasowanych klientów
 */
export const searchClients = async (query, limit = 10) => {
  if (!query || query.trim().length < 2) {
    return [];
  }

  const params = buildQueryString({ q: query.trim(), limit });
  const response = await apiClient.get(`/clients/search/quick/${params}`);
  return response.results || [];
};

/**
 * Pobiera klientów według archetypu
 * @param {string} archetype - Nazwa archetypu
 * @param {number} page - Numer strony
 * @param {number} size - Rozmiar strony
 * @returns {Promise<Object>} Lista klientów z danym archetypem
 */
export const getClientsByArchetype = async (archetype, page = 1, size = 10) => {
  return await getClients({ archetype, page, size });
};

/**
 * Pobiera dostępne archetypy klientów
 * @returns {Array<Object>} Lista archetypów
 */
export const getAvailableArchetypes = () => {
  // Te dane mogłyby pochodzić z API, ale na razie są zahardkodowane
  return [
    { value: 'Zdobywca Statusu', label: 'Zdobywca Statusu', description: 'Postrzega Teslę jako symbol sukcesu' },
    { value: 'Strażnik Rodziny', label: 'Strażnik Rodziny', description: 'Priorytet: bezpieczeństwo i praktyczność' },
    { value: 'Pragmatyczny Analityk', label: 'Pragmatyczny Analityk', description: 'Kieruje się danymi i ROI' },
    { value: 'Eko-Entuzjasta', label: 'Eko-Entuzjasta', description: 'Motywowany wartościami ekologicznymi' },
    { value: 'Pionier Technologii', label: 'Pionier Technologii', description: 'Zafascynowany technologią' },
    { value: 'Techniczny Sceptyk', label: 'Techniczny Sceptyk', description: 'Ma obawy co do technologii EV' },
    { value: 'Lojalista Premium', label: 'Lojalista Premium', description: 'Kierowca tradycyjnych marek premium' },
    { value: 'Łowca Okazji', label: 'Łowca Okazji', description: 'Skupiony na cenie i ofercie' },
    { value: 'Niezdecydowany Odkrywca', label: 'Niezdecydowany Odkrywca', description: 'Potrzebuje edukacji' },
    { value: 'Entuzjasta Osiągów', label: 'Entuzjasta Osiągów', description: 'Kluczowe: przyspieszenie i wrażenia' }
  ];
};

/**
 * Eksportuje dane klientów (placeholder dla przyszłej funkcjonalności)
 * @param {Object} filters - Filtry eksportu
 * @returns {Promise<Blob>} Plik do pobrania
 */
export const exportClients = async (filters = {}) => {
  // TODO: Implementacja gdy backend będzie wspierał eksport
  throw new Error('Export functionality not yet implemented');
};

// Pomocnicze funkcje do pracy z danymi klientów

/**
 * Formatuje dane klienta do wyświetlenia
 * @param {Object} client - Obiekt klienta z API
 * @returns {Object} Sformatowane dane
 */
export const formatClientData = (client) => {
  return {
    ...client,
    displayAlias: client.alias,
    displayArchetype: client.archetype || 'Nieprzypisany',
    hasNotes: !!client.notes,
    tagsCount: client.tags?.length || 0,
    createdDate: new Date(client.created_at).toLocaleDateString('pl-PL'),
    updatedDate: new Date(client.updated_at).toLocaleDateString('pl-PL')
  };
};

/**
 * Waliduje dane klienta przed wysłaniem
 * @param {Object} clientData - Dane do walidacji
 * @returns {Object} Wynik walidacji
 */
export const validateClientData = (clientData) => {
  const errors = {};

  // Tylko walidacja danych profilujących - brak wymaganych pól

  // Walidacja archetype
  if (clientData.archetype && !getAvailableArchetypes().includes(clientData.archetype)) {
    errors.archetype = 'Nieprawidłowy archetyp klienta';
  }

  if (clientData.tags && !Array.isArray(clientData.tags)) {
    errors.tags = 'Tagi muszą być tablicą';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};
