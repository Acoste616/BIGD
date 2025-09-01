import React from 'react';
import { 
    Box, 
    Card, 
    CardContent, 
    Typography, 
    Chip, 
    Alert,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Grid,
    LinearProgress,
    Fade
} from '@mui/material';
import { 
    Psychology as PsychologyIcon,
    CheckCircle as DoIcon,
    Cancel as DontIcon,
    TrendingUp as ConfidenceIcon,
    Person as ArchetypeIcon
} from '@mui/icons-material';

const CustomerArchetypeDisplay = ({ 
    customerArchetype, 
    psychologyConfidence = 0,
    loading = false,
    // 🧠⚡ ULTRA MÓZG v4.2.0: NOWE PROPSY
    dnaKlienta = null,
    isDnaReady = false
}) => {
    // Loading state
    if (loading) {
        return (
            <Card elevation={3} sx={{ mb: 3 }}>
                <CardContent sx={{ textAlign: 'center', py: 4 }}>
                    <PsychologyIcon sx={{ fontSize: 48, mb: 2, color: 'primary.main' }} />
                    <Typography variant="h6" gutterBottom>
                        Analiza Archetypu Klienta
                    </Typography>
                    <LinearProgress sx={{ mt: 2 }} />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        AI analizuje profil psychologiczny...
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    // 🧠⚡ LOGIKA DECYZYJNA ULTRA MÓZGU
    // Priorytetyzuj DNA Klienta nad legacy customer archetype
    let activeArchetype, activeConfidence, activeDNA, isUltraBrainActive;
    
    if (isDnaReady && dnaKlienta) {
        // ULTRA MÓZG: Używamy DNA Klienta
        isUltraBrainActive = true;
        activeArchetype = {
            archetype_name: dnaKlienta.holistic_summary || 'DNA Klienta',
            archetype_key: 'ultra_brain',
            description: dnaKlienta.main_drive || 'Identyfikuję główny motor napędowy...',
            motivation: dnaKlienta.main_drive || '',
            communication_style: dnaKlienta.communication_style?.recommended_tone || '',
            key_traits: dnaKlienta.key_levers || [],
            sales_strategy: {
                do: dnaKlienta.key_levers || [],
                dont: dnaKlienta.red_flags || []
            }
        };
        activeConfidence = dnaKlienta.confidence || psychologyConfidence;
        activeDNA = dnaKlienta;
    } else {
        // LEGACY: Używamy starych danych
        isUltraBrainActive = false;
        activeArchetype = customerArchetype;
        activeConfidence = psychologyConfidence;
        activeDNA = null;
    }

    // Brak danych (ani legacy ani Ultra Mózg)
    if (!activeArchetype) {
        return (
            <Card variant="outlined" sx={{ mb: 3 }}>
                <CardContent sx={{ textAlign: 'center', py: 3 }}>
                    <ArchetypeIcon sx={{ fontSize: 32, mb: 1, color: 'text.secondary' }} />
                    <Typography variant="body1" color="text.secondary">
                        {isUltraBrainActive ? 
                            'Ultra Mózg analizuje profil psychologiczny klienta...' :
                            'Archetyp klienta zostanie określony po zebraniu wystarczających danych psychologicznych'
                        }
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    const {
        archetype_name = 'Nieznany Archetyp',
        archetype_key = 'unknown',
        confidence = activeConfidence,
        key_traits = [],
        sales_strategy = {},
        description = '',
        motivation = '',
        communication_style = ''
    } = activeArchetype;

    const { do: doActions = [], dont: dontActions = [] } = sales_strategy;

    // Kolory dla różnych archetypów
    const getArchetypeColor = (key) => {
        const colors = {
            'analityk': '#1976d2',        // Blue - Analytical
            'wizjoner': '#7b1fa2',        // Purple - Visionary  
            'relacyjny_budowniczy': '#388e3c', // Green - Relationship
            'szybki_decydent': '#d32f2f', // Red - Quick Decision
            'ultra_brain': '#2196f3'      // 🧠⚡ ULTRA MÓZG - Special color
        };
        return colors[key] || '#616161';
    };

    const archetypeColor = getArchetypeColor(archetype_key);
    const displayConfidence = confidence || activeConfidence;

    return (
        <Fade in={true} timeout={500}>
            <Card 
                elevation={4} 
                sx={{ 
                    mb: 3,
                    background: `linear-gradient(135deg, ${archetypeColor}15 0%, ${archetypeColor}05 100%)`,
                    border: `2px solid ${archetypeColor}30`
                }}
            >
                <CardContent sx={{ pb: 2 }}>
                    {/* Header z archetypem */}
                    <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                        <Box display="flex" alignItems="center" gap={2}>
                            <Box
                                sx={{
                                    width: 48,
                                    height: 48,
                                    borderRadius: '50%',
                                    bgcolor: archetypeColor,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '24px'
                                }}
                            >
                                {archetype_name.split(' ')[0]} {/* First emoji */}
                            </Box>
                            <Box>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                    <Typography 
                                        variant="h5" 
                                        sx={{ 
                                            fontWeight: 'bold', 
                                            color: archetypeColor 
                                        }}
                                    >
                                        {archetype_name}
                                    </Typography>
                                    {isUltraBrainActive && (
                                        <Chip 
                                            label="🧠⚡ ULTRA MÓZG" 
                                            size="small" 
                                            color="primary" 
                                            sx={{ fontSize: '0.7rem', fontWeight: 'bold' }}
                                        />
                                    )}
                                </Box>
                                <Typography variant="body2" color="text.secondary">
                                    {isUltraBrainActive ? 
                                        'DNA Klienta wygenerowane przez Ultra Mózg' :
                                        'Dominujący archetyp klienta'
                                    }
                                </Typography>
                            </Box>
                        </Box>

                        {/* Confidence indicator */}
                        <Box textAlign="center">
                            <Chip 
                                icon={<ConfidenceIcon />}
                                label={`${displayConfidence}%`}
                                color={displayConfidence >= 80 ? "success" : displayConfidence >= 60 ? "warning" : "default"}
                                variant="outlined"
                                sx={{ fontWeight: 'bold' }}
                            />
                            <Typography variant="caption" display="block" color="text.secondary">
                                Pewność
                            </Typography>
                        </Box>
                    </Box>

                    {/* Opis archetypu */}
                    {description && (
                        <Alert severity="info" sx={{ mb: 2, backgroundColor: `${archetypeColor}10` }}>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                📋 <strong>Profil:</strong> {description}
                            </Typography>
                        </Alert>
                    )}

                    {/* Motywacja i styl komunikacji */}
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                        {motivation && (
                            <Grid item xs={12} md={6}>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                    🎯 <strong>Główna motywacja:</strong>
                                </Typography>
                                <Typography variant="body2">{motivation}</Typography>
                            </Grid>
                        )}
                        {communication_style && (
                            <Grid item xs={12} md={6}>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                    💬 <strong>Styl komunikacji:</strong>
                                </Typography>
                                <Typography variant="body2">{communication_style}</Typography>
                            </Grid>
                        )}
                    </Grid>

                    {/* Kluczowe cechy */}
                    {key_traits.length > 0 && (
                        <Box mb={3}>
                            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                                🎯 Kluczowe Cechy:
                            </Typography>
                            <Box display="flex" gap={1} flexWrap="wrap">
                                {key_traits.map((trait, index) => (
                                    <Chip 
                                        key={index}
                                        label={trait}
                                        size="small"
                                        sx={{ 
                                            bgcolor: `${archetypeColor}20`,
                                            color: archetypeColor,
                                            fontWeight: 'medium'
                                        }}
                                    />
                                ))}
                            </Box>
                        </Box>
                    )}

                    {/* Strategia sprzedażowa */}
                    {(doActions.length > 0 || dontActions.length > 0) && (
                        <Grid container spacing={2}>
                            {/* DO - Zalecane działania */}
                            {doActions.length > 0 && (
                                <Grid item xs={12} md={6}>
                                    <Alert 
                                        severity="success" 
                                        variant="outlined"
                                        sx={{ height: '100%' }}
                                    >
                                        <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                                            ✅ RÓB TO:
                                        </Typography>
                                        <List dense>
                                            {doActions.map((action, index) => (
                                                <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                                                    <ListItemIcon sx={{ minWidth: 24 }}>
                                                        <DoIcon color="success" fontSize="small" />
                                                    </ListItemIcon>
                                                    <ListItemText 
                                                        primary={action}
                                                        primaryTypographyProps={{ 
                                                            variant: 'body2',
                                                            sx: { fontWeight: 'medium' }
                                                        }}
                                                    />
                                                </ListItem>
                                            ))}
                                        </List>
                                    </Alert>
                                </Grid>
                            )}

                            {/* DON'T - Działania do uniknięcia */}
                            {dontActions.length > 0 && (
                                <Grid item xs={12} md={6}>
                                    <Alert 
                                        severity="warning" 
                                        variant="outlined"
                                        sx={{ height: '100%' }}
                                    >
                                        <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                                            ❌ NIE RÓB TEGO:
                                        </Typography>
                                        <List dense>
                                            {dontActions.map((action, index) => (
                                                <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                                                    <ListItemIcon sx={{ minWidth: 24 }}>
                                                        <DontIcon color="warning" fontSize="small" />
                                                    </ListItemIcon>
                                                    <ListItemText 
                                                        primary={action}
                                                        primaryTypographyProps={{ 
                                                            variant: 'body2',
                                                            sx: { fontWeight: 'medium' }
                                                        }}
                                                    />
                                                </ListItem>
                                            ))}
                                        </List>
                                    </Alert>
                                </Grid>
                            )}
                        </Grid>
                    )}

                    {/* Low confidence warning */}
                    {confidence < 70 && (
                        <Alert severity="info" sx={{ mt: 2 }}>
                            <Typography variant="body2">
                                💡 <strong>Niski poziom pewności:</strong> Zadaj klientowi więcej pytań aby potwierdzić archetyp i dostosować strategię.
                            </Typography>
                        </Alert>
                    )}
                </CardContent>
            </Card>
        </Fade>
    );
};

export default CustomerArchetypeDisplay;
