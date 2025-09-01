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


const ConversationStream = ({ 
  currentClientId,
  currentSessionId,
  currentSession, 
  interactions = [], 
  isLoading,
  isSendingMessage,
  conversationError,
  onSendMessage = () => console.warn('onSendMessage nie został przekazany'),
  onNewInteraction,
  onSessionUpdate,
  onClientIdUpdate,
  onSessionIdUpdate,
  onArchetypesUpdate,
  onInsightsUpdate
}) => {
  
  // 🔒 DEBUG: Sprawdź props przy renderowaniu - USUNIĘTE DLA WYDAJNOŚCI
  const [inputValue, setInputValue] = useState('');
  const [error, setError] = useState(null);
  
  // Ref do kontenera z historią do auto-scroll
  const historyRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll do najnowszej interakcji
  useEffect(() => {
    if (historyRef.current && interactions && interactions.length > 0) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [interactions]);

  // Status inicjalizacji: czy mamy clientId i sessionId gotowe do pracy
  const isSessionReady = currentClientId && currentSessionId;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;
    if (isSendingMessage) return;

    // 🔒 ZABEZPIECZENIE: Sprawdzamy, czy prop jest funkcją, zanim go wywołamy
    if (typeof onSendMessage !== 'function') {
      console.error("❌ Błąd: prop 'onSendMessage' nie jest funkcją!", onSendMessage);
      setError('Błąd: Funkcja wysyłania nie jest dostępna');
      return;
    }

    try {
      console.log('🚀 ConversationStream - Wywołuję onSendMessage z:', inputValue.trim());
      
      // 🚀 UŻYJ NOWEJ FUNKCJI CIĄGŁEJ KONWERSACJI z SessionDetail
      const result = await onSendMessage(inputValue.trim());
      console.log('✅ ConversationStream - onSendMessage zakończone:', result);
      
      // Wyczyść formularz po pomyślnym wysłaniu
      setInputValue('');
      
      // Fokus z powrotem na input
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 100);

    } catch (error) {
      console.error('❌ Błąd w ConversationStream:', error);
      setError(`Błąd wysłania: ${error.message || 'Unknown error'}`);
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
      
      // 🔒 ZABEZPIECZENIE: Sprawdzamy, czy możemy wysłać wiadomość
      if (!isSendingMessage && inputValue.trim() && typeof onSendMessage === 'function') {
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
          label={`${interactions ? interactions.length : 0} interactions`}
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
        {!interactions || interactions.length === 0 ? (
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
      {(error || conversationError) && (
        <Box sx={{ p: 2, pt: 0 }}>
          <Alert 
            severity="error" 
            onClose={() => {
              setError(null);
              // conversationError jest zarządzany przez SessionDetail
            }}
            sx={{ mb: 0 }}
          >
            {error || conversationError}
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
              disabled={isSendingMessage}
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
                  disabled={isSendingMessage}
                  size="small"
                >
                  <ClearIcon />
                </IconButton>
              </Tooltip>
            )}
            
            <Button
              type="submit"
              variant="contained"
              endIcon={isSendingMessage ? <CircularProgress size={16} color="inherit" /> : <SendIcon />}
              disabled={!inputValue.trim() || isSendingMessage}
              sx={{ 
                minWidth: 100,
                height: 40
              }}
            >
              {isSendingMessage ? 'Thinking...' : 'Send'}
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
