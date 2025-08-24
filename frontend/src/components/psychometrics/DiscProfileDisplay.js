import React from 'react';
import { 
    Box, 
    Typography, 
    LinearProgress, 
    Tooltip,
    Paper,
    Grid
} from '@mui/material';

// Mapowanie nazw DISC na polskie etykiety i kolory
const discTraitConfig = {
    dominance: { 
        label: 'Dominacja', 
        color: 'error',
        icon: '🔥',
        description: 'Bezpośredni, asertywny, zorientowany na wyniki'
    },
    influence: { 
        label: 'Wpływ', 
        color: 'warning',
        icon: '🌟', 
        description: 'Towarzyski, optymistyczny, perswazyjny'
    },
    steadiness: { 
        label: 'Stałość', 
        color: 'success',
        icon: '🛡️',
        description: 'Cierpliwy, lojalny, stabilny'
    },
    compliance: { 
        label: 'Sumienność', 
        color: 'info',
        icon: '📊',
        description: 'Analityczny, precyzyjny, systematyczny'
    }
};

// Komponent pojedynczego paska DISC
const DiscBar = ({ traitKey, trait, config }) => {
    // 🔧 NAPRAWA: Zabezpieczenie przed null trait
    const score = (trait && trait.score) || 0;
    const rationale = (trait && trait.rationale) || 'Brak danych - analiza w toku';
    const strategy = (trait && trait.strategy) || 'Strategia będzie dostępna po analizie';
    const percentage = (score / 10) * 100;
    
    return (
        <Tooltip 
            title={
                <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {config.icon} {config.label}: {score}/10
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1, opacity: 0.9 }}>
                        {config.description}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1, color: 'yellow' }}>
                        <strong>Uzasadnienie AI:</strong>
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2, fontSize: '0.85rem' }}>
                        {rationale}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'lightgreen', fontWeight: 'bold' }}>
                        💡 Strategia Sprzedażowa:
                    </Typography>
                    <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
                        {strategy}
                    </Typography>
                </Box>
            }
            arrow
            placement="right"
        >
            <Paper 
                elevation={1} 
                sx={{ 
                    p: 2, 
                    mb: 2, 
                    cursor: 'pointer',
                    '&:hover': { 
                        elevation: 3,
                        bgcolor: 'action.hover'
                    }
                }}
            >
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                    <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body1" component="span">
                            {config.icon}
                        </Typography>
                        <Typography variant="body1" component="span" fontWeight={500}>
                            {config.label}
                        </Typography>
                    </Box>
                    <Typography 
                        variant="body2" 
                        component="span" 
                        fontWeight="bold"
                        color={`${config.color}.main`}
                    >
                        {score}/10
                    </Typography>
                </Box>
                
                <LinearProgress 
                    variant="determinate" 
                    value={percentage} 
                    color={config.color}
                    sx={{ 
                        height: 8, 
                        borderRadius: 4,
                        '& .MuiLinearProgress-bar': {
                            borderRadius: 4
                        }
                    }}
                />
                
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                    {config.description}
                </Typography>
            </Paper>
        </Tooltip>
    );
};

const DiscProfileDisplay = ({ data }) => {
    if (!data) {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" color="text.secondary">
                    Brak danych DISC do wyświetlenia
                </Typography>
            </Box>
        );
    }

    // Znajdź dominujący styl DISC
    const dominantTrait = React.useMemo(() => {
        const traits = Object.entries(data);
        return traits.reduce((max, [key, trait]) => {
            // 🔧 NAPRAWA: Sprawdź czy trait nie jest null
            const score = (trait && trait.score) || 0;
            return score > max.score ? { key, score, ...trait } : max;
        }, { score: 0 });
    }, [data]);

    return (
        <Box>
            {/* Podsumowanie dominującego stylu */}
            {dominantTrait.score > 0 && (
                <Paper 
                    elevation={0} 
                    sx={{ 
                        p: 2, 
                        mb: 3, 
                        bgcolor: 'primary.main', 
                        color: 'primary.contrastText',
                        borderRadius: 2
                    }}
                >
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {discTraitConfig[dominantTrait.key]?.icon} Dominujący Styl: {' '}
                        {discTraitConfig[dominantTrait.key]?.label}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        Ocena: {dominantTrait.score}/10 • {discTraitConfig[dominantTrait.key]?.description}
                    </Typography>
                </Paper>
            )}

                        {/* NOWA LOGIKA: Dominująca cecha DISC prominentnie + pozostałe wyszarzone */}
            <Box>
                {Object.entries(data).map(([traitKey, trait]) => {
                    const config = discTraitConfig[traitKey];
                    if (!config) return null;
                    
                    // Sprawdź czy to dominująca cecha
                    const isDominant = traitKey === dominantTrait.key;
                    
                    return (
                        <Box key={traitKey} sx={{ 
                            opacity: isDominant ? 1 : 0.3,  // Wyszarz pozostałe
                            transform: isDominant ? 'scale(1.05)' : 'scale(1)',  // Powiększ dominującą
                            transition: 'all 0.3s ease',
                            mb: 1
                        }}>
                            <DiscBar
                                traitKey={traitKey}
                                trait={trait}
                                config={config}
                            />
                            {/* Dodatkowy marker dla dominującej */}
                            {isDominant && (
                                <Typography 
                                    variant="caption" 
                                    color="primary.main" 
                                    fontWeight="bold"
                                    sx={{ ml: 1 }}
                                >
                                    ← DOMINUJĄCY STYL
                                </Typography>
                            )}
                        </Box>
                    );
                })}
            </Box>

            {/* Informacja pomocnicza */}
            <Box sx={{ mt: 2, textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                    Najedź na pasek aby zobaczyć szczegółową strategię sprzedażową dla tego stylu
                </Typography>
            </Box>
        </Box>
    );
};

export default DiscProfileDisplay;
