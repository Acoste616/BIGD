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
import ClarifyingQuestions from './ClarifyingQuestions';

const PsychometricDashboard = ({ 
    analysisData, 
    loading = false, 
    isPolling = false, 
    attempts = 0, 
    maxAttempts = 12,
    interactionId = null,
    onClarificationAnswered = null,
    // 🧠⚡ ULTRA MÓZG v4.0: NOWE PROPSY
    surowePsychology = null,  // Surowe dane z Ultra Mózgu
    isUltraBrainReady = false, // Czy Ultra Mózg ma dane gotowe
    // NOWE PROPSY DLA INTEGRACJI Z SESJĄ
    sessionId = null,
    psychometricsData = null,
    psychometricsLoading = false
}) => {
    const [submitting, setSubmitting] = useState(false);
    
    // Stan ładowania
    if (loading || psychometricsLoading) {
        return (
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ textAlign: 'center', py: 4, flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
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

    // 🧠⚡ LOGIKA DECYZYJNA ULTRA MÓZGU
    // Priorytetyzuj surowe dane z Ultra Mózgu nad legacy analysisData
    let activePsychology, isUsingUltraBrain;
    
    // Jeśli mamy dane z nowego endpointu, użyj ich
    if (psychometricsData) {
        activePsychology = {
            big_five: psychometricsData.big_five,
            disc: psychometricsData.disc_profile,
            schwartz_values: psychometricsData.schwartz_values
        };
        isUsingUltraBrain = true;
        console.log('🧠⚡ [PSYCHOMETRIC DASHBOARD] Używam danych z nowego endpointu:', psychometricsData);
    } else if (isUltraBrainReady && surowePsychology) {
        // ULTRA MÓZG: Używamy surowych danych psychology
        activePsychology = surowePsychology;
        isUsingUltraBrain = true;
        console.log('🧠⚡ [PSYCHOMETRIC DASHBOARD] Używam danych z Ultra Mózgu:', surowePsychology);
    } else {
        // LEGACY: Używamy analysisData.cumulative_psychology
        activePsychology = analysisData?.cumulative_psychology || {};
        isUsingUltraBrain = false;
        console.log('🧠 [PSYCHOMETRIC DASHBOARD] Używam legacy danych:', analysisData?.cumulative_psychology);
    }
    
    // Debug logging
    console.log('PsychometricDashboard - analysisData:', analysisData);
    console.log('PsychometricDashboard - activePsychology:', activePsychology);
    console.log('PsychometricDashboard - isUsingUltraBrain:', isUsingUltraBrain);
    console.log('PsychometricDashboard - has big_five:', !!activePsychology?.big_five);
    console.log('PsychometricDashboard - has disc:', !!activePsychology?.disc);
    console.log('PsychometricDashboard - has schwartz:', !!activePsychology?.schwartz_values);

    // Brak danych (legacy lub Ultra Mózg)
    if (!analysisData && !isUsingUltraBrain && !psychometricsData) {
        return (
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ textAlign: 'center', py: 4, flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <PsychologyIcon sx={{ fontSize: 48, mb: 2, color: 'text.secondary' }} />
                    <Typography variant="h6" gutterBottom color="text.secondary">
                        Profil Psychometryczny
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {isUsingUltraBrain ? 
                            'Ultra Mózg przygotowuje szczegółową analizę psychologiczną...' :
                            'Oczekiwanie na dane do analizy psychologicznej...'
                        }
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    // ✅ ULTRA MÓZG v4.0: Sprawdzenie danych z activePsychology (priorytet dla Ultra Mózgu)
    const hasBigFive = activePsychology?.big_five && Object.keys(activePsychology.big_five).length > 0;
    const hasDisc = activePsychology?.disc && Object.keys(activePsychology.disc).length > 0;
    const hasSchwartz = activePsychology?.schwartz_values && Array.isArray(activePsychology.schwartz_values) && activePsychology.schwartz_values.length > 0;

    // 🔍 SZCZEGÓŁOWY DEBUG: Sprawdźmy strukturę danych (Ultra Mózg v4.0)
    console.log('🔍 [FULL DATA] analysisData:', analysisData);
    console.log('🔍 [ACTIVE PSYCHOLOGY] activePsychology:', activePsychology);
    console.log('🔍 [BIG FIVE] raw data:', activePsychology?.big_five);
    console.log('🔍 [DISC] raw data:', activePsychology?.disc);
    console.log('🔍 [SCHWARTZ] raw data:', activePsychology?.schwartz_values);
    console.log('🔍 [ARCHETYPE] customer_archetype:', analysisData?.customer_archetype);
    console.log('🔍 [FLAGS] hasBigFive:', hasBigFive, 'hasDisc:', hasDisc, 'hasSchwartz:', hasSchwartz);
    console.log('🧠⚡ [SOURCE] isUsingUltraBrain:', isUsingUltraBrain);

    // NOWA LOGIKA: Interactive Mode z ClarifyingQuestions component
    // analysisData może być psychometric_analysis OR ai_response_json
    console.log('🔍 PsychometricDashboard - sprawdzam clarifying questions w:', analysisData);
    
    // Sprawdź czy AI potrzebuje clarification (może być w różnych miejscach)
    const needsClarification = analysisData?.needs_clarification || 
                              analysisData?.mode === 'interactive';
    
    // Znajdź clarifying questions (mogą być w różnych strukturach)
    let clarifyingQuestions = analysisData?.clarifying_questions || [];
    
    // Fallback: konwertuj starą strukturę probing_questions
    if (!clarifyingQuestions.length && analysisData?.probing_questions) {
        clarifyingQuestions = analysisData.probing_questions.map((q, index) => ({
            id: `legacy_q${index + 1}`,
            question: typeof q === 'string' ? q : q.question || 'Pytanie AI',
            option_a: "Tak / Wysoki poziom",
            option_b: "Nie / Niski poziom", 
            psychological_target: "Ocena ogólna"
        }));
    }
    
    console.log('🔍 PsychometricDashboard - needsClarification:', needsClarification);
    console.log('🔍 PsychometricDashboard - clarifyingQuestions:', clarifyingQuestions);

    if (needsClarification && clarifyingQuestions.length > 0) {
        return (
            <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <ClarifyingQuestions
                    questions={clarifyingQuestions}
                    interactionId={interactionId}
                    onAnswerSubmitted={onClarificationAnswered}
                    loading={submitting}
                />
            </Box>
        );
    }

    if (!hasBigFive && !hasDisc && !hasSchwartz) {
        return (
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ textAlign: 'center', py: 4, flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
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
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
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
                                '🧠⚡ Ultra MóZG: Big Five • DISC • Wartości Schwartza' :
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
                </Box>
                
                {/* Wyświetlanie confidence score i podsumowania jeśli dostępne */}
                {(psychometricsData?.confidence_score || analysisData?.psychology_confidence) && (
                    <Box sx={{ mt: 1, p: 1, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                        <Typography variant="body2">
                            🔍 Pewność analizy: <strong>{psychometricsData?.confidence_score || analysisData?.psychology_confidence}%</strong>
                        </Typography>
                        {psychometricsData?.summary && (
                            <Typography variant="body2" sx={{ mt: 0.5 }}>
                                📝 {psychometricsData.summary}
                            </Typography>
                        )}
                    </Box>
                )}
            </Paper>

            {/* ✅ GŁÓWNE SEKCJE ANALIZY - Z WARUNKAMI RENDERINGU */}
            <Grid container spacing={3} sx={{ flexGrow: 1, overflow: 'auto' }}>
                {/* Big Five Radar Chart */}
                {hasBigFive && (
                    <Grid item xs={12} md={6}>
                        <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    📊 Model Big Five
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                    Pięć głównych wymiarów osobowości
                                </Typography>
                                <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <BigFiveRadarChart data={activePsychology?.big_five} />
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                )}

                {/* DISC Profile */}
                {hasDisc && (
                    <Grid item xs={12} md={6}>
                        <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    🎭 Profil DISC
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                    Style zachowania i komunikacji
                                </Typography>
                                <Box sx={{ flexGrow: 1 }}>
                                    <DiscProfileDisplay data={activePsychology?.disc} />
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                )}

                {/* Schwartz Values */}
                {hasSchwartz && (
                    <Grid item xs={12}>
                        <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    💎 Wartości Schwartza
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                    Kluczowe motywacje i systemy wartości klienta
                                </Typography>
                                <Box sx={{ flexGrow: 1 }}>
                                    <SchwartzValuesList data={activePsychology?.schwartz_values} />
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                )}
            </Grid>

            {/* Informacja o źródle analizy */}
            <Alert severity="info" sx={{ mt: 3 }}>
                <Typography variant="body2">
                    💡 <strong>Wskazówka:</strong> Najedź myszą na elementy wizualizacji aby zobaczyć 
                    szczegółowe strategie sprzedażowe dostosowane do profilu klienta.
                </Typography>
            </Alert>
        </Box>
    );
};

export default PsychometricDashboard;