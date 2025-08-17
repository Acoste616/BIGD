/**
 * Komponent SessionList - wyświetla listę sesji dla konkretnego klienta
 * Reużywalny komponent z Material-UI
 */
import React from 'react';
import { Link } from 'react-router-dom';
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
  Typography,
  Chip,
  Box,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Phone as PhoneIcon,
  Business as HandshakeIcon,
  Slideshow as PresentationIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonChecked as ActiveIcon,
  CheckCircleOutline as CompletedIcon,
  MoreVert as MoreVertIcon,
  CalendarToday as CalendarIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
} from '@mui/icons-material';
import { useClientSessions } from '../hooks/useSessions';

// Mapowanie typów sesji na ikony
const sessionTypeIcons = {
  consultation: <ChatIcon />,
  'follow-up': <PhoneIcon />,
  negotiation: <HandshakeIcon />,
  demo: <PresentationIcon />,
  closing: <CheckCircleIcon />,
  default: <ChatIcon />
};

// Mapowanie wyników na kolory
const outcomeColors = {
  interested: 'success',
  needs_time: 'warning', 
  not_interested: 'error',
  closed_deal: 'primary',
  follow_up_needed: 'info',
  default: 'default'
};

// Mapowanie sentymentu na ikony
const getSentimentIcon = (score) => {
  if (!score) return <TrendingFlatIcon color="disabled" />;
  if (score >= 7) return <TrendingUpIcon color="success" />;
  if (score >= 4) return <TrendingFlatIcon color="warning" />;
  return <TrendingDownIcon color="error" />;
};

const SessionList = ({ clientId, maxItems = null, showHeader = true }) => {
  const { 
    sessions, 
    loading, 
    error, 
    hasActiveSessions,
    totalSessions,
    activeSessions,
    completedSessions 
  } = useClientSessions(clientId, {
    pageSize: maxItems || 10
  });

  // Loading state
  if (loading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={100}>
          <CircularProgress size={40} />
        </Box>
      </Paper>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  // Empty state
  if (!sessions || sessions.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <CalendarIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Brak sesji
        </Typography>
        <Typography variant="body2" color="text.disabled">
          Ten klient nie ma jeszcze żadnych sesji.
        </Typography>
      </Paper>
    );
  }

  // Limit items if specified
  const displayedSessions = maxItems ? sessions.slice(0, maxItems) : sessions;

  return (
    <Paper sx={{ overflow: 'hidden' }}>
      {/* Header z statystykami */}
      {showHeader && (
        <Box sx={{ p: 2, bgcolor: 'grey.50', borderBottom: '1px solid', borderColor: 'grey.200' }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CalendarIcon color="primary" />
            Historia Sesji
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              size="small"
              label={`Łącznie: ${totalSessions}`}
              color="default"
              variant="outlined"
            />
            {hasActiveSessions && (
              <Chip
                size="small"
                label={`Aktywnych: ${activeSessions.length}`}
                color="success"
                variant="filled"
                icon={<ActiveIcon />}
              />
            )}
            {completedSessions.length > 0 && (
              <Chip
                size="small"
                label={`Zakończonych: ${completedSessions.length}`}
                color="default"
                variant="outlined"
                icon={<CompletedIcon />}
              />
            )}
          </Box>
        </Box>
      )}

      {/* Lista sesji */}
      <List sx={{ py: 0 }}>
        {displayedSessions.map((session, index) => (
          <React.Fragment key={session.id}>
            <ListItem
              component={Link}
              to={`/sessions/${session.id}`}
              sx={{ 
                py: 2,
                cursor: 'pointer',
                textDecoration: 'none',
                color: 'inherit',
                '&:hover': {
                  bgcolor: 'action.hover'
                }
              }}
            >
              {/* Ikona typu sesji */}
              <ListItemIcon>
                <Box sx={{ position: 'relative' }}>
                  {sessionTypeIcons[session.session_type] || sessionTypeIcons.default}
                  {session.isActive && (
                    <Box
                      sx={{
                        position: 'absolute',
                        top: -4,
                        right: -4,
                        width: 8,
                        height: 8,
                        bgcolor: 'success.main',
                        borderRadius: '50%',
                        border: '2px solid white'
                      }}
                    />
                  )}
                </Box>
              </ListItemIcon>

              {/* Główne informacje */}
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography variant="body1" component="span">
                      {session.displayType}
                    </Typography>
                    <Chip
                      size="small"
                      label={session.status}
                      color={session.isActive ? 'success' : 'default'}
                      variant={session.isActive ? 'filled' : 'outlined'}
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 0.5 }}>
                    {/* Data i czas */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                      <ScheduleIcon sx={{ fontSize: 14 }} color="action" />
                      <Typography variant="caption" color="text.secondary">
                        {session.displayStartTime}
                        {session.displayEndTime && ` - ${session.displayEndTime}`}
                      </Typography>
                    </Box>
                    
                    {/* Czas trwania */}
                    <Typography variant="caption" color="text.secondary" display="block">
                      {session.duration}
                    </Typography>
                    
                    {/* Wynik sesji */}
                    {session.outcome && (
                      <Box sx={{ mt: 1 }}>
                        <Chip
                          size="small"
                          label={session.displayOutcome}
                          color={outcomeColors[session.outcome] || 'default'}
                          variant="outlined"
                          sx={{ mr: 1 }}
                        />
                      </Box>
                    )}
                  </Box>
                }
              />

              {/* Metryki w prawym górnym rogu */}
              <ListItemSecondaryAction>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
                  {/* Sentiment */}
                  {session.sentiment_score && (
                    <Tooltip title={`Sentyment: ${session.sentimentLabel}`} arrow>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getSentimentIcon(session.sentiment_score)}
                      </Box>
                    </Tooltip>
                  )}
                  
                  {/* Potencjał */}
                  {session.potential_score && (
                    <Tooltip title={`Potencjał: ${session.potentialLabel}`} arrow>
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          fontWeight: 600,
                          color: session.potential_score >= 7 ? 'success.main' : 
                                 session.potential_score >= 4 ? 'warning.main' : 'error.main'
                        }}
                      >
                        {session.potential_score}/10
                      </Typography>
                    </Tooltip>
                  )}
                  
                  {/* Menu akcji */}
                  <IconButton size="small" onClick={(e) => e.stopPropagation()}>
                    <MoreVertIcon fontSize="small" />
                  </IconButton>
                </Box>
              </ListItemSecondaryAction>
            </ListItem>
            
            {/* Divider między sesjami */}
            {index < displayedSessions.length - 1 && (
              <Divider variant="inset" component="li" />
            )}
          </React.Fragment>
        ))}
      </List>

      {/* Footer z informacją o ograniczeniu */}
      {maxItems && sessions.length > maxItems && (
        <Box sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.50', borderTop: '1px solid', borderColor: 'grey.200' }}>
          <Typography variant="body2" color="text.secondary">
            Pokazano {maxItems} z {sessions.length} sesji
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default SessionList;
