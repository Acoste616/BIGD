import React from 'react';
import { 
    Box, 
    Typography, 
    Chip,
    Grid,
    Paper,
    Tooltip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

// Konfiguracja wartości Schwartza z ikonami i kolorami
const schwartzValueConfig = {
    'Bezpieczeństwo': { icon: '🛡️', color: 'success', description: 'Stabilność, bezpieczeństwo osobiste i społeczne' },
    'Władza': { icon: '👑', color: 'error', description: 'Status społeczny, prestiż, kontrola nad ludźmi' },
    'Osiągnięcia': { icon: '🏆', color: 'warning', description: 'Osobisty sukces, kompetencje, ambicje' },
    'Hedonizm': { icon: '🎉', color: 'secondary', description: 'Przyjemność, zadowolenie, komfort' },
    'Stymulacja': { icon: '⚡', color: 'info', description: 'Nowość, wyzwania, ekscytujące doświadczenia' },
    'Samostanowienie': { icon: '🎯', color: 'primary', description: 'Niezależność myślenia i działania' },
    'Uniwersalizm': { icon: '🌍', color: 'success', description: 'Troska o dobro wszystkich ludzi i przyrody' },
    'Życzliwość': { icon: '❤️', color: 'error', description: 'Zachowanie dobrostanu bliskich osób' },
    'Tradycja': { icon: '🏛️', color: 'default', description: 'Szacunek dla tradycji i kultury' },
    'Przystosowanie': { icon: '🤝', color: 'info', description: 'Powściągliwość, uprzejmość, samodyscyplina' }
};

// Komponent pojedynczej wartości
const ValueChip = ({ value }) => {
    const config = schwartzValueConfig[value.value_name] || { 
        icon: '💎', 
        color: 'default', 
        description: value.value_name 
    };
    
    return (
        <Tooltip 
            title={
                <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {config.icon} {value.value_name}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1, opacity: 0.9 }}>
                        {config.description}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1, color: 'yellow' }}>
                        <strong>Analiza AI:</strong>
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2, fontSize: '0.85rem' }}>
                        {value.rationale}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'lightgreen', fontWeight: 'bold' }}>
                        💡 Strategia Sprzedażowa:
                    </Typography>
                    <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
                        {value.strategy}
                    </Typography>
                </Box>
            }
            arrow
            placement="top"
        >
            <Chip
                icon={
                    value.is_present ? 
                        <CheckCircleIcon sx={{ fontSize: 16 }} /> : 
                        <CancelIcon sx={{ fontSize: 16 }} />
                }
                label={
                    <Box display="flex" alignItems="center" gap={0.5}>
                        <span>{config.icon}</span>
                        <span>{value.value_name}</span>
                    </Box>
                }
                color={value.is_present ? config.color : 'default'}
                variant={value.is_present ? 'filled' : 'outlined'}
                sx={{ 
                    m: 0.5,
                    cursor: 'pointer',
                    '&:hover': {
                        boxShadow: 2
                    }
                }}
            />
        </Tooltip>
    );
};

const SchwartzValuesList = ({ data }) => {
    if (!data || !Array.isArray(data)) {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" color="text.secondary">
                    Brak danych o wartościach Schwartza do wyświetlenia
                </Typography>
            </Box>
        );
    }

    // Podziel na obecne i nieobecne wartości
    const presentValues = data.filter(value => value.is_present);
    const absentValues = data.filter(value => !value.is_present);

    return (
        <Box>
            {/* Obecne wartości */}
            {presentValues.length > 0 && (
                <Box mb={3}>
                    <Paper 
                        elevation={0} 
                        sx={{ 
                            p: 2, 
                            mb: 2, 
                            bgcolor: 'success.light', 
                            color: 'success.contrastText',
                            borderRadius: 2
                        }}
                    >
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                            ✅ Kluczowe Wartości Klienta ({presentValues.length})
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                            Wartości wyraźnie obecne w wypowiedziach i zachowaniu klienta
                        </Typography>
                    </Paper>
                    
                    <Box display="flex" flexWrap="wrap" gap={0.5}>
                        {presentValues.map((value, index) => (
                            <ValueChip key={`present-${index}`} value={value} />
                        ))}
                    </Box>
                </Box>
            )}

            {/* Nieobecne wartości */}
            {absentValues.length > 0 && (
                <Box>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                        Wartości nieobecne lub słabo wyrażone:
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={0.5}>
                        {absentValues.map((value, index) => (
                            <ValueChip key={`absent-${index}`} value={value} />
                        ))}
                    </Box>
                </Box>
            )}

            {/* Podsumowanie */}
            {presentValues.length > 0 && (
                <Paper 
                    elevation={0} 
                    sx={{ 
                        p: 2, 
                        mt: 3, 
                        bgcolor: 'info.lighter',
                        borderRadius: 2
                    }}
                >
                    <Typography variant="body2" color="info.dark">
                        <strong>💡 Wskazówka sprzedażowa:</strong> Klient kieruje się głównie {presentValues.length === 1 ? 'wartością' : 'wartościami'}{' '}
                        {presentValues.slice(0, 2).map(v => `"${v.value_name}"`).join(' i ')}.
                        {presentValues.length > 2 && ` oraz ${presentValues.length - 2} innymi`}.
                        {' '}Najedź na wartość aby zobaczyć dedykowaną strategię sprzedażową.
                    </Typography>
                </Paper>
            )}
        </Box>
    );
};

export default SchwartzValuesList;
