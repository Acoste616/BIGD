/**
 * Panel Zarządzania Wiedzą - Knowledge Management Admin
 * Interfejs do dodawania, przeglądania i usuwania wskazówek w bazie wektorowej Qdrant
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Grid,
  Card,
  CardContent,
  CardActions,
  Autocomplete,
  Tooltip,
  CircularProgress,
  Divider,
  Stack,
  Badge,
  Collapse
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  Psychology as PsychologyIcon,
  Storage as StorageIcon,
  Analytics as AnalyticsIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Close as CloseIcon,
  ContentCopy as ContentCopyIcon,
  Upload as UploadIcon,
  FileUpload as FileUploadIcon
} from '@mui/icons-material';

import MainLayout from '../components/MainLayout';
import {
  useKnowledgeList,
  useCreateKnowledge,
  useDeleteKnowledge,
  useKnowledgeSearch,
  useKnowledgeStats,
  useQdrantHealth,
  useKnowledgeForm
} from '../hooks/useKnowledge';
import { 
  getLocalKnowledgeTypes, 
  getAvailableKnowledgeArchetypes,
  bulkImportFromJSON
} from '../services';

const KnowledgeAdmin = () => {
  // State dla UI
  const [showAddForm, setShowAddForm] = useState(false);
  const [showSearchForm, setShowSearchForm] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState({ open: false, item: null });
  const [detailDialog, setDetailDialog] = useState({ open: false, item: null });
  const [importDialog, setImportDialog] = useState({ 
    open: false, 
    importing: false,
    progress: null,
    results: null,
    error: null
  });

  // Hooks dla danych
  const knowledgeList = useKnowledgeList();
  const createKnowledge = useCreateKnowledge();
  const deleteKnowledge = useDeleteKnowledge();
  const searchKnowledge = useKnowledgeSearch();
  const stats = useKnowledgeStats();
  const qdrantHealth = useQdrantHealth();
  
  // Hook dla formularza
  const form = useKnowledgeForm();

  // Opcje dla selectów
  const knowledgeTypes = getLocalKnowledgeTypes();
  const archetypes = getAvailableKnowledgeArchetypes();

  // Auto-refresh list po dodaniu/usunięciu
  useEffect(() => {
    if (createKnowledge.success || deleteKnowledge.success) {
      knowledgeList.fetchKnowledge();
      stats.fetchStats();
    }
  }, [createKnowledge.success, deleteKnowledge.success]);

  // Handler dodawania wskazówki
  const handleAddKnowledge = async () => {
    if (!form.validateForm()) {
      return;
    }

    const result = await createKnowledge.createKnowledgeItem(form.formData);
    if (result) {
      form.resetForm();
      setShowAddForm(false);
    }
  };

  // Handler usuwania wskazówki
  const handleDeleteKnowledge = async () => {
    if (!deleteDialog.item) return;

    const success = await deleteKnowledge.deleteKnowledgeItem(deleteDialog.item.id);
    if (success) {
      setDeleteDialog({ open: false, item: null });
    }
  };

  // Handler wyszukiwania
  const handleSearch = async (query) => {
    if (!query.trim()) {
      knowledgeList.updateFilters({ search: null });
      return;
    }

    await searchKnowledge.searchKnowledgeItems({
      query: query.trim(),
      limit: 10
    });
  };

  // Handler kopiowania treści
  const handleCopyContent = async (content) => {
    try {
      await navigator.clipboard.writeText(content);
      // TODO: Dodać notyfikację toast o skopiowaniu
    } catch (err) {
      console.error('Nie udało się skopiować:', err);
    }
  };

  // Handler importu z pliku JSON
  const handleJSONImport = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    // Reset state importu
    setImportDialog({
      open: true,
      importing: true,
      progress: { phase: 'starting', message: 'Rozpoczynanie importu...' },
      results: null,
      error: null
    });

    try {
      const results = await bulkImportFromJSON(file, (progressData) => {
        setImportDialog(prev => ({
          ...prev,
          progress: progressData
        }));
      });

      // Sukces - pokaż wyniki
      setImportDialog(prev => ({
        ...prev,
        importing: false,
        results,
        progress: null
      }));

      // Odśwież listę i statystyki
      knowledgeList.fetchKnowledge();
      stats.fetchStats();

    } catch (error) {
      console.error('Błąd importu:', error);
      setImportDialog(prev => ({
        ...prev,
        importing: false,
        error: error.message,
        progress: null
      }));
    }

    // Wyczyść input file
    event.target.value = '';
  };

  // Handler zamknięcia dialogu importu
  const handleCloseImportDialog = () => {
    setImportDialog({
      open: false,
      importing: false,
      progress: null,
      results: null,
      error: null
    });
  };

  return (
    <MainLayout>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <PsychologyIcon sx={{ fontSize: 40, color: 'primary.main' }} />
            <Box>
              <Typography variant="h4" gutterBottom>
                Panel Zarządzania Wiedzą
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Baza wiedzy sprzedażowej z wyszukiwaniem wektorowym
              </Typography>
            </Box>
          </Box>

          {/* Status Qdrant */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            {qdrantHealth.isHealthy && (
              <Chip
                icon={<CheckCircleIcon />}
                label="Qdrant Online"
                color="success"
                variant="outlined"
              />
            )}
            {qdrantHealth.isUnhealthy && (
              <Chip
                icon={<WarningIcon />}
                label="Qdrant Offline"
                color="error"
                variant="outlined"
              />
            )}
          </Box>
        </Box>

        {/* Szybkie statystyki */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <StorageIcon color="primary" />
                  <Box>
                    <Typography variant="h6">{stats.totalItems}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Wskazówek w bazie
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <AnalyticsIcon color="success" />
                  <Box>
                    <Typography variant="h6">
                      {stats.stats?.collection_info?.points_count || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Punktów w Qdrant
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6">Szybkie akcje</Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      onClick={() => setShowAddForm(true)}
                      size="small"
                    >
                      Dodaj
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<SearchIcon />}
                      onClick={() => setShowSearchForm(!showSearchForm)}
                      size="small"
                    >
                      Szukaj
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<AnalyticsIcon />}
                      onClick={() => setShowStats(!showStats)}
                      size="small"
                    >
                      Statystyki
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<FileUploadIcon />}
                      component="label"
                      size="small"
                      color="secondary"
                    >
                      Importuj JSON
                      <input
                        type="file"
                        accept=".json"
                        onChange={handleJSONImport}
                        style={{ display: 'none' }}
                      />
                    </Button>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Rozwijane statystyki */}
        <Collapse in={showStats}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              📊 Szczegółowe statystyki
            </Typography>
            
            {stats.loading ? (
              <CircularProgress />
            ) : stats.stats ? (
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Według typu wiedzy:
                  </Typography>
                  <Stack spacing={1}>
                    {Object.entries(stats.stats.by_type || {}).map(([type, count]) => (
                      <Box key={type} sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Chip label={type} size="small" />
                        <Typography variant="body2">{count}</Typography>
                      </Box>
                    ))}
                  </Stack>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Według archetypu:
                  </Typography>
                  <Stack spacing={1}>
                    {Object.entries(stats.stats.by_archetype || {}).map(([archetype, count]) => (
                      <Box key={archetype} sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Chip label={archetype} size="small" />
                        <Typography variant="body2">{count}</Typography>
                      </Box>
                    ))}
                  </Stack>
                </Grid>
              </Grid>
            ) : (
              <Alert severity="info">Brak statystyk do wyświetlenia</Alert>
            )}
          </Paper>
        </Collapse>

        {/* Formularz wyszukiwania */}
        <Collapse in={showSearchForm}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              🔍 Wyszukiwanie wektorowe
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <TextField
                label="Wpisz zapytanie..."
                placeholder="np. jak odpowiedzieć na zastrzeżenia cenowe"
                variant="outlined"
                fullWidth
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSearch(e.target.value);
                  }
                }}
              />
              <Button
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={(e) => {
                  const input = e.target.closest('div').querySelector('input');
                  handleSearch(input.value);
                }}
                disabled={searchKnowledge.searching}
              >
                Szukaj
              </Button>
            </Box>

            {/* Wyniki wyszukiwania */}
            {searchKnowledge.hasResults && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Znalezione wskazówki (podobieństwo):
                </Typography>
                <Stack spacing={2}>
                  {searchKnowledge.results.map((result) => (
                    <Card key={result.id} variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="subtitle2">
                            {result.displayTitle}
                          </Typography>
                          <Chip 
                            label={result.displayScore} 
                            color={result.isHighlyRelevant ? 'success' : result.isModeratelyRelevant ? 'warning' : 'default'}
                            size="small"
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {result.displayContent}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          <Chip label={result.displayType} size="small" />
                          {result.archetype && (
                            <Chip label={result.archetype} size="small" variant="outlined" />
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                </Stack>
              </Box>
            )}
          </Paper>
        </Collapse>

        {/* Filtry i kontrolki */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Typ wiedzy</InputLabel>
              <Select
                value={knowledgeList.filters.knowledge_type || ''}
                label="Typ wiedzy"
                onChange={(e) => knowledgeList.updateFilters({ 
                  knowledge_type: e.target.value || null 
                })}
              >
                <MenuItem value="">Wszystkie</MenuItem>
                {knowledgeTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Archetyp</InputLabel>
              <Select
                value={knowledgeList.filters.archetype || ''}
                label="Archetyp"
                onChange={(e) => knowledgeList.updateFilters({ 
                  archetype: e.target.value || null 
                })}
              >
                <MenuItem value="">Wszystkie</MenuItem>
                {archetypes.map((archetype) => (
                  <MenuItem key={archetype.value} value={archetype.value}>
                    {archetype.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {knowledgeList.isFiltered && (
              <Button
                startIcon={<ClearIcon />}
                onClick={knowledgeList.clearFilters}
                size="small"
              >
                Wyczyść filtry
              </Button>
            )}

            <Box sx={{ flexGrow: 1 }} />

            <Button
              startIcon={<RefreshIcon />}
              onClick={knowledgeList.fetchKnowledge}
              disabled={knowledgeList.loading}
              size="small"
            >
              Odśwież
            </Button>
          </Box>
        </Paper>

        {/* Tabela wskazówek */}
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Tytuł</TableCell>
                  <TableCell>Typ</TableCell>
                  <TableCell>Archetyp</TableCell>
                  <TableCell>Tagi</TableCell>
                  <TableCell>Utworzono</TableCell>
                  <TableCell align="right">Akcje</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {knowledgeList.loading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : knowledgeList.isEmpty ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary">
                        {knowledgeList.isFiltered ? 'Brak wyników dla obecnych filtrów' : 'Brak wskazówek w bazie'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  knowledgeList.knowledge.map((item) => (
                    <TableRow key={item.id} hover>
                      <TableCell>
                        <Typography variant="subtitle2" gutterBottom>
                          {item.displayTitle}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {item.displayContent}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={item.displayType} 
                          size="small"
                          color={knowledgeTypes.find(t => t.value === item.knowledge_type)?.color || 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        {item.archetype ? (
                          <Chip label={item.displayArchetype} size="small" variant="outlined" />
                        ) : (
                          <Typography variant="body2" color="text.disabled">
                            Brak
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {item.displayTags.slice(0, 3).map((tag) => (
                            <Chip key={tag} label={tag} size="small" variant="outlined" />
                          ))}
                          {item.displayTags.length > 3 && (
                            <Chip label={`+${item.displayTags.length - 3}`} size="small" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {item.displayCreatedAt}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="Zobacz szczegóły">
                          <IconButton
                            size="small"
                            onClick={() => setDetailDialog({ open: true, item })}
                          >
                            <InfoIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Kopiuj treść">
                          <IconButton
                            size="small"
                            onClick={() => handleCopyContent(item.content)}
                          >
                            <ContentCopyIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Usuń">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => setDeleteDialog({ open: true, item })}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Paginacja */}
          {knowledgeList.hasItems && (
            <TablePagination
              component="div"
              count={knowledgeList.total}
              page={knowledgeList.page - 1} // MUI używa 0-based index
              onPageChange={(e, newPage) => knowledgeList.changePage(newPage + 1)}
              rowsPerPage={knowledgeList.size}
              onRowsPerPageChange={(e) => knowledgeList.changeSize(parseInt(e.target.value))}
              rowsPerPageOptions={[5, 10, 25, 50]}
              labelRowsPerPage="Wierszy na stronę:"
              labelDisplayedRows={({ from, to, count }) => 
                `${from}-${to} z ${count !== -1 ? count : `więcej niż ${to}`}`
              }
            />
          )}
        </Paper>

        {/* Floating Action Button */}
        <Tooltip title="Dodaj nową wskazówkę">
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setShowAddForm(true)}
            sx={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              borderRadius: '28px',
              px: 3
            }}
          >
            Dodaj wskazówkę
          </Button>
        </Tooltip>
      </Box>

      {/* Dialog dodawania wskazówki */}
      <Dialog 
        open={showAddForm} 
        onClose={() => setShowAddForm(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          ✨ Dodaj nową wskazówkę
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  label="Tytuł wskazówki"
                  placeholder="np. Obsługa zastrzeżeń cenowych"
                  fullWidth
                  value={form.formData.title}
                  onChange={(e) => form.updateField('title', e.target.value)}
                  error={!!form.errors.title}
                  helperText={form.errors.title}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth error={!!form.errors.knowledge_type}>
                  <InputLabel>Typ wiedzy</InputLabel>
                  <Select
                    value={form.formData.knowledge_type}
                    label="Typ wiedzy"
                    onChange={(e) => form.updateField('knowledge_type', e.target.value)}
                  >
                    {knowledgeTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Archetyp klienta</InputLabel>
                  <Select
                    value={form.formData.archetype}
                    label="Archetyp klienta"
                    onChange={(e) => form.updateField('archetype', e.target.value)}
                  >
                    <MenuItem value="">Ogólne (wszystkie archetypy)</MenuItem>
                    {archetypes.map((archetype) => (
                      <MenuItem key={archetype.value} value={archetype.value}>
                        {archetype.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <Autocomplete
                  multiple
                  options={[]}
                  freeSolo
                  value={form.formData.tags}
                  onChange={(e, newValue) => form.updateField('tags', newValue)}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip variant="outlined" label={option} {...getTagProps({ index })} />
                    ))
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Tagi"
                      placeholder="Wpisz tag i naciśnij Enter"
                      error={!!form.errors.tags}
                      helperText={form.errors.tags || "Dodaj tagi aby ułatwić kategoryzację"}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  label="Treść wskazówki"
                  placeholder="Opisz szczegółowo wskazówkę sprzedażową..."
                  fullWidth
                  multiline
                  rows={6}
                  value={form.formData.content}
                  onChange={(e) => form.updateField('content', e.target.value)}
                  error={!!form.errors.content}
                  helperText={form.errors.content || `${form.formData.content.length}/5000 znaków`}
                />
              </Grid>
            </Grid>

            {/* Błędy tworzenia */}
            {createKnowledge.error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {createKnowledge.error}
              </Alert>
            )}

            {/* Sukces */}
            {createKnowledge.success && (
              <Alert severity="success" sx={{ mt: 2 }}>
                Wskazówka została dodana pomyślnie!
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAddForm(false)}>
            Anuluj
          </Button>
          <Button
            variant="contained"
            onClick={handleAddKnowledge}
            disabled={createKnowledge.creating || !form.isValid}
            startIcon={createKnowledge.creating ? <CircularProgress size={20} /> : <AddIcon />}
          >
            {createKnowledge.creating ? 'Dodaję...' : 'Dodaj wskazówkę'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog szczegółów */}
      <Dialog
        open={detailDialog.open}
        onClose={() => setDetailDialog({ open: false, item: null })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          📄 Szczegóły wskazówki
        </DialogTitle>
        <DialogContent>
          {detailDialog.item && (
            <Box sx={{ pt: 2 }}>
              <Typography variant="h6" gutterBottom>
                {detailDialog.item.displayTitle}
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip label={detailDialog.item.displayType} />
                {detailDialog.item.archetype && (
                  <Chip label={detailDialog.item.displayArchetype} variant="outlined" />
                )}
              </Box>

              <Typography variant="body1" paragraph>
                {detailDialog.item.content}
              </Typography>

              {detailDialog.item.displayTags.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>Tagi:</Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {detailDialog.item.displayTags.map((tag) => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Box>
              )}

              <Typography variant="caption" color="text.secondary">
                ID: {detailDialog.item.id} • Utworzono: {detailDialog.item.displayCreatedAt}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialog({ open: false, item: null })}>
            Zamknij
          </Button>
          <Button
            variant="outlined"
            startIcon={<ContentCopyIcon />}
            onClick={() => handleCopyContent(detailDialog.item?.content || '')}
          >
            Kopiuj treść
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog potwierdzenia usunięcia */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, item: null })}
      >
        <DialogTitle>
          ⚠️ Potwierdź usunięcie
        </DialogTitle>
        <DialogContent>
          <Typography>
            Czy na pewno chcesz usunąć wskazówkę "{deleteDialog.item?.displayTitle}"?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Ta operacja jest nieodwracalna.
          </Typography>

          {deleteKnowledge.error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {deleteKnowledge.error}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, item: null })}>
            Anuluj
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleDeleteKnowledge}
            disabled={deleteKnowledge.deleting}
            startIcon={deleteKnowledge.deleting ? <CircularProgress size={20} /> : <DeleteIcon />}
          >
            {deleteKnowledge.deleting ? 'Usuwam...' : 'Usuń'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog importu JSON */}
      <Dialog
        open={importDialog.open}
        onClose={!importDialog.importing ? handleCloseImportDialog : undefined}
        maxWidth="md"
        fullWidth
        disableEscapeKeyDown={importDialog.importing}
      >
        <DialogTitle>
          📦 Import bazy wiedzy z JSON
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            {/* Trwa import - pokaż postęp */}
            {importDialog.importing && importDialog.progress && (
              <Box sx={{ textAlign: 'center' }}>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {importDialog.progress.message}
                </Typography>
                
                {importDialog.progress.phase === 'parsing' && (
                  <Typography variant="body2" color="text.secondary">
                    Analizuję strukturę pliku JSON...
                  </Typography>
                )}
                
                {importDialog.progress.phase === 'importing' && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Batch {importDialog.progress.currentBatch} z {importDialog.progress.totalBatches}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Przetworzono: {importDialog.progress.itemsProcessed} elementów
                    </Typography>
                  </Box>
                )}
              </Box>
            )}

            {/* Import zakończony - pokaż wyniki */}
            {!importDialog.importing && importDialog.results && (
              <Box>
                <Alert 
                  severity={importDialog.results.totalErrors === 0 ? "success" : "warning"}
                  sx={{ mb: 3 }}
                >
                  {importDialog.results.summary}
                </Alert>

                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h6" color="primary">
                          {importDialog.results.totalItems}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Znaleziono
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={4}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h6" color="success.main">
                          {importDialog.results.totalImported}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Zaimportowano
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={4}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h6" color="error.main">
                          {importDialog.results.totalErrors}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Błędów
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Szczegóły błędów jeśli występują */}
                {importDialog.results.totalErrors > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Szczegóły błędów:
                    </Typography>
                    <Stack spacing={1}>
                      {importDialog.results.results
                        .filter(result => result.error)
                        .map((result, index) => (
                          <Alert key={index} severity="error" variant="outlined">
                            Batch {result.batch}: {result.error} ({result.itemsInBatch} elementów)
                          </Alert>
                        ))}
                    </Stack>
                  </Box>
                )}
              </Box>
            )}

            {/* Błąd importu */}
            {!importDialog.importing && importDialog.error && (
              <Alert severity="error">
                <Typography variant="subtitle2" gutterBottom>
                  Błąd podczas importu:
                </Typography>
                <Typography variant="body2">
                  {importDialog.error}
                </Typography>
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          {!importDialog.importing && (
            <Button onClick={handleCloseImportDialog} variant="contained">
              Zamknij
            </Button>
          )}
          {importDialog.importing && (
            <Typography variant="body2" color="text.secondary" sx={{ px: 2 }}>
              Trwa import... Proszę czekać
            </Typography>
          )}
        </DialogActions>
      </Dialog>
    </MainLayout>
  );
};

export default KnowledgeAdmin;
