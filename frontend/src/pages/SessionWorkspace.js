import React, { useEffect, useCallback } from 'react';
import { Grid, Box } from '@mui/material';
import { useParams } from 'react-router-dom';

// Import istniejących i nowych komponentów
import StrategicPanel from '../components/conversation/StrategicPanel';
import ConversationView from '../components/ConversationView'; // Zakładając, że to jest główny widok czatu/notatek
import QuestionsPanel from '../components/conversation/QuestionsPanel'; // Nowy komponent
import PsychometricDashboard from '../components/psychometrics/PsychometricDashboard';
import SalesIndicatorsDashboard from '../components/indicators/SalesIndicatorsDashboard';
import { useSessionPsychometrics } from '../hooks/usePsychometrics';
import { useSalesIndicators } from '../hooks/useSalesIndicators';

const SessionWorkspace = () => {
    const { sessionId } = useParams(); // Pobranie ID sesji z URL
    const {
        psychometricsData,
        loading: psychometricsLoading,
        error: psychometricsError,
        refetch: refetchPsychometrics
    } = useSessionPsychometrics(sessionId, { autoFetch: true });

    const {
        indicatorsData: salesIndicatorsData,
        loading: salesIndicatorsLoading,
        error: salesIndicatorsError,
        refetch: refetchSalesIndicators
    } = useSalesIndicators(sessionId, { autoFetch: true });

    // Funkcja do odświeżania danych psychometrycznych
    const handleInteractionAdded = useCallback(() => {
        // Po dodaniu nowej interakcji, odśwież dane psychometryczne
        if (sessionId) {
            refetchPsychometrics();
            // Odśwież również wskaźniki sprzedażowe
            refetchSalesIndicators();
        }
    }, [sessionId, refetchPsychometrics, refetchSalesIndicators]);

    return (
        <Box sx={{ flexGrow: 1, p: 2, height: 'calc(100vh - 64px)', overflow: 'hidden' /* Wysokość minus Appbar */ }}>
            <Grid container spacing={2} sx={{ height: '100%' }}>
                {/* === LEWA KOLUMNA: PYTANIA === */}
                {/* <Grid item xs={12} md={3} lg={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
                        <QuestionsPanel sessionId={sessionId} />
                    </Box>
                </Grid> */}

                {/* === CENTRALNA KOLUMNA: GŁÓWNY WIDOK PRACY === */}
                {/* <Grid item xs={12} md={5} lg={5} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    {/* Ten komponent zawiera historię interakcji i pole do wprowadzania danych */}
                    {/* <Box sx={{ flexGrow: 1, mb: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
                        <ConversationView sessionId={sessionId} onInteractionAdded={handleInteractionAdded} />
                    </Box>
                    
                    {/* Dashboard psychometryczny */}
                    {/* <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                        <PsychometricDashboard 
                            sessionId={sessionId}
                            psychometricsData={psychometricsData}
                            psychometricsLoading={psychometricsLoading}
                        />
                    </Box> */}
                {/* </Grid> */}

                {/* === PRAWA KOLUMNA: PANEL STRATEGICZNY === */}
                <Grid item xs={12} md={4} lg={4} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    {/* <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
                        <StrategicPanel sessionId={sessionId} />
                    </Box> */}
                    {/* Dashboard wskaźników sprzedażowych */}
                    <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column' }}>
                        <SalesIndicatorsDashboard
                            indicatorsData={salesIndicatorsData}
                            loading={salesIndicatorsLoading}
                            error={salesIndicatorsError}
                            customerArchetype={psychometricsData?.archetype}
                            psychologyConfidence={psychometricsData?.confidence_score}
                            cumulativePsychology={psychometricsData?.big_five ? {
                                big_five: psychometricsData.big_five,
                                disc: psychometricsData.disc_profile,
                                schwartz_values: psychometricsData.schwartz_values
                            } : null}
                        />
                    </Box>
                </Grid>
            </Grid>
        </Box>
    );
};

export default SessionWorkspace;