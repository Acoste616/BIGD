/**
 * DojoChat Component - Główny interfejs konwersacji treningowej AI Dojo
 * 
 * Moduł 3: Interaktywne AI Dojo "Sparing z Mistrzem"
 * 
 * Komponent zawiera:
 * - Interfejs chatu z AI
 * - Obsługę różnych typów odpowiedzi AI
 * - Specjalne renderowanie dla confirmation (structured_data)
 * - Przyciski "Zatwierdź i zapisz" / "Anuluj"
 * - Auto-scroll, loading states, error handling
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardHeader,
  CardContent,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  CircularProgress,
  Tooltip,
  Badge,
  Stack,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Send as SendIcon,
  Psychology as PsychologyIcon,
  Clear as ClearIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  QuestionAnswer as QuestionIcon,
  ExpandMore as ExpandMoreIcon,
  ContentCopy as ContentCopyIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useDojoChat } from '../../hooks/useDojoChat';
import { TRAINING_MODES, RESPONSE_TYPES } from '../../services/dojoApi';

/**
 * Komponent główny AI Dojo Chat
 * 
 * @param {Object} props - Props komponentu
 * @param {string} [props.expertName='Administrator'] - Nazwa eksperta
 * @param {string} [props.trainingMode='knowledge_update'] - Tryb treningu
 * @param {boolean} [props.showHeader=true] - Czy pokazać header
 * @param {boolean} [props.showSessionInfo=true] - Czy pokazać info o sesji
 * @param {Function} [props.onError] - Callback błędów
 * @param {Function} [props.onSuccess] - Callback sukcesu
 * @param {Object} [props.sx] - Stylowanie Material-UI
 * @returns {JSX.Element} Komponent DojoChat
 */
