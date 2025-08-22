/**
 * AdminBrainInterface - Interfejs administracyjny AI Dojo
 * 
 * Moduł 3: Interaktywne AI Dojo "Sparing z Mistrzem"
 * 
 * Strona umożliwia administratorom i ekspertom:
 * - Prowadzenie interaktywnej konwersacji treningowej z AI
 * - Przekazywanie nowej wiedzy sprzedażowej
 * - Korygowanie błędów i nieścisłości AI
 * - Zatwierdzanie i zapisywanie strukturalnych danych w bazie Qdrant
 */
import React, { useState, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Alert,
  Tabs,
  Tab,
  Paper,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Stack,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  School as SchoolIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import MainLayout from '../components/MainLayout';
import DojoChat from '../components/dojo/DojoChat';
import { useDojoAnalytics } from '../hooks/useDojoChat';
import { TRAINING_MODES } from '../services/dojoApi';

/**
 * Główny komponent interfejsu administracyjnego AI Dojo
 */
const AdminBrainInterface = () => {
  // === STATE ===
  const [activeTab, setActiveTab] = useState(0);
  const [expertName, setExpertName] = useState('Administrator');
  const [trainingMode, setTrainingMode] = useState(TRAINING_MODES.KNOWLEDGE_UPDATE);
  const [showInfoDialog, setShowInfoDialog] = useState(false);
  const [notification, setNotification] = useState(null);

  // === ANALYTICS HOOK ===
  const { analytics, loading: analyticsLoading, error: analyticsError, refresh: refreshAnalytics } = useDojoAnalytics();

  // === HANDLERS ===
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleDojoError = useCallback((error) => {
    console.error('❌ AdminBrainInterface: Dojo error:', error);
    setNotification({
      type: 'error',
      message: `Błąd AI Dojo: ${error.message}`
    });
  }, []);

  const handleDojoSuccess = useCallback((response) => {
    console.log('✅ AdminBrainInterface: Dojo success:', response);
    
    if (response.response_type === 'confirmation') {
      setNotification({
        type: 'info',
        message: 'AI przygotował dane do zapisu. Sprawdź i zatwierdź.'
      });
    } else if (response.response_type === 'status') {
      setNotification({
        type: 'success',
        message: 'Operacja zakończona pomyślnie.'
      });
    }
  }, []);

  const clearNotification = () => {
    setNotification(null);
  };

  // === RENDER METHODS ===

  const renderHeader = () => (
    <Box mb={3}>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Box display="flex" alignItems="center" gap={2}>
          <PsychologyIcon sx={{ fontSize: 40, color: 'primary.main' }} />
          <Box>
            <Typography variant="h4" component="h1" color="primary">
              AI Dojo: Sparing z Mistrzem
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Interaktywne środowisko treningowe Tesla Co-Pilot AI
            </Typography>
          </Box>
        </Box>
        <Box display="flex" gap={1}>
          <Tooltip title="Informacje o AI Dojo">
            <IconButton onClick={() => setShowInfoDialog(true)}>
              <InfoIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Odśwież statystyki">
            <IconButton onClick={refreshAnalytics} disabled={analyticsLoading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Notification */}
      {notification && (
        <Alert 
          severity={notification.type} 
          onClose={clearNotification}
          sx={{ mb: 2 }}
        >
          {notification.message}
        </Alert>
      )}

      {/* Status Line */}
      <Box display="flex" alignItems="center" gap={2} p={2} bgcolor="background.paper" borderRadius={1}>
        <Chip 
          icon={<SchoolIcon />} 
          label={`Ekspert: ${expertName}`} 
          color="primary" 
          variant="outlined"
        />
        <Chip 
          label={getTrainingModeLabel(trainingMode)} 
          color="secondary"
          variant="outlined" 
        />
        {analytics && (
          <Chip 
            icon={analytics.active_sessions > 0 ? <SuccessIcon /> : <InfoIcon />}
            label={`Aktywne sesje: ${analytics.active_sessions}`}
            color={analytics.active_sessions > 0 ? 'success' : 'default'}
            variant="outlined"
          />
        )}
      </Box>
    </Box>
  );

  const renderTabs = () => (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
      <Tabs value={activeTab} onChange={handleTabChange}>
        <Tab 
          icon={<PsychologyIcon />} 
          iconPosition="start"
          label="Trening AI" 
        />
        <Tab 
          icon={<AnalyticsIcon />} 
          iconPosition="start"
          label="Analityka" 
        />
        <Tab 
          icon={<SettingsIcon />} 
          iconPosition="start"
          label="Ustawienia" 
        />
      </Tabs>
    </Box>
  );

  const renderTrainingTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <DojoChat
          expertName={expertName}
          trainingMode={trainingMode}
          onError={handleDojoError}
          onSuccess={handleDojoSuccess}
          sx={{ height: '70vh' }}
        />
      </Grid>
    </Grid>
  );

  const renderAnalyticsTab = () => (
    <Grid container spacing={3}>
      {/* Quick Stats */}
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>
              Aktywne Sesje
            </Typography>
            <Typography variant="h4">
              {analyticsLoading ? '...' : analytics?.active_sessions || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>
              Łączne Sesje
            </Typography>
            <Typography variant="h4">
              {analyticsLoading ? '...' : analytics?.total_sessions || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>
              Status Systemu
            </Typography>
            <Chip 
              label={analyticsLoading ? 'Ładowanie...' : analytics?.system_status || 'Nieznany'}
              color={analytics?.system_status === 'operational' ? 'success' : 'warning'}
            />
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>
              Ostatnia Aktualizacja
            </Typography>
            <Typography variant="body2">
              {analyticsLoading ? 'Ładowanie...' : formatTimestamp(analytics?.last_updated)}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Features Status */}
      <Grid item xs={12}>
        <Card>
          <CardHeader title="Status Funkcji" />
          <CardContent>
            {analyticsError ? (
              <Alert severity="error">
                Błąd podczas pobierania danych: {analyticsError}
              </Alert>
            ) : (
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {analytics?.features ? Object.entries(analytics.features).map(([feature, enabled]) => (
                  <Chip
                    key={feature}
                    label={formatFeatureName(feature)}
                    color={enabled ? 'success' : 'error'}
                    icon={enabled ? <SuccessIcon /> : <ErrorIcon />}
                    variant={enabled ? 'filled' : 'outlined'}
                  />
                )) : (
                  <Typography color="text.secondary">
                    Brak danych o funkcjach
                  </Typography>
                )}
              </Stack>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderSettingsTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Konfiguracja Eksperta" />
          <CardContent>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Ustawienia będą dostępne w przyszłych wersjach
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Preferencje Treningu" />
          <CardContent>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Zaawansowane opcje treningowe będą dodane
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderInfoDialog = () => (
    <Dialog open={showInfoDialog} onClose={() => setShowInfoDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <PsychologyIcon color="primary" />
          Informacje o AI Dojo
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body1" gutterBottom>
          <strong>AI Dojo: Sparing z Mistrzem</strong> to zaawansowane narzędzie do interaktywnego treningu Tesla Co-Pilot AI.
        </Typography>
        
        <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>
          🎯 Główne Funkcje:
        </Typography>
        <Box component="ul" sx={{ pl: 2 }}>
          <li><Typography variant="body2">Przekazywanie nowej wiedzy sprzedażowej do AI</Typography></li>
          <li><Typography variant="body2">Korygowanie błędów i nieścisłości w odpowiedziach AI</Typography></li>
          <li><Typography variant="body2">Interaktywny dialog z możliwością zadawania pytań doprecyzowujących</Typography></li>
          <li><Typography variant="body2">Automatyczne strukturyzowanie i zapisywanie wiedzy w bazie Qdrant</Typography></li>
        </Box>

        <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>
          🔧 Jak używać:
        </Typography>
        <Box component="ol" sx={{ pl: 2 }}>
          <li><Typography variant="body2">Napisz wiadomość z nową wiedzą lub komentarzem</Typography></li>
          <li><Typography variant="body2">AI może zadać pytania doprecyzowujące</Typography></li>
          <li><Typography variant="body2">Gdy AI przygotuje dane, zatwierdź ich zapis do bazy</Typography></li>
          <li><Typography variant="body2">Wiedza będzie automatycznie dostępna w systemie sprzedażowym</Typography></li>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowInfoDialog(false)}>
          Zamknij
        </Button>
      </DialogActions>
    </Dialog>
  );

  // === MAIN RENDER ===
  return (
    <MainLayout>
      <Box sx={{ p: 3 }}>
        {renderHeader()}
        {renderTabs()}
        
        {/* Tab Content */}
        <Box>
          {activeTab === 0 && renderTrainingTab()}
          {activeTab === 1 && renderAnalyticsTab()}
          {activeTab === 2 && renderSettingsTab()}
        </Box>

        {renderInfoDialog()}
      </Box>
    </MainLayout>
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

const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'Nieznany';
  
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('pl-PL', {
      day: '2-digit',
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    return timestamp;
  }
};

const formatFeatureName = (feature) => {
  const names = {
    ai_training: 'Trening AI',
    knowledge_storage: 'Baza wiedzy',
    session_management: 'Zarządzanie sesjami',
    analytics: 'Analityka'
  };
  return names[feature] || feature;
};

export default AdminBrainInterface;
