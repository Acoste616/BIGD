/**
 * ConversationStream - Lewa strona interfejsu konwersacyjnego
 * 
 * Zawiera:
 * - Formularz wejściowy na dole
 * - Oś czasu z historią interakcji nad formularzem
 * - Używa InteractionCard.js dla każdego wpisu
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Fab,
  Divider,
  Stack,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Send as SendIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon,
  Person as PersonIcon,
  SmartToy as SmartToyIcon
} from '@mui/icons-material';
import InteractionCard from '../InteractionCard';
import { createInteraction } from '../../services/interactionsApi';
import { createClient } from '../../services/clientsApi';
import { createSession } from '../../services/sessionsApi';


const ConversationStream = ({ 
  currentClientId,
  currentSessionId,
  currentSession, 
  interactions, 
  isLoading,
  onNewInteraction,
  onSessionUpdate,
  onClientIdUpdate,
  onSessionIdUpdate,
  onArchetypesUpdate,
  onInsightsUpdate
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  
  // Ref do kontenera z historią do auto-scroll
  const historyRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll do najnowszej interakcji
  useEffect(() => {
    if (historyRef.current && interactions.length > 0) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [interactions]);

  // Status inicjalizacji: czy mamy clientId i sessionId gotowe do pracy
  const isSessionReady = currentClientId && currentSessionId;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;
    if (isSubmitting) return;

    setIsSubmitting(true);
    setError(null);

    try {
      // Pobierz bieżące ID, nawet jeśli są null
      let sessionId = currentSessionId;
      let clientId = currentClientId;

      // Sprawdź, czy to jest PIERWSZA interakcja w sesji przeglądarki
      if (!clientId) {
        console.log('🚀 Pierwsza interakcja - tworzę nowego klienta i sesję...');
        
        // Krok A: Stwórz klienta i POCZEKAJ na jego ID
        const clientData = {
          name: 'Anonymous User',
          email: `user_${Date.now()}@anonymous.local`,
          phone: null,
          notes: 'Automatically created for conversation session'
        };
        
        const newClient = await createClient(clientData); // KLUCZOWE JEST 'AWAIT'
        clientId = newClient.id;
        onClientIdUpdate(clientId); // Zaktualizuj stan w komponencie nadrzędnym
        console.log('✅ Klient utworzony:', clientId);

        // Krok B: Mając clientId, stwórz sesję i POCZEKAJ na jej ID
        const sessionData = {
          session_type: 'conversation',
          summary: 'AI Co-Pilot conversation session',
          notes: 'Interactive conversation session'
        };
        
        const newSession = await createSession(clientId, sessionData); // KLUCZOWE JEST 'AWAIT'
        sessionId = newSession.id;
        onSessionIdUpdate(sessionId); // Zaktualizuj stan w komponencie nadrzędnym
        onSessionUpdate(newSession);
        console.log('✅ Sesja utworzona:', sessionId);
      }

      // Krok C: Mając GWARANTOWANY sessionId, stwórz interakcję
      const interactionData = {
        user_input: inputValue.trim(),
        context: 'conversation_stream'
      };

      console.log('📤 Wysyłam interakcję do sesji:', sessionId);
      const response = await createInteraction(sessionId, interactionData);
      
      // Aktualizacja stanu (odśwież dane, aby zobaczyć nową interakcję w UI)
      onNewInteraction(response);
      
      // Aktualizacja panelu strategicznego na podstawie odpowiedzi AI
      if (response.ai_response_json) {
        const aiResponse = response.ai_response_json;
        
        // Aktualizuj archetypy jeśli są dostępne
        if (aiResponse.likely_archetypes) {
          onArchetypesUpdate(aiResponse.likely_archetypes);
        }
        
        // Aktualizuj insights strategiczne
        if (aiResponse.strategic_notes) {
          onInsightsUpdate(aiResponse.strategic_notes);
        }
      }
      
      // Wyczyść formularz
      setInputValue('');
      
      // Fokus z powrotem na input
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 100);

    } catch (error) {
      console.error('❌ Błąd krytyczny w przepływie interakcji:', error);
      
      // Bardziej szczegółowe komunikaty błędów
      if (error.message?.includes('Client ID is required')) {
        setError('Błąd tworzenia sesji. Spróbuj odświeżyć stronę.');
      } else if (error.message?.includes('Network Error')) {
        setError('Problem z połączeniem. Sprawdź czy backend działa.');
      } else {
        setError(`Nie udało się przetworzyć Twojej prośby: ${error.message || 'Unknown error'}`);
      }
    } finally {
      // Ukryj wskaźnik ładowania
      setIsSubmitting(false);
    }
  };

  const handleClear = () => {
    setInputValue('');
    setError(null);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Handler dla obsługi klawisza Enter w formularzu
  const handleKeyDown = (event) => {
    // Sprawdź, czy naciśnięto Enter i czy NIE wciśnięto Shift
    if (event.key === 'Enter' && !event.shiftKey) {
      // Zapobiegaj domyślnej akcji (np. dodaniu nowej linii)
      event.preventDefault();
      
      // Wywołaj istniejącą logikę wysyłania
      if (!isSubmitting && inputValue.trim()) {
        handleSubmit(event);
      }
    }
  };

  return (
    <Box 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Header z info o sesji */}
      <Box 
        sx={{ 
          p: 2,
          bgcolor: 'grey.50',
          borderBottom: '1px solid',
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
            <SmartToyIcon color="primary" />
            Live Conversation
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {currentSessionId ? `Session #${currentSessionId}` : 'Ready to start conversation...'}
          </Typography>
        </Box>
        
        <Chip 
          label={`${interactions.length} interactions`}
          size="small"
          variant="outlined"
          color="primary"
        />
      </Box>

      {/* Historia konwersacji */}
      <Box 
        ref={historyRef}
        sx={{ 
          flexGrow: 1,
          overflowY: 'auto',
          p: 2,
          bgcolor: 'background.default'
        }}
      >
        {interactions.length === 0 ? (
          <Box 
            sx={{ 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              textAlign: 'center',
              py: 4
            }}
          >
            <SmartToyIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Ready to Help!
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Share any customer situation below and I'll provide instant strategic guidance.
            </Typography>
          </Box>
        ) : (
          <Stack spacing={2}>
            {interactions.map((interaction, index) => (
              <InteractionCard
                key={interaction.id || index}
                interaction={interaction}
                showFullDetails={true}
                onCopyQuickResponse={(text) => {
                  // Optional: Show toast notification
                  console.log('Copied:', text);
                }}
              />
            ))}
          </Stack>
        )}
      </Box>

      {/* Error Alert */}
      {error && (
        <Box sx={{ p: 2, pt: 0 }}>
          <Alert 
            severity="error" 
            onClose={() => setError(null)}
            sx={{ mb: 0 }}
          >
            {error}
          </Alert>
        </Box>
      )}

      {/* Formularz wejściowy */}
      <Paper 
        elevation={3}
        sx={{ 
          p: 2,
          borderRadius: 0,
          borderTop: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Box component="form" onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
            <TextField
              ref={inputRef}
              fullWidth
              multiline
              maxRows={4}
              placeholder="Describe the customer situation, their questions, objections, or any sales challenge..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isSubmitting}
              variant="outlined"
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: 'background.paper',
                }
              }}
            />
            
            {inputValue.trim() && (
              <Tooltip title="Clear input">
                <IconButton 
                  onClick={handleClear}
                  disabled={isSubmitting}
                  size="small"
                >
                  <ClearIcon />
                </IconButton>
              </Tooltip>
            )}
            
            <Button
              type="submit"
              variant="contained"
              endIcon={isSubmitting ? <CircularProgress size={16} color="inherit" /> : <SendIcon />}
              disabled={!inputValue.trim() || isSubmitting}
              sx={{ 
                minWidth: 100,
                height: 40
              }}
            >
              {isSubmitting ? 'Thinking...' : 'Send'}
            </Button>
          </Box>
          
          <Typography 
            variant="caption" 
            color="text.secondary" 
            sx={{ 
              display: 'block',
              mt: 1,
              textAlign: 'center'
            }}
          >
            Press Enter to send • Shift+Enter for new line
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default ConversationStream;
