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
    
    // === STAN ULTRA MÓZGU ===
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
    
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [pollingActive, setPollingActive] = useState(false);
    
    const debugLog = useCallback((message, data) => {
        if (debug) {
            console.log(`🧠⚡ [ULTRA BRAIN] ${message}`, data);
        }
    }, [debug]);

    const fetchUltraBrainData = useCallback(async () => {
        if (!interactionId) return;
        
        try {
            setLoading(true);
            setError(null);
            
            debugLog('Pobieranie danych Ultra Mózgu...', { interactionId });
            
            // Pobierz pełne dane interakcji z API
            const interaction = await getInteractionById(interactionId);
            debugLog('Otrzymana interakcja:', interaction);
            
            // ULTRA MÓZG v4.0: Ekstraktuj dane z nowej architektury
            const session = interaction?.session;
            const aiResponse = interaction?.ai_response_json || {};
            
            // === DNA KLIENTA (holistic_profile z backendu) ===
            const holisticProfile = session?.holistic_psychometric_profile;
            // 🔧 NAPRAWA: Backend nie ustawia is_fallback, sprawdzamy czy dane istnieją
            const dnaReady = !!(holisticProfile && typeof holisticProfile === 'object' && Object.keys(holisticProfile).length > 0);
            
            debugLog('DNA Klienta:', { holisticProfile, dnaReady });
            
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
            
            // STWÓRZ NOWY STAN ULTRA MÓZGU
            const newUltraBrainState = {
                // DNA KLIENTA
                dnaKlienta: holisticProfile,
                dnaReady,
                dnaConfidence: holisticProfile?.confidence || session?.psychology_confidence || 0,
                
                // PAKIET STRATEGICZNY
                strategia: strategicData,
                strategiaReady,
                
                // SUROWE DANE
                surowePsychology: rawPsychology,
                
                // KOMPATYBILNOŚĆ
                legacy: legacyData
            };
            
            debugLog('Nowy stan Ultra Mózgu:', newUltraBrainState);
            
            setUltraBrainData(newUltraBrainState);
            
            // ZATRZYMAJ POLLING jeśli DNA i strategia są gotowe
            if (dnaReady && strategiaReady && pollingActive) {
                setPollingActive(false);
                debugLog('Ultra Mózg kompletny - zatrzymuję polling');
            }
            
        } catch (err) {
            console.error('❌ [ULTRA BRAIN] Błąd podczas pobierania danych:', err);
            setError(err.message);
            if (onError) onError(err);
        } finally {
            setLoading(false);
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

    // === API HOOKA ===
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
        
        // KOMPATYBILNOŚĆ WSTECZNA
        legacy: ultraBrainData.legacy,
        
        // KONTROLA
        loading,
        error,
        isPolling: pollingActive,
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
