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
    onClarificationAnswered = null
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

    // Debug logging
    console.log('PsychometricDashboard - analysisData:', analysisData);
    console.log('PsychometricDashboard - has big_five:', !!analysisData?.big_five);
    console.log('PsychometricDashboard - has disc:', !!analysisData?.disc);
    console.log('PsychometricDashboard - has schwartz:', !!analysisData?.schwartz_values);

    // Brak danych - uproszczona logika
    if (!analysisData) {
        return (
            <Card>
                <CardContent sx={{ textAlign: 'center', py: 4 }}>
                    <PsychologyIcon sx={{ fontSize: 48, mb: 2, color: 'text.secondary' }} />
                    <Typography variant="h6" gutterBottom color="text.secondary">
                        Profil Psychometryczny
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Oczekiwanie na dane do analizy psychologicznej...
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    // ✅ POPRAWKA: Sprawdzenie danych z cumulative_psychology
    const hasBigFive = analysisData.cumulative_psychology?.big_five && Object.keys(analysisData.cumulative_psychology.big_five).length > 0;
    const hasDisc = analysisData.cumulative_psychology?.disc && Object.keys(analysisData.cumulative_psychology.disc).length > 0;
    const hasSchwartz = analysisData.cumulative_psychology?.schwartz_values && Array.isArray(analysisData.cumulative_psychology.schwartz_values) && analysisData.cumulative_psychology.schwartz_values.length > 0;

    // 🔍 SZCZEGÓŁOWY DEBUG: Sprawdźmy strukturę danych
    console.log('🔍 [FULL DATA] analysisData:', analysisData);
    console.log('🔍 [CUMULATIVE] cumulative_psychology:', analysisData.cumulative_psychology);
    console.log('🔍 [BIG FIVE] raw data:', analysisData.cumulative_psychology?.big_five);
    console.log('🔍 [DISC] raw data:', analysisData.cumulative_psychology?.disc);
    console.log('🔍 [SCHWARTZ] raw data:', analysisData.cumulative_psychology?.schwartz_values);
    console.log('🔍 [ARCHETYPE] customer_archetype:', analysisData.customer_archetype);
    console.log('🔍 [FLAGS] hasBigFive:', hasBigFive, 'hasDisc:', hasDisc, 'hasSchwartz:', hasSchwartz);

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
            {/* Header */}
            <Paper elevation={1} sx={{ p: 2, mb: 3, bgcolor: 'primary.main', color: 'primary.contrastText' }}>
                <Box display="flex" alignItems="center" gap={2}>
                    <PsychologyIcon sx={{ fontSize: 32 }} />
                    <Box>
                        <Typography variant="h6" component="h2">
                            Profil Psychometryczny Klienta
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                            Analiza AI: Big Five • DISC • Wartości Schwartza
                        </Typography>
                    </Box>
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
                                <BigFiveRadarChart data={analysisData.cumulative_psychology?.big_five} />
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
                                <DiscProfileDisplay data={analysisData.cumulative_psychology?.disc} />
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
                                <SchwartzValuesList data={analysisData.cumulative_psychology?.schwartz_values} />
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
