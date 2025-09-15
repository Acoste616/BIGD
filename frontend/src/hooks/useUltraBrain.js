import { useState, useEffect, useCallback } from 'react';
import { getInteractionById } from '../services';

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
            
            // === DNA KLIENTA (holistic_profile z backendu) ===
            const holisticProfile = session?.holistic_psychometric_profile;
            
            // 🔧 v4.1 BLUEPRINT: Ulepszone zarządzanie holisticProfile
            let dnaReady = false;
            let processedHolisticProfile = null;
            
            if (holisticProfile && typeof holisticProfile === 'object' && Object.keys(holisticProfile).length > 0) {
                // Sprawdź czy to jest prawdziwy profil czy fallback
                const hasRealData = holisticProfile.holistic_summary || holisticProfile.main_drive || 
                                  (holisticProfile.communication_style && Object.keys(holisticProfile.communication_style).length > 0);
                
                if (hasRealData) {
                    dnaReady = true;
                    processedHolisticProfile = {
                        // Dekomponuj na łatwe do użycia części zgodnie z blueprintem
                        holistic_summary: holisticProfile.holistic_summary,
                        main_drive: holisticProfile.main_drive,
                        communication_style: holisticProfile.communication_style || {},
                        key_levers: holisticProfile.key_levers || [],
                        red_flags: holisticProfile.red_flags || [],
                        missing_data_gaps: holisticProfile.missing_data_gaps || '',
                        confidence: holisticProfile.confidence || session?.psychology_confidence || 0,
                        ...holisticProfile
                    };
                    debugLog('✅ DNA Klienta: Rzeczywiste dane', { processedHolisticProfile });
                } else {
                    debugLog('⚠️ DNA Klienta: Dane fallback lub niekompletne', { holisticProfile });
                }
            } else {
                debugLog('❌ DNA Klienta: Brak danych', { holisticProfile });
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
            const rawPsychology = session?.cumulative_psychology || {};
            
            // === LEGACY DATA (kompatybilność wsteczna) ===
            const legacyData = {
                analysisData: {
                    // Mapuj nowe dane na stary format dla kompatybilności
                    cumulative_psychology: rawPsychology,
                    customer_archetype: session?.customer_archetype,
                    psychology_confidence: session?.psychology_confidence || 0,
                    
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
                dnaConfidence: processedHolisticProfile?.confidence || session?.psychology_confidence || 0,
                
                // PAKIET STRATEGICZNY
                strategia: strategicData,
                strategiaReady,
                
                // SUROWE DANE
                surowePsychology: rawPsychology,
                
                // KOMPATYBILNOŚĆ
                legacy: legacyData
            };
            
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
        confidenceScore: ultraBrainData.dnaConfidence, // Alias dla Progressive Disclosure
        
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
        getArchetypeName: () => ultraBrainData.dnaKlienta?.holistic_summary || 'Analiza w toku...',
        getMainDrive: () => ultraBrainData.dnaKlienta?.main_drive || 'Identyfikowanie...',
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
