import React, { useState, useEffect } from 'react';
import { Box, Typography, Button } from '@mui/material';
import ClientList from '../components/ClientList';
import AddClientModal from '../components/AddClientModal';
// Załóżmy, że mamy taki serwis API. Jeśli nie, stwórz go.
// import clientsApi from '../services/clientsApi';

const Dashboard = () => {
  const [clients, setClients] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchClients = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Symulacja pobierania danych z API
      console.log("Pobieranie listy klientów...");
      await new Promise(res => setTimeout(res, 1500)); // Symulacja opóźnienia sieciowego
      // Zastąp to prawdziwym wywołaniem: const data = await clientsApi.getAllClients();
      const mockData = [
         { id: 1, name: 'Klient A', archetype: 'Analityk', created_at: '2025-08-26T10:00:00Z' },
         { id: 2, name: 'Klient B', archetype: 'Innowator', created_at: '2025-08-25T12:30:00Z' }
      ];
      setClients(mockData);
    } catch (err) {
      setError('Nie udało się załadować listy klientów.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const handleClientAdded = (newClient) => {
    setClients(prevClients => [newClient, ...prevClients]);
    fetchClients(); // Odśwież listę po dodaniu
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">
          Dashboard ({clients.length} klientów w bazie)
        </Typography>
        <Button variant="contained" onClick={() => setIsModalOpen(true)}>
          Dodaj Klienta (Manual)
        </Button>
      </Box>

      <ClientList 
        clients={clients} 
        isLoading={isLoading} 
        error={error} 
        onSortChange={(sortConfig) => {
          // Tu zaimplementuj logikę sortowania w przyszłości
          console.log('Zmiana sortowania:', sortConfig);
        }}
      />

      <AddClientModal 
        open={isModalOpen}
        handleClose={() => setIsModalOpen(false)}
        onClientAdded={handleClientAdded}
      />
    </Box>
  );
};

export default Dashboard;
