/**
 * ChatMessage Component - Renderowanie pojedynczej wiadomości w AI Dojo
 * 
 * Komponent pomocniczy do wyświetlania różnych typów wiadomości:
 * - Wiadomości eksperta (user)
 * - Odpowiedzi AI (assistant)  
 * - Wiadomości systemowe (system)
 * - Powiadomienia błędów (error)
 */
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Avatar,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Collapse,
  Stack,
  Button
} from '@mui/material';
import {
  Person as PersonIcon,
  Psychology as PsychologyIcon,
  Settings as SettingsIcon,
  Error as ErrorIcon,
  ContentCopy as CopyIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  CheckCircle as SuccessIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { RESPONSE_TYPES } from '../../services/dojoApi';

/**
 * Główny komponent wiadomości
 * 
 * @param {Object} props
 * @param {Object} props.message - Obiekt wiadomości
 * @param {Function} [props.onCopy] - Callback kopiowania tekstu
 * @param {boolean} [props.showAvatar=true] - Czy pokazać awatar
 * @param {boolean} [props.showTimestamp=true] - Czy pokazać timestamp
 * @param {boolean} [props.allowCopy=true] - Czy pozwolić na kopiowanie
 * @returns {JSX.Element}
 */
const ChatMessage = ({
  message,
  onCopy = null,
  showAvatar = true,
  showTimestamp = true,
  allowCopy = true
}) => {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!message) return null;

  const { type, text, response, timestamp, expertName, confidence_level, response_type } = message;

  const handleCopy = async (content) => {
    if (!allowCopy || !content) return;

    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      
      if (onCopy) {
        onCopy(content);
      }
    } catch (error) {
      console.error('❌ ChatMessage: Error copying text:', error);
    }
  };

  // Renderowanie wiadomości eksperta
  if (type === 'user' || type === 'expert') {
    return (
      <Box display="flex" justifyContent="flex-end" mb={2} gap={1}>
        {showAvatar && (
          <Avatar sx={{ bgcolor: 'primary.main', order: 2 }}>
            <PersonIcon />
          </Avatar>
        )}
        <Box maxWidth="70%" sx={{ order: 1 }}>
          <Paper
            elevation={2}
            sx={{
              p: 2,
              bgcolor: 'primary.main',
              color: 'primary.contrastText',
              borderRadius: 2,
              position: 'relative'
            }}
          >
            <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>
              {text}
            </Typography>
            
            {showTimestamp && (
              <Typography 
                variant="caption" 
                sx={{ 
                  display: 'block', 
                  mt: 1, 
                  opacity: 0.8 
                }}
              >
                {expertName || 'Ekspert'} • {formatTimestamp(timestamp)}
              </Typography>
            )}

            {allowCopy && (
              <Tooltip title={copied ? 'Skopiowano!' : 'Kopiuj wiadomość'}>
                <IconButton
                  size="small"
                  onClick={() => handleCopy(text)}
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    color: 'primary.contrastText',
                    opacity: 0.7,
                    '&:hover': { opacity: 1 }
                  }}
                >
                  <CopyIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Paper>
        </Box>
      </Box>
    );
  }

  // Renderowanie odpowiedzi AI
  if (type === 'ai' || type === 'assistant') {
    return (
      <Box display="flex" justifyContent="flex-start" mb={2} gap={1}>
        {showAvatar && (
          <Avatar sx={{ bgcolor: 'secondary.main' }}>
            <PsychologyIcon />
          </Avatar>
        )}
        <Box maxWidth="85%">
          <Paper
            elevation={1}
            sx={{
              p: 2,
              bgcolor: 'background.paper',
              borderRadius: 2,
              border: 1,
              borderColor: 'divider',
              position: 'relative'
            }}
          >
            {/* Header z typem odpowiedzi i confidence */}
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <PsychologyIcon color="secondary" fontSize="small" />
              <Typography variant="subtitle2" color="secondary">
                Tesla AI Co-Pilot
              </Typography>
              {response_type && (
                <Chip
                  size="small"
                  label={getResponseTypeLabel(response_type)}
                  color={getResponseTypeColor(response_type)}
                />
              )}
              {confidence_level && (
                <Chip
                  size="small"
                  label={`${confidence_level}%`}
                  variant="outlined"
                />
              )}
            </Box>

            {/* Główna treść odpowiedzi */}
            <Typography variant="body1" sx={{ mb: 1, wordBreak: 'break-word' }}>
              {response}
            </Typography>

            {/* Dodatkowe informacje (structured_data, suggested_follow_up) */}
            {message.structured_data && (
              <Box mt={2}>
                <Button
                  size="small"
                  onClick={() => setExpanded(!expanded)}
                  endIcon={expanded ? <CollapseIcon /> : <ExpandIcon />}
                  variant="outlined"
                >
                  {expanded ? 'Ukryj' : 'Pokaż'} szczegóły
                </Button>
                <Collapse in={expanded}>
                  <Box mt={1} p={1} bgcolor="grey.50" borderRadius={1}>
                    <Typography variant="caption" color="text.secondary">
                      Dane strukturalne:
                    </Typography>
                    <pre style={{ fontSize: '0.75rem', marginTop: 4 }}>
                      {JSON.stringify(message.structured_data, null, 2)}
                    </pre>
                  </Box>
                </Collapse>
              </Box>
            )}

            {/* Sugerowane akcje */}
            {message.suggested_follow_up && message.suggested_follow_up.length > 0 && (
              <Box mt={2}>
                <Typography variant="caption" color="text.secondary" display="block" mb={1}>
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
                      sx={{ mb: 1 }}
                    />
                  ))}
                </Stack>
              </Box>
            )}

            {/* Footer z timestampem i przyciskiem kopiowania */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}>
              {showTimestamp && (
                <Typography variant="caption" color="text.secondary">
                  {formatTimestamp(timestamp)}
                </Typography>
              )}
              {allowCopy && (
                <Tooltip title={copied ? 'Skopiowano!' : 'Kopiuj odpowiedź'}>
                  <IconButton
                    size="small"
                    onClick={() => handleCopy(response)}
                    sx={{ ml: 'auto' }}
                  >
                    <CopyIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Paper>
        </Box>
      </Box>
    );
  }

  // Renderowanie wiadomości systemowych
  if (type === 'system') {
    const isSuccess = message.success;
    const isError = message.error;
    const isCancelled = message.cancelled;

    let severity = 'info';
    let icon = <InfoIcon />;

    if (isSuccess) {
      severity = 'success';
      icon = <SuccessIcon />;
    } else if (isError) {
      severity = 'error';
      icon = <ErrorIcon />;
    }

    return (
      <Box display="flex" justifyContent="center" mb={2}>
        <Alert 
          severity={severity}
          icon={icon}
          sx={{ 
            maxWidth: '80%',
            '& .MuiAlert-message': {
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }
          }}
        >
          <Box>
            <Typography variant="body2">
              {text}
            </Typography>
            {showTimestamp && (
              <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                {formatTimestamp(timestamp)}
              </Typography>
            )}
          </Box>
          {allowCopy && (
            <Tooltip title="Kopiuj wiadomość">
              <IconButton 
                size="small" 
                onClick={() => handleCopy(text)}
                sx={{ ml: 1 }}
              >
                <CopyIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Alert>
      </Box>
    );
  }

  // Renderowanie błędów
  if (type === 'error') {
    return (
      <Box display="flex" justifyContent="center" mb={2}>
        <Alert severity="error" icon={<ErrorIcon />} sx={{ maxWidth: '80%' }}>
          <Typography variant="body2">
            {text || 'Wystąpił nieznany błąd'}
          </Typography>
          {showTimestamp && (
            <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
              {formatTimestamp(timestamp)}
            </Typography>
          )}
        </Alert>
      </Box>
    );
  }

  // Fallback - nieznany typ wiadomości
  return (
    <Box display="flex" justifyContent="center" mb={2}>
      <Paper elevation={1} sx={{ p: 2, maxWidth: '80%', bgcolor: 'grey.100' }}>
        <Typography variant="body2" color="text.secondary">
          Nieznany typ wiadomości: {type}
        </Typography>
        <Typography variant="body2">
          {text || response || 'Brak treści'}
        </Typography>
      </Paper>
    </Box>
  );
};

/**
 * UTILITY FUNCTIONS
 */

const getResponseTypeLabel = (responseType) => {
  const labels = {
    [RESPONSE_TYPES.QUESTION]: 'Pytanie',
    [RESPONSE_TYPES.CONFIRMATION]: 'Potwierdzenie',
    [RESPONSE_TYPES.STATUS]: 'Status',
    [RESPONSE_TYPES.ERROR]: 'Błąd'
  };
  return labels[responseType] || responseType;
};

const getResponseTypeColor = (responseType) => {
  const colors = {
    [RESPONSE_TYPES.QUESTION]: 'info',
    [RESPONSE_TYPES.CONFIRMATION]: 'warning',
    [RESPONSE_TYPES.STATUS]: 'success',
    [RESPONSE_TYPES.ERROR]: 'error'
  };
  return colors[responseType] || 'default';
};

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '';
  
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('pl-PL', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  } catch (error) {
    return timestamp;
  }
};

export default ChatMessage;
