/**
 * Strona szczegółów klienta
 * Wyświetla pełne dane profilujące dla wybranego klienta
 */
import React, { useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Divider,
  Breadcrumbs,
  CircularProgress,
  Alert,
  Avatar,
  Card,
  CardContent,
  Button,
  Tooltip,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  LocalOffer as LocalOfferIcon,
  Notes as NotesIcon,
  ArrowBack as ArrowBackIcon,
  CalendarToday as CalendarTodayIcon,
  Person as PersonIcon,
  AddCircleOutline as AddCircleOutlineIcon,
} from '@mui/icons-material';
import MainLayout from '../components/MainLayout';
import SessionList from '../components/SessionList';
import { useClient } from '../hooks/useClients';
import { getAvailableArchetypes } from '../services/clientsApi';

// Kolory dla różnych archetypów (takie same jak w ClientList)
const archetypeColors = {
  'Zdobywca Statusu': 'primary',
  'Strażnik Rodziny': 'success', 
  'Pragmatyczny Analityk': 'info',
  'Eko-Entuzjasta': 'success',
  'Pionier Technologii': 'secondary',
  'Techniczny Sceptyk': 'warning',
  'Lojalista Premium': 'primary',
  'Łowca Okazji': 'warning',
  'Niezdecydowany Odkrywca': 'default',
  'Entuzjasta Osiągów': 'error'
};

