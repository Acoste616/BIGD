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
    isUltraBrainReady = false // Czy Ultra Mózg ma dane gotowe
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

    // 🧠⚡ LOGIKA DECYZYJNA ULTRA MÓZGU
    // Priorytetyzuj surowe dane z Ultra Mózgu nad legacy analysisData
    let activePsychology, isUsingUltraBrain;
    
    if (isUltraBrainReady && surowePsychology) {
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
            <Box>
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
                </Box>
            </Paper>

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
