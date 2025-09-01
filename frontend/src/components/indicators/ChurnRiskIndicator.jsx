import React from 'react';
import { 
    Box, 
    Typography, 
    Card,
    CardContent,
    Tooltip,
    Chip,
    LinearProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemText
} from '@mui/material';
import { 
    Shield as ShieldIcon,
    Warning as WarningIcon,
    Error as ErrorIcon,
    CheckCircle as CheckIcon,
    Cancel as CancelIcon
} from '@mui/icons-material';
import SecurityIcon from '@mui/icons-material/Security';

const ChurnRiskIndicator = ({ data, loading = false }) => {
    if (loading) {
        return (
            <Card elevation={2} sx={{ height: '250px', display: 'flex', alignItems: 'center' }}>
                <CardContent sx={{ width: '100%', textAlign: 'center' }}>
                    <SecurityIcon sx={{ fontSize: 40, mb: 2, color: 'primary.main' }} />
                    <Typography variant="h6" gutterBottom>⚖️ Ryzyko Utraty</Typography>
                    <LinearProgress sx={{ mt: 2 }} />
                </CardContent>
            </Card>
        );
    }

    if (!data) {
        return (
            <Card elevation={2} sx={{ height: '250px', display: 'flex', alignItems: 'center' }}>
                <CardContent sx={{ width: '100%', textAlign: 'center' }}>
                    <SecurityIcon sx={{ fontSize: 40, mb: 2, color: 'text.secondary' }} />
                    <Typography variant="h6" color="text.secondary">⚖️ Ryzyko Utraty</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Brak danych do analizy
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    const { 
        value = 0, 
        risk_level = 'low', 
        risk_factors = [],
        rationale = '', 
        strategy = '', 
        confidence = 0 
    } = data;

    // Konfiguracja poziomów ryzyka
    const getRiskConfig = (level, riskValue) => {
        if (level === 'high' || riskValue >= 70) {
            return {
                color: '#f44336',
                icon: <ErrorIcon />,
                label: 'Wysokie',
                emoji: '🚨',
                bgColor: '#f4433620'
            };
        }
        if (level === 'medium' || riskValue >= 30) {
            return {
                color: '#ff9800', 
                icon: <WarningIcon />,
                label: 'Średnie',
                emoji: '⚠️',
                bgColor: '#ff980020'
            };
        }
        return {
            color: '#4caf50',
            icon: <ShieldIcon />,
            label: 'Niskie', 
            emoji: '🛡️',
            bgColor: '#4caf5020'
        };
    };

    const riskConfig = getRiskConfig(risk_level, value);

    return (
        <Tooltip 
            title={
                <Box sx={{ p: 1, maxWidth: 400 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {riskConfig.emoji} Ryzyko: {value}% ({riskConfig.label})
                    </Typography>
                    
                    {risk_factors.length > 0 && (
                        <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'orange', mb: 1 }}>
                                ⚡ Czynniki ryzyka:
                            </Typography>
                            {risk_factors.map((factor, index) => (
                                <Typography 
                                    key={index} 
                                    variant="body2" 
                                    sx={{ fontSize: '0.8rem', ml: 1, mb: 0.5 }}
                                >
                                    • {factor}
                                </Typography>
                            ))}
                        </Box>
                    )}
                    
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
                        borderLeft: `4px solid ${riskConfig.color}`
                    }
                }}
            >
                <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 2 }}>
                    {/* Header */}
                    <Box sx={{ textAlign: 'center', mb: 2 }}>
                        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                            {riskConfig.emoji} Ryzyko Utraty
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            Prawdopodobieństwo utraty klienta
                        </Typography>
                    </Box>

                    {/* Risk Shield Icon */}
                    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                        <Box 
                            sx={{ 
                                width: 100, 
                                height: 100, 
                                borderRadius: '50%',
                                backgroundColor: riskConfig.bgColor,
                                border: `4px solid ${riskConfig.color}`,
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                mb: 2,
                                position: 'relative'
                            }}
                        >
                            {React.cloneElement(riskConfig.icon, { 
                                sx: { fontSize: 40, color: riskConfig.color, mb: 1 } 
                            })}
                            <Typography 
                                variant="h5" 
                                sx={{ 
                                    fontWeight: 'bold',
                                    color: riskConfig.color,
                                    lineHeight: 1
                                }}
                            >
                                {value}%
                            </Typography>
                        </Box>

                        {/* Risk Level Chip */}
                        <Chip 
                            label={`Ryzyko ${riskConfig.label}`}
                            sx={{ 
                                backgroundColor: riskConfig.bgColor,
                                color: riskConfig.color,
                                fontWeight: 'bold',
                                mb: 1
                            }}
                        />
                    </Box>

                    {/* Risk Factors Count */}
                    {risk_factors.length > 0 && (
                        <Box sx={{ textAlign: 'center', mt: 'auto', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                                {risk_factors.length} czynnik{risk_factors.length === 1 ? '' : risk_factors.length < 5 ? 'i' : 'ów'} ryzyka
                            </Typography>
                        </Box>
                    )}

                    {/* Footer */}
                    <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                            Najedź aby zobaczyć szczegóły
                        </Typography>
                    </Box>
                </CardContent>
            </Card>
        </Tooltip>
    );
};

export default ChurnRiskIndicator;