const DojoChat = ({
  expertName = 'Administrator',
  trainingMode = TRAINING_MODES.KNOWLEDGE_UPDATE,
  showHeader = true,
  showSessionInfo = true,
  onError = null,
  onSuccess = null,
  sx = {}
}) => {
  // === HOOK STATE ===
  const {
    messages,
    isLoading,
    error,
    sessionId,
    pendingConfirmation,
    isConfirming,
    sendMessage,
    confirmKnowledge,
    clearChat,
    scrollToBottom,
    hasMessages,
    hasPendingConfirmation,
    messageCount,
    messagesEndRef,
    inputRef
  } = useDojoChat({
    expertName,
    trainingMode,
    onError,
    onSuccess
  });

  // === LOCAL STATE ===
  const [messageInput, setMessageInput] = useState('');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [expandedMessage, setExpandedMessage] = useState(null);
  const [copySuccess, setCopySuccess] = useState(null);
  const [notification, setNotification] = useState(null);

  // === COMPUTED VALUES ===
  const canSendMessage = messageInput.trim().length > 0 && !isLoading;
  const trainingModeLabel = getTrainingModeLabel(trainingMode);

  /**
   * EVENT HANDLERS
   */

  const handleSendMessage = async () => {
    if (!canSendMessage) return;

    const message = messageInput.trim();
    setMessageInput('');

    try {
      await sendMessage(message);
    } catch (error) {
      console.error('❌ DojoChat: Error sending message:', error);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleConfirmKnowledge = async (confirmed) => {
    setShowConfirmDialog(false);
    
    try {
      await confirmKnowledge(confirmed);
      
      // Pokaż potwierdzenie sukcesu
      if (confirmed) {
        setNotification({
          type: 'success',
          message: '✅ Wiedza została pomyślnie zapisana w bazie danych!'
        });
      } else {
        setNotification({
          type: 'info', 
          message: 'ℹ️ Operacja anulowana przez użytkownika'
        });
      }
      
      // Auto-clear notification po 3 sekundach
      setTimeout(() => setNotification(null), 3000);
      
    } catch (error) {
      console.error('❌ DojoChat: Error confirming knowledge:', error);
      setNotification({
        type: 'error',
        message: `❌ Błąd podczas zapisu: ${error.message}`
      });
    }
  };

  const handleClearChat = () => {
    clearChat();
    setMessageInput('');
    setExpandedMessage(null);
  };

  const handleCopyText = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess(text.substring(0, 50));
      setTimeout(() => setCopySuccess(null), 2000);
    } catch (error) {
      console.error('❌ DojoChat: Error copying text:', error);
    }
  };

  /**
   * EFFECTS
   */

  // Auto-focus na input po załadowaniu
  useEffect(() => {
    if (inputRef.current && !isLoading) {
      inputRef.current.focus();
    }
  }, [isLoading, inputRef]);

  // Otwórz dialog confirmation automatycznie
  useEffect(() => {
    if (hasPendingConfirmation && !showConfirmDialog) {
      setShowConfirmDialog(true);
    }
  }, [hasPendingConfirmation, showConfirmDialog]);

  // Zamknij dialog confirmation po zakończeniu operacji
  useEffect(() => {
    if (!hasPendingConfirmation && showConfirmDialog) {
      setShowConfirmDialog(false);
    }
  }, [hasPendingConfirmation, showConfirmDialog]);

  /**
   * RENDER FUNCTIONS
   */

  const renderHeader = () => {
    if (!showHeader) return null;

    return (
      <CardHeader
        avatar={
          <Badge
            badgeContent={messageCount}
            color="primary"
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          >
            <PsychologyIcon color="primary" sx={{ fontSize: 40 }} />
          </Badge>
        }
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="h6" component="h2">
              AI Dojo: Sparing z Mistrzem
            </Typography>
            <Chip 
              label={trainingModeLabel} 
              size="small" 
              color="secondary"
              variant="outlined" 
            />
          </Box>
        }
        subheader={
          <Box display="flex" alignItems="center" gap={1} mt={1}>
            <Typography variant="body2" color="text.secondary">
              Ekspert: {expertName}
            </Typography>
            {sessionId && showSessionInfo && (
              <>
                <Divider orientation="vertical" flexItem />
                <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                  Sesja: {sessionId.split('_')[1]?.substring(0, 6)}...
                </Typography>
              </>
            )}
          </Box>
        }
        action={
          <Box display="flex" gap={1}>
            <Tooltip title="Odśwież">
              <IconButton onClick={scrollToBottom} size="small">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Wyczyść chat">
              <IconButton 
                onClick={handleClearChat} 
                disabled={!hasMessages || isLoading}
                size="small"
              >
                <ClearIcon />
              </IconButton>
            </Tooltip>
          </Box>
        }
        sx={{ pb: 1 }}
      />
    );
  };

  const renderMessage = (message) => {
    const { id, type, text, response, timestamp, confidence_level, response_type, structured_data } = message;

    if (type === 'user') {
      return (
        <Box key={id} display="flex" justifyContent="flex-end" mb={2}>
          <Paper 
            elevation={1} 
            sx={{ 
              p: 2, 
              maxWidth: '70%', 
              bgcolor: 'primary.main', 
              color: 'primary.contrastText' 
            }}
          >
            <Typography variant="body1">{text}</Typography>
            <Typography variant="caption" sx={{ opacity: 0.8, mt: 1, display: 'block' }}>
              {expertName} • {formatTimestamp(timestamp)}
            </Typography>
          </Paper>
        </Box>
      );
    }

    if (type === 'ai') {
      return (
        <Box key={id} display="flex" justifyContent="flex-start" mb={2}>
          <Box maxWidth="85%">
            {/* Main AI Response */}
            <Paper elevation={2} sx={{ p: 2, bgcolor: 'background.paper' }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <PsychologyIcon color="secondary" fontSize="small" />
                <Typography variant="subtitle2" color="secondary">
                  AI Tesla Co-Pilot
                </Typography>
                <Chip 
                  size="small" 
                  label={getResponseTypeLabel(response_type)} 
                  color={getResponseTypeColor(response_type)}
                />
                {confidence_level && (
                  <Chip 
                    size="small" 
                    label={`${confidence_level}%`} 
                    variant="outlined"
                  />
                )}
              </Box>
              
              <Typography variant="body1" sx={{ mb: 1 }}>
                {response}
              </Typography>

              {/* Copy Button */}
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="caption" color="text.secondary">
                  {formatTimestamp(timestamp)}
                </Typography>
                <Tooltip title="Kopiuj odpowiedź">
                  <IconButton size="small" onClick={() => handleCopyText(response)}>
                    <ContentCopyIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Paper>

            {/* Structured Data (Confirmation) */}
            {response_type === RESPONSE_TYPES.CONFIRMATION && structured_data && (
              <Box mt={1}>
                <StructuredDataDisplay 
                  data={structured_data} 
                  onConfirm={() => setShowConfirmDialog(true)}
                />
              </Box>
            )}

            {/* Suggested Follow-up */}
            {message.suggested_follow_up && message.suggested_follow_up.length > 0 && (
              <Box mt={1}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  💡 Sugerowane akcje:
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {message.suggested_follow_up.map((suggestion, index) => (
                    <Chip
                      key={index}
                      label={suggestion}
                      size="small"
                      variant="outlined"
                      clickable
                      onClick={() => setMessageInput(suggestion)}
                      sx={{ mb: 1 }}
                    />
                  ))}
                </Stack>
              </Box>
            )}
          </Box>
        </Box>
      );
    }

    if (type === 'system') {
      return (
        <Box key={id} display="flex" justifyContent="center" mb={2}>
          <Alert 
            severity={message.success ? 'success' : message.cancelled ? 'info' : 'info'}
            icon={message.success ? <CheckCircleIcon /> : <InfoIcon />}
            sx={{ maxWidth: '80%' }}
          >
            <Typography variant="body2">{text}</Typography>
          </Alert>
        </Box>
      );
    }

    return null;
  };

  const renderInputArea = () => (
    <Box p={2} bgcolor="background.default">
      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => {}}>
          {error}
        </Alert>
      )}

      {/* Notification (success/info/error) */}
      {notification && (
        <Alert 
          severity={notification.type} 
          sx={{ mb: 2 }}
          onClose={() => setNotification(null)}
        >
          {notification.message}
        </Alert>
      )}

      {/* Copy Success */}
      {copySuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Skopiowano: "{copySuccess}..."
        </Alert>
      )}

      {/* Loading Progress */}
      {isLoading && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
            AI analizuje Twoją wiadomość...
          </Typography>
        </Box>
      )}

      {/* Input Field */}
      <Box display="flex" gap={1} alignItems="flex-end">
        <TextField
          ref={inputRef}
          fullWidth
          multiline
          maxRows={4}
          value={messageInput}
          onChange={(e) => setMessageInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Napisz wiadomość do AI (np. nowa wiedza, korekta błędu, pytanie)..."
          disabled={isLoading}
          variant="outlined"
          size="small"
          helperText={`${messageInput.length}/5000 znaków`}
          FormHelperTextProps={{ sx: { textAlign: 'right' } }}
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={!canSendMessage}
          startIcon={isLoading ? <CircularProgress size={16} /> : <SendIcon />}
          sx={{ minWidth: 100, height: 40 }}
        >
          Wyślij
        </Button>
      </Box>
    </Box>
  );

  const renderEmptyState = () => (
    <Box 
      display="flex" 
      flexDirection="column" 
      alignItems="center" 
      justifyContent="center"
      p={4}
      sx={{ minHeight: 300 }}
    >
      <PsychologyIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
      <Typography variant="h6" color="text.secondary" gutterBottom>
        Witaj w AI Dojo! 
      </Typography>
      <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ maxWidth: 400, mb: 3 }}>
        To interaktywne środowisko treningowe dla Tesla Co-Pilot AI. 
        Możesz przekazywać nową wiedzę, korygować błędy, lub zadawać pytania.
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap" justifyContent="center">
        <Chip 
          label="💡 'Tesla Model Y ma nową opcję...'"
          variant="outlined"
          clickable
          onClick={() => setMessageInput("Tesla Model Y ma nową opcję kolorystyczną - Midnight Silver Metallic")}
        />
        <Chip 
          label="❓ 'Jak odpowiadać na pytania o cenę?'"
          variant="outlined" 
          clickable
          onClick={() => setMessageInput("Jak najlepiej odpowiadać klientom pytającym o cenę Tesla?")}
        />
        <Chip 
          label="🔧 'Poprawka: zasięg Model 3 to...'"
          variant="outlined"
          clickable
          onClick={() => setMessageInput("Poprawka: zasięg Tesla Model 3 Long Range to 602 km WLTP")}
        />
      </Stack>
    </Box>
  );

  /**
   * MAIN RENDER
   */
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', ...sx }}>
      {renderHeader()}
      
      {/* Messages Area */}
      <CardContent 
        sx={{ 
          flex: 1, 
          overflow: 'hidden', 
          display: 'flex', 
          flexDirection: 'column',
          p: 0 
        }}
      >
        <Box 
          sx={{ 
            flex: 1, 
            overflow: 'auto', 
            p: 2,
            '&::-webkit-scrollbar': { width: '8px' },
            '&::-webkit-scrollbar-track': { backgroundColor: '#f1f1f1' },
            '&::-webkit-scrollbar-thumb': { backgroundColor: '#c1c1c1', borderRadius: '4px' }
          }}
        >
          {!hasMessages ? renderEmptyState() : (
            <>
              {messages.map(renderMessage)}
              <div ref={messagesEndRef} />
            </>
          )}
        </Box>
      </CardContent>

      {/* Input Area */}
      {renderInputArea()}

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        open={showConfirmDialog}
        onClose={() => setShowConfirmDialog(false)}
        onConfirm={handleConfirmKnowledge}
        structuredData={pendingConfirmation?.structuredData}
        isLoading={isConfirming}
      />
    </Card>
  );
};

