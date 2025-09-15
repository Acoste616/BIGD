import React from 'react';
import { 
    Box, 
    Typography, 
    Grid,
    Paper,
    Alert,
    Card,
    CardContent
} from '@mui/material';
import { 
    Analytics as AnalyticsIcon,
    TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

// Import komponentów wskaźników
import PurchaseTemperatureGauge from './PurchaseTemperatureGauge';
import JourneyStageFunnel from './JourneyStageFunnel';
import ChurnRiskIndicator from './ChurnRiskIndicator';
import SalesPotentialCard from './SalesPotentialCard';

const SalesIndicatorsDashboard = ({ 
    indicatorsData, 
    customerArchetype = null,
    psychologyConfidence = 0,
    cumulativePsychology = null,
    loading = false, 
    error = null,
    // 🧠⚡ ULTRA MÓZG v4.1: PRIORYTET 3 - Nowe propsy z DNA Klienta
    dnaKlienta = null,
    isDnaReady = false,
    strategia = null
}) => {
    
    // 🧠⚡ LOGIKA DECYZYJNA ULTRA MÓZGU - PRIORYTET 3
    // Priorytetyzuj sales indicators z strategii Ultra Mózgu nad legacy indicatorsData
    let activeIndicatorsData, isUsingUltraBrain, salesIndicatorsSource;
    
    if (isDnaReady && strategia?.sales_indicators) {
        // ULTRA MÓZG: Używamy wskaźników wygenerowanych na podstawie DNA Klienta
        activeIndicatorsData = strategia.sales_indicators;
        isUsingUltraBrain = true;
        salesIndicatorsSource = "Ultra Mózg DNA";
        console.log('🧠⚡ [SALES INDICATORS DASHBOARD] Używam wskaźników z Ultra Mózgu (DNA):', activeIndicatorsData);
    } else if (indicatorsData) {
        // LEGACY: Używamy legacy indicatorsData
        activeIndicatorsData = indicatorsData;
        isUsingUltraBrain = false;
        salesIndicatorsSource = "Legacy AI";
        console.log('🧠 [SALES INDICATORS DASHBOARD] Używam legacy wskaźników:', activeIndicatorsData);
    } else {
        activeIndicatorsData = null;
        isUsingUltraBrain = false;
        salesIndicatorsSource = "Brak danych";
        console.log('❌ [SALES INDICATORS DASHBOARD] Brak danych wskaźników');
    }
    // Loading state
    if (loading) {
        return (
            <Paper elevation={1} sx={{ p: 3, mb: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                    <AnalyticsIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                    <Box>
                        <Typography variant="h6" component="h2">
                            📊 Wskaźniki Sprzedażowe
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.7 }}>
                            AI analizuje dane w czasie rzeczywistym...
                        </Typography>
                    </Box>
                </Box>

                {/* Loading Grid */}
                <Grid container spacing={3} sx={{ flexGrow: 1 }}>
                    {[1, 2, 3, 4].map((item) => (
                        <Grid item xs={12} md={6} key={item}>
                            <PurchaseTemperatureGauge loading={true} />
                        </Grid>
                    ))}
                </Grid>
            </Paper>
        );
    }

    // Error state
    if (error) {
        return (
            <Paper elevation={1} sx={{ p: 3, mb: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                    <AnalyticsIcon sx={{ fontSize: 32, color: 'error.main' }} />
                    <Box>
                        <Typography variant="h6" component="h2">
                            📊 Wskaźniki Sprzedażowe
                        </Typography>
                        <Typography variant="body2" color="error" sx={{ opacity: 0.7 }}>
                            Wystąpił błąd podczas analizy
                        </Typography>
                    </Box>
                </Box>

                <Alert severity="error" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                        {error}
                    </Typography>
                </Alert>
            </Paper>
        );
    }

    // No data state
    if (!activeIndicatorsData) {
        return (
            <Paper elevation={1} sx={{ p: 3, mb: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                    <AnalyticsIcon sx={{ fontSize: 32, color: 'text.secondary' }} />
                    <Box>
                        <Typography variant="h6" component="h2">
                            📊 Wskaźniki Sprzedażowe
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.7 }}>
                            Analiza w toku - wskaźniki będą dostępne po zebraniu danych
                        </Typography>
                    </Box>
                </Box>

                <Alert severity="info" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                        🧠 <strong>Unified Psychology Engine:</strong> {customerArchetype ? `Archetyp "${customerArchetype.archetype_name}" zidentyfikowany, generowanie wskaźników...` : 'AI analizuje profil psychometryczny klienta (Big Five + DISC + Wartości) aby wygenerować personalizowane wskaźniki sprzedażowe.'}
                    </Typography>
                </Alert>
            </Paper>
        );
    }

    // Extract data for each indicator (z Ultra Mózgu lub legacy)
    const {
        purchase_temperature,
        customer_journey_stage, 
        churn_risk,
        sales_potential
    } = activeIndicatorsData;

    // Calculate overall score
    const calculateOverallScore = () => {
        if (!purchase_temperature?.value || !churn_risk?.value || !sales_potential?.probability) {
            return null;
        }
        
        const tempScore = purchase_temperature.value || 0;
        const riskScore = 100 - (churn_risk.value || 0); // Odwrotnie - mniejsze ryzyko = lepszy wynik
        const potentialScore = sales_potential.probability || 0;
        
        return Math.round((tempScore + riskScore + potentialScore) / 3);
    };

    const overallScore = calculateOverallScore();

    return (
        <Paper elevation={1} sx={{ p: 3, mb: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Header z ogólnym wynikiem i archetypem */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <AnalyticsIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                    <Box>
                        <Typography variant="h6" component="h2">
                            📊 Wskaźniki Sprzedażowe
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.7 }}>
                            {customerArchetype ? (
                                <>🎯 Analiza dla: {customerArchetype.archetype_name} ({psychologyConfidence}%)</>
                            ) : (
                                <>⏳ Analiza psychometryczna w toku...</>
                            )}
                        </Typography>
                    </Box>
                </Box>

                {/* Overall Score */}
                {overallScore !== null && (
                    <Box sx={{ textAlign: 'right' }}>
                        <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main', lineHeight: 1 }}>
                            {overallScore}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
                            Ogólny Wynik
                        </Typography>
                    </Box>
                )}
            </Box>

            {/* Grid wskaźników */}
            <Grid container spacing={3} sx={{ flexGrow: 1 }}>
                {/* Temperatura Zakupowa */}
                <Grid item xs={12} md={6}>
                    <PurchaseTemperatureGauge 
                        data={purchase_temperature} 
                        loading={loading}
                    />
                </Grid>

                {/* Etap Podróży */}
                <Grid item xs={12} md={6}>
                    <JourneyStageFunnel 
                        data={customer_journey_stage}
                        loading={loading}
                    />
                </Grid>

                {/* Ryzyko Utraty */}
                <Grid item xs={12} md={6}>
                    <ChurnRiskIndicator 
                        data={churn_risk}
                        loading={loading}
                    />
                </Grid>

                {/* Potencjał Sprzedażowy */}
                <Grid item xs={12} md={6}>
                    <SalesPotentialCard 
                        data={sales_potential}
                        loading={loading}
                    />
                </Grid>
            </Grid>

            {/* 🧠⚡ PRIORYTET 3: Enhanced informacja o źródle danych */}
            <Alert severity={isUsingUltraBrain ? "success" : "info"} sx={{ mt: 2 }}>
                <Typography variant="body2">
                    <TrendingUpIcon sx={{ fontSize: 16, mr: 1, verticalAlign: 'text-bottom' }} />
                    <strong>{isUsingUltraBrain ? '🧠⚡ Ultra Mózg DNA Engine:' : '🧠 Legacy Psychology Engine:'}</strong> 
                    {isUsingUltraBrain ? (
                        <>Wskaźniki wygenerowane na podstawie DNA Klienta (holistic profile) przez Ultra Mózg. Źródło: {salesIndicatorsSource} - {isDnaReady ? 'DNA Ready' : 'Fallback Mode'}</>
                    ) : customerArchetype ? (
                        <>Wskaźniki generowane dla archetypu <strong>{customerArchetype.archetype_name}</strong> ({psychologyConfidence}% pewności) na podstawie profilu Big Five + DISC + Wartości Schwartza. Źródło: {salesIndicatorsSource}</>
                    ) : (
                        <>Analiza psychometryczna w toku - wskaźniki będą dostępne po identyfikacji archetypu klienta. Źródło: {salesIndicatorsSource}</>
                    )}
                </Typography>
            </Alert>
        </Paper>
    );
};

export default SalesIndicatorsDashboard;