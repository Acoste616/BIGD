import React from 'react';
import { 
    Box, 
    Typography, 
    Card,
    CardContent,
    Tooltip,
    LinearProgress
} from '@mui/material';
import { 
    ResponsiveContainer,
    RadialBarChart, 
    RadialBar,
    Cell
} from 'recharts';
import ThermostatIcon from '@mui/icons-material/Thermostat';

const PurchaseTemperatureGauge = ({ data, loading = false }) => {
    if (loading) {
        return (
            <Card elevation={2} sx={{ height: '250px', display: 'flex', alignItems: 'center' }}>
                <CardContent sx={{ width: '100%', textAlign: 'center' }}>
                    <ThermostatIcon sx={{ fontSize: 40, mb: 2, color: 'primary.main' }} />
                    <Typography variant="h6" gutterBottom>🌡️ Temperatura Zakupowa</Typography>
                    <LinearProgress sx={{ mt: 2 }} />
                </CardContent>
            </Card>
        );
    }

    if (!data) {
        return (
            <Card elevation={2} sx={{ height: '250px', display: 'flex', alignItems: 'center' }}>
                <CardContent sx={{ width: '100%', textAlign: 'center' }}>
                    <ThermostatIcon sx={{ fontSize: 40, mb: 2, color: 'text.secondary' }} />
                    <Typography variant="h6" color="text.secondary">🌡️ Temperatura Zakupowa</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Brak danych do analizy
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    const { value = 0, temperature_level = 'cold', rationale = '', strategy = '', confidence = 0 } = data;

    // Kolory temperatury
    const getTemperatureColor = (level, temp) => {
        if (level === 'hot' || temp >= 70) return '#f44336';      // Czerwony - gorący
        if (level === 'warm' || temp >= 40) return '#ff9800';     // Pomarańczowy - ciepły  
        return '#2196f3';                                          // Niebieski - zimny
    };

    // Emoji dla temperatury
    const getTemperatureEmoji = (level, temp) => {
        if (level === 'hot' || temp >= 70) return '🔥';
        if (level === 'warm' || temp >= 40) return '🌡️';
        return '❄️';
    };

    const temperatureColor = getTemperatureColor(temperature_level, value);
    const temperatureEmoji = getTemperatureEmoji(temperature_level, value);

    // Dane dla RadialBarChart
    const chartData = [{
        name: 'Temperature',
        value: value,
        fill: temperatureColor
    }];

    return (
        <Tooltip 
            title={
                <Box sx={{ p: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {temperatureEmoji} Temperatura: {value}% ({temperature_level})
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
                        borderLeft: `4px solid ${temperatureColor}`
                    }
                }}
            >
                <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    {/* Header */}
                    <Box sx={{ textAlign: 'center', mb: 2 }}>
                        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                            {temperatureEmoji} Temperatura Zakupowa
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            Jak "gorący" jest lead
                        </Typography>
                    </Box>

                    {/* Radial Chart */}
                    <Box sx={{ flexGrow: 1, minHeight: '120px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <RadialBarChart 
                                cx="50%" 
                                cy="50%" 
                                innerRadius="40%" 
                                outerRadius="80%" 
                                data={chartData}
                                startAngle={180}
                                endAngle={0}
                            >
                                <RadialBar 
                                    dataKey="value" 
                                    cornerRadius={10} 
                                    fill={temperatureColor}
                                />
                            </RadialBarChart>
                        </ResponsiveContainer>
                        
                        {/* Centered Value */}
                        <Box 
                            sx={{ 
                                position: 'absolute', 
                                top: '50%', 
                                left: '50%', 
                                transform: 'translate(-50%, -50%)',
                                textAlign: 'center'
                            }}
                        >
                            <Typography 
                                variant="h3" 
                                sx={{ 
                                    fontWeight: 'bold', 
                                    color: temperatureColor,
                                    lineHeight: 1
                                }}
                            >
                                {value}%
                            </Typography>
                            <Typography 
                                variant="caption" 
                                sx={{ 
                                    textTransform: 'uppercase',
                                    fontWeight: 'bold',
                                    color: temperatureColor 
                                }}
                            >
                                {temperature_level}
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

export default PurchaseTemperatureGauge;
