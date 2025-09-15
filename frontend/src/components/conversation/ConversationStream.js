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
  const [websocket, setWebsocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected'); // connecting, connected, disconnected, failed, reconnecting
  
  // Ref to store the latest interactions for WebSocket message handling
  const interactionsRef = useRef(interactions);
  
  // Ref to store WebSocket reconnection attempts
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  
  // Ref to kontenera z historią do auto-scroll
  const historyRef = useRef(null);
  const inputRef = useRef(null);

  // Update interactionsRef when interactions change
  useEffect(() => {
    interactionsRef.current = interactions;
  }, [interactions]);

  // Auto-scroll do najnowszej interakcji
  useEffect(() => {
    if (historyRef.current && interactions.length > 0) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [interactions]);

  // WebSocket connection management
  useEffect(() => {
    if (currentSessionId) {
      connectWebSocket(currentSessionId);
    }

    // Cleanup function to close WebSocket connection
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [currentSessionId]);

  // Status inicjalizacji: czy mamy clientId i sessionId gotowe do pracy
  const isSessionReady = currentClientId && currentSessionId;

  const connectWebSocket = (sessionId) => {
    // Close existing connection if any
    if (websocket) {
      websocket.close();
    }

    setConnectionStatus('connecting');
    
    try {
      // Create WebSocket connection
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${window.location.host}/api/v1/ws/${sessionId}`;
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connected for session:', sessionId);
        setWebsocket(ws);
        setConnectionStatus('connected');
        reconnectAttempts.current = 0; // Reset reconnect attempts on successful connection
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };
      
      ws.onclose = (event) => {
        console.log('WebSocket disconnected for session:', sessionId);
        setWebsocket(null);
        setConnectionStatus('disconnected');
        
        // Attempt to reconnect if the session is still active and we haven't exceeded max attempts
        if (currentSessionId && reconnectAttempts.current < maxReconnectAttempts) {
          setConnectionStatus('reconnecting');
          reconnectAttempts.current += 1;
          
          // Exponential backoff: 1s, 2s, 4s, 8s, 16s
          const reconnectDelay = Math.min(1000 * Math.pow(2, reconnectAttempts.current - 1), 16000);
          
          setTimeout(() => {
            if (currentSessionId) {
              connectWebSocket(currentSessionId);
            }
          }, reconnectDelay);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          setConnectionStatus('failed');
          setError('Connection lost. Please refresh the page to reconnect.');
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('failed');
        setError('Connection error. Please check your network.');
      };
      
    } catch (e) {
      console.error('Error creating WebSocket connection:', e);
      setConnectionStatus('failed');
      setError('Failed to establish connection.');
    }
  };

  const handleWebSocketMessage = (message) => {
    console.log('Received WebSocket message:', message);
    
    if (message.event === 'analysis_complete') {
      // Handle the complete AI analysis
      const interactionData = {
        id: message.data.interaction_id,
        ai_response_json: message.data.ai_response,
        timestamp: message.timestamp
      };
      
      // Update the UI with the new interaction
      onNewInteraction(interactionData);
      
      // Update panel with AI response data
      if (message.data.ai_response) {
        const aiResponse = message.data.ai_response;
        
        // Update archetypes if available
        if (aiResponse.likely_archetypes) {
          onArchetypesUpdate(aiResponse.likely_archetypes);
        }
        
        // Update strategic insights
        if (aiResponse.strategic_notes) {
          onInsightsUpdate(aiResponse.strategic_notes);
        }
      }
      
      // Hide loading indicator
      setIsSubmitting(false);
    } else if (message.event === 'connected') {
      console.log('WebSocket connection established:', message.message);
    } else if (message.event === 'error') {
      console.error('WebSocket error message:', message.data);
      setError(`Connection error: ${message.data}`);
      setIsSubmitting(false);
    }
  };

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
      // Note: We're not waiting for the response here since we'll get it via WebSocket
      await createInteraction(sessionId, interactionData);
      
      // Clear the input but keep the submitting state until we get the WebSocket response
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
      
      // Hide loading indicator on error
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
          {connectionStatus !== 'connected' && (
            <Typography variant="caption" color={
              connectionStatus === 'connecting' || connectionStatus === 'reconnecting' 
                ? 'warning.main' 
                : connectionStatus === 'failed' 
                  ? 'error.main' 
                  : 'text.secondary'
            }>
              {connectionStatus === 'connecting' && 'Connecting...'}
              {connectionStatus === 'reconnecting' && `Reconnecting... (${reconnectAttempts.current}/${maxReconnectAttempts})`}
              {connectionStatus === 'disconnected' && 'Disconnected'}
              {connectionStatus === 'failed' && 'Connection failed'}
            </Typography>
          )}
        </Box>
        
        <Chip 
          label={`${interactions.length} interactions`}
          size="small"
          variant="outlined"
          color="primary"
        />
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