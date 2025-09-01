import { useState, useEffect, useCallback } from 'react';
import { getInteractionById } from '../services';
import { useSessionAnalytics } from './useSessionAnalytics';

/**
 * 🧠⚡ ULTRA MÓZG v4.0 - CENTRALNE ŹRÓDŁO PRAWDY
 * 
 * Hook zarządzający danymi z dwuetapowej architektury Ultra Mózgu:
 * - holistic_profile: DNA Klienta z Syntezatora
 * - strategic_response: Pakiet taktyczny z Generatora Strategii
 * 
 * Filozofia: Jeden hook, jedna prawda, wszystkie komponenty synchroniczne
 */
export const useUltraBrain = (interactionId, options = {}) => {
    const {
        autoFetch = true,
        onError = null,
        enablePolling = true,
        pollingInterval = 3000,  // Szybsze polling dla Ultra Mózgu
        debug = false
    } = options;

    // 🧠⚡ INTEGRACJA: Dodajemy useSessionAnalytics dla danych psychometrycznych
    const [sessionId, setSessionId] = useState(null);

    // 🧠⚡ INTEGRACJA: Hook do pobierania danych psychometrycznych z analytics
    const { data: analyticsData, loading: analyticsLoading, error: analyticsError } = useSessionAnalytics(sessionId);

    // === STAN ULTRA MÓZGU v4.1 ===
    const [ultraBrainData, setUltraBrainData] = useState({
        // DNA KLIENTA (z Syntezatora)
        dnaKlienta: null,           // holistic_profile z backendu
        dnaReady: false,            // Czy DNA zostało wygenerowane
        dnaConfidence: 0,           // Poziom pewności DNA
        
        // PAKIET STRATEGICZNY (z Generatora)
        strategia: null,            // strategic_response z AI
        strategiaReady: false,      // Czy strategia została wygenerowana
        
        // SUROWE DANE PSYCHOLOGY (dla głębokiej analizy)
        surowePsychology: null,     // raw psychology data dla wykresów
        
        // STARE DANE (kompatybilność wsteczna)
        legacy: {
            analysisData: null,
            customerArchetype: null,
            psychologyConfidence: 0
        }
    });
    
    // 🔧 BLUEPRINT v4.1: Enhanced loading states + PRIORYTET 4 optimistic UI
    const [loading, setLoading] = useState(false);
    const [isHolisticProfileLoading, setIsHolisticProfileLoading] = useState(false);
    const [holisticProfileError, setHolisticProfileError] = useState(null);
    const [error, setError] = useState(null);
    const [pollingActive, setPollingActive] = useState(false);
    
    // 🚀 PRIORYTET 4: Optimistic UI states
    const [optimisticUpdate, setOptimisticUpdate] = useState(false);
    const [estimatedResponseTime, setEstimatedResponseTime] = useState(15); // sekund
    
    const debugLog = useCallback((message, data) => {
        if (debug) {
            console.log(`🧠⚡ [ULTRA BRAIN] ${message}`, data);
        }
    }, [debug]);

    // 🚀 PRIORYTET 4: Optimistic UI helpers
    const startOptimisticUpdate = useCallback(() => {
        setOptimisticUpdate(true);
        setEstimatedResponseTime(15); // Domyślnie 15s
        
        debugLog('🚀 OPTIMISTIC UI: Started optimistic update');
        
        // Timer do pokazania postępu
        const progressTimer = setInterval(() => {
            setEstimatedResponseTime(prev => Math.max(0, prev - 1));
        }, 1000);
        
        // Cleanup timer po 20 sekundach
        setTimeout(() => {
            clearInterval(progressTimer);
            setOptimisticUpdate(false);
        }, 20000);
        
    }, [debugLog]);

    const stopOptimisticUpdate = useCallback(() => {
        setOptimisticUpdate(false);
        debugLog('✅ OPTIMISTIC UI: Stopped optimistic update');
    }, [debugLog]);

    const fetchUltraBrainData = useCallback(async () => {
        if (!interactionId) return;
        
        try {
            setLoading(true);
            setIsHolisticProfileLoading(true);
            setError(null);
            setHolisticProfileError(null);
            
            debugLog('🔧 v4.1: Pobieranie danych Ultra Mózgu...', { interactionId });
            
            // 🚀 PRIORYTET 4: Start optimistic update jeśli to nie polling
            if (!pollingActive) {
                startOptimisticUpdate();
            }
            
            // Pobierz pełne dane interakcji z API
            const interaction = await getInteractionById(interactionId);
            debugLog('Otrzymana interakcja:', interaction);

            // 🚀 PRIORYTET 4: Stop optimistic update gdy dane są gotowe
            stopOptimisticUpdate();

            // ULTRA MÓZG v4.0: Ekstraktuj dane z nowej architektury
            const session = interaction?.session;
            const aiResponse = interaction?.ai_response_json || {};

            // 🧠⚡ INTEGRACJA: Ustaw sessionId dla useSessionAnalytics
            if (session?.id && session.id !== sessionId) {
                setSessionId(session.id);
                debugLog('🧠⚡ Ustawiono sessionId dla analytics:', session.id);
            }
            
            // === DNA KLIENTA (holistic_profile z backendu) ===
            const holisticProfile = session?.holistic_psychometric_profile;
            
            // 🔧 v4.1 BLUEPRINT: Ulepszone zarządzanie holisticProfile
            let dnaReady = false;
            let processedHolisticProfile = null;
            
            // 🔧 FIX: Enhanced logic for detecting real archetype data
            if (holisticProfile && typeof holisticProfile === 'object' && Object.keys(holisticProfile).length > 0) {
                // Check for substantial real data (not just placeholders)
                const hasRealData = (
                    holisticProfile.holistic_summary && 
                    holisticProfile.holistic_summary !== 'Profil w trakcie analizy...' &&
                    holisticProfile.holistic_summary !== 'neutral'
                ) || (
                    holisticProfile.main_drive && 
                    holisticProfile.main_drive !== 'Identyfikowanie...' &&
                    holisticProfile.main_drive.length > 10
                ) || (
                    holisticProfile.communication_style && 
                    Object.keys(holisticProfile.communication_style).length > 0 &&
                    holisticProfile.communication_style.recommended_tone
                );
                
                if (hasRealData) {
                    dnaReady = true;
                    processedHolisticProfile = {
                        holistic_summary: holisticProfile.holistic_summary,
                        main_drive: holisticProfile.main_drive,
                        communication_style: holisticProfile.communication_style || {},
                        key_levers: holisticProfile.key_levers || [],
                        red_flags: holisticProfile.red_flags || [],
                        missing_data_gaps: holisticProfile.missing_data_gaps || '',
                        confidence: holisticProfile.confidence || session?.psychology_confidence || 0,
                        ...holisticProfile
                    };
                    debugLog('✅ DNA Klienta: Real holistic profile data detected', { processedHolisticProfile });
                } else {
                    debugLog('⚠️ DNA Klienta: Placeholder or incomplete data', { holisticProfile });
                }
            }
            
            // 🔧 FIX: Enhanced analytics backup with better validation
            if (!dnaReady && analyticsData?.customer_archetype) {
                const archetype = analyticsData.customer_archetype;
                const hasValidArchetype = (
                    archetype.archetype_name && 
                    archetype.archetype_name !== 'neutral' && 
                    archetype.archetype_name !== 'Profil w trakcie analizy...' &&
                    archetype.archetype_name !== 'Analiza w toku...' &&
                    archetype.archetype_name.length > 3
                );
                
                if (hasValidArchetype) {
                    dnaReady = true;
                    processedHolisticProfile = {
                        holistic_summary: archetype.archetype_name,
                        main_drive: archetype.description || archetype.motivation || 'Główny motor napędowy',
                        communication_style: { 
                            recommended_tone: archetype.communication_style || 'Profesjonalny',
                            keywords_to_use: archetype.key_traits || [],
                            keywords_to_avoid: []
                        },
                        key_levers: archetype.key_traits || archetype.motivators || [],
                        red_flags: archetype.sales_strategy?.dont || [],
                        confidence: archetype.confidence || session?.psychology_confidence || 0
                    };
                    debugLog('✅ DNA Klienta: Valid archetype from analytics', { processedHolisticProfile });
                }
            }
            
            if (!processedHolisticProfile) {
                debugLog('❌ DNA Klienta: Brak danych', { holisticProfile, analyticsArchetype: analyticsData?.customer_archetype });
            }
            
            // === PAKIET STRATEGICZNY (strategic_response z AI) ===
            // Nowe AI response zawiera strategic_recommendation, proactive_guidance itp.
            const strategicData = {
                mainAnalysis: aiResponse.main_analysis,
                quickResponse: aiResponse.quick_response,
                suggestedQuestions: aiResponse.suggested_questions || [],
                strategicRecommendation: aiResponse.strategic_recommendation,
                proactiveGuidance: aiResponse.proactive_guidance,
                strategicNotes: aiResponse.strategic_notes || [],
                nextBestAction: aiResponse.next_best_action
            };
            
            const strategiaReady = !!(strategicData.strategicRecommendation || strategicData.nextBestAction);
            
            debugLog('Pakiet Strategiczny:', { strategicData, strategiaReady });
            
            // === SUROWE DANE PSYCHOLOGY (dla wykresów) ===
            // 🧠⚡ INTEGRACJA: Użyj danych z analytics jeśli są dostępne
            const rawPsychology = analyticsData?.cumulative_psychology ||
                                analyticsData?.psychology_profile?.cumulative_psychology ||
                                session?.cumulative_psychology || {};
            
            // === LEGACY DATA (kompatybilność wsteczna) ===
            const legacyData = {
                analysisData: {
                    // 🧠⚡ INTEGRACJA: Mapuj dane z analytics na stary format dla kompatybilności
                    cumulative_psychology: rawPsychology,
                    customer_archetype: analyticsData?.customer_archetype || session?.customer_archetype,
                    psychology_confidence: analyticsData?.psychology_confidence || session?.psychology_confidence || 0,
                    
                    // Sales indicators (jeśli dostępne)
                    purchase_temperature: aiResponse.purchase_temperature,
                    journey_stage: aiResponse.journey_stage,
                    churn_risk: aiResponse.churn_risk,
                    sales_potential: aiResponse.potential_score
                },
                customerArchetype: session?.customer_archetype,
                psychologyConfidence: session?.psychology_confidence || 0
            };
            
            // STWÓRZ NOWY STAN ULTRA MÓZGU v4.1
            const newUltraBrainState = {
                // DNA KLIENTA - używamy processedHolisticProfile
                dnaKlienta: processedHolisticProfile,
                dnaReady,
                dnaConfidence: analyticsData?.psychology_confidence || processedHolisticProfile?.confidence || session?.psychology_confidence || 0,
                
                // PAKIET STRATEGICZNY
                strategia: strategicData,
                strategiaReady,
                
                // SUROWE DANE
                surowePsychology: rawPsychology,
                
                // KOMPATYBILNOŚĆ
                legacy: legacyData
            };
            
            // 🔧 DEBUG: Log final Ultra Brain state
            console.log('🔧 [ULTRA BRAIN DEBUG] Final Ultra Brain State:', {
                dnaReady,
                strategiaReady,
                dnaKlienta: processedHolisticProfile,
                customerArchetype: legacyData.customerArchetype,
                psychologyConfidence: newUltraBrainState.dnaConfidence,
                rawPsychology: Object.keys(rawPsychology),
                analyticsData: analyticsData ? 'Available' : 'Not available'
            });
            
            debugLog('🔧 v4.1: Nowy stan Ultra Mózgu:', newUltraBrainState);
            
            setUltraBrainData(newUltraBrainState);
            
            // Zaktualizuj loading states zgodnie z blueprintem
            setIsHolisticProfileLoading(false);
            
            // ZATRZYMAJ POLLING jeśli DNA i strategia są gotowe
            if (dnaReady && strategiaReady && pollingActive) {
                setPollingActive(false);
                debugLog('✅ Ultra Mózg kompletny - zatrzymuję polling');
            }
            
        } catch (err) {
            console.error('❌ [ULTRA BRAIN] Błąd podczas pobierania danych:', err);
            setError(err.message);
            setHolisticProfileError(err.message);
            if (onError) onError(err);
        } finally {
            setLoading(false);
            setIsHolisticProfileLoading(false);
        }
    }, [interactionId, onError, pollingActive, debugLog]);

    // AUTO-FETCH przy inicjalizacji
    useEffect(() => {
        if (autoFetch && interactionId) {
            fetchUltraBrainData();
        }
    }, [autoFetch, interactionId, fetchUltraBrainData]);

    // 🧠⚡ INTEGRACJA: Reaguj na zmiany w danych analytics
    useEffect(() => {
        if (analyticsData && Object.keys(analyticsData).length > 0) {
            debugLog('🧠⚡ Otrzymano dane analytics, aktualizuję Ultra Mózg:', analyticsData);

            // Zaktualizuj stan używając danych z analytics
            setUltraBrainData(prevState => ({
                ...prevState,
                surowePsychology: analyticsData.cumulative_psychology ||
                                analyticsData.psychology_profile?.cumulative_psychology || {},
                legacy: {
                    ...prevState.legacy,
                    analysisData: {
                        cumulative_psychology: analyticsData.cumulative_psychology ||
                                             analyticsData.psychology_profile?.cumulative_psychology || {},
                        customer_archetype: analyticsData.customer_archetype,
                        psychology_confidence: analyticsData.psychology_confidence || 0
                    }
                }
            }));
        }
    }, [analyticsData, debugLog]);

    // INTELIGENTNE POLLING - zatrzymuje się gdy dane są kompletne
    useEffect(() => {
        if (!enablePolling || !interactionId) return;
        
        const { dnaReady, strategiaReady } = ultraBrainData;
        
        // Uruchom polling tylko jeśli dane są niekompletne
        if (!dnaReady || !strategiaReady) {
            setPollingActive(true);
            
            const intervalId = setInterval(() => {
                fetchUltraBrainData();
            }, pollingInterval);
            
            debugLog('Polling aktywny', { dnaReady, strategiaReady });
            
            return () => {
                clearInterval(intervalId);
                setPollingActive(false);
            };
        }
    }, [enablePolling, interactionId, pollingInterval, ultraBrainData, fetchUltraBrainData, debugLog]);

    // === API HOOKA v4.1 ===
    return {
        // GŁÓWNE DANE ULTRA MÓZGU
        dnaKlienta: ultraBrainData.dnaKlienta,
        strategia: ultraBrainData.strategia,
        surowePsychology: ultraBrainData.surowePsychology,
        
        // STATUSY
        isDnaReady: ultraBrainData.dnaReady,
        isStrategiaReady: ultraBrainData.strategiaReady,
        isUltraBrainReady: ultraBrainData.dnaReady && ultraBrainData.strategiaReady,
        confidence: ultraBrainData.dnaConfidence,
        
        // 🔧 BLUEPRINT v4.1: Enhanced loading states
        loading,
        isHolisticProfileLoading,
        holisticProfileError,
        error,
        isPolling: pollingActive,
        
        // 🚀 PRIORYTET 4: Optimistic UI states
        optimisticUpdate,
        estimatedResponseTime,
        
        // KOMPATYBILNOŚĆ WSTECZNA
        legacy: ultraBrainData.legacy,
        
        // KONTROLA
        refresh: fetchUltraBrainData,
        
        // POMOCNICZE GETTERY
        getArchetypeName: () => {
            // 🔧 FIX: Improved fallback logic with better data validation
            if (ultraBrainData.dnaReady && ultraBrainData.dnaKlienta?.holistic_summary) {
                const summary = ultraBrainData.dnaKlienta.holistic_summary;
                if (summary !== 'Profil w trakcie analizy...' && summary !== 'neutral' && summary.length > 3) {
                    return summary;
                }
            }
            
            // Check analytics data as secondary source
            if (analyticsData?.customer_archetype?.archetype_name) {
                const archetypeName = analyticsData.customer_archetype.archetype_name;
                if (archetypeName !== 'neutral' && archetypeName !== 'Profil w trakcie analizy...' && archetypeName.length > 3) {
                    return archetypeName;
                }
            }
            
            // Check legacy data as tertiary source
            if (ultraBrainData.legacy?.customerArchetype?.archetype_name) {
                const legacyName = ultraBrainData.legacy.customerArchetype.archetype_name;
                if (legacyName !== 'neutral' && legacyName !== 'Profil w trakcie analizy...' && legacyName.length > 3) {
                    return legacyName;
                }
            }
            
            return 'Analiza w toku...';
        },
        getMainDrive: () => {
            // 🔧 FIX: Enhanced main drive detection
            if (ultraBrainData.dnaReady && ultraBrainData.dnaKlienta?.main_drive) {
                const mainDrive = ultraBrainData.dnaKlienta.main_drive;
                if (mainDrive !== 'Identyfikowanie...' && mainDrive.length > 5) {
                    return mainDrive;
                }
            }
            
            // Check analytics data for description
            if (analyticsData?.customer_archetype?.description) {
                const description = analyticsData.customer_archetype.description;
                if (description.length > 5) {
                    return description;
                }
            }
            
            // Check analytics motivation field
            if (analyticsData?.customer_archetype?.motivation) {
                return analyticsData.customer_archetype.motivation;
            }
            
            return 'Identyfikowanie głównego motoru...';
        },
        getCommunicationStyle: () => ultraBrainData.dnaKlienta?.communication_style || {},
        getKeyLevers: () => ultraBrainData.dnaKlienta?.key_levers || [],
        getRedFlags: () => ultraBrainData.dnaKlienta?.red_flags || [],
        getStrategicRecommendation: () => ultraBrainData.strategia?.strategicRecommendation || 'Przygotowuję strategię...',
        getQuickResponse: () => ultraBrainData.strategia?.quickResponse?.text || 'Analizuję sytuację...',
        getSuggestedQuestions: () => ultraBrainData.strategia?.suggestedQuestions || [],
        getProactiveGuidance: () => ultraBrainData.strategia?.proactiveGuidance || {}
    };
};

export default useUltraBrain;
