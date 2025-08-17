/**
 * Strona dodawania nowego klienta
 * Formularz tworzenia nowego profilu klienta
 */
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Container,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
  Breadcrumbs,
  Chip,
  IconButton,
  InputAdornment,
  Divider,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Business as BusinessIcon,
  Work as WorkIcon,
  Psychology as PsychologyIcon,
  Label as LabelIcon,
  Notes as NotesIcon,
  NavigateNext as NavigateNextIcon,
} from '@mui/icons-material';
import MainLayout from '../components/MainLayout';
import { useCreateClient } from '../hooks/useClients';
import { getAvailableArchetypes } from '../services';

const AddClient = () => {
  const navigate = useNavigate();
  const { createClient, loading, error, validationErrors, clearErrors } = useCreateClient();
  
  // Stan formularza (tylko dane profilujące - alias generowany automatycznie przez backend)
  const [formData, setFormData] = useState({
    archetype: '',
    notes: '',
    tags: [],
  });

  const [tagInput, setTagInput] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Pobierz dostępne archetypy
  const archetypes = getAvailableArchetypes();

  // Obsługa zmiany pól formularza
  const handleChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
    // Wyczyść błąd dla tego pola
    if (validationErrors[field]) {
      clearErrors();
    }
  };

  // Obsługa dodawania tagów
  const handleAddTag = (event) => {
    if (event.key === 'Enter' && tagInput.trim()) {
      event.preventDefault();
      if (!formData.tags.includes(tagInput.trim())) {
        setFormData({
          ...formData,
          tags: [...formData.tags, tagInput.trim()],
        });
      }
      setTagInput('');
    }
  };

  // Obsługa usuwania tagów
  const handleDeleteTag = (tagToDelete) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(tag => tag !== tagToDelete),
    });
  };

  // Obsługa wysyłania formularza
  const handleSubmit = async (event) => {
    event.preventDefault();
    setSuccessMessage('');

    const result = await createClient(formData);
    
    if (result.success) {
      setSuccessMessage('Klient został pomyślnie dodany!');
      // Przekieruj do listy klientów po 2 sekundach
      setTimeout(() => {
        navigate('/');
      }, 2000);
    }
  };

  // Anulowanie i powrót
  const handleCancel = () => {
    navigate('/');
  };

  return (
    <MainLayout title="Dodaj Nowego Klienta">
      <Container maxWidth="md">
        {/* Breadcrumbs */}
        <Breadcrumbs 
          separator={<NavigateNextIcon fontSize="small" />}
          sx={{ mb: 3 }}
        >
          <Link 
            to="/"
            style={{ 
              color: 'inherit', 
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <Typography color="text.primary">Dashboard</Typography>
          </Link>
          <Typography color="text.primary">Dodaj Klienta</Typography>
        </Breadcrumbs>

        {/* Nagłówek */}
        <Box sx={{ mb: 4 }}>
          <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
            <IconButton onClick={handleCancel} size="large">
              <ArrowBackIcon />
            </IconButton>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 600 }}>
                Dodaj Nowego Klienta
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Wypełnij formularz, aby utworzyć nowy profil klienta
              </Typography>
            </Box>
          </Stack>
        </Box>

        {/* Komunikaty */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {successMessage && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {successMessage}
          </Alert>
        )}

        {/* Formularz */}
        <Paper sx={{ p: 4 }}>
          <form onSubmit={handleSubmit}>
            <Stack spacing={3}>
              {/* Sekcja: Profilowanie (jedyna pozostała sekcja) */}
              <Box>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PsychologyIcon color="primary" />
                  Profilowanie
                </Typography>
                <Divider sx={{ mb: 3 }} />
                
                <Stack spacing={3}>
                  {/* Archetyp */}
                  <FormControl fullWidth>
                    <InputLabel id="archetype-label">Archetyp klienta</InputLabel>
                    <Select
                      labelId="archetype-label"
                      value={formData.archetype}
                      onChange={handleChange('archetype')}
                      label="Archetyp klienta"
                      startAdornment={
                        <InputAdornment position="start">
                          <PsychologyIcon />
                        </InputAdornment>
                      }
                    >
                      <MenuItem value="">
                        <em>Nieprzypisany</em>
                      </MenuItem>
                      {archetypes.map((archetype) => (
                        <MenuItem key={archetype.value} value={archetype.value}>
                          <Box>
                            <Typography variant="body2">{archetype.label}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {archetype.description}
                            </Typography>
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                    <FormHelperText>Wybierz archetyp najlepiej opisujący klienta</FormHelperText>
                  </FormControl>

                  {/* Tagi */}
                  <Box>
                    <TextField
                      fullWidth
                      label="Dodaj tagi"
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyDown={handleAddTag}
                      placeholder="Wpisz tag i naciśnij Enter"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LabelIcon />
                          </InputAdornment>
                        ),
                      }}
                      helperText="Tagi pomagają w kategoryzacji i wyszukiwaniu klientów"
                    />
                    
                    {formData.tags.length > 0 && (
                      <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: 'wrap', gap: 1 }}>
                        {formData.tags.map((tag, index) => (
                          <Chip
                            key={index}
                            label={tag}
                            onDelete={() => handleDeleteTag(tag)}
                            color="primary"
                            variant="outlined"
                          />
                        ))}
                      </Stack>
                    )}
                  </Box>

                  {/* Notatki */}
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Notatki"
                    value={formData.notes}
                    onChange={handleChange('notes')}
                    placeholder="Dodatkowe informacje o kliencie..."
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start" sx={{ alignSelf: 'flex-start', mt: 1 }}>
                          <NotesIcon />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Stack>
              </Box>

              {/* Przyciski akcji */}
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', pt: 2 }}>
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<CancelIcon />}
                  onClick={handleCancel}
                  disabled={loading}
                >
                  Anuluj
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  startIcon={<SaveIcon />}
                  disabled={loading}
                >
                  {loading ? 'Zapisywanie...' : 'Zapisz klienta'}
                </Button>
              </Box>
            </Stack>
          </form>
        </Paper>

        {/* Podpowiedź */}
        <Card sx={{ mt: 3, backgroundColor: 'info.lighter' }}>
          <CardContent>
            <Typography variant="subtitle2" color="info.main" gutterBottom>
              💡 Wskazówka
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Im więcej informacji podasz o kliencie, tym lepiej AI będzie mogło dopasować strategie sprzedażowe.
              Archetyp klienta jest szczególnie ważny dla personalizacji sugestii.
            </Typography>
          </CardContent>
        </Card>
      </Container>
    </MainLayout>
  );
};

export default AddClient;