/**
 * Komponent wyświetlania structured data
 */
const StructuredDataDisplay = ({ data, onConfirm }) => {
  const [expanded, setExpanded] = useState(false);

  if (!data) return null;

  return (
    <Paper variant="outlined" sx={{ p: 2, bgcolor: 'primary.lighter' }}>
      <Box display="flex" alignItems="center" gap={1} mb={1}>
        <SaveIcon color="primary" fontSize="small" />
        <Typography variant="subtitle2" color="primary">
          Przygotowano dane do zapisu w bazie wiedzy
        </Typography>
      </Box>

      <Accordion expanded={expanded} onChange={(_, isExpanded) => setExpanded(isExpanded)}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="body2" fontWeight={500}>
            {data.title || 'Nowa wiedza'}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={1}>
            <Typography variant="body2">
              <strong>Treść:</strong> {data.content}
            </Typography>
            <Typography variant="body2">
              <strong>Typ:</strong> {data.knowledge_type}
            </Typography>
            {data.archetype && (
              <Typography variant="body2">
                <strong>Archetyp:</strong> {data.archetype}
              </Typography>
            )}
            {data.tags && data.tags.length > 0 && (
              <Box>
                <Typography variant="body2" component="span">
                  <strong>Tagi:</strong>
                </Typography>
                <Stack direction="row" spacing={0.5} mt={0.5}>
                  {data.tags.map((tag, index) => (
                    <Chip key={index} label={tag} size="small" variant="outlined" />
                  ))}
                </Stack>
              </Box>
            )}
            {data.source && (
              <Typography variant="body2">
                <strong>Źródło:</strong> {data.source}
              </Typography>
            )}
          </Stack>
        </AccordionDetails>
      </Accordion>

      <Box display="flex" gap={1} mt={2}>
        <Button
          variant="contained"
          color="success"
          startIcon={<CheckCircleIcon />}
          onClick={onConfirm}
          size="small"
        >
          Zatwierdź i zapisz
        </Button>
        <Button
          variant="outlined"
          color="error"
          startIcon={<CancelIcon />}
          onClick={() => onConfirm?.(false)}
          size="small"
        >
          Anuluj
        </Button>
      </Box>
    </Paper>
  );
};

