import { useState, useEffect, useCallback } from 'react';
import { getInteractionById } from '../services';

/**
 * Hook do zarządzania danymi analizy psychometrycznej v3.0
 * NOWA ARCHITEKTURA: Pobiera session-level psychology zamiast interaction-level
 * 
 * Zmiana: analysisData zawiera teraz dane z session (cumulative_psychology, customer_archetype)
 */
export const usePsychometrics = (interactionId, options = {}) => {
    const { 
        autoFetch = true, 
        onError = null,
        enablePolling = true,  // KROK 2: Włącz inteligentne polling
        pollingInterval = 5000  // Co 5 sekund
    } = options;
    
    const [analysisData, setAnalysisData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [pollingActive, setPollingActive] = useState(false);
    const [attempts, setAttempts] = useState(0);

    const fetchAnalysisData = useCallback(async () => {
        if (!interactionId) return;
        
        try {
            setLoading(true);
            setError(null);
            
            // Pobierz pełne dane interakcji z API
            const interaction = await getInteractionById(interactionId);
            console.log('usePsychometrics v3.0 - pobrana interakcja:', interaction);
            
            // NOWA ARCHITEKTURA v3.0: Pobierz dane session-level psychology
            const session = interaction?.session;  // Session object z interaction
            const sessionPsychology = session?.cumulative_psychology || {};
            const customerArchetype = session?.customer_archetype || null;
            const psychologyConfidence = session?.psychology_confidence || 0;
            const activeClarifyingQuestions = session?.active_clarifying_questions || [];
            
            // Combined data z session-level psychology
            const combinedData = {
                // Session-level psychology data (NOWE v3.0)
                cumulative_psychology: sessionPsychology,
                customer_archetype: customerArchetype, 
                psychology_confidence: psychologyConfidence,
                active_clarifying_questions: activeClarifyingQuestions,
                
                // Backwards compatibility z interaction-level data
                ...sessionPsychology,  // Spread session psychology jako główne dane
                
                // Legacy fields dla compatibility
                needs_more_info: activeClarifyingQuestions.length > 0,
                clarifying_questions: activeClarifyingQuestions,
                analysis_confidence: psychologyConfidence
            };
            
            console.log('usePsychometrics v3.0 - session psychology:', sessionPsychology);
            console.log('usePsychometrics v3.0 - customer archetype:', customerArchetype);
            console.log('usePsychometrics v3.0 - combined data:', combinedData);
            console.log('usePsychometrics v3.0 - confidence:', psychologyConfidence);
            console.log('usePsychometrics v3.0 - attempts:', attempts + 1);
            
            setAnalysisData(combinedData);
            setAttempts(prev => prev + 1);
            
            // NOWA LOGIKA v3.0: Sprawdź różne typy kompletnych danych z session-level
            const hasFullPsychology = sessionPsychology.big_five || sessionPsychology.disc || sessionPsychology.schwartz_values;
            const hasArchetypeReady = customerArchetype && psychologyConfidence >= 75;
            const hasActiveQuestions = activeClarifyingQuestions.length > 0;
            const hasCompleteData = hasFullPsychology || hasArchetypeReady || hasActiveQuestions;
            
            console.log('🔍 usePsychometrics v3.0 - hasFullPsychology:', hasFullPsychology);
            console.log('🔍 usePsychometrics v3.0 - hasArchetypeReady:', hasArchetypeReady);
            console.log('🔍 usePsychometrics v3.0 - hasActiveQuestions:', hasActiveQuestions);
            console.log('🔍 usePsychometrics v3.0 - hasCompleteData:', hasCompleteData);
            
            if (hasCompleteData) {
                console.log('🎯 usePsychometrics - dane kompletne, zatrzymuję polling');
                setPollingActive(false); // Zatrzymaj polling gdy mamy dane
            } else if (enablePolling && attempts < 12) { // Max 12 prób = 1 minuta
                console.log('⏳ usePsychometrics - brak danych, kontynuuję polling...');
                setPollingActive(true); // Kontynuuj polling
            } else {
                console.log('⚠️ usePsychometrics - przekroczono limit prób lub polling wyłączony');
                setPollingActive(false);
            }
            
        } catch (err) {
            console.error('Błąd podczas pobierania analizy psychometrycznej:', err);
            setError(err.message || 'Nie udało się pobrać danych analizy');
            
            if (onError) {
                onError(err);
            }
        } finally {
            setLoading(false);
        }
    }, [interactionId, onError]);

    // Automatyczne pobieranie danych przy inicjalizacji
    useEffect(() => {
        if (autoFetch && interactionId) {
            setAttempts(0); // Reset prób
            fetchAnalysisData();
        }
    }, [autoFetch, interactionId, fetchAnalysisData]);

    // KROK 2: Inteligentne polling dla oczekiwania na dane background
    useEffect(() => {
        let pollingTimer = null;
        
        if (pollingActive && interactionId && enablePolling) {
            console.log(`⏳ usePsychometrics - uruchamiam polling co ${pollingInterval}ms`);
            
            pollingTimer = setInterval(() => {
                console.log(`🔄 usePsychometrics - polling attempt ${attempts + 1}/12`);
                fetchAnalysisData();
            }, pollingInterval);
        }
        
        // Cleanup
        return () => {
            if (pollingTimer) {
                console.log('🛑 usePsychometrics - zatrzymuję polling timer');
                clearInterval(pollingTimer);
            }
        };
    }, [pollingActive, interactionId, enablePolling, pollingInterval, attempts, fetchAnalysisData]);

    return {
        analysisData,
        loading,
        error,
        refetch: fetchAnalysisData,
        hasData: !!analysisData,
        // KROK 2: Dodatkowe informacje o polling
        isPolling: pollingActive,
        attempts,
        maxAttempts: 12
    };
};

/**
 * Hook do pobierania danych psychometrycznych z multiple interakcji
 * Przydatny dla widoków z historią sesji
 */
export const useMultiplePsychometrics = (interactionIds = []) => {
    const [analysisDataMap, setAnalysisDataMap] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchMultipleAnalyses = useCallback(async () => {
        if (!interactionIds.length) return;
        
        try {
            setLoading(true);
            setError(null);
            
            // Pobierz wszystkie interakcje równolegle
            const promises = interactionIds.map(id => 
                getInteractionById(id).catch(err => ({ id, error: err }))
            );
            
            const results = await Promise.all(promises);
            
            // Zbuduj mapę wyników
            const dataMap = {};
            results.forEach((result, index) => {
                const id = interactionIds[index];
                if (result.error) {
                    console.warn(`Błąd dla interakcji ${id}:`, result.error);
                } else {
                    dataMap[id] = result?.psychometric_analysis_result;
                }
            });
            
            setAnalysisDataMap(dataMap);
            
        } catch (err) {
            console.error('Błąd podczas pobierania wielu analiz psychometrycznych:', err);
            setError(err.message || 'Nie udało się pobrać danych');
        } finally {
            setLoading(false);
        }
    }, [interactionIds]);

    useEffect(() => {
        fetchMultipleAnalyses();
    }, [fetchMultipleAnalyses]);

    return {
        analysisDataMap,
        loading,
        error,
        refetch: fetchMultipleAnalyses,
        hasData: Object.keys(analysisDataMap).length > 0
    };
};

/**
 * Hook do agregacji danych psychometrycznych z sesji
 * Analizuje trendy w profilach psychometrycznych klienta w czasie
 */
export const usePsychometricTrends = (sessionInteractions = []) => {
    const [trends, setTrends] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const calculateTrends = () => {
            setLoading(true);
            
            try {
                // Filtruj interakcje z danymi psychometrycznymi
                const psychometricInteractions = sessionInteractions.filter(
                    interaction => interaction.psychometric_analysis
                );
                
                if (psychometricInteractions.length === 0) {
                    setTrends(null);
                    return;
                }
                
                // Analizuj trendy Big Five
                const bigFiveTrends = {};
                const bigFiveTraits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'];
                
                bigFiveTraits.forEach(trait => {
                    const scores = psychometricInteractions.map(interaction => 
                        interaction.psychometric_analysis?.big_five?.[trait]?.score
                    ).filter(score => score !== undefined);
                    
                    if (scores.length > 1) {
                        const trend = scores[scores.length - 1] - scores[0]; // Zmiana od pierwszej do ostatniej
                        bigFiveTrends[trait] = {
                            trend: trend > 1 ? 'growing' : trend < -1 ? 'declining' : 'stable',
                            change: trend,
                            latest: scores[scores.length - 1],
                            samples: scores.length
                        };
                    }
                });
                
                // Najbardziej stabilne wartości Schwartza
                const stableValues = [];
                const allValues = {};
                
                psychometricInteractions.forEach(interaction => {
                    const values = interaction.psychometric_analysis?.schwartz_values || [];
                    values.forEach(value => {
                        if (value.is_present) {
                            allValues[value.value_name] = (allValues[value.value_name] || 0) + 1;
                        }
                    });
                });
                
                // Wartości występujące w większości analiz
                Object.entries(allValues).forEach(([valueName, count]) => {
                    if (count >= psychometricInteractions.length * 0.6) { // 60% próg
                        stableValues.push({
                            name: valueName,
                            consistency: count / psychometricInteractions.length
                        });
                    }
                });
                
                setTrends({
                    bigFiveTrends,
                    stableValues: stableValues.sort((a, b) => b.consistency - a.consistency),
                    sampleSize: psychometricInteractions.length,
                    timespan: {
                        first: psychometricInteractions[0].timestamp,
                        last: psychometricInteractions[psychometricInteractions.length - 1].timestamp
                    }
                });
                
            } finally {
                setLoading(false);
            }
        };
        
        calculateTrends();
    }, [sessionInteractions]);

    return {
        trends,
        loading,
        hasTrends: !!trends && trends.sampleSize > 0
    };
};
