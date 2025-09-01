/**
 * Komponent listy klientów
 * Wyświetla tabelę z danymi klientów pobranymi z API
 */
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
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
  Badge,
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
} from '@mui/icons-material';
import { useClientsList } from '../hooks/useClients';

// Mapowanie archetypów na kolory
const archetypeColors = {
  'Zdobywca Statusu': 'primary',
  'Strażnik Rodziny': 'success',
  'Pragmatyczny Analityk': 'info',
  'Eko-Entuzjasta': 'success',
  'Pionier Technologii': 'secondary',
  'Techniczny Sceptyk': 'warning',
  'Lojalista Premium': 'primary',
  'Łowca Okazji': 'error',
  'Niezdecydowany Odkrywca': 'default',
  'Entuzjasta Osiągów': 'secondary',
};

// Funkcja do generowania inicjałów
const getInitials = (name) => {
  const names = name.split(' ');
  if (names.length >= 2) {
    return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
  }
  return name.substring(0, 2).toUpperCase();
};

// Funkcja do określenia typu kontaktu (email/telefon)
const getContactType = (contact) => {
  if (contact.includes('@')) return 'email';
  if (contact.match(/^\+?\d[\d\s-]+$/)) return 'phone';
  return 'other';
};

const ClientList = ({ 
  clients: externalClients, 
  isLoading: externalLoading, 
  error: externalError,
  onSortChange 
}) => {
  // Hook do zarządzania listą klientów (fallback)
  const {
    clients: hookClients,
    loading: hookLoading,
    error: hookError,
    pagination,
    filters,
    changePage,
    changePageSize,
    changeSort,
    applyFilters,
    refresh,
    hasClients,
    isEmpty,
  } = useClientsList();

  // Użyj zewnętrznych props lub fallback do hooka
  const clients = externalClients || hookClients;
  const loading = externalLoading !== undefined ? externalLoading : hookLoading;
  const error = externalError !== undefined ? externalError : hookError;

  // Stan lokalny
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedClient, setSelectedClient] = useState(null);

  // Obsługa menu akcji
  const handleMenuOpen = (event, client) => {
    setAnchorEl(event.currentTarget);
    setSelectedClient(client);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedClient(null);
  };

  // Obsługa wyszukiwania
  const handleSearch = (event) => {
    const value = event.target.value;
    setSearchTerm(value);
    
    // Debounce - aplikuj filtr po zatrzymaniu pisania
    if (value.length >= 2 || value === '') {
      setTimeout(() => {
        applyFilters({ search: value });
      }, 300);
    }
  };

  // Obsługa zmiany strony
  const handleChangePage = (event, newPage) => {
    changePage(newPage + 1); // MUI używa indeksowania od 0
  };

  // Obsługa zmiany rozmiaru strony
  const handleChangeRowsPerPage = (event) => {
    changePageSize(parseInt(event.target.value, 10));
  };

  // Obsługa sortowania
  const handleSort = (column) => {
    if (onSortChange) {
      onSortChange({ column, direction: 'asc' }); // Przykład
    } else {
      changeSort(column); // Fallback do hooka
    }
  };

  // Renderowanie stanu ładowania
  if (loading && !hasClients) {
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
            Lista Klientów
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Zarządzaj bazą klientów i przeglądaj ich profile
          </Typography>
        </Box>
        
        <Stack direction="row" spacing={2}>
          <Button
            component={Link}
            to="/analysis/new"
            variant="contained"
            startIcon={<ChatIcon />}
            size="large"
            sx={{ px: 3, textDecoration: 'none' }}
          >
            Rozpocznij Nową Analizę
          </Button>
          <Button
            component={Link}
            to="/clients/new"
            variant="outlined"
            startIcon={<AddIcon />}
            size="large"
            sx={{ px: 3, textDecoration: 'none' }}
          >
            Dodaj Klienta (Manual)
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
            placeholder="Szukaj klientów..."
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
              <IconButton onClick={refresh} disabled={loading}>
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
              Wszyscy klienci
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>
              {pagination.total}
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>
              Aktywne sesje
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
              0
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>
              Dzisiejsze interakcje
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 600, color: 'info.main' }}>
              0
            </Typography>
          </CardContent>
        </Card>
      </Stack>

      {/* Tabela klientów */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Klient</TableCell>
              <TableCell>Archetyp</TableCell>
              <TableCell>Tagi</TableCell>
              <TableCell>
                <TableSortLabel
                  active={filters.sort_by === 'created_at'}
                  direction={filters.sort_order}
                  onClick={() => handleSort('created_at')}
                >
                  Data dodania
                </TableSortLabel>
              </TableCell>
              <TableCell align="center">Akcje</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isEmpty ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Box sx={{ py: 8 }}>
                    <PersonIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      Brak klientów
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      Dodaj pierwszego klienta, aby rozpocząć
                    </Typography>
                    <Button 
                      component={Link}
                      to="/clients/new"
                      variant="contained" 
                      startIcon={<AddIcon />}
                      sx={{ textDecoration: 'none' }}
                    >
                      Dodaj Klienta
                    </Button>
                  </Box>
                </TableCell>
              </TableRow>
            ) : (
              clients.map((client) => {
                const initials = getInitials(client.alias);
                
                return (
                  <TableRow key={client.id} hover>
                    {/* Kolumna: Klient */}
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          {initials}
                        </Avatar>
                        <Box>
                          <Typography 
                            component={Link}
                            to={`/clients/${client.id}`}
                            variant="body1" 
                            sx={{ 
                              fontWeight: 500,
                              textDecoration: 'none',
                              color: 'primary.main',
                              '&:hover': {
                                textDecoration: 'underline',
                                color: 'primary.dark'
                              }
                            }}
                          >
                            {client.alias}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>

                    {/* Kolumna: Archetyp */}
                    <TableCell>
                      {client.archetype ? (
                        <Chip
                          icon={<PsychologyIcon />}
                          label={client.archetype}
                          size="small"
                          color={archetypeColors[client.archetype] || 'default'}
                          variant="outlined"
                        />
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          Nieprzypisany
                        </Typography>
                      )}
                    </TableCell>

                    {/* Kolumna: Tagi */}
                    <TableCell>
                      {client.tags && client.tags.length > 0 ? (
                        <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap' }}>
                          {client.tags.slice(0, 3).map((tag, index) => (
                            <Chip
                              key={index}
                              label={tag}
                              size="small"
                              variant="outlined"
                            />
                          ))}
                          {client.tags.length > 3 && (
                            <Chip
                              label={`+${client.tags.length - 3}`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Stack>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          —
                        </Typography>
                      )}
                    </TableCell>

                    {/* Kolumna: Data dodania */}
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(client.created_at).toLocaleDateString('pl-PL', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </Typography>
                    </TableCell>

                    {/* Kolumna: Akcje */}
                    <TableCell align="center">
                      <Stack direction="row" spacing={1} justifyContent="center">
                        <Tooltip title="Edytuj">
                          <IconButton size="small">
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Więcej opcji">
                          <IconButton
                            size="small"
                            onClick={(e) => handleMenuOpen(e, client)}
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
        {hasClients && (
          <TablePagination
            component="div"
            count={pagination.total}
            page={pagination.page - 1}
            onPageChange={handleChangePage}
            rowsPerPage={pagination.size}
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
        <MenuItem onClick={handleMenuClose}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Edytuj
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <PersonIcon fontSize="small" sx={{ mr: 1 }} />
          Zobacz profil
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <ChatIcon fontSize="small" sx={{ mr: 1 }} />
          Rozpocznij sesję
        </MenuItem>
        <MenuItem onClick={handleMenuClose} sx={{ color: 'error.main' }}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Usuń
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ClientList;
