import React from 'react';
import { 
    Box, 
    Typography, 
    Card,
    CardContent,
    Tooltip,
    Stepper,
    Step,
    StepLabel,
    LinearProgress,
    Chip
} from '@mui/material';
import { 
    Lightbulb as AwarenessIcon,
    Compare as ConsiderationIcon, 
    Assessment as EvaluationIcon,
    CheckCircle as DecisionIcon,
    ShoppingCart as PurchaseIcon
} from '@mui/icons-material';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';

const JourneyStageFunnel = ({ data, loading = false }) => {
    if (loading) {
        return (
            <Card elevation={2} sx={{ height: '250px', display: 'flex', alignItems: 'center' }}>
                <CardContent sx={{ width: '100%', textAlign: 'center' }}>
                    <TravelExploreIcon sx={{ fontSize: 40, mb: 2, color: 'primary.main' }} />
                    <Typography variant="h6" gutterBottom>🗺️ Etap Podróży</Typography>
                    <LinearProgress sx={{ mt: 2 }} />
                </CardContent>
            </Card>
        );
    }

    if (!data) {
        return (
            <Card elevation={2} sx={{ height: '250px', display: 'flex', alignItems: 'center' }}>
                <CardContent sx={{ width: '100%', textAlign: 'center' }}>
                    <TravelExploreIcon sx={{ fontSize: 40, mb: 2, color: 'text.secondary' }} />
                    <Typography variant="h6" color="text.secondary">🗺️ Etap Podróży</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Brak danych do analizy
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    const { 
        value = 'awareness', 
        progress_percentage = 0, 
        next_stage = null,
        rationale = '', 
        strategy = '', 
        confidence = 0 
    } = data;

    // Definicja etapów podróży
    const journeyStages = [
        { key: 'awareness', label: 'Świadomość', icon: <AwarenessIcon />, color: '#9e9e9e' },
        { key: 'consideration', label: 'Rozważanie', icon: <ConsiderationIcon />, color: '#2196f3' },
        { key: 'evaluation', label: 'Ocena', icon: <EvaluationIcon />, color: '#ff9800' },
        { key: 'decision', label: 'Decyzja', icon: <DecisionIcon />, color: '#4caf50' },
        { key: 'purchase', label: 'Zakup', icon: <PurchaseIcon />, color: '#f44336' }
    ];

    // Znajdź indeks aktualnego etapu
    const currentStageIndex = journeyStages.findIndex(stage => stage.key === value);
    const currentStage = journeyStages[currentStageIndex] || journeyStages[0];

    // Polskie tłumaczenia
    const getPolishStageName = (stageKey) => {
        const translations = {
            'awareness': 'Świadomość Potrzeby',
            'consideration': 'Rozważanie Opcji', 
            'evaluation': 'Ocena i Porównanie',
            'decision': 'Podejmowanie Decyzji',
            'purchase': 'Finalizacja Zakupu'
        };
        return translations[stageKey] || stageKey;
    };

    return (
        <Tooltip 
            title={
                <Box sx={{ p: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        🗺️ Etap: {getPolishStageName(value)} ({progress_percentage}%)
                    </Typography>
                    {next_stage && (
                        <Typography variant="body2" sx={{ mb: 1, color: 'lightblue' }}>
                            Następny: {getPolishStageName(next_stage)}
                        </Typography>
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
                        borderLeft: `4px solid ${currentStage.color}`
                    }
                }}
            >
                <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 2 }}>
                    {/* Header */}
                    <Box sx={{ textAlign: 'center', mb: 2 }}>
                        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                            🗺️ Etap Podróży
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            Pozycja w lejku sprzedażowym
                        </Typography>
                    </Box>

                    {/* Progress Bar */}
                    <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="body2" color="text.secondary">
                                Postęp
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 'bold', color: currentStage.color }}>
                                {progress_percentage}%
                            </Typography>
                        </Box>
                        <LinearProgress 
                            variant="determinate" 
                            value={progress_percentage} 
                            sx={{ 
                                height: 8, 
                                borderRadius: 4,
                                backgroundColor: 'grey.300',
                                '& .MuiLinearProgress-bar': {
                                    backgroundColor: currentStage.color,
                                    borderRadius: 4
                                }
                            }}
                        />
                    </Box>

                    {/* Current Stage Display */}
                    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                        <Box 
                            sx={{ 
                                width: 80, 
                                height: 80, 
                                borderRadius: '50%',
                                backgroundColor: currentStage.color + '20',
                                border: `3px solid ${currentStage.color}`,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                mb: 2
                            }}
                        >
                            {React.cloneElement(currentStage.icon, { 
                                sx: { fontSize: 32, color: currentStage.color } 
                            })}
                        </Box>
                        
                        <Typography 
                            variant="h6" 
                            sx={{ 
                                fontWeight: 'bold',
                                color: currentStage.color,
                                textAlign: 'center',
                                mb: 1
                            }}
                        >
                            {getPolishStageName(value)}
                        </Typography>
                        
                        <Chip 
                            label={`Etap ${currentStageIndex + 1}/5`}
                            size="small"
                            sx={{ 
                                backgroundColor: currentStage.color + '20',
                                color: currentStage.color,
                                fontWeight: 'bold'
                            }}
                        />
                    </Box>

                    {/* Next Stage Hint */}
                    {next_stage && (
                        <Box sx={{ textAlign: 'center', mt: 'auto' }}>
                            <Typography variant="caption" color="text.secondary">
                                Następny: {getPolishStageName(next_stage)}
                            </Typography>
                        </Box>
                    )}

                    {/* Footer */}
                    <Box sx={{ textAlign: 'center', mt: 1 }}>
                        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                            Najedź aby zobaczyć strategię
                        </Typography>
                    </Box>
                </CardContent>
            </Card>
        </Tooltip>
    );
};

export default JourneyStageFunnel;