/**
 * Dialog potwierdzenia zapisu wiedzy
 */
const ConfirmationDialog = ({ open, onClose, onConfirm, structuredData, isLoading }) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <SaveIcon color="primary" />
          Potwierdzenie zapisu wiedzy
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {structuredData ? (
          <StructuredDataDisplay data={structuredData} />
        ) : (
          <Typography>Brak danych do wyświetlenia</Typography>
        )}
      </DialogContent>

      <DialogActions>
        <Button 
          onClick={() => onConfirm(false)} 
          disabled={isLoading}
          startIcon={<CancelIcon />}
        >
          Anuluj
        </Button>
        <Button 
          onClick={() => onConfirm(true)} 
          variant="contained"
          disabled={isLoading}
          startIcon={isLoading ? <CircularProgress size={16} /> : <CheckCircleIcon />}
        >
          {isLoading ? 'Zapisuję...' : 'Zatwierdź i zapisz'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

/**
 * UTILITY FUNCTIONS
 */

const getTrainingModeLabel = (mode) => {
  const labels = {
    [TRAINING_MODES.KNOWLEDGE_UPDATE]: 'Aktualizacja wiedzy',
    [TRAINING_MODES.ERROR_CORRECTION]: 'Korekta błędów',
    [TRAINING_MODES.GENERAL_CHAT]: 'Rozmowa ogólna'
  };
  return labels[mode] || mode;
};

const getResponseTypeLabel = (type) => {
  const labels = {
    [RESPONSE_TYPES.QUESTION]: 'Pytanie',
    [RESPONSE_TYPES.CONFIRMATION]: 'Potwierdzenie',
    [RESPONSE_TYPES.STATUS]: 'Status',
    [RESPONSE_TYPES.ERROR]: 'Błąd'
  };
  return labels[type] || type;
};

const getResponseTypeColor = (type) => {
  const colors = {
    [RESPONSE_TYPES.QUESTION]: 'info',
    [RESPONSE_TYPES.CONFIRMATION]: 'warning',
    [RESPONSE_TYPES.STATUS]: 'success',
    [RESPONSE_TYPES.ERROR]: 'error'
  };
  return colors[type] || 'default';
};

const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('pl-PL', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

export default DojoChat;
