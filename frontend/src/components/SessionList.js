/**
 * Komponent listy sesji
 * Wyświetla tabelę z danymi sesji pobranymi z API
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Badge,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  TextField,
  Tooltip,
  Typography,
  InputAdornment,
  Stack,
  Avatar,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  OutlinedInput,
  FormHelperText,
  TextareaAutosize,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  FilterList as FilterListIcon,
  Business as BusinessIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Person as PersonIcon,
  Psychology as PsychologyIcon,
  Chat as ChatIcon,
  CheckCircle as CheckCircleIcon,
  AccessTime as AccessTimeIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useSessions, useConcludeSession } from '../hooks/useSessionAnalytics';

// Mapowanie statusów na kolory
const statusColors = {
  'active': 'success',
  'closed': 'default',
  'completed': 'primary',
};

const SessionList = () => {
  // Stan lokalny
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [concludeModalOpen, setConcludeModalOpen] = useState(false);
  const [conclusionData, setConclusionData] = useState({
    outcome: '',
    notes: '',
    summary: ''
  });
  const [errors, setErrors] = useState({});

  // Użyj hooka do pobierania sesji
  const { sessions, loading, error, refresh } = useSessions();
  // Użyj hooka do finalizacji sesji
  const { concludeSession, loading: concludeLoading, error: concludeError, success } = useConcludeSession({
    onSuccess: () => {
      setConcludeModalOpen(false);
      setConclusionData({ outcome: '', notes: '', summary: '' });
      setErrors({});
      refresh(); // Odśwież listę sesji
    }
  });

  // Obsługa menu akcji
  const handleMenuOpen = (event, session) => {
    setAnchorEl(event.currentTarget);
    setSelectedSession(session);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedSession(null);
  };

  // Obsługa wyszukiwania
  const handleSearch = (event) => {
    const value = event.target.value;
    setSearchTerm(value);
    // TODO: Implement search functionality
  };

  // Obsługa zmiany strony
  const handleChangePage = (event, newPage) => {
    // TODO: Implement pagination
  };

  // Obsługa zmiany rozmiaru strony
  const handleChangeRowsPerPage = (event) => {
    // TODO: Implement page size change
  };

  // Obsługa sortowania
  const handleSort = (column) => {
    // TODO: Implement sorting
  };

  // Obsługa otwarcia modalu finalizacji
  const handleOpenConcludeModal = (session) => {
    setSelectedSession(session);
    setConcludeModalOpen(true);
    handleMenuClose();
  };

  // Obsługa zamknięcia modalu finalizacji
  const handleCloseConcludeModal = () => {
    setConcludeModalOpen(false);
    setSelectedSession(null);
    setConclusionData({ outcome: '', notes: '', summary: '' });
    setErrors({});
  };

  // Obsługa zmiany danych finalizacji
  const handleConclusionDataChange = (field, value) => {
    setConclusionData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  // Walidacja formularza
  const validateForm = () => {
    const newErrors = {};
    
    if (!conclusionData.outcome) {
      newErrors.outcome = 'Wynik sesji jest wymagany';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Obsługa przesłania formularza finalizacji
  const handleConcludeSubmit = async () => {
    if (!validateForm()) {
      return;
    }
    
    try {
      await concludeSession(selectedSession.id, conclusionData);
    } catch (err) {
      // Error is handled by the hook
      console.error('Error concluding session:', err);
    }
  };

  // Renderowanie stanu ładowania
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: 400,
        }}
      >
        <CircularProgress size={48} />
      </Box>
    );
  }

  // Renderowanie błędu
  if (error) {
    return (
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={refresh}>
            Spróbuj ponownie
          </Button>
        }
      >
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Nagłówek z akcjami */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
            Lista Sesji
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Zarządzaj sesjami i przeglądaj historię interakcji
          </Typography>
        </Box>
        
        <Stack direction="row" spacing={2}>
          <Button
            component={Link}
            to="/sessions/new"
            variant="contained"
            startIcon={<AddIcon />}
            size="large"
            sx={{ px: 3, textDecoration: 'none' }}
          >
            Rozpocznij Nową Sesję
          </Button>
        </Stack>
      </Box>

      {/* Pasek filtrów */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
          {/* Wyszukiwarka */}
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Szukaj sesji..."
            value={searchTerm}
            onChange={handleSearch}
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ maxWidth: { sm: 400 } }}
          />

          {/* Przyciski filtrów */}
          <Stack direction="row" spacing={1} sx={{ ml: 'auto' }}>
            <Tooltip title="Filtry">
              <IconButton>
                <Badge badgeContent={0} color="error">
                  <FilterListIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Odśwież">
              <IconButton disabled={loading} onClick={refresh}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>
      </Paper>

      {/* Statystyki */}
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>
              Wszystkie sesje
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>
              {sessions.length}
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>
              Aktywne sesje
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
              {sessions.filter(s => s.isActive).length}
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>
              Zakończone sesje
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 600, color: 'info.main' }}>
              {sessions.filter(s => !s.isActive).length}
            </Typography>
          </CardContent>
        </Card>
      </Stack>

      {/* Tabela sesji */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Sesja</TableCell>
              <TableCell>Klient</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>
                <TableSortLabel
                  active={false}
                  direction={'asc'}
                  onClick={() => handleSort('start_timestamp')}
                >
                  Data rozpoczęcia
                </TableSortLabel>
              </TableCell>
              <TableCell align="center">Akcje</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sessions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <Box sx={{ py: 8 }}>
                    <ChatIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      Brak sesji
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      Rozpocznij pierwszą sesję, aby rozpocząć
                    </Typography>
                    <Button 
                      component={Link}
                      to="/sessions/new"
                      variant="contained" 
                      startIcon={<AddIcon />}
                      sx={{ textDecoration: 'none' }}
                    >
                      Rozpocznij Sesję
                    </Button>
                  </Box>
                </TableCell>
              </TableRow>
            ) : (
              sessions.map((session) => {
                return (
                  <TableRow key={session.id} hover>
                    {/* Kolumna: Sesja */}
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32, fontSize: '0.75rem' }}>
                          S{session.id}
                        </Avatar>
                        <Typography 
                          component={Link}
                          to={`/sessions/${session.id}`}
                          variant="body2" 
                          sx={{ 
                            fontWeight: 500,
                            textDecoration: 'none',
                            color: 'primary.main',
                            '&:hover': {
                              textDecoration: 'underline'
                            }
                          }}
                        >
                          Sesja #{session.id}
                        </Typography>
                      </Box>
                    </TableCell>

                    {/* Kolumna: Klient */}
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32, fontSize: '0.75rem' }}>
                          {session.client_alias ? session.client_alias.charAt(0) : 'K'}
                        </Avatar>
                        <Typography 
                          component={Link}
                          to={`/clients/${session.client_id}`}
                          variant="body2" 
                          sx={{ 
                            fontWeight: 500,
                            textDecoration: 'none',
                            color: 'secondary.main',
                            '&:hover': {
                              textDecoration: 'underline'
                            }
                          }}
                        >
                          {session.client_alias || `Klient #${session.client_id}`}
                        </Typography>
                      </Box>
                    </TableCell>

                    {/* Kolumna: Status */}
                    <TableCell>
                      <Chip
                        icon={session.isActive ? <AccessTimeIcon /> : <CheckCircleIcon />}
                        label={session.isActive ? 'Aktywna' : 'Zakończona'}
                        size="small"
                        color={session.isActive ? 'success' : 'default'}
                        variant="outlined"
                      />
                    </TableCell>

                    {/* Kolumna: Data rozpoczęcia */}
                    <TableCell>
                      <Typography variant="body2">
                        {session.displayStartTime || new Date(session.start_timestamp).toLocaleDateString('pl-PL', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </Typography>
                    </TableCell>

                    {/* Kolumna: Akcje */}
                    <TableCell align="center">
                      <Stack direction="row" spacing={1} justifyContent="center">
                        <Tooltip title="Zobacz szczegóły">
                          <IconButton 
                            size="small"
                            component={Link}
                            to={`/sessions/${session.id}`}
                          >
                            <ChatIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {!session.isActive ? (
                          <Tooltip title="Sesja zakończona">
                            <IconButton size="small" disabled>
                              <CheckCircleIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        ) : (
                          <Tooltip title="Finalizuj sesję">
                            <IconButton
                              size="small"
                              onClick={(e) => handleOpenConcludeModal(session)}
                            >
                              <CloseIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Więcej opcji">
                          <IconButton
                            size="small"
                            onClick={(e) => handleMenuOpen(e, session)}
                          >
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>

        {/* Paginacja */}
        {sessions.length > 0 && (
          <TablePagination
            component="div"
            count={sessions.length}
            page={0}
            onPageChange={handleChangePage}
            rowsPerPage={10}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[5, 10, 25, 50]}
            labelRowsPerPage="Wierszy na stronę:"
            labelDisplayedRows={({ from, to, count }) =>
              `${from}-${to} z ${count !== -1 ? count : `więcej niż ${to}`}`
            }
          />
        )}
      </TableContainer>

      {/* Menu kontekstowe */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem 
          component={Link} 
          to={`/sessions/${selectedSession?.id}`}
          onClick={handleMenuClose}
        >
          <ChatIcon fontSize="small" sx={{ mr: 1 }} />
          Zobacz szczegóły
        </MenuItem>
        {selectedSession?.isActive && (
          <MenuItem onClick={() => handleOpenConcludeModal(selectedSession)}>
            <CloseIcon fontSize="small" sx={{ mr: 1 }} />
            Finalizuj sesję
          </MenuItem>
        )}
        <MenuItem onClick={handleMenuClose}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Edytuj
        </MenuItem>
        <MenuItem onClick={handleMenuClose} sx={{ color: 'error.main' }}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Usuń
        </MenuItem>
      </Menu>

      {/* Modal finalizacji sesji */}
      <Dialog open={concludeModalOpen} onClose={handleCloseConcludeModal} maxWidth="sm" fullWidth>
        <DialogTitle>
          Finalizuj sesję #{selectedSession?.id}
          <IconButton
            aria-label="close"
            onClick={handleCloseConcludeModal}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {concludeError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {concludeError}
            </Alert>
          )}
          
          <Box sx={{ pt: 1 }}>
            <FormControl fullWidth sx={{ mb: 2 }} error={!!errors.outcome}>
              <InputLabel id="outcome-label">Wynik sesji *</InputLabel>
              <Select
                labelId="outcome-label"
                value={conclusionData.outcome}
                label="Wynik sesji *"
                onChange={(e) => handleConclusionDataChange('outcome', e.target.value)}
              >
                <MenuItem value="interested">Zainteresowany</MenuItem>
                <MenuItem value="needs_time">Potrzebuje czasu</MenuItem>
                <MenuItem value="not_interested">Niezainteresowany</MenuItem>
                <MenuItem value="closed_deal">Transakcja zamknięta</MenuItem>
                <MenuItem value="follow_up_needed">Wymaga kontaktu</MenuItem>
              </Select>
              {errors.outcome && <FormHelperText>{errors.outcome}</FormHelperText>}
            </FormControl>
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <TextField
                label="Notatki"
                multiline
                rows={3}
                value={conclusionData.notes}
                onChange={(e) => handleConclusionDataChange('notes', e.target.value)}
                variant="outlined"
              />
            </FormControl>
            
            <FormControl fullWidth>
              <TextField
                label="Podsumowanie"
                multiline
                rows={4}
                value={conclusionData.summary}
                onChange={(e) => handleConclusionDataChange('summary', e.target.value)}
                variant="outlined"
              />
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseConcludeModal}>Anuluj</Button>
          <Button 
            onClick={handleConcludeSubmit} 
            variant="contained" 
            disabled={concludeLoading}
          >
            {concludeLoading ? <CircularProgress size={24} /> : 'Finalizuj'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SessionList;