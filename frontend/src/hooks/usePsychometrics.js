import { useState, useEffect, useCallback } from 'react';
import { getInteractionById } from '../services';

/**
 * Funkcja pomocnicza do sprawdzania stabilności danych między iteracjami
 * PRZYORYTET 1: Zapewnia, że dane przestały się zmieniać przed zakończeniem polling
 */
const checkDataStability = (currentData, previousData) => {
  if (!previousData || !currentData) return false;

  // Sprawdź kluczowe pola psychometryczne
  const currentPsych = currentData.cumulative_psychology || {};
  const previousPsych = previousData.cumulative_psychology || {};

  // Porównaj Big Five (główne cechy)
  const currentBigFive = currentPsych.big_five || {};
  const previousBigFive = previousPsych.big_five || {};

  const bigFiveStable = Object.keys(currentBigFive).every(trait => {
    const currentScore = currentBigFive[trait]?.score;
    const previousScore = previousBigFive[trait]?.score;
    return Math.abs((currentScore || 0) - (previousScore || 0)) < 0.1; // Tolerancja 0.1
  });

  // Porównaj archetyp klienta
  const archetypeStable = currentData.customer_archetype === previousData.customer_archetype;

  // Porównaj confidence level
  const confidenceStable = Math.abs(
    (currentData.psychology_confidence || 0) - (previousData.psychology_confidence || 0)
  ) < 1; // Tolerancja 1%

    return bigFiveStable && archetypeStable && confidenceStable;
};

/**
 * Hook do zarządzania danymi analizy psychometrycznej v4.0
 * NOWA ARCHITEKTURA: Pobiera session-level psychology z rygorystycznym sprawdzaniem stabilności
 *
 * Zmiana: analysisData zawiera teraz dane z session (cumulative_psychology, customer_archetype)
 * PRZYORYTET 1: Polling trwa dopóki dane nie są kompletne I stabilne przez minimum 3 iteracje
 */
export const usePsychometrics = (interactionId, options = {}) => {
    const { 
        autoFetch = true, 
        onError = null,
        enablePolling = true,  // KROK 2: Włącz inteligentne polling
        pollingInterval = 5000  // Co 5 sekund
    } = options;
    
    const [analysisData, setAnalysisData] = useState(null);
    const [previousData, setPreviousData] = useState(null); // Dla sprawdzania stabilności
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [pollingActive, setPollingActive] = useState(false);
    const [attempts, setAttempts] = useState(0);
    const [dataStabilityCounter, setDataStabilityCounter] = useState(0); // Liczy stabilne iteracje

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
            
            // Combined data z session-level psychology
            const combinedData = {
                // Session-level psychology data (NOWE v3.0)
                cumulative_psychology: sessionPsychology,
                customer_archetype: customerArchetype,
                psychology_confidence: psychologyConfidence,

                // MODUŁ 4: Sales indicators
                sales_indicators: session?.sales_indicators || null,

                // Backwards compatibility z interaction-level data
                ...sessionPsychology,  // Spread session psychology jako główne dane

                // Legacy fields dla compatibility
                analysis_confidence: psychologyConfidence
            };
            
            // DEBUG: Streamlined logging
            if (session?.sales_indicators) {
                console.log('📊 Sales Indicators Generated:', Object.keys(session.sales_indicators));
            }
            if (psychologyConfidence > 0) {
                console.log('🧠 Psychology Confidence:', `${psychologyConfidence}%`);
            }
            
            // PRZYORYTET 1: Sprawdź stabilność danych przed aktualizacją stanu
            const isDataStable = checkDataStability(combinedData, previousData);

            setAnalysisData(combinedData);
            setPreviousData(combinedData); // Zapisz jako poprzednie dane
            setAttempts(prev => prev + 1);

            // NOWA LOGIKA v4.0: Rygorystyczne sprawdzanie kompletności I stabilności
            const hasFullPsychology = sessionPsychology.big_five || sessionPsychology.disc || sessionPsychology.schwartz_values;
            const hasArchetypeReady = customerArchetype && psychologyConfidence >= 75;
            const hasSalesIndicators = session?.sales_indicators && Object.keys(session.sales_indicators).length > 0;

            // NOWE: Sprawdzanie kompletności - wymagamy pełnego zestawu danych
            const isPsychologyComplete = hasFullPsychology && psychologyConfidence >= 80;
            const isArchetypeComplete = hasArchetypeReady;
            const isDataComplete = isPsychologyComplete && isArchetypeComplete && hasSalesIndicators;

            // Liczenie stabilnych iteracji
            if (isDataStable && isDataComplete) {
                setDataStabilityCounter(prev => prev + 1);
            } else {
                setDataStabilityCounter(0); // Reset jeśli dane się zmieniły lub nie są kompletne
            }

            console.log('🔍 usePsychometrics v4.0 - ANALYSIS STATUS:');
            console.log('  - Psychology Complete:', isPsychologyComplete, `(confidence: ${psychologyConfidence}%)`);
            console.log('  - Archetype Complete:', isArchetypeComplete);
            console.log('  - Sales Indicators:', hasSalesIndicators);
            console.log('  - Data Stable:', isDataStable, `(counter: ${dataStabilityCounter}/3)`);
            console.log('  - FULLY COMPLETE:', isDataComplete && dataStabilityCounter >= 3);

            // NOWA LOGIKA: Polling trwa dopóki dane nie są kompletne I stabilne przez 3 iteracje
            if (isDataComplete && dataStabilityCounter >= 3) {
                console.log('🎯 usePsychometrics v4.0 - DANE KOMPLETNE I STABILNE - zatrzymuję polling');
                setPollingActive(false);
            } else if (enablePolling && attempts < 20) { // Zwiększony limit do 20 prób = 1.67 minuty
                console.log(`⏳ usePsychometrics v4.0 - kontynuuję polling... (attempt ${attempts + 1}/20)`);
                setPollingActive(true);
            } else {
                console.log('⚠️ usePsychometrics v4.0 - przekroczono limit prób lub polling wyłączony');
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
        // PRZYORYTET 1: Rozszerzone informacje o polling i stabilności
        isPolling: pollingActive,
        attempts,
        maxAttempts: 20, // Zwiększony limit prób
        dataStabilityCounter,
        isDataStable: dataStabilityCounter >= 3,
        isAnalysisComplete: dataStabilityCounter >= 3 && analysisData // Dane kompletne gdy stabilne przez 3 iteracje
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
