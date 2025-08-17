/**
 * Strona tworzenia nowej sesji dla klienta
 * Pełnofunkcjonalny formularz z integracją API
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  Chip,
  Breadcrumbs,
  CircularProgress,
  Alert,
  Avatar,
  Divider,
  Stack,
} from '@mui/material';
import {
  Save as SaveIcon,
  ArrowBack as ArrowBackIcon,
  Person as PersonIcon,
  Chat as ChatIcon,
  Phone as PhoneIcon,
  Business as HandshakeIcon,
  Slideshow as PresentationIcon,
  CheckCircle as CheckCircleIcon,
  Notes as NotesIcon,
  LocalOffer as LocalOfferIcon,
} from '@mui/icons-material';
import MainLayout from '../components/MainLayout';
import { useClient } from '../hooks/useClients';
import { useCreateSession } from '../hooks/useSessions';
import { getAvailableSessionTypes } from '../services';

// Mapowanie typów sesji na ikony (takie samo jak w SessionList)
const sessionTypeIcons = {
  consultation: <ChatIcon />,
  'follow-up': <PhoneIcon />,
  negotiation: <HandshakeIcon />,
  demo: <PresentationIcon />,
  closing: <CheckCircleIcon />,
};

// Funkcja do generowania inicjałów z aliasu (taka sama jak w ClientDetail)
const getInitials = (alias) => {
  if (!alias) return '?';
  const matches = alias.match(/Klient #(\d+)/);
  if (matches) {
    return `K${matches[1]}`;
  }
  return alias.substring(0, 2).toUpperCase();
};

// Domyślne tagi do sugestii
const suggestedTags = [
  'pierwsza rozmowa',
  'kontynuacja',
  'pilne',
  'zainteresowany',
  'wątpliwości',
  'konkurencja',
  'budżet',
  'decyzja',
  'techniczne',
  'prezentacja',
  'demo',
  'negocjacje',
  'finalizacja',
  'follow-up',
];

const NewSession = () => {
  const { clientId } = useParams();
  const navigate = useNavigate();
  
  // Hooks dla danych i logiki
  const { client, loading: clientLoading, error: clientError, fetchClient } = useClient(clientId);
  const { 
    createNewSession, 
    loading: sessionLoading, 
    error: sessionError, 
    validationErrors,
    success,
    resetState
  } = useCreateSession({
    onSuccess: (newSession) => {
      console.log('Sesja utworzona pomyślnie:', newSession);
    }
  });

  // Stan formularza
  const [formData, setFormData] = useState({
    session_type: 'consultation', // Domyślny typ
    notes: '',
    tags: [],
  });

  const [tagInput, setTagInput] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Dostępne typy sesji
  const sessionTypes = getAvailableSessionTypes();

  // Pobranie danych klienta przy pierwszym renderowaniu
  useEffect(() => {
    if (clientId) {
      fetchClient();
    }
  }, [clientId, fetchClient]);

  // Obsługa sukcesu tworzenia sesji
  useEffect(() => {
    if (success) {
      setSuccessMessage('Sesja została pomyślnie rozpoczęta! Przekierowuję...');
      
      // Przekierowanie po 2 sekundach na stronę klienta
      setTimeout(() => {
        navigate(`/clients/${clientId}`);
      }, 2000);
    }
  }, [success, navigate, clientId]);

  // Reset błędów przy zmianie danych formularza
  useEffect(() => {
    if (sessionError || Object.keys(validationErrors).length > 0) {
      const timer = setTimeout(() => {
        resetState();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [formData, sessionError, validationErrors, resetState]);

  // Obsługa zmian w formularzu
  const handleChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
  };

  // Obsługa dodawania tagów
  const handleTagsChange = (event, newTags) => {
    setFormData({
      ...formData,
      tags: newTags,
    });
  };

  // Obsługa submit formularza
  const handleSubmit = async (event) => {
    event.preventDefault();
    setSuccessMessage('');

    // Przygotowanie danych do wysłania
    const sessionData = {
      session_type: formData.session_type,
      notes: formData.notes.trim() || null,
      tags: formData.tags.length > 0 ? formData.tags : null,
    };

    // Utworzenie sesji
    const result = await createNewSession(clientId, sessionData);
    
    if (result.success) {
      console.log('Sesja utworzona:', result.data);
    }
  };

  // Loading state dla danych klienta
  if (clientLoading) {
    return (
      <MainLayout title="Ładowanie...">
        <Box 
          display="flex" 
          justifyContent="center" 
          alignItems="center" 
          minHeight="50vh"
        >
          <CircularProgress size={60} />
        </Box>
      </MainLayout>
    );
  }

  // Error state dla danych klienta
  if (clientError || !client) {
    return (
      <MainLayout title="Błąd">
        <Box sx={{ py: 3 }}>
          <Alert 
            severity="error" 
            sx={{ mb: 3 }}
            action={
              <Button color="inherit" onClick={() => navigate(`/clients/${clientId}`)}>
                Powrót do klienta
              </Button>
            }
          >
            {clientError || `Nie udało się pobrać danych klienta o ID ${clientId}`}
          </Alert>
        </Box>
      </MainLayout>
    );
  }

  const initials = getInitials(client.alias);
  const selectedSessionType = sessionTypes.find(type => type.value === formData.session_type);

  return (
    <MainLayout title={`Nowa Sesja - ${client.alias}`}>
      <Box sx={{ py: 3 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
          <Link 
            component={Link} 
            to="/" 
            color="inherit" 
            underline="hover"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            Dashboard
          </Link>
          <Link 
            component={Link} 
            to={`/clients/${client.id}`}
            color="inherit" 
            underline="hover"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            <PersonIcon fontSize="small" />
            {client.alias}
          </Link>
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {sessionTypeIcons[formData.session_type] || <ChatIcon />}
            Nowa Sesja
          </Typography>
        </Breadcrumbs>

        {/* Przycisk powrotu */}
        <Button
          component={Link}
          to={`/clients/${clientId}`}
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 3 }}
        >
          Powrót do profilu klienta
        </Button>

        {/* Komunikaty o sukcesie */}
        {successMessage && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {successMessage}
          </Alert>
        )}

        {/* Główny formularz */}
        <Grid container spacing={3}>
          {/* Kolumna formularza */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4 }}>
              {/* Header z klientem */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 4 }}>
                <Avatar 
                  sx={{ 
                    bgcolor: 'primary.main', 
                    width: 64, 
                    height: 64,
                    fontSize: '1.25rem',
                    fontWeight: 600
                  }}
                >
                  {initials}
                </Avatar>
                <Box>
                  <Typography variant="h5" component="h1" gutterBottom>
                    Nowa sesja dla: {client.alias}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary">
                    {client.archetype && `Archetyp: ${client.archetype}`}
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ mb: 4 }} />

              {/* Formularz */}
              <form onSubmit={handleSubmit}>
                <Stack spacing={4}>
                  {/* Typ sesji */}
                  <FormControl fullWidth error={!!validationErrors.session_type}>
                    <InputLabel>Typ Sesji</InputLabel>
                    <Select
                      value={formData.session_type}
                      label="Typ Sesji"
                      onChange={handleChange('session_type')}
                      startAdornment={
                        <Box sx={{ display: 'flex', alignItems: 'center', mr: 1 }}>
                          {sessionTypeIcons[formData.session_type] || <ChatIcon />}
                        </Box>
                      }
                    >
                      {sessionTypes.map((type) => (
                        <MenuItem key={type.value} value={type.value}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {sessionTypeIcons[type.value] || <ChatIcon />}
                            <Typography>{type.label}</Typography>
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                    {validationErrors.session_type && (
                      <Typography variant="caption" color="error" sx={{ mt: 1 }}>
                        {validationErrors.session_type}
                      </Typography>
                    )}
                  </FormControl>

                  {/* Opis wybranego typu sesji */}
                  {selectedSessionType && (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        <strong>{selectedSessionType.label}</strong>
                        {selectedSessionType.description && ` - ${selectedSessionType.description}`}
                      </Typography>
                    </Alert>
                  )}

                  {/* Tagi początkowe */}
                  <Box>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LocalOfferIcon color="primary" />
                      Tagi Początkowe
                    </Typography>
                    
                    <Autocomplete
                      multiple
                      freeSolo
                      options={suggestedTags}
                      value={formData.tags}
                      onChange={handleTagsChange}
                      renderTags={(value, getTagProps) =>
                        value.map((option, index) => (
                          <Chip
                            variant="outlined"
                            label={option}
                            {...getTagProps({ index })}
                            key={index}
                          />
                        ))
                      }
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Dodaj tagi (wpisz i naciśnij Enter)"
                          placeholder="np. pierwsza rozmowa, pilne, zainteresowany"
                          error={!!validationErrors.tags}
                          helperText={
                            validationErrors.tags || 
                            'Dodaj tagi opisujące kontekst lub cel sesji'
                          }
                        />
                      )}
                      sx={{ mt: 1 }}
                    />
                  </Box>

                  {/* Notatki początkowe */}
                  <Box>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <NotesIcon color="primary" />
                      Notatki Początkowe
                    </Typography>
                    
                    <TextField
                      fullWidth
                      multiline
                      rows={6}
                      value={formData.notes}
                      onChange={handleChange('notes')}
                      label="Opisz cel sesji, kluczowe punkty do omówienia..."
                      placeholder="Przykład:&#10;- Prezentacja funkcjonalności X&#10;- Omówienie budżetu&#10;- Odpowiedź na zastrzeżenia co do...&#10;- Ustalenie następnych kroków"
                      error={!!validationErrors.notes}
                      helperText={validationErrors.notes || 'Opcjonalne, ale zalecane dla lepszego przygotowania'}
                      sx={{ mt: 1 }}
                    />
                  </Box>

                  {/* Przyciski akcji */}
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 4 }}>
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={() => navigate(`/clients/${clientId}`)}
                      disabled={sessionLoading}
                    >
                      Anuluj
                    </Button>
                    <Button
                      type="submit"
                      variant="contained"
                      size="large"
                      startIcon={sessionLoading ? <CircularProgress size={20} /> : <SaveIcon />}
                      disabled={sessionLoading}
                      sx={{ minWidth: 200 }}
                    >
                      {sessionLoading ? 'Tworzenie...' : 'Zapisz i rozpocznij'}
                    </Button>
                  </Box>
                </Stack>
              </form>

              {/* Błędy formularza */}
              {sessionError && (
                <Alert severity="error" sx={{ mt: 3 }}>
                  Błąd podczas tworzenia sesji: {sessionError}
                </Alert>
              )}
            </Paper>
          </Grid>

          {/* Sidebar z informacjami o kliencie */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Kontekst Klienta
              </Typography>
              
              <Stack spacing={2} sx={{ mt: 2 }}>
                {/* Archetyp */}
                {client.archetype && (
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Archetyp:
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {client.archetype}
                    </Typography>
                  </Box>
                )}

                {/* Tagi klienta */}
                {client.tags && client.tags.length > 0 && (
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Tagi profilujące:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {client.tags.map((tag) => (
                        <Chip key={tag} label={tag} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Notatki */}
                {client.notes && (
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Notatki analityczne:
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontStyle: 'italic',
                        maxHeight: 100,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis'
                      }}
                    >
                      {client.notes.length > 150 
                        ? `${client.notes.substring(0, 150)}...` 
                        : client.notes
                      }
                    </Typography>
                  </Box>
                )}

                {/* Data utworzenia */}
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Klient od:
                  </Typography>
                  <Typography variant="body2">
                    {new Date(client.created_at).toLocaleDateString('pl-PL', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </Typography>
                </Box>
              </Stack>
            </Paper>

            {/* Wskazówki */}
            <Paper sx={{ p: 3, mt: 2, bgcolor: 'grey.50' }}>
              <Typography variant="h6" gutterBottom color="primary">
                💡 Wskazówki
              </Typography>
              
              <Stack spacing={1} sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  • <strong>Typ sesji</strong> pomoże w organizacji rozmowy
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • <strong>Tagi</strong> ułatwią późniejsze wyszukiwanie
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • <strong>Notatki</strong> przygotują Cię mentalnie do rozmowy
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Pamiętaj o <strong>archetyp klienta</strong> podczas rozmowy
                </Typography>
              </Stack>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </MainLayout>
  );
};

export default NewSession;
