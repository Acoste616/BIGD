/**
 * Modal do finalizacji sesji
 * Pozwala użytkownikowi na wprowadzenie wyniku sesji i jej zakończenie
 */
import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  TextField,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useConcludeSession } from '../../hooks/useSessionAnalytics';

const outcomeOptions = [
  { value: 'interested', label: 'Zainteresowany' },
  { value: 'needs_time', label: 'Potrzebuje czasu' },
  { value: 'not_interested', label: 'Niezainteresowany' },
  { value: 'closed_deal', label: 'Transakcja zamknięta' },
  { value: 'follow_up_needed', label: 'Wymaga kontaktu' },
];

const ConcludeSessionModal = ({ open, onClose, session, onConcludeSuccess }) => {
  const [outcome, setOutcome] = useState('');
  const [notes, setNotes] = useState('');
  const [summary, setSummary] = useState('');
  
  const { concludeSession, loading, error, success, resetState } = useConcludeSession({
    onSuccess: (data) => {
      if (onConcludeSuccess) {
        onConcludeSuccess(data);
      }
      handleClose();
    },
    onError: (err) => {
      console.error('Błąd podczas finalizacji sesji:', err);
    }
  });

  const handleSubmit = async () => {
    if (!outcome) {
      alert('Proszę wybrać wynik sesji');
      return;
    }

    const conclusionData = {
      outcome,
      notes: notes || undefined,
      summary: summary || undefined,
    };

    try {
      await concludeSession(session.id, conclusionData);
    } catch (err) {
      console.error('Błąd podczas finalizacji sesji:', err);
    }
  };

  const handleClose = () => {
    // Reset form
    setOutcome('');
    setNotes('');
    setSummary('');
    resetState();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Zakończ sesję</DialogTitle>
      
      <DialogContent>
        <DialogContentText sx={{ mb: 2 }}>
          Finalizuj sesję #{session?.id} z klientem {session?.client?.alias || 'nieznany'}.
          Wprowadź wynik sesji i dodatkowe informacje.
        </DialogContentText>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Sesja została pomyślnie zakończona!
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 2 }}>
          <FormControl component="fieldset">
            <FormLabel component="legend" required>Wynik sesji</FormLabel>
            <RadioGroup
              value={outcome}
              onChange={(e) => setOutcome(e.target.value)}
            >
              {outcomeOptions.map((option) => (
                <FormControlLabel
                  key={option.value}
                  value={option.value}
                  control={<Radio />}
                  label={option.label}
                />
              ))}
            </RadioGroup>
          </FormControl>

          <TextField
            label="Podsumowanie"
            multiline
            rows={3}
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="Krótkie podsumowanie sesji..."
            fullWidth
          />

          <TextField
            label="Dodatkowe notatki"
            multiline
            rows={4}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Dodatkowe informacje o sesji..."
            fullWidth
          />
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Anuluj
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={loading || !outcome}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Finalizowanie...' : 'Zakończ sesję'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConcludeSessionModal;