# API Services Documentation

## Przegląd

Warstwa `services` zapewnia scentralizowany dostęp do API backendu. Wszystkie żądania HTTP przechodzą przez skonfigurowany klient axios z obsługą błędów, interceptorami i pomocniczymi funkcjami.

## Struktura

```
services/
├── api.js           # Główna konfiguracja axios i interceptory
├── clientsApi.js    # Funkcje API dla modułu Klientów
├── index.js         # Główny punkt eksportu
└── README.md        # Ta dokumentacja
```

## Konfiguracja

### Zmienne środowiskowe

Utwórz plik `.env` w katalogu `/frontend` z następującą zawartością:

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_API_TIMEOUT=30000
REACT_APP_DEBUG=true
```

### Podstawowe użycie

```javascript
import { getClients, createClient, updateClient } from '../services';

// Pobieranie listy klientów
const fetchClients = async () => {
  try {
    const response = await getClients({ 
      page: 1, 
      size: 10,
      sort_by: 'created_at',
      sort_order: 'desc'
    });
    console.log(response.items); // Lista klientów
    console.log(response.total); // Całkowita liczba
  } catch (error) {
    console.error('Error:', error.message);
  }
};

// Tworzenie nowego klienta
const addClient = async () => {
  try {
    const newClient = await createClient({
      name: 'Jan Kowalski',
      contact_info: 'jan@example.com',
      company: 'ABC Corp',
      archetype: 'Pragmatyczny Analityk'
    });
    console.log('Created:', newClient);
  } catch (error) {
    console.error('Error:', error.message);
  }
};
```

## Obsługa błędów

Wszystkie błędy API są standaryzowane do formatu:

```javascript
{
  code: 'ERROR_CODE',        // np. 'NOT_FOUND', 'VALIDATION_ERROR'
  message: 'Opis błędu',     // Czytelny komunikat
  statusCode: 404,           // Kod HTTP (jeśli dostępny)
  originalError: {...}       // Oryginalny błąd axios
}
```

### Przykład obsługi błędów

```javascript
try {
  const client = await getClientById(123);
} catch (error) {
  switch (error.code) {
    case 'NOT_FOUND':
      alert('Klient nie został znaleziony');
      break;
    case 'NETWORK_ERROR':
      alert('Brak połączenia z serwerem');
      break;
    case 'VALIDATION_ERROR':
      alert(`Błąd walidacji: ${error.message}`);
      break;
    default:
      alert('Wystąpił nieoczekiwany błąd');
  }
}
```

## Custom Hooks

Dla łatwiejszego użycia w komponentach React, używaj custom hooków:

```javascript
import { useClientsList, useClient, useCreateClient } from '../hooks/useClients';

// W komponencie React
function ClientsPage() {
  // Hook do listy klientów
  const {
    clients,
    loading,
    error,
    pagination,
    changePage,
    refresh
  } = useClientsList();

  // Hook do tworzenia klienta
  const {
    createClient,
    loading: creating,
    validationErrors
  } = useCreateClient();

  if (loading) return <div>Ładowanie...</div>;
  if (error) return <div>Błąd: {error}</div>;

  return (
    <div>
      {clients.map(client => (
        <div key={client.id}>{client.name}</div>
      ))}
    </div>
  );
}
```

## Funkcje pomocnicze

### Walidacja danych

```javascript
import { validateClientData } from '../services';

const clientData = {
  name: 'John Doe',
  contact_info: 'john@example.com'
};

const validation = validateClientData(clientData);
if (!validation.isValid) {
  console.log('Errors:', validation.errors);
}
```

### Formatowanie danych

```javascript
import { formatClientData } from '../services';

const formatted = formatClientData(rawClient);
console.log(formatted.displayName);     // Sformatowana nazwa
console.log(formatted.createdDate);     // Data w formacie PL
```

### Cache API

```javascript
import { cacheApiResponse, getCachedApiResponse } from '../services';

// Zapisz do cache
cacheApiResponse('clients_list', response, 5); // 5 minut TTL

// Pobierz z cache
const cached = getCachedApiResponse('clients_list');
if (cached) {
  console.log('Using cached data:', cached);
}
```

## Paginacja

Wszystkie endpointy listowe zwracają dane w formacie:

```javascript
{
  items: [...],    // Tablica elementów
  total: 100,      // Całkowita liczba
  page: 1,         // Aktualna strona
  size: 10,        // Rozmiar strony
  pages: 10        // Liczba stron
}
```

## Archetypy klientów

Lista dostępnych archetypów:

```javascript
import { getAvailableArchetypes } from '../services';

const archetypes = getAvailableArchetypes();
// [
//   { value: 'Zdobywca Statusu', label: 'Zdobywca Statusu', description: '...' },
//   { value: 'Strażnik Rodziny', label: 'Strażnik Rodziny', description: '...' },
//   ...
// ]
```

## Debugging

W trybie development (gdy `REACT_APP_DEBUG=true`), wszystkie requesty i response'y są logowane do konsoli.

## Przyszłe moduły

Struktura jest przygotowana na dodanie kolejnych modułów:

- `sessionsApi.js` - Zarządzanie sesjami
- `interactionsApi.js` - Interakcje z AI
- `feedbackApi.js` - System ocen
- `authApi.js` - Autoryzacja i uwierzytelnianie

## Best Practices

1. **Zawsze używaj try/catch** przy wywołaniach API
2. **Pokazuj loading state** podczas ładowania danych
3. **Obsługuj błędy** w sposób przyjazny dla użytkownika
4. **Używaj custom hooków** zamiast bezpośrednich wywołań API w komponentach
5. **Cachuj dane** które rzadko się zmieniają
6. **Debounce** wywołania wyszukiwania
7. **Waliduj dane** przed wysłaniem do API

## Przykład kompletnego komponentu

```javascript
import React, { useState } from 'react';
import { useClientsList, useCreateClient } from '../hooks/useClients';

function ClientsManager() {
  const { clients, loading, error, refresh } = useClientsList();
  const { createClient, validationErrors } = useCreateClient();
  const [formData, setFormData] = useState({
    name: '',
    contact_info: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await createClient(formData);
    
    if (result.success) {
      alert('Klient utworzony!');
      refresh(); // Odśwież listę
      setFormData({ name: '', contact_info: '' });
    }
  };

  return (
    <div>
      <h1>Zarządzanie Klientami</h1>
      
      {/* Formularz dodawania */}
      <form onSubmit={handleSubmit}>
        <input
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          placeholder="Imię i nazwisko"
        />
        {validationErrors.name && <span>{validationErrors.name}</span>}
        
        <input
          value={formData.contact_info}
          onChange={(e) => setFormData({...formData, contact_info: e.target.value})}
          placeholder="Email lub telefon"
        />
        {validationErrors.contact_info && <span>{validationErrors.contact_info}</span>}
        
        <button type="submit">Dodaj klienta</button>
      </form>

      {/* Lista klientów */}
      {loading && <div>Ładowanie...</div>}
      {error && <div>Błąd: {error}</div>}
      
      <ul>
        {clients.map(client => (
          <li key={client.id}>
            {client.name} - {client.contact_info}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ClientsManager;
```
