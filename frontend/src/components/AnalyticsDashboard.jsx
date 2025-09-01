/**
 * Komponent wizualizacyjny dla wskaźników analitycznych sesji
 * Wyświetla PRL (Purchase Readiness Level) i FDS (Fun Driver Score) z gauges i podsumowaniem
 */
import React, { forwardRef, useImperativeHandle } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  CircularProgress, 
  Skeleton, 
  Chip, 
  Tooltip 
} from '@mui/material';
import { useSessionAnalytics } from '../hooks/useSessionAnalytics';

/**
 * Funkcja określająca kolor dla wskaźnika PRL
 * @param {number} score - Wartość PRL (0-100)
 * @returns {string} Kolor Material-UI
 */
const getPrlColor = (score) => {
    if (score > 66) return 'success';
    if (score > 33) return 'warning';
    return 'error';
};

/**
 * Funkcja określająca kolor dla wskaźnika FDS (odwrotnie - niski FDS to dobrze)
 * @param {number} score - Wartość FDS (0-100)
 * @returns {string} Kolor Material-UI
 */
const getFdsColor = (score) => {
    if (score > 66) return 'error';
    if (score > 33) return 'warning';
    return 'success';
};

/**
 * Komponent wizualizacji wskaźnika w formie circular progress z wartością
 * @param {Object} props - Właściwości komponentu
 */
const ScoreGauge = ({ value, label, color, tooltip }) => (
    <Tooltip title={tooltip} arrow>
        <Box position="relative" display="inline-flex" flexDirection="column" alignItems="center">
            <Box position="relative" display="inline-flex">
                <CircularProgress 
                    variant="determinate" 
                    value={100} 
                    sx={{ color: (theme) => theme.palette.grey[300] }} 
                    size={80} 
                    thickness={4} 
                />
                <CircularProgress 
                    variant="determinate" 
                    value={value} 
                    color={color} 
                    size={80} 
                    thickness={4} 
                    sx={{ position: 'absolute', left: 0 }} 
                />
                <Box 
                    top={0} 
                    left={0} 
                    bottom={0} 
                    right={0} 
                    position="absolute" 
                    display="flex" 
                    alignItems="center" 
                    justifyContent="center"
                >
                    <Typography variant="h6" component="div" color="text.primary">
                        {`${Math.round(value)}%`}
                    </Typography>
                </Box>
            </Box>
            <Typography variant="caption" component="div" color="text.secondary" mt={1}>
                {label}
            </Typography>
        </Box>
    </Tooltip>
);

/**
 * Główny komponent dashboardu analitycznego z możliwością odświeżania przez ref
 */
const AnalyticsDashboard = forwardRef(({ sessionId }, ref) => {
    const { data, loading, error, refresh } = useSessionAnalytics(sessionId);

    // Udostępnienie funkcji refresh przez ref
    useImperativeHandle(ref, () => ({
        refresh,
    }));

    if (loading) {
        return <Skeleton variant="rounded" width="100%" height={220} />;
    }
    
    if (error) {
        return <Typography color="error">Błąd ładowania analityki.</Typography>;
    }
    
    if (!data) {
        return null;
    }

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    Analityka Sesji
                </Typography>
                
                <Box display="flex" justifyContent="space-around" my={2}>
                    <ScoreGauge 
                        value={data.prl_score} 
                        label="Gotowość do Zakupu" 
                        color={getPrlColor(data.prl_score)} 
                        tooltip="Wskaźnik określający, jak blisko klient jest podjęcia decyzji o zakupie." 
                    />
                    <ScoreGauge 
                        value={data.fds_score} 
                        label="Ryzyko Fun Drivera" 
                        color={getFdsColor(data.fds_score)} 
                        tooltip="Wskaźnik określający, czy motywacją klienta jest głównie 'przejażdżka dla zabawy'." 
                    />
                </Box>
                
                <Typography variant="body2" align="center" fontStyle="italic">
                    "{data.summary}"
                </Typography>
                
                <Box mt={2}>
                    <Typography variant="subtitle2" color="text.secondary">
                        Dominujące Cechy:
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                        {data.dominant_traits.map(trait => (
                            <Chip key={trait} label={trait} size="small" />
                        ))}
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );
});

// Dodanie displayName dla lepszego debugowania
AnalyticsDashboard.displayName = 'AnalyticsDashboard';

export default AnalyticsDashboard;
