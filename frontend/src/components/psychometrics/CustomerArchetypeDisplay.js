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
    loading = false 
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

    // Brak danych
    if (!customerArchetype) {
        return (
            <Card variant="outlined" sx={{ mb: 3 }}>
                <CardContent sx={{ textAlign: 'center', py: 3 }}>
                    <ArchetypeIcon sx={{ fontSize: 32, mb: 1, color: 'text.secondary' }} />
                    <Typography variant="body1" color="text.secondary">
                        Archetyp klienta zostanie określony po zebraniu wystarczających danych psychologicznych
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    const {
        archetype_name = 'Nieznany Archetyp',
        archetype_key = 'unknown',
        confidence = psychologyConfidence,
        key_traits = [],
        sales_strategy = {},
        description = '',
        motivation = '',
        communication_style = ''
    } = customerArchetype;

    const { do: doActions = [], dont: dontActions = [] } = sales_strategy;

    // Kolory dla różnych archetypów
    const getArchetypeColor = (key) => {
        const colors = {
            'analityk': '#1976d2',        // Blue - Analytical
            'wizjoner': '#7b1fa2',        // Purple - Visionary  
            'relacyjny_budowniczy': '#388e3c', // Green - Relationship
            'szybki_decydent': '#d32f2f'  // Red - Quick Decision
        };
        return colors[key] || '#616161';
    };

    const archetypeColor = getArchetypeColor(archetype_key);

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
                                <Typography 
                                    variant="h5" 
                                    sx={{ 
                                        fontWeight: 'bold', 
                                        color: archetypeColor 
                                    }}
                                >
                                    {archetype_name}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Dominujący archetyp klienta
                                </Typography>
                            </Box>
                        </Box>

                        {/* Confidence indicator */}
                        <Box textAlign="center">
                            <Chip 
                                icon={<ConfidenceIcon />}
                                label={`${confidence}%`}
                                color={confidence >= 80 ? "success" : confidence >= 60 ? "warning" : "default"}
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
