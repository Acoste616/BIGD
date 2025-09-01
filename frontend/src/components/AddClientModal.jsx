import React, { useState } from 'react';
import { Modal, Box, Typography, TextField, Button, CircularProgress } from '@mui/material';

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};

const AddClientModal = ({ open, handleClose, onClientAdded }) => {
  const [clientName, setClientName] = useState('');
  const [clientArchetype, setClientArchetype] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    // Tu w przyszłości będzie walidacja
    if (!clientName) {
      setError('Nazwa klienta jest wymagana.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      // UWAGA: Ta funkcja zostanie zaimplementowana w kolejnym kroku
      // const newClient = await clientsApi.createClient({ name: clientName, archetype: clientArchetype });
      // onClientAdded(newClient);

      // Symulacja wywołania API na razie
      console.log('Wysyłanie nowego klienta:', { name: clientName, archetype: clientArchetype });
      setTimeout(() => {
        onClientAdded({ id: Date.now(), name: clientName, archetype: clientArchetype, created_at: new Date().toISOString() });
        setIsLoading(false);
        handleClose();
      }, 1000);

    } catch (err) {
      setError('Nie udało się dodać klienta. Spróbuj ponownie.');
      setIsLoading(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      aria-labelledby="add-client-modal-title"
    >
      <Box sx={style}>
        <Typography id="add-client-modal-title" variant="h6" component="h2">
          Dodaj Nowego Klienta
        </Typography>
        <TextField
          autoFocus
          margin="dense"
          id="name"
          label="Nazwa Klienta"
          type="text"
          fullWidth
          variant="standard"
          value={clientName}
          onChange={(e) => setClientName(e.target.value)}
        />
        <TextField
          margin="dense"
          id="archetype"
          label="Archetyp (opcjonalnie)"
          type="text"
          fullWidth
          variant="standard"
          value={clientArchetype}
          onChange={(e) => setClientArchetype(e.target.value)}
        />
        {error && <Typography color="error" sx={{ mt: 2 }}>{error}</Typography>}
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button onClick={handleClose}>Anuluj</Button>
          <Button onClick={handleSubmit} variant="contained" sx={{ ml: 2 }} disabled={isLoading}>
            {isLoading ? <CircularProgress size={24} /> : 'Dodaj'}
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};

export default AddClientModal;
