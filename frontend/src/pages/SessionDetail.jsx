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
  Grid,
  Chip,
  Divider,
  Container,
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
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Psychology as PsychologyIcon,
  Assessment as AssessmentIcon,
  Home as HomeIcon
} from '@mui/icons-material';

import MainLayout from '../components/MainLayout';
// 🧠⚡ DODAJĘ KOMPONENTY DLA PEŁNEJ FUNKCJONALNOŚCI PSYCHOMETRYCZNEJ
import ConversationStream from '../components/conversation/ConversationStream';
import StrategicPanel from '../components/conversation/StrategicPanel';
import { useSession } from '../hooks/useSessions';
import { useClient } from '../hooks/useClients';
// 🧠⚡ DODAJĘ ULTRA MÓZG dla analizy psychometrycznej
import { useUltraBrain } from '../hooks/useUltraBrain';
// 🧠⚡ DODAJĘ API DLA CIĄGŁEJ KONWERSACJI
import { createInteraction } from '../services/interactionsApi';

const SessionDetail = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  
  const [showSessionInfo, setShowSessionInfo] = useState(false);

  // Hook do pobierania danych sesji z interakcjami
  const { 
    session, 
    loading, 
    error, 
    interactions: sessionInteractions, 
    fetchSession,
    hasInteractions,
    interactionsCount
  } = useSession(sessionId, { includeInteractions: true });

  // 🧠⚡ STAN KONWERSACJI - Dynamiczne zarządzanie historią interakcji
  const [interactions, setInteractions] = useState([]);
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  const [conversationError, setConversationError] = useState(null);

  // Hook do pobierania danych klienta (dla breadcrumbs i kontekstu)
  const clientId = session?.client_id;
  const { 
    client, 
    loading: clientLoading 
  } = useClient(clientId);

  // 🧠⚡ ULTRA MÓZG - CENTRALNE ŹRÓDŁO PRAWDY dla analizy psychometrycznej
  // Używamy ostatniej interakcji jako źródła danych dla analizy
  const lastInteractionId = interactions && interactions.length > 0 ? interactions[interactions.length - 1]?.id : null;
  const {
    dnaKlienta,
    strategia,
    surowePsychology,
    isDnaReady,
    isStrategiaReady,
    isUltraBrainReady,
    confidence: ultraBrainConfidence,
    legacy: ultraBrainLegacy,
    loading: ultraBrainLoading,
    error: ultraBrainError,
    isPolling: ultraBrainPolling,
    getArchetypeName,
    getMainDrive,
    getCommunicationStyle,
    getKeyLevers,
    getRedFlags,
    getStrategicRecommendation,
    getQuickResponse,
    getSuggestedQuestions,
    getProactiveGuidance
  } = useUltraBrain(lastInteractionId, {
    autoFetch: !!lastInteractionId,
    enablePolling: true,
    debug: true
  });

  // 🧠⚡ ULTRA MÓZG - Przygotuj dane dla StrategicPanel
  const [archetypes, setArchetypes] = useState([]);
  const [strategicInsights, setStrategicInsights] = useState([]);

  // 🧠⚡ SYNCHRONIZACJA STANU KONWERSACJI - Aktualizuj lokalny stan po pobraniu danych z API
  // --- POCZĄTEK POPRAWKI ---
  // Usuń stary, błędny useEffect, jeśli istnieje
  
  // Dodajemy nowy, stabilny useEffect do synchronizacji interakcji
  useEffect(() => {
    // Sprawdzamy, czy dane sesji istnieją i czy tablica interakcji faktycznie się zmieniła,
    // porównując długość lub głębszą strukturę, aby uniknąć niepotrzebnych re-renderów.
    // Najprostsza i często wystarczająca jest serializacja do JSONa.
    if (sessionInteractions && JSON.stringify(interactions) !== JSON.stringify(sessionInteractions)) {
      setInteractions(sessionInteractions);
      console.log('🔄 SessionDetail - zsynchronizowano stan konwersacji:', sessionInteractions.length, 'interakcji');
    } else if (sessionInteractions && Array.isArray(sessionInteractions) && interactions.length === 0) {
      // Nawet jeśli nie ma interakcji, ustaw pustą tablicę tylko raz
      setInteractions([]);
      console.log('🔄 SessionDetail - ustawiono pustą tablicę interakcji');
    }
    // W tablicy zależności używamy tylko `sessionData`, ale warunek wewnątrz zapobiega pętli.
    // Lepszym rozwiązaniem byłoby przekazanie tylko sessionData.interactions, jeśli hook na to pozwala.
  }, [sessionInteractions, interactions]); // Dodajemy `interactions` do zależności, aby uniknąć przestarzałego stanu w porównaniu
  // --- KONIEC POPRAWKI ---

  // 🧠⚡ ULTRA MÓZG - Aktualizuj archetypes i insights z Ultra Mózgu
  useEffect(() => {
    if (isDnaReady && dnaKlienta) {
      // Aktualizuj archetypes z DNA klienta
      const newArchetypes = [{
        name: getArchetypeName(),
        confidence: ultraBrainConfidence,
        description: dnaKlienta.archetype_description || 'Profil w trakcie analizy...',
        traits: dnaKlienta.dominant_traits || [],
        motivators: dnaKlienta.motivators || []
      }];
      setArchetypes(newArchetypes);
      
      // Aktualizuj strategic insights
      const newInsights = [{
        type: 'psychometric',
        title: 'Profil Psychometryczny',
        content: `Archetyp: ${getArchetypeName()}`,
        confidence: ultraBrainConfidence,
        data: {
          mainDrive: getMainDrive(),
          communicationStyle: getCommunicationStyle(),
          keyLevers: getKeyLevers(),
          redFlags: getRedFlags()
        }
      }];
      
      if (isStrategiaReady && strategia) {
        newInsights.push({
          type: 'strategy',
          title: 'Strategia Sprzedażowa',
          content: getStrategicRecommendation(),
          confidence: ultraBrainConfidence,
          data: strategia
        });
      }
      
      setStrategicInsights(newInsights);
    }
  }, [isDnaReady, isStrategiaReady, dnaKlienta, strategia, ultraBrainConfidence, 
      getArchetypeName, getMainDrive, getCommunicationStyle, getKeyLevers, 
      getRedFlags, getStrategicRecommendation]);

  // Auto-scroll do najnowszej interakcji
  useEffect(() => {
    if (interactions && interactions.length > 0) {
      const timelineContainer = document.getElementById('interactions-timeline');
      if (timelineContainer) {
        timelineContainer.scrollTop = timelineContainer.scrollHeight;
      }
    }
  }, [interactions]);



  // 🧠⚡ HANDLER CIĄGŁEJ KONWERSACJI - Główna logika wysyłania wiadomości
  const handleSendMessage = async (newMessageText) => {
    if (!newMessageText.trim() || isSendingMessage) {
      return;
    }

    setIsSendingMessage(true);
    setConversationError(null);

    try {
      // 🚀 OPTYMISTYCZNE UI UPDATE - Natychmiast dodaj wiadomość użytkownika
      const optimisticUserInteraction = {
        id: `temp_${Date.now()}`,
        author: 'user',
        content: newMessageText.trim(),
        created_at: new Date().toISOString(),
        isOptimistic: true
      };

      setInteractions(currentInteractions => [...currentInteractions, optimisticUserInteraction]);
      console.log('✅ SessionDetail - dodano optymistyczną wiadomość użytkownika');

      // 📤 WYWOŁANIE API - Wyślij wiadomość do backendu
      const interactionData = {
        user_input: newMessageText.trim(),
        context: 'continuous_conversation'
      };

      console.log('📤 SessionDetail - wysyłam wiadomość do backendu:', interactionData);
      const response = await createInteraction(sessionId, interactionData);
      
      // 🔄 AKTUALIZACJA STANU PO ODPOWIEDZI - Zastąp optymistyczną wiadomość prawdziwą odpowiedzią
      setInteractions(currentInteractions => {
        // Usuń optymistyczną wiadomość i dodaj prawdziwą odpowiedź z backendu
        const filteredInteractions = currentInteractions.filter(interaction => !interaction.isOptimistic);
        
        // Dodaj prawdziwą interakcję z backendu (zawiera odpowiedź AI)
        return [...filteredInteractions, response];
      });

      console.log('✅ SessionDetail - zaktualizowano stan po odpowiedzi AI:', response);

      // 🔄 ODŚWIEŻ SESJĘ - Pobierz zaktualizowane dane z backendu
      await fetchSession();

    } catch (error) {
      console.error('❌ SessionDetail - błąd podczas wysyłania wiadomości:', error);
      
      // 🚨 COFNIJ OPTYMISTYCZNE UI UPDATE w przypadku błędu
      setInteractions(currentInteractions => 
        currentInteractions.filter(interaction => !interaction.isOptimistic)
      );
      
      setConversationError(`Nie udało się wysłać wiadomości: ${error.message || 'Unknown error'}`);
    } finally {
      setIsSendingMessage(false);
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
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Ładowanie sesji...
              </Typography>
            </Box>
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
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="error" gutterBottom>
              Błąd podczas ładowania sesji
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              {error}
            </Typography>
            <Button
              component={Link}
              to="/"
              startIcon={<ArrowBackIcon />}
              variant="outlined"
            >
              Powrót do dashboardu
            </Button>
          </Box>
        </Container>
      </MainLayout>
    );
  }

  // Not found state
  if (!session) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="warning.main" gutterBottom>
              Nie znaleziono sesji
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Sesja o ID: {sessionId} nie została znaleziona
            </Typography>
            <Button
              component={Link}
              to="/"
              startIcon={<ArrowBackIcon />}
              variant="outlined"
            >
              Powrót do dashboardu
            </Button>
          </Box>
        </Container>
      </MainLayout>
    );
  }

  // Format client alias for breadcrumbs
  const clientAlias = client?.alias || `Klient #${clientId}`;
  const sessionLabel = `Sesja #${sessionId}`;
  
  // 🔒 ZABEZPIECZENIE: Sprawdź czy handleSendMessage jest dostępna
  console.log('🔒 SessionDetail - handleSendMessage dostępna:', typeof handleSendMessage, handleSendMessage);

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

        {/* 🧠⚡ GŁÓWNA ZAWARTOŚĆ - NOWY INTERFEJS KONWERSACYJNY Z ULTRA MÓZGIEM */}
        <Grid container spacing={3}>
          {/* 🧠⚡ LEWA STRONA: Strumień konwersacji (70%) */}
          <Grid 
            item 
            xs={12} 
            lg={8.5} 
            sx={{ 
              height: 'calc(100vh - 300px)',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Paper 
              elevation={1}
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid',
                borderColor: 'divider'
              }}
            >
              <ConversationStream
                interactions={interactions}
                onSendMessage={handleSendMessage || (() => console.error('❌ handleSendMessage nie jest dostępna!'))}
                isSendingMessage={isSendingMessage}
                conversationError={conversationError}
                currentClientId={clientId}
                currentSessionId={sessionId}
                currentSession={session}
                isLoading={loading || ultraBrainLoading}
                onNewInteraction={(interaction) => {
                  console.log('SessionDetail - nowa interakcja:', interaction);
                  // Odśwież sesję po dodaniu nowej interakcji
                  fetchSession();
                }}
                onSessionUpdate={fetchSession}
                onClientIdUpdate={() => {}}
                onSessionIdUpdate={() => {}}
                onArchetypesUpdate={setArchetypes}
                onInsightsUpdate={setStrategicInsights}
              />
            </Paper>
          </Grid>

          {/* 🧠⚡ PRAWA STRONA: Panel strategiczny (30%) */}
          <Grid 
            item 
            xs={12} 
            lg={3.5} 
            sx={{ 
              height: 'calc(100vh - 300px)',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Paper 
              elevation={1}
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid',
                borderColor: 'divider',
                bgcolor: 'background.paper'
              }}
            >
              <StrategicPanel
                // 🧠⚡ ULTRA MÓZG - Pełne dane psychometryczne
                data={{
                  quick_response_for_client: getQuickResponse(),
                  strategic_tip_for_seller: getStrategicRecommendation(),
                  knowledge_summary: dnaKlienta?.archetype_description || 'Profil w trakcie analizy...',
                  certainty_level: ultraBrainConfidence
                }}
                
                // 🧠⚡ NOWE - Pełne dane analizy z ostatniej interakcji
                analysis={{
                  // Dane z ostatniej interakcji (jeśli istnieje)
                  lastInteraction: interactions && interactions.length > 0 ? interactions[interactions.length - 1] : null,
                  // Pełna analiza AI
                  aiResponse: interactions && interactions.length > 0 ? interactions[interactions.length - 1]?.ai_response_json : null,
                  // Metryki
                  sentimentScore: interactions && interactions.length > 0 ? interactions[interactions.length - 1]?.ai_response_json?.sentiment_score : null,
                  potentialScore: interactions && interactions.length > 0 ? interactions[interactions.length - 1]?.ai_response_json?.potential_score : null,
                  urgencyLevel: interactions && interactions.length > 0 ? interactions[interactions.length - 1]?.ai_response_json?.urgency_level : null,
                  // Sugerowane pytania
                  suggestedQuestions: interactions && interactions.length > 0 ? interactions[interactions.length - 1]?.ai_response_json?.suggested_questions : [],
                  // Sygnały
                  buySignals: interactions && interactions.length > 0 ? interactions[interactions.length - 1]?.ai_response_json?.buy_signals : [],
                  riskSignals: interactions && interactions.length > 0 ? interactions[interactions.length - 1]?.ai_response_json?.risk_signals : [],
                  // Następne kroki
                  nextBestAction: interactions && interactions.length > 0 ? interactions[interactions.length - 1]?.ai_response_json?.next_best_action : null
                }}
                
                // LEGACY PROPS dla backward compatibility
                archetypes={archetypes}
                insights={strategicInsights}
                currentSession={session}
                currentInteractionId={lastInteractionId}
                isLoading={loading || ultraBrainLoading}
                
                // 🧠⚡ ULTRA MÓZG - Dodatkowe dane dla pełnej analizy
                ultraBrainData={{
                  dnaKlienta,
                  strategia,
                  surowePsychology,
                  isDnaReady,
                  isStrategiaReady,
                  isUltraBrainReady,
                  confidence: ultraBrainConfidence,
                  legacy: ultraBrainLegacy,
                  loading: ultraBrainLoading,
                  error: ultraBrainError,
                  isPolling: ultraBrainPolling
                }}
                
                // 🧠⚡ ULTRA MÓZG - Funkcje pomocnicze
                ultraBrainFunctions={{
                  getArchetypeName,
                  getMainDrive,
                  getCommunicationStyle,
                  getKeyLevers,
                  getRedFlags,
                  getStrategicRecommendation,
                  getQuickResponse,
                  getSuggestedQuestions,
                  getProactiveGuidance
                }}
              />
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