// Funkcja do generowania inicjałów z aliasu
const getInitials = (alias) => {
  if (!alias) return '?';
  // Dla "Klient #N" zwróć pierwszą literę i numer
  const matches = alias.match(/Klient #(\d+)/);
  if (matches) {
    return `K${matches[1]}`;
  }
  // Fallback dla innych formatów
  return alias.substring(0, 2).toUpperCase();
};

const ClientDetail = () => {
  const { clientId } = useParams();
  const navigate = useNavigate();
  const { client, loading, error, fetchClient } = useClient(clientId);

  // Pobranie danych przy pierwszym renderowaniu
  useEffect(() => {
    fetchClient();
  }, [fetchClient]);

  // Funkcja do znajdowania opisu archetypu
  const getArchetypeDescription = (archetypeValue) => {
    const archetypes = getAvailableArchetypes();
    const archetype = archetypes.find(a => a.value === archetypeValue);
    return archetype?.description || '';
  };

  // Loading state
  if (loading) {
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

  // Error state
  if (error) {
    return (
      <MainLayout title="Błąd">
        <Box sx={{ py: 3 }}>
          <Alert 
            severity="error" 
            sx={{ mb: 3 }}
            action={
              <Button color="inherit" onClick={() => navigate('/')}>
                Powrót do listy
              </Button>
            }
          >
            {error}
          </Alert>
        </Box>
      </MainLayout>
    );
  }

  // Not found state
  if (!client) {
    return (
      <MainLayout title="Nie znaleziono">
        <Box sx={{ py: 3 }}>
          <Alert 
            severity="warning"
            sx={{ mb: 3 }}
            action={
              <Button color="inherit" onClick={() => navigate('/')}>
                Powrót do listy
              </Button>
            }
          >
            Klient o ID {clientId} nie został znaleziony.
          </Alert>
        </Box>
      </MainLayout>
    );
  }

  const initials = getInitials(client.alias);
  const archetypeColor = archetypeColors[client.archetype] || 'default';
  const archetypeDescription = getArchetypeDescription(client.archetype);

  return (
    <MainLayout title={`Szczegóły - ${client.alias}`}>
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
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <PersonIcon fontSize="small" />
            {client.alias}
          </Typography>
        </Breadcrumbs>

        {/* Przycisk powrotu */}
        <Button
          component={Link}
          to="/"
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 3 }}
        >
          Powrót do listy klientów
        </Button>

        <Grid container spacing={3}>
          {/* Główna karta klienta */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4 }}>
              {/* Header z avatarem, nazwą i przyciskiem akcji */}
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                  <Avatar 
                    sx={{ 
                      bgcolor: 'primary.main', 
                      width: 80, 
                      height: 80,
                      fontSize: '1.5rem',
                      fontWeight: 600
                    }}
                  >
                    {initials}
                  </Avatar>
                  <Box>
                    <Typography variant="h4" component="h1" gutterBottom>
                      {client.alias}
                    </Typography>
                    <Typography variant="subtitle1" color="text.secondary">
                      ID: {client.id}
                    </Typography>
                  </Box>
                </Box>
                
                {/* Przycisk Call to Action */}
                <Button
                  component={Link}
                  to={`/clients/${client.id}/sessions/new`}
                  variant="contained"
                  size="large"
                  startIcon={<AddCircleOutlineIcon />}
                  sx={{ 
                    minWidth: 200,
                    height: 48,
                    fontWeight: 600
                  }}
                >
                  Rozpocznij Nową Sesję
                </Button>
              </Box>

              <Divider sx={{ mb: 4 }} />

              {/* Archetyp */}
              <Box sx={{ mb: 4 }}>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}
                >
                  <PsychologyIcon color="primary" />
                  Archetyp Psychologiczny
                </Typography>
                
                {client.archetype ? (
                  <Box>
                    <Chip
                      icon={<PsychologyIcon />}
                      label={client.archetype}
                      color={archetypeColor}
                      variant="filled"
                      size="large"
                      sx={{ 
                        mb: 2,
                        fontSize: '1rem',
                        height: 40,
                        '& .MuiChip-label': {
                          px: 2
                        }
                      }}
                    />
                    {archetypeDescription && (
                      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                        {archetypeDescription}
                      </Typography>
                    )}
                  </Box>
                ) : (
                  <Typography variant="body1" color="text.secondary">
                    Brak przypisanego archetypu
                  </Typography>
                )}
              </Box>

              <Divider sx={{ mb: 4 }} />

              {/* Tagi */}
              <Box sx={{ mb: 4 }}>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}
                >
                  <LocalOfferIcon color="primary" />
                  Tagi Profilujące
                </Typography>
                
                {client.tags && client.tags.length > 0 ? (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {client.tags.map((tag, index) => (
                      <Chip
                        key={index}
                        label={tag}
                        variant="outlined"
                        color="secondary"
                        size="medium"
                      />
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body1" color="text.secondary">
                    Brak przypisanych tagów
                  </Typography>
                )}
              </Box>

              <Divider sx={{ mb: 4 }} />

              {/* Notatki */}
              <Box>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}
                >
                  <NotesIcon color="primary" />
                  Notatki Analityczne
                </Typography>
                
                {client.notes ? (
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 3, 
                      bgcolor: 'grey.50',
                      border: '1px solid',
                      borderColor: 'grey.200'
                    }}
                  >
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.6
                      }}
                    >
                      {client.notes}
                    </Typography>
                  </Paper>
                ) : (
                  <Typography variant="body1" color="text.secondary">
                    Brak notatek analitycznych
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>

          {/* Sidebar z informacjami systemowymi */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CalendarTodayIcon color="primary" />
                  Informacje Systemowe
                </Typography>
                
                <Box sx={{ mt: 2, '& > *': { mb: 2 } }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Data utworzenia:
                    </Typography>
                    <Typography variant="body1">
                      {new Date(client.created_at).toLocaleDateString('pl-PL', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </Typography>
                  </Box>

                  {client.updated_at && client.updated_at !== client.created_at && (
                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Ostatnia aktualizacja:
                      </Typography>
                      <Typography variant="body1">
                        {new Date(client.updated_at).toLocaleDateString('pl-PL', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </Typography>
                    </Box>
                  )}

                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Identyfikator:
                    </Typography>
                    <Typography variant="body1" sx={{ fontFamily: 'monospace', fontSize: '0.9rem' }}>
                      #{client.id}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* Lista sesji klienta */}
            <Box sx={{ mt: 2 }}>
              <SessionList 
                clientId={client.id} 
                maxItems={5}
                showHeader={true}
              />
            </Box>
          </Grid>
        </Grid>
      </Box>
    </MainLayout>
  );
};

export default ClientDetail;
