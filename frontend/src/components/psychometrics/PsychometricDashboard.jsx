import React, { useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Paper,
    Alert,
    Stack
} from '@mui/material';
import PsychologyIcon from '@mui/icons-material/Psychology';
import BigFiveRadarChart from './BigFiveRadarChart';
import DiscProfileDisplay from './DiscProfileDisplay';
import SchwartzValuesList from './SchwartzValuesList';
import CustomerArchetypeDisplay from './CustomerArchetypeDisplay';


const PsychometricDashboard = ({ 
    analysisData, 
    loading = false, 
    isPolling = false, 
    attempts = 0, 
    maxAttempts = 12,
    interactionId = null,
    onClarificationAnswered = null,
    // 🧠⚡ ULTRA MÓZG v4.2.0: NOWE PROPSY
    cumulativePsychology = null,  // cumulative_psychology z sesji
    isPsychologyReady = false,    // Czy profil psychologiczny jest gotowy
    dnaKlienta = null,           // holistic_psychometric_profile z sesji
    isDnaReady = false           // Czy DNA jest gotowe
}) => {
    const [submitting, setSubmitting] = useState(false);
    
    // Stan ładowania
    if (loading) {
        return (
            <Card>
                <CardContent sx={{ textAlign: 'center', py: 4 }}>
                    <PsychologyIcon sx={{ fontSize: 48, mb: 2, color: 'primary.main' }} />
                    <Typography variant="h6" gutterBottom>
                        Analiza Psychometryczna w Toku...
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        AI analizuje profil psychologiczny klienta
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    // 🧠⚡ LOGIKA DECYZYJNA ULTRA MÓZGU v4.2.0
    // Priorytetyzuj dane z nowej architektury backendu
    let activePsychology, isUsingUltraBrain;

    if (isPsychologyReady && cumulativePsychology) {
        // ULTRA MÓZG v4.2.0: Używamy cumulative_psychology z sesji
        activePsychology = cumulativePsychology;
        isUsingUltraBrain = true;
        console.log('🧠⚡ [PSYCHOMETRIC DASHBOARD v4.2.0] Używam danych z nowej architektury:', cumulativePsychology);
    } else {
        // LEGACY: Używamy analysisData.cumulative_psychology
        activePsychology = analysisData?.cumulative_psychology || {};
        isUsingUltraBrain = false;
        console.log('🧠 [PSYCHOMETRIC DASHBOARD] Używam legacy danych:', analysisData?.cumulative_psychology);
    }

    // KALIBRACJA: Określ poziom analizy
    const analysisLevel = analysisData?.analysis_level || 'pełna'; // Domyślnie pełna dla kompatybilności wstecznej
    const isPreliminaryAnalysis = analysisLevel === 'wstępna';
    const interactionCount = analysisData?.interaction_count || 0;

    console.log('🎯 [ANALYSIS LEVEL] Poziom analizy:', analysisLevel, 'Wstępna:', isPreliminaryAnalysis, 'Interakcje:', interactionCount);
    
    // Debug logging
    console.log('PsychometricDashboard v4.2.0 - analysisData:', analysisData);
    console.log('PsychometricDashboard v4.2.0 - activePsychology:', activePsychology);
    console.log('PsychometricDashboard v4.2.0 - isUsingUltraBrain:', isUsingUltraBrain);
    console.log('PsychometricDashboard v4.2.0 - has big_five:', !!activePsychology?.big_five);
    console.log('PsychometricDashboard v4.2.0 - has disc:', !!activePsychology?.disc);
    console.log('PsychometricDashboard v4.2.0 - has schwartz:', !!activePsychology?.schwartz_values);

    // Brak danych (legacy lub Ultra Mózg)
    if (!analysisData && !isUsingUltraBrain) {
        return (
            <Card>
                <CardContent sx={{ textAlign: 'center', py: 4 }}>
                    <PsychologyIcon sx={{ fontSize: 48, mb: 2, color: 'text.secondary' }} />
                    <Typography variant="h6" gutterBottom color="text.secondary">
                        Profil Psychometryczny
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {isUsingUltraBrain ? 
                            'Ultra Mózg v4.2.0 przygotowuje szczegółową analizę psychologiczną...' :
                            'Oczekiwanie na dane do analizy psychologicznej...'
                        }
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    // ✅ ULTRA MÓZG v4.2.0: Sprawdzenie danych z activePsychology (priorytet dla nowej architektury)
    const hasBigFive = activePsychology?.big_five && Object.keys(activePsychology.big_five).length > 0;
    const hasDisc = activePsychology?.disc && Object.keys(activePsychology.disc).length > 0;
    const hasSchwartz = activePsychology?.schwartz_values && Array.isArray(activePsychology.schwartz_values) && activePsychology.schwartz_values.length > 0;

    // 🔍 SZCZEGÓŁOWY DEBUG: Sprawdźmy strukturę danych (Ultra Mózg v4.2.0)
    console.log('🔍 [FULL DATA v4.2.0] analysisData:', analysisData);
    console.log('🔍 [ACTIVE PSYCHOLOGY v4.2.0] activePsychology:', activePsychology);
    console.log('🔍 [BIG FIVE] raw data:', activePsychology?.big_five);
    console.log('🔍 [DISC] raw data:', activePsychology?.disc);
    console.log('🔍 [SCHWARTZ] raw data:', activePsychology?.schwartz_values);
    console.log('🔍 [ARCHETYPE] customer_archetype:', analysisData?.customer_archetype);
    console.log('🔍 [FLAGS] hasBigFive:', hasBigFive, 'hasDisc:', hasDisc, 'hasSchwartz:', hasSchwartz);
    console.log('🧠⚡ [SOURCE] isUsingUltraBrain:', isUsingUltraBrain);

    // USUNIĘTO: Przestarzały komponent ClarifyingQuestions - funkcjonalność przeniesiona do Ultra Mózgu

    if (!hasBigFive && !hasDisc && !hasSchwartz) {
        return (
            <Card>
                <CardContent sx={{ textAlign: 'center', py: 4 }}>
                    <PsychologyIcon sx={{ fontSize: 48, mb: 2, color: 'warning.main' }} />
                    <Typography variant="h6" gutterBottom color="text.secondary">
                        Profil Psychometryczny
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Analiza psychometryczna w toku...
                    </Typography>
                    
                    {/* KROK 2: Polling Status */}
                    {isPolling && (
                        <Alert severity="info" sx={{ mt: 2, textAlign: 'left' }}>
                            <Typography variant="body2">
                                🔄 <strong>Czekam na AI:</strong> Próba {attempts}/{maxAttempts}
                                <br />
                                💡 System automatycznie odpytuje backend co 5 sekund...
                            </Typography>
                        </Alert>
                    )}
                    
                    {!isPolling && attempts > 0 && (
                        <Alert severity="warning" sx={{ mt: 2, textAlign: 'left' }}>
                            <Typography variant="body2">
                                ⏰ <strong>Limit prób osiągnięty:</strong> {attempts}/{maxAttempts}
                                <br />
                                🔄 Spróbuj odświeżyć lub utworzyć nową interakcję
                            </Typography>
                        </Alert>
                    )}
                </CardContent>
            </Card>
        );
    }

    // Główny dashboard z analizą
    return (
        <Box>
            {/* Header z Ultra Mózg Badge */}
            <Paper elevation={1} sx={{ p: 2, mb: 3, bgcolor: 'primary.main', color: 'primary.contrastText', position: 'relative' }}>
                <Box display="flex" alignItems="center" gap={2}>
                    <PsychologyIcon sx={{ fontSize: 32 }} />
                    <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" component="h2">
                            Profil Psychometryczny Klienta
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                            {isUsingUltraBrain ? 
                                '🧠⚡ Ultra Mózg: Big Five • DISC • Wartości Schwartza' :
                                'Analiza AI: Big Five • DISC • Wartości Schwartza'
                            }
                        </Typography>
                    </Box>
                    {isUsingUltraBrain && (
                        <Box sx={{
                            position: 'absolute',
                            top: -8,
                            right: 16,
                            bgcolor: 'secondary.main',
                            color: 'secondary.contrastText',
                            px: 1.5,
                            py: 0.5,
                            borderRadius: 2,
                            fontSize: '0.75rem',
                            fontWeight: 'bold'
                        }}>
                            🧠⚡ ULTRA MÓZG
                        </Box>
                    )}

                    {/* KALIBRACJA: Komunikat o poziomie analizy */}
                    {isPreliminaryAnalysis && (
                        <Box sx={{
                            position: 'absolute',
                            bottom: -8,
                            left: 16,
                            bgcolor: 'warning.main',
                            color: 'warning.contrastText',
                            px: 1.5,
                            py: 0.5,
                            borderRadius: 2,
                            fontSize: '0.75rem',
                            fontWeight: 'bold'
                        }}>
                            📊 ANALIZA WSTĘPNA ({interactionCount} interakcji)
                        </Box>
                    )}
                </Box>
            </Paper>

            {/* 🚀 ULTRA MÓZG v4.1 - ARCHETYP KLIENTA TESLI */}
            {analysisData?.customer_archetype && (
                <Box sx={{ mb: 3 }}>
                    <CustomerArchetypeDisplay
                        customerArchetype={analysisData.customer_archetype}
                        psychologyConfidence={analysisData.psychology_confidence || 0}
                        loading={loading}
                        dnaKlienta={dnaKlienta}
                        isDnaReady={isDnaReady}
                    />
                </Box>
            )}

            {/* ✅ GŁÓWNE SEKCJE ANALIZY - Z WARUNKAMI RENDERINGU */}
            <Grid container spacing={3}>
                {/* Big Five Radar Chart */}
                {hasBigFive && (
                    <Grid item xs={12} md={6}>
                        <Card elevation={2}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    📊 Model Big Five
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                    Pięć głównych wymiarów osobowości
                                </Typography>
                                <BigFiveRadarChart data={activePsychology?.big_five} />
                            </CardContent>
                        </Card>
                    </Grid>
                )}

                {/* DISC Profile */}
                {hasDisc && (
                    <Grid item xs={12} md={6}>
                        <Card elevation={2}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    🎭 Profil DISC
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                    Style zachowania i komunikacji
                                </Typography>
                                <DiscProfileDisplay data={activePsychology?.disc} />
                            </CardContent>
                        </Card>
                    </Grid>
                )}

                {/* Schwartz Values */}
                {hasSchwartz && (
                    <Grid item xs={12}>
                        <Card elevation={2}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    💎 Wartości Schwartza
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                    Kluczowe motywacje i systemy wartości klienta
                                </Typography>
                                <SchwartzValuesList data={activePsychology?.schwartz_values} />
                            </CardContent>
                        </Card>
                    </Grid>
                )}
            </Grid>

            {/* KALIBRACJA: Komunikat o analizie wstępnej */}
            {isPreliminaryAnalysis && (
                <Alert severity="warning" sx={{ mt: 3 }}>
                    <Typography variant="body2">
                        ⚠️ <strong>Analiza wstępna:</strong> Profil został utworzony na podstawie {interactionCount} interakcji.
                        Dodaj więcej obserwacji, aby zwiększyć precyzję analizy psychologicznej i uzyskać bardziej trafne strategie sprzedażowe.
                    </Typography>
                </Alert>
            )}

            {/* Informacja o źródle analizy */}
            <Alert severity="info" sx={{ mt: isPreliminaryAnalysis ? 1 : 3 }}>
                <Typography variant="body2">
                    💡 <strong>Wskazówka:</strong> Najedź myszą na elementy wizualizacji aby zobaczyć
                    szczegółowe strategie sprzedażowe dostosowane do profilu klienta.
                </Typography>
            </Alert>
        </Box>
    );
};

export default PsychometricDashboard;
