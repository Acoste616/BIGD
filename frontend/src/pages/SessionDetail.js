/**
 * Strona szczegółów sesji - główny interfejs do pracy z Co-Pilotem
 * Wyświetla oś czasu konwersacji i umożliwia dodawanie nowych interakcji
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Breadcrumbs,
  Button,
  TextField,
  Card,
  CardContent,
  Grid,
  Chip,
  Divider,
  Alert,
  CircularProgress,
  Container,
  Stack,
  IconButton,
  Tooltip,
  Avatar,
  Collapse
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Chat as ChatIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Timeline as TimelineIcon,
  Psychology as PsychologyIcon,
  Assessment as AssessmentIcon,
  Home as HomeIcon,
  Add as AddIcon
} from '@mui/icons-material';

import MainLayout from '../components/MainLayout';
import InteractionCard from '../components/InteractionCard';
import { useSession } from '../hooks/useSessions';
import { useClient } from '../hooks/useClients';
import { createInteraction, validateInteractionData } from '../services';

const SessionDetail = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  
  // State dla formularza nowej interakcji
  const [newInteractionInput, setNewInteractionInput] = useState('');
  const [submittingInteraction, setSubmittingInteraction] = useState(false);
  const [interactionError, setInteractionError] = useState(null);
  const [interactionSuccess, setInteractionSuccess] = useState(false);
  const [showSessionInfo, setShowSessionInfo] = useState(false);

  // Hook do pobierania danych sesji z interakcjami
  const { 
    session, 
    loading, 
    error, 
    interactions, 
    fetchSession,
    hasInteractions,
    interactionsCount
  } = useSession(sessionId, { includeInteractions: true });

  // Hook do pobierania danych klienta (dla breadcrumbs i kontekstu)
  const clientId = session?.client_id;
  const { 
    client, 
    loading: clientLoading 
  } = useClient(clientId);

  // Auto-scroll do najnowszej interakcji
  useEffect(() => {
    if (interactions.length > 0) {
      const timelineContainer = document.getElementById('interactions-timeline');
      if (timelineContainer) {
        timelineContainer.scrollTop = timelineContainer.scrollHeight;
      }
    }
  }, [interactions.length]);

  // Auto-clear success message
  useEffect(() => {
    if (interactionSuccess) {
      const timer = setTimeout(() => {
        setInteractionSuccess(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [interactionSuccess]);

  // Handler dla dodawania nowej interakcji
  const handleAddInteraction = async () => {
    if (!newInteractionInput.trim()) {
      setInteractionError('Opis sytuacji jest wymagany');
      return;
    }

    // Walidacja lokalna
    const validation = validateInteractionData({ user_input: newInteractionInput });
    if (!validation.isValid) {
      setInteractionError(Object.values(validation.errors)[0]);
      return;
    }

    setSubmittingInteraction(true);
    setInteractionError(null);

    try {
      await createInteraction(sessionId, {
        user_input: newInteractionInput.trim(),
        interaction_type: 'question' // Domyślny typ
      });

      // Odśwież dane sesji po dodaniu interakcji
      await fetchSession();
      
      // Wyczyść formularz i pokaż sukces
      setNewInteractionInput('');
      setInteractionSuccess(true);
      
    } catch (err) {
      setInteractionError(err.message || 'Nie udało się dodać interakcji');
    } finally {
      setSubmittingInteraction(false);
    }
  };

  // Handler dla kopiowania quick response
  const handleCopyQuickResponse = (quickResponse) => {
    console.log('Skopiowano quick response:', quickResponse);
    // Tutaj można dodać notyfikację lub toast
  };

  // Loading state
  if (loading || clientLoading) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
            <CircularProgress size={60} />
          </Box>
        </Container>
      </MainLayout>
    );
  }

  // Error state
  if (error) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
          <Button
            component={Link}
            to="/"
            startIcon={<ArrowBackIcon />}
            variant="outlined"
          >
            Powrót do dashboardu
          </Button>
        </Container>
      </MainLayout>
    );
  }

  // Not found state
  if (!session) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Alert severity="warning" sx={{ mb: 3 }}>
            Nie znaleziono sesji o ID: {sessionId}
          </Alert>
          <Button
            component={Link}
            to="/"
            startIcon={<ArrowBackIcon />}
            variant="outlined"
          >
            Powrót do dashboardu
          </Button>
        </Container>
      </MainLayout>
    );
  }

  // Format client alias for breadcrumbs
  const clientAlias = client?.alias || `Klient #${clientId}`;
  const sessionLabel = `Sesja #${sessionId}`;

  return (
    <MainLayout>
      <Container maxWidth="lg" sx={{ py: 3 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs sx={{ mb: 3 }} separator="›">
          <Button
            component={Link}
            to="/"
            startIcon={<HomeIcon />}
            sx={{ textTransform: 'none', color: 'text.primary' }}
          >
            Dashboard
          </Button>
          {client && (
            <Button
              component={Link}
              to={`/clients/${clientId}`}
              startIcon={<PersonIcon />}
              sx={{ textTransform: 'none', color: 'text.primary' }}
            >
              {clientAlias}
            </Button>
          )}
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ChatIcon fontSize="small" />
            {sessionLabel}
          </Typography>
        </Breadcrumbs>

        {/* Header z podstawowymi informacjami o sesji */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ bgcolor: 'primary.main' }}>
                <ChatIcon />
              </Avatar>
              <Box>
                <Typography variant="h4" gutterBottom>
                  {sessionLabel}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {session.displayType} • {session.status}
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Odśwież dane">
                <IconButton onClick={fetchSession} disabled={loading}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title={showSessionInfo ? "Ukryj szczegóły" : "Pokaż szczegóły"}>
                <IconButton onClick={() => setShowSessionInfo(!showSessionInfo)}>
                  {showSessionInfo ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {/* Podstawowe metryki sesji */}
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            <Chip
              icon={<ScheduleIcon />}
              label={session.duration}
              color={session.isActive ? 'success' : 'default'}
              variant={session.isActive ? 'filled' : 'outlined'}
            />
            <Chip
              icon={<TimelineIcon />}
              label={`${interactionsCount} interakcji`}
              color="primary"
              variant="outlined"
            />
            {session.sentiment_score && (
              <Chip
                icon={<AssessmentIcon />}
                label={`Sentyment: ${session.sentiment_score}/10`}
                color={session.sentiment_score >= 7 ? 'success' : session.sentiment_score >= 4 ? 'warning' : 'error'}
                variant="outlined"
              />
            )}
            {session.potential_score && (
              <Chip
                icon={<PsychologyIcon />}
                label={`Potencjał: ${session.potential_score}/10`}
                color={session.potential_score >= 7 ? 'success' : session.potential_score >= 4 ? 'warning' : 'error'}
                variant="outlined"
              />
            )}
          </Box>

          {/* Rozwijane szczegóły sesji */}
          <Collapse in={showSessionInfo}>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Informacje o sesji
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <strong>Rozpoczęta:</strong> {session.displayStartTime}
                </Typography>
                {session.displayEndTime && (
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Zakończona:</strong> {session.displayEndTime}
                  </Typography>
                )}
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <strong>Typ:</strong> {session.displayType}
                </Typography>
                {session.outcome && (
                  <Typography variant="body2" color="text.secondary">
                    <strong>Wynik:</strong> {session.displayOutcome}
                  </Typography>
                )}
              </Grid>
              
              {client && (
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Kontekst klienta
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Alias:</strong> {client.alias}
                  </Typography>
                  {client.archetype && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>Archetyp:</strong> {client.archetype}
                    </Typography>
                  )}
                  {client.tags && client.tags.length > 0 && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        <strong>Tagi:</strong>
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {client.tags.map(tag => (
                          <Chip key={tag} label={tag} size="small" variant="outlined" />
                        ))}
                      </Box>
                    </Box>
                  )}
                </Grid>
              )}
            </Grid>
          </Collapse>
        </Paper>

        {/* Główna zawartość - oś czasu interakcji i formularz */}
        <Grid container spacing={3}>
          {/* Oś czasu interakcji */}
          <Grid item xs={12} lg={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TimelineIcon color="primary" />
                Oś czasu konwersacji
              </Typography>
              
              {!hasInteractions ? (
                <Box sx={{ textAlign: 'center', py: 6 }}>
                  <TimelineIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    Brak interakcji
                  </Typography>
                  <Typography variant="body2" color="text.disabled">
                    Ta sesja nie ma jeszcze żadnych interakcji. Dodaj pierwszą obserwację poniżej.
                  </Typography>
                </Box>
              ) : (
                <Box
                  id="interactions-timeline"
                  sx={{
                    maxHeight: 600,
                    overflowY: 'auto',
                    pr: 1,
                    '&::-webkit-scrollbar': {
                      width: '8px',
                    },
                    '&::-webkit-scrollbar-track': {
                      backgroundColor: 'grey.100',
                      borderRadius: '4px',
                    },
                    '&::-webkit-scrollbar-thumb': {
                      backgroundColor: 'grey.400',
                      borderRadius: '4px',
                      '&:hover': {
                        backgroundColor: 'grey.600',
                      },
                    },
                  }}
                >
                  <Stack spacing={2}>
                    {interactions.map((interaction) => (
                      <InteractionCard
                        key={interaction.id}
                        interaction={interaction}
                        showFullDetails={true}
                        onCopyQuickResponse={handleCopyQuickResponse}
                      />
                    ))}
                  </Stack>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Formularz nowej interakcji */}
          <Grid item xs={12} lg={4}>
            <Paper sx={{ p: 3, position: 'sticky', top: 20 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AddIcon color="primary" />
                Nowa interakcja
              </Typography>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Opisz aktualną sytuację z klientem, a Co-Pilot przeanalizuje ją i zasugeruje najlepsze działania.
              </Typography>

              {interactionSuccess && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  Interakcja została dodana pomyślnie!
                </Alert>
              )}

              {interactionError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {interactionError}
                </Alert>
              )}

              <TextField
                fullWidth
                multiline
                rows={4}
                label="Opisz sytuację"
                placeholder="Np. Klient pyta o cenę Model Y i martwi się kosztami eksploatacji..."
                value={newInteractionInput}
                onChange={(e) => setNewInteractionInput(e.target.value)}
                disabled={submittingInteraction}
                error={!!interactionError}
                sx={{ mb: 2 }}
              />

              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={submittingInteraction ? <CircularProgress size={20} /> : <SendIcon />}
                onClick={handleAddInteraction}
                disabled={submittingInteraction || !newInteractionInput.trim()}
                sx={{ mb: 2 }}
              >
                {submittingInteraction ? 'Analizuję...' : 'Wyślij do analizy AI'}
              </Button>

              <Typography variant="caption" color="text.secondary" display="block" sx={{ textAlign: 'center' }}>
                Analiza zajmuje zwykle 2-5 sekund
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Przycisk powrotu */}
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button
            component={Link}
            to={client ? `/clients/${clientId}` : '/'}
            startIcon={<ArrowBackIcon />}
            variant="outlined"
          >
            {client ? `Powrót do profilu ${clientAlias}` : 'Powrót do dashboardu'}
          </Button>
        </Box>
      </Container>
    </MainLayout>
  );
};

export default SessionDetail;
