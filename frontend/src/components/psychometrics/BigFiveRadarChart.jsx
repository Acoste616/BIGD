import React from 'react';
import { 
    ResponsiveContainer, 
    RadarChart, 
    PolarGrid, 
    PolarAngleAxis, 
    PolarRadiusAxis, 
    Radar,
    Tooltip
} from 'recharts';
import { 
    Box, 
    Typography,
    useTheme
} from '@mui/material';

// Mapowanie nazw traits na polskie etykiety
const traitLabels = {
    openness: 'Otwartość',
    conscientiousness: 'Sumienność', 
    extraversion: 'Ekstrawersja',
    agreeableness: 'Ugodowość',
    neuroticism: 'Neurotyczność'
};

// Custom Tooltip z strategią sprzedażową
const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        const data = payload[0].payload;
        return (
            <Box
                sx={{
                    bgcolor: 'background.paper',
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    p: 2,
                    maxWidth: 300,
                    boxShadow: 2
                }}
            >
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {label}: {data.A}/10
                </Typography>
                
                <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary' }}>
                    <strong>Uzasadnienie:</strong>
                </Typography>
                <Typography variant="body2" sx={{ mb: 2, fontSize: '0.8rem' }}>
                    {data.rationale}
                </Typography>
                
                <Typography variant="body2" sx={{ mb: 1, color: 'primary.main', fontWeight: 'bold' }}>
                    💡 Strategia Sprzedażowa:
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                    {data.strategy}
                </Typography>
            </Box>
        );
    }
    return null;
};

const BigFiveRadarChart = ({ data }) => {
    const theme = useTheme();
    
    // 🔍 DEBUG: Log incoming data
    React.useEffect(() => {
        console.log('📊 [BIG FIVE RADAR CHART] Received data:', {
            hasData: !!data,
            dataKeys: data ? Object.keys(data) : 'No data',
            sampleTraits: data ? {
                openness: data.openness ? { score: data.openness.score, hasRationale: !!data.openness.rationale } : 'Missing',
                conscientiousness: data.conscientiousness ? { score: data.conscientiousness.score, hasRationale: !!data.conscientiousness.rationale } : 'Missing'
            } : 'No sample data'
        });
    }, [data]);
    
    // Przekształć dane z formatu API na poprawny format dla Recharts RadarChart
    const chartData = React.useMemo(() => {
        if (!data) return [];
        
        return Object.entries(data).map(([key, trait]) => ({
            subject: traitLabels[key] || key,        // ✅ POPRAWKA: subject zamiast trait
            A: (trait && trait.score) || 0,          // 🔧 NAPRAWA: Sprawdź czy trait nie jest null
            rationale: (trait && trait.rationale) || 'Brak danych',
            strategy: (trait && trait.strategy) || 'Identyfikacja w toku',
            fullMark: 10
        }));
    }, [data]);

    if (!data || chartData.length === 0) {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" color="text.secondary">
                    Brak danych Big Five do wyświetlenia
                </Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ width: '100%', minWidth: 350, height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={chartData} margin={{ top: 40, right: 40, bottom: 40, left: 40 }}>
                    <PolarGrid
                        stroke={theme.palette.divider}
                        strokeWidth={1}
                    />
                    <PolarAngleAxis
                        dataKey="subject"
                        tick={{
                            fontSize: 13,
                            fill: theme.palette.text.primary,
                            fontWeight: 600
                        }}
                        style={{
                            textAnchor: 'middle',
                            dominantBaseline: 'middle'
                        }}
                    />
                    <PolarRadiusAxis
                        angle={90}
                        domain={[0, 10]}
                        tick={{
                            fontSize: 11,
                            fill: theme.palette.text.secondary,
                            fontWeight: 500
                        }}
                        tickCount={6}
                        axisLine={false}
                    />
                    <Radar
                        name="Big Five"
                        dataKey="A"
                        stroke={theme.palette.primary.main}
                        fill={theme.palette.primary.main}
                        fillOpacity={0.2}
                        strokeWidth={2}
                        dot={{ 
                            r: 4, 
                            fill: theme.palette.primary.main,
                            strokeWidth: 2,
                            stroke: theme.palette.background.paper
                        }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                </RadarChart>
            </ResponsiveContainer>
            
            {/* Legenda */}
            <Box sx={{ mt: 2, textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary">
                    Skala: 0-10 • Najedź na punkt aby zobaczyć strategię sprzedażową
                </Typography>
            </Box>
        </Box>
    );
};

export default BigFiveRadarChart;
