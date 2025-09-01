import React from 'react';
import { 
    Box, 
    Typography, 
    Card,
    CardContent,
    Tooltip,
    Chip,
    LinearProgress,
    Divider
} from '@mui/material';
import { 
    AttachMoney as MoneyIcon,
    TrendingUp as TrendingUpIcon,
    Schedule as ScheduleIcon,
    Percent as PercentIcon
} from '@mui/icons-material';
import PaidIcon from '@mui/icons-material/Paid';

const SalesPotentialCard = ({ data, loading = false }) => {
    if (loading) {
        return (
            <Card elevation={2} sx={{ height: '250px', display: 'flex', alignItems: 'center' }}>
                <CardContent sx={{ width: '100%', textAlign: 'center' }}>
                    <PaidIcon sx={{ fontSize: 40, mb: 2, color: 'primary.main' }} />
                    <Typography variant="h6" gutterBottom>💰 Potencjał Sprzedażowy</Typography>
                    <LinearProgress sx={{ mt: 2 }} />
                </CardContent>
            </Card>
        );
    }

    if (!data) {
        return (
            <Card elevation={2} sx={{ height: '250px', display: 'flex', alignItems: 'center' }}>
                <CardContent sx={{ width: '100%', textAlign: 'center' }}>
                    <PaidIcon sx={{ fontSize: 40, mb: 2, color: 'text.secondary' }} />
                    <Typography variant="h6" color="text.secondary">💰 Potencjał Sprzedażowy</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Brak danych do analizy
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    const { 
        value = 0, 
        probability = 0, 
        estimated_timeframe = 'Nieznany',
        rationale = '', 
        strategy = '', 
        confidence = 0 
    } = data;

    // Formatowanie kwoty
    const formatCurrency = (amount) => {
        if (amount >= 1000000) {
            return `${(amount / 1000000).toFixed(1)}M PLN`;
        }
        if (amount >= 1000) {
            return `${(amount / 1000).toFixed(0)}k PLN`;
        }
        return `${amount.toFixed(0)} PLN`;
    };

    // Kolory prawdopodobieństwa
    const getProbabilityColor = (prob) => {
        if (prob >= 80) return '#4caf50';    // Zielony - wysokie
        if (prob >= 50) return '#ff9800';    // Pomarańczowy - średnie
        if (prob >= 20) return '#f44336';    // Czerwony - niskie
        return '#9e9e9e';                    // Szary - bardzo niskie
    };

    // Emoji prawdopodobieństwa
    const getProbabilityEmoji = (prob) => {
        if (prob >= 80) return '🚀';
        if (prob >= 50) return '📈';
        if (prob >= 20) return '📊';
        return '📉';
    };

    const probabilityColor = getProbabilityColor(probability);
    const probabilityEmoji = getProbabilityEmoji(probability);

    return (
        <Tooltip 
            title={
                <Box sx={{ p: 1, maxWidth: 350 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        💰 Wartość: {formatCurrency(value)} ({probability}% prawdopodobieństwo)
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2, color: 'lightblue' }}>
                        ⏰ Szacowany czas: {estimated_timeframe}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1, fontWeight: 'bold', color: 'yellow' }}>
                        📋 Uzasadnienie AI:
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2, fontSize: '0.85rem' }}>
                        {rationale}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1, fontWeight: 'bold', color: 'lightgreen' }}>
                        💡 Strategia:
                    </Typography>
                    <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
                        {strategy}
                    </Typography>
                    {confidence > 0 && (
                        <Typography variant="caption" sx={{ mt: 1, display: 'block', opacity: 0.8 }}>
                            Pewność AI: {confidence}%
                        </Typography>
                    )}
                </Box>
            }
            arrow
            placement="top"
        >
            <Card 
                elevation={2} 
                sx={{ 
                    height: '250px',
                    cursor: 'help',
                    transition: 'all 0.3s ease',
                    '&:hover': { 
                        transform: 'translateY(-4px)',
                        boxShadow: 4,
                        borderLeft: `4px solid ${probabilityColor}`
                    }
                }}
            >
                <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 2 }}>
                    {/* Header */}
                    <Box sx={{ textAlign: 'center', mb: 2 }}>
                        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                            💰 Potencjał Sprzedażowy
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            Szacowana wartość i prawdopodobieństwo
                        </Typography>
                    </Box>

                    {/* Value Display */}
                    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        {/* Main Value */}
                        <Box sx={{ textAlign: 'center', mb: 2 }}>
                            <Typography 
                                variant="h4" 
                                sx={{ 
                                    fontWeight: 'bold',
                                    color: 'primary.main',
                                    lineHeight: 1,
                                    mb: 1
                                }}
                            >
                                {formatCurrency(value)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Szacowana wartość transakcji
                            </Typography>
                        </Box>

                        <Divider sx={{ mb: 2 }} />

                        {/* Probability */}
                        <Box sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                    {probabilityEmoji} Prawdopodobieństwo
                                </Typography>
                                <Typography 
                                    variant="h6" 
                                    sx={{ fontWeight: 'bold', color: probabilityColor }}
                                >
                                    {probability}%
                                </Typography>
                            </Box>
                            <LinearProgress 
                                variant="determinate" 
                                value={probability} 
                                sx={{ 
                                    height: 8, 
                                    borderRadius: 4,
                                    backgroundColor: 'grey.300',
                                    '& .MuiLinearProgress-bar': {
                                        backgroundColor: probabilityColor,
                                        borderRadius: 4
                                    }
                                }}
                            />
                        </Box>

                        {/* Timeframe */}
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 1 }}>
                            <ScheduleIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                                {estimated_timeframe}
                            </Typography>
                        </Box>
                    </Box>

                    {/* Footer */}
                    <Box sx={{ textAlign: 'center', mt: 'auto' }}>
                        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                            Najedź aby zobaczyć strategię
                        </Typography>
                    </Box>
                </CardContent>
            </Card>
        </Tooltip>
    );
};

export default SalesPotentialCard;
