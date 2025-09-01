/**
 * StrategicPanel - Prawa strona interfejsu konwersacyjnego
 * 
 * Zawiera:
 * - Sekcję archetypów na górze (1-2 najbardziej prawdopodobne)
 * - Sekcję strategii poniżej (rozwijane panele z nuggetami wiedzy)
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  LinearProgress,
  Stack,
  Divider,
  Card,
  CardContent,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  Badge,
  CircularProgress
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Psychology as PsychologyIcon,
  Lightbulb as LightbulbIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Star as StarIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  QuestionAnswer as QuestionAnswerIcon,
  SupportAgent as SupportAgentIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { getKnowledgeList } from '../../services/knowledgeApi';
// ZASTĄPIONE przez DetailedClientProfile (BLUEPRINT ZADANIE 3)
// import PsychometricDashboard from '../psychometrics/PsychometricDashboard';
// import CustomerArchetypeDisplay from '../psychometrics/CustomerArchetypeDisplay';
// import DetailedClientProfile from '../ComprehensiveAnalysis/DetailedClientProfile';
import BigFiveRadarChart from '../psychometrics/BigFiveRadarChart';
import SalesIndicatorsDashboard from '../indicators/SalesIndicatorsDashboard';
import SuggestedQuestions from '../SuggestedQuestions';

const StrategicPanel = ({ 
  // 🧠⚡ ULTRA MÓZG - Pełne dane psychometryczne
  data = null, // {quick_response_for_client, strategic_tip_for_seller, knowledge_summary, certainty_level}
  
  // 🧠⚡ NOWE - Pełne dane analizy z ostatniej interakcji
  analysis = null, // {lastInteraction, aiResponse, sentimentScore, potentialScore, urgencyLevel, suggestedQuestions, buySignals, riskSignals, nextBestAction}
  
  // LEGACY PROPS dla backward compatibility
  archetypes = [], 
  insights = [], 
  currentSession, 
  currentInteractionId = null,
  isLoading = false,
  
  // 🧠⚡ ULTRA MÓZG - Dodatkowe dane dla pełnej analizy
  ultraBrainData = null,
  
  // 🧠⚡ ULTRA MÓZG - Funkcje pomocnicze
  ultraBrainFunctions = null
}) => {
  const [knowledgeItems, setKnowledgeItems] = useState([]);
  const [loadingKnowledge, setLoadingKnowledge] = useState(false);
  const [expandedAccordion, setExpandedAccordion] = useState('psychometric'); // Domyślnie otwórz psychometric
  
  // 🧠⚡ NOWE - Stan dla dynamicznej aktualizacji
  const [lastAnalysisUpdate, setLastAnalysisUpdate] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // 🧠⚡ ULTRA MÓZG - UŻYWAJ DANYCH Z PROPS ZAMIAST WEWNĘTRZNEGO HOOKA
  const {
    dnaKlienta,
    strategia,
    surowePsychology,
    isDnaReady,
    isStrategiaReady,
    isUltraBrainReady,
    confidence: ultraBrainConfidence,
    legacy: ultraBrainLegacy,
    loading: ultraBrainLoading,
    error: ultraBrainError,
    isPolling: ultraBrainPolling
  } = ultraBrainData || {};

  const {
    getArchetypeName,
    getMainDrive,
    getCommunicationStyle,
    getKeyLevers,
    getRedFlags,
    getStrategicRecommendation,
    getQuickResponse,
    getSuggestedQuestions,
    getProactiveGuidance
  } = ultraBrainFunctions || {};

  // 🧠⚡ NOWE - Śledzenie zmian w analizie dla dynamicznej aktualizacji
  useEffect(() => {
    if (analysis?.lastInteraction && analysis.lastInteraction.id !== lastAnalysisUpdate) {
      console.log('🔄 StrategicPanel - wykryto nową analizę:', analysis.lastInteraction.id);
      setLastAnalysisUpdate(analysis.lastInteraction.id);
    }
  }, [analysis?.lastInteraction, lastAnalysisUpdate]);

  // 🧠⚡ NOWE - Funkcja do odświeżania danych
  const handleRefreshInsights = async () => {
    setIsRefreshing(true);
    try {
      // Symulacja odświeżania - w przyszłości będzie wywołanie API
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('🔄 StrategicPanel - odświeżono dane');
    } catch (error) {
      console.error('❌ StrategicPanel - błąd podczas odświeżania:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  // 🔧 DEBUG: Enhanced data flow logging with detailed analysis
  React.useEffect(() => {
    console.log('🔧 [STRATEGIC PANEL DEBUG] Data flow analysis:', {
      isDnaReady,
      isStrategiaReady,
      dnaKlienta: dnaKlienta ? {
        holistic_summary: dnaKlienta.holistic_summary,
        main_drive: dnaKlienta.main_drive,
        hasRealData: !!(dnaKlienta.holistic_summary && dnaKlienta.holistic_summary !== 'Profil w trakcie analizy...')
      } : 'Not available',
      // 🔍 PSYCHOMETRIC DATA DEBUG
      psychometricData: {
        surowePsychology: surowePsychology ? 'Available' : 'Not available',
        bigFiveKeys: surowePsychology?.big_five ? Object.keys(surowePsychology.big_five) : 'No Big Five data',
        sampleBigFiveData: surowePsychology?.big_five ? {
          openness: surowePsychology.big_five.openness?.score || 'No score',
          conscientiousness: surowePsychology.big_five.conscientiousness?.score || 'No score'
        } : 'No data structure'
      },
      ultraBrainLegacy: {
        customerArchetype: ultraBrainLegacy?.customerArchetype ? {
          archetype_name: ultraBrainLegacy.customerArchetype.archetype_name,
          isValid: (
            ultraBrainLegacy.customerArchetype.archetype_name !== 'neutral' &&
            ultraBrainLegacy.customerArchetype.archetype_name !== 'Profil w trakcie analizy...'
          )
        } : 'Not available',
        analysisData: ultraBrainLegacy?.analysisData ? 'Available' : 'Not available'
      },
      helperFunctions: {
        getArchetypeName: getArchetypeName ? {
          available: true,
          result: getArchetypeName(),
          isPlaceholder: getArchetypeName() === 'Analiza w toku...'
        } : { available: false },
        getMainDrive: getMainDrive ? {
          available: true,
          result: getMainDrive(),
          isPlaceholder: getMainDrive().includes('Identyfikowanie')
        } : { available: false }
      },
      activeConfidence: ultraBrainConfidence
    });
    
    // 🔍 SPECIFIC BIG FIVE LOGGING
    if (surowePsychology?.big_five) {
      console.log('📊 [BIG FIVE RADAR] Data available for chart:', {
        traits: Object.keys(surowePsychology.big_five),
        sampleData: surowePsychology.big_five
      });
    } else {
      console.log('⚠️ [BIG FIVE RADAR] No Big Five data available yet');
    }
    
    // Call the global validator if available
    if (window.validateUltraBrainData && (isDnaReady || isStrategiaReady)) {
      window.validateUltraBrainData({
        dnaKlienta,
        confidence: ultraBrainConfidence,
        isDnaReady,
        isStrategiaReady
      });
    }
  }, [isDnaReady, isStrategiaReady, dnaKlienta, surowePsychology, ultraBrainLegacy, ultraBrainConfidence, getArchetypeName, getMainDrive]);

  // 🧠⚡ ULTRA MÓZG - TYLKO JEDNA CENTRALNA PRAWDA
  const activeData = ultraBrainLegacy?.analysisData || {};  // Dla kompatybilności z wykresami

  // 🔧 NAPRAWA: Enhanced customerArchetype construction with React.useMemo
  const customerArchetype = React.useMemo(() => {
    console.log('🔧 [STRATEGIC PANEL] Constructing customerArchetype with data:', {
      isDnaReady,
      dnaKlienta: dnaKlienta ? 'Available' : 'Not available',
      ultraBrainLegacy: ultraBrainLegacy ? 'Available' : 'Not available',
      getArchetypeName: getArchetypeName ? getArchetypeName() : 'Function not available'
    });
    
    // 🔧 FIX: Primary source - DNA Klienta from Ultra Brain
    if (isDnaReady && dnaKlienta) {
      const archetype = {
        archetype_name: dnaKlienta.holistic_summary || 'DNA Klienta',
        archetype_key: 'ultra_brain',
        description: dnaKlienta.main_drive || 'Identyfikuję główny motor napędowy...',
        motivation: dnaKlienta.main_drive || '',
        communication_style: dnaKlienta.communication_style?.recommended_tone || '',
        key_traits: dnaKlienta.key_levers || [],
        sales_strategy: {
          do: dnaKlienta.key_levers || [],
          dont: dnaKlienta.red_flags || []
        },
        confidence: dnaKlienta.confidence || ultraBrainConfidence || 0
      };
      console.log('✅ [STRATEGIC PANEL] Using DNA Klienta archetype:', archetype.archetype_name);
      return archetype;
    }
    
    // 🔧 FIX: Secondary source - Legacy Ultra Brain data with validation
    if (ultraBrainLegacy?.customerArchetype?.archetype_name) {
      const legacyArchetype = ultraBrainLegacy.customerArchetype;
      const isValidLegacy = (
        legacyArchetype.archetype_name !== 'neutral' &&
        legacyArchetype.archetype_name !== 'Profil w trakcie analizy...' &&
        legacyArchetype.archetype_name !== 'Analiza w toku...' &&
        legacyArchetype.archetype_name.length > 3
      );
      
      if (isValidLegacy) {
        console.log('✅ [STRATEGIC PANEL] Using legacy Ultra Brain archetype:', legacyArchetype.archetype_name);
        return legacyArchetype;
      }
    }
    
    // 🔧 FIX: Tertiary source - Helper functions with validation
    if (getArchetypeName) {
      const archetypeName = getArchetypeName();
      if (archetypeName && archetypeName !== 'Analiza w toku...' && archetypeName.length > 3) {
        const archetype = {
          archetype_name: archetypeName,
          archetype_key: 'helper_function',
          description: getMainDrive ? getMainDrive() : 'AI analizuje profil klienta...',
          motivation: '',
          communication_style: '',
          key_traits: [],
          sales_strategy: { do: [], dont: [] },
          confidence: ultraBrainConfidence || 0
        };
        console.log('✅ [STRATEGIC PANEL] Using helper function archetype:', archetypeName);
        return archetype;
      }
    }
    
    // 🔧 FIX: Final fallback with proper structure
    const fallbackArchetype = {
      archetype_name: 'Profil w trakcie analizy...',
      archetype_key: 'analyzing',
      description: 'AI analizuje profil klienta w czasie rzeczywistym...',
      motivation: '',
      communication_style: '',
      key_traits: [],
      sales_strategy: { do: [], dont: [] },
      confidence: 0
    };
    console.log('⚠️ [STRATEGIC PANEL] Using fallback archetype');
    return fallbackArchetype;
  }, [isDnaReady, dnaKlienta, ultraBrainLegacy, getArchetypeName, getMainDrive, ultraBrainConfidence]);

  const activeArchetype = customerArchetype.archetype_name;
  const activeConfidence = ultraBrainConfidence || 0;
  const activeLoading = ultraBrainLoading || isLoading;

  // 🔧 DEBUG: Log customerArchetype after it's safely defined
  React.useEffect(() => {
    if (customerArchetype) {
      console.log('🔧 [STRATEGIC PANEL] CustomerArchetype constructed:', {
        archetype_name: customerArchetype.archetype_name,
        isPlaceholder: customerArchetype.archetype_name === 'Profil w trakcie analizy...',
        confidence: customerArchetype.confidence,
        dataQuality: {
          hasValidArchetype: (
            customerArchetype.archetype_name && 
            customerArchetype.archetype_name !== 'Profil w trakcie analizy...' &&
            customerArchetype.archetype_name.length > 3
          ),
          hasDescription: !!(customerArchetype.description && customerArchetype.description.length > 10),
          hasConfidence: !!(ultraBrainConfidence && ultraBrainConfidence > 0)
        }
      });
    }
  }, [customerArchetype, ultraBrainConfidence]);

  // Handler dla odpowiedzi na pytania pomocnicze
  const handleClarificationAnswered = (questionId, selectedOption, clarifyingAnswer) => {
    console.log('🎯 StrategicPanel - otrzymano odpowiedź na pytanie:', questionId, selectedOption);
    // Wymuś refresh analizy po odpowiedzi
    setTimeout(() => {
      // Po 2 sekundach uruchom refresh aby dać czas na backend processing
      if (window.location.reload) {
        console.log('🔄 StrategicPanel - odświeżam po clarification');
        // Tu w przyszłości można dodać bardziej elegancki refresh
      }
    }, 2000);
  };

  // Load strategic knowledge based on dominant archetype
  useEffect(() => {
    if (archetypes.length > 0) {
      loadStrategicKnowledge(archetypes[0]);
    }
  }, [archetypes]);

  const loadStrategicKnowledge = async (dominantArchetype) => {
    if (!dominantArchetype || !dominantArchetype.name) return;

    setLoadingKnowledge(true);
    try {
      // Fetch knowledge items relevant to the archetype
      const response = await getKnowledgeList({
        archetype: dominantArchetype.name,
        page: 1,
        size: 5
      });
      
      setKnowledgeItems(response.items || []);
    } catch (error) {
      console.error('Error loading strategic knowledge:', error);
    } finally {
      setLoadingKnowledge(false);
    }
  };

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpandedAccordion(isExpanded ? panel : false);
  };

  // Get archetype icon
  const getArchetypeIcon = (archetypeName) => {
    const iconMap = {
      'Zdobywca Statusu': '🏆',
      'Strażnik Rodziny': '👨‍👩‍👧‍👦',
      'Pragmatyczny Analityk': '📊',
      'Eko-Entuzjasta': '🌱',
      'Pionier Technologii': '🚀',
      'Techniczny Sceptyk': '🤔',
      'Lojalista Premium': '💎',
      'Łowca Okazji': '💰',
      'Niezdecydowany Odkrywca': '🧭',
      'Entuzjasta Osiągów': '⚡'
    };
    return iconMap[archetypeName] || '👤';
  };

  // Get confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'success';
    if (confidence >= 60) return 'warning';
    return 'error';
  };

  return (
    <Box 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}
    >
      {/* Header */}
      <Box 
        sx={{ 
          p: 2,
          bgcolor: 'grey.50',
          borderBottom: '1px solid',
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
          <AssessmentIcon color="primary" />
          Strategic Panel
        </Typography>
        
        <Tooltip title="Refresh insights">
          <IconButton size="small" onClick={() => loadStrategicKnowledge(archetypes[0])}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 1 }}>
        {/* BLUEPRINT ZADANIE 2: NOWA STRUKTURA - Dwie odrębne sekcje */}
        {data && (
          <>
            {/* Header z wskaźniklem pewności (BLUEPRINT ZADANIE 2) */}
            <Paper 
              elevation={2}
              sx={{ 
                p: 2, 
                mb: 2,
                bgcolor: 'primary.lighter',
                border: '1px solid',
                borderColor: 'primary.main',
                borderRadius: 2
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>  
                <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                  ⚡ Strategic Guidance
                </Typography>
                
                {/* BLUEPRINT ZADANIE 2: Wskaźnik pewności */}
                <Chip 
                  label={`Poziom Pewności: ${Math.round((data.certainty_level || 0) * 100)}%`}
                  color={data.certainty_level >= 0.8 ? 'success' : data.certainty_level >= 0.6 ? 'warning' : 'error'}
                  variant="filled"
                  size="small"
                  sx={{ fontWeight: 600 }}
                />
              </Box>
              

              
              {/* SEKCJA 2: Wskazówka dla Sprzedawcy */}
              <Box sx={{ mb: 3, p: 1.5, bgcolor: 'rgba(255, 193, 7, 0.08)', borderRadius: 1, borderLeft: '4px solid #ff9800' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'warning.main', mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                  💡 Wskazówka dla Ciebie:
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.9rem', lineHeight: 1.5, mb: 1 }}>
                  {data.strategic_tip_for_seller}
                </Typography>
                {data.seller_guidance && (
                  <Typography variant="caption" sx={{ color: 'warning.dark', fontSize: '0.8rem' }}>
                    ➡️ {data.seller_guidance}
                  </Typography>
                )}
              </Box>
              
              {/* SEKCJA 3: Podsumowanie Wiedzy o Kliencie (zastąpiła zduplikowaną zakładkę) */}
              <Box sx={{ p: 1.5, bgcolor: 'rgba(156, 39, 176, 0.08)', borderRadius: 1, borderLeft: '4px solid #9c27b0' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'secondary.main', mb: 1 }}>
                  📝 Podsumowanie Wiedzy o Kliencie:
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.85rem', lineHeight: 1.4, mb: 1 }}>
                  {data.knowledge_summary}
                </Typography>
                
                {/* Client Insights */}
                {data.client_insights && data.client_insights.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: 'secondary.dark' }}>
                      ✨ Kluczowe Spostrzerzenia:
                    </Typography>
                    <Box sx={{ mt: 0.5 }}>  
                      {data.client_insights.map((insight, index) => (
                        <Chip 
                          key={index}
                          label={insight}
                          size="small" 
                          variant="outlined"
                          color="secondary"
                          sx={{ m: 0.25, fontSize: '0.7rem' }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            </Paper>
          </>
        )}
        {/* LEGACY SUPPORT: ULTRA MÓZG v4.2.0 - tylko jeśli brak nowych danych */}
        {!data && isStrategiaReady && (
          <Paper
            elevation={3}
            sx={{ 
              p: 2, 
              mb: 2, 
              background: 'linear-gradient(145deg, #e3f2fd 0%, #f3e5f5 100%)',
              border: '2px solid #2196f3',
              position: 'relative'
            }}
          >
            {/* Badge dla Ultra Mózgu */}
            <Box sx={{ position: 'absolute', top: -8, right: 16 }}>
              <Chip 
                label="🧠⚡ ULTRA MÓZG" 
                size="small" 
                color="primary" 
                sx={{ fontWeight: 'bold', fontSize: '0.7rem' }}
              />
            </Box>
            
            <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
              ⚡ Rekomendacje Taktyczne
              <Badge badgeContent={activeConfidence.toFixed(0) + '%'} color="success" />
            </Typography>
            
            {/* Strategic Recommendation */}
            <Box sx={{ mb: 2, p: 1.5, bgcolor: 'rgba(25, 118, 210, 0.08)', borderRadius: 1, borderLeft: '4px solid #1976d2' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main', mb: 0.5 }}>
                🎯 Strategia na Ten Moment:
              </Typography>
              <Typography variant="body2" sx={{ fontSize: '0.9rem', lineHeight: 1.5 }}>
                {getStrategicRecommendation()}
              </Typography>
            </Box>
            
            {/* Quick Response */}
            <Box sx={{ mb: 2, p: 1.5, bgcolor: 'rgba(46, 125, 50, 0.08)', borderRadius: 1, borderLeft: '4px solid #2e7d32' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'success.main' }}>
                  💬 Sugerowana Odpowiedź:
                </Typography>
                
                {/* 🧠⚡ NOWY - Przycisk odświeżania z wskaźnikiem ładowania */}
                <Tooltip title="Odśwież dane">
                  <IconButton
                    size="small"
                    onClick={handleRefreshInsights}
                    disabled={isRefreshing}
                    sx={{ 
                      color: 'success.main',
                      '&:hover': { backgroundColor: 'success.lighter' }
                    }}
                  >
                    {isRefreshing ? (
                      <CircularProgress size={16} color="inherit" />
                    ) : (
                      <RefreshIcon fontSize="small" />
                    )}
                  </IconButton>
                </Tooltip>
              </Box>
              
              <Typography variant="body2" sx={{ fontSize: '0.9rem', lineHeight: 1.5, fontStyle: 'italic' }}>
                "{getQuickResponse()}"
              </Typography>
            </Box>
            
            {/* BLUEPRINT ZADANIE 1: SuggestedQuestions component in Strategic Panel */}
            {getSuggestedQuestions().length > 0 && (
              <Box sx={{ mb: 1.5 }}>
                <SuggestedQuestions
                  questions={getSuggestedQuestions()}
                  interactionId={currentInteractionId}
                  onQuestionFeedback={(questionId, score, type, text) => {
                    console.log('🎯 StrategicPanel - Question feedback:', questionId, score, type, text);
                    // Optional: Handle feedback in StrategicPanel context
                  }}
                  title="❓ Pytania Pogłębiające"
                  maxVisible={3}
                />
              </Box>
            )}
            
            {/* Proactive Guidance */}
            {getProactiveGuidance().for_client && (
              <Box sx={{ p: 1, bgcolor: 'rgba(156, 39, 176, 0.08)', borderRadius: 1, borderLeft: '4px solid #9c27b0' }}>
                <Typography variant="caption" sx={{ fontWeight: 600, color: 'secondary.main', textTransform: 'uppercase' }}>
                  🔮 Proaktywne Wskazówki:
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.85rem', mt: 0.5 }}>
                  {getProactiveGuidance().for_client}
                </Typography>
              </Box>
            )}
          </Paper>
        )}

        {/* BLUEPRINT ZADANIE 3: DetailedClientProfile zastępuje CustomerArchetypeDisplay */}
        {/* {data?.detailed_client_profile ? (
          <DetailedClientProfile 
            data={data.detailed_client_profile}
            loading={activeLoading}
          />
        ) : (
          // LEGACY fallback
          <DetailedClientProfile 
            data={{
              customer_archetype: {
                archetype_name: activeArchetype || 'Profil w trakcie analizy',
                archetype_description: 'AI analizuje profil klienta...',
                confidence: activeConfidence || 0,
                dominant_traits: [],
                motivators: [],
                communication_preferences: []
              },
              sales_indicators: [],
              psychometric_analysis: surowePsychology || {},
              analysis_confidence: activeConfidence || 0
            }}
          loading={activeLoading}
        />
        )} */}

        {/* MODUŁ 4: Zaawansowane Wskaźniki Sprzedażowe - ULTRA MÓZG v4.2.0 */}
        {ultraBrainLegacy?.salesIndicators && isStrategiaReady && (
          <Accordion 
            expanded={expandedAccordion === 'indicators'} 
            onChange={handleAccordionChange('indicators')}
            elevation={1}
            sx={{ mb: 1 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                <AssessmentIcon color="secondary" fontSize="small" />
                📊 Wskaźniki Sprzedażowe
                <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                  (Temperatura • Etap • Ryzyko • Potencjał)
                </Typography>
                <Badge 
                  badgeContent={isUltraBrainReady ? "🧠⚡" : "AI"} 
                  color={isUltraBrainReady ? "primary" : "secondary"} 
                />
                {activeLoading && (
                  <Badge badgeContent="..." color="info" />
                )}
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ p: 0 }}>
              <Box sx={{ width: '100%' }}>
                <SalesIndicatorsDashboard
                  indicatorsData={ultraBrainLegacy?.salesIndicators}
                  customerArchetype={customerArchetype}
                  psychologyConfidence={activeConfidence}
                  cumulativePsychology={surowePsychology}
                  loading={activeLoading}
                  // NOWE PROPSY dla Ultra Mózgu v4.2.0
                  dnaKlienta={dnaKlienta}
                  isDnaReady={isDnaReady}
                  aiResponse={analysis?.aiResponse}
                  isAiResponseReady={analysis?.aiResponse ? true : false}
                />
              </Box>
            </AccordionDetails>
          </Accordion>
        )}
        
        {/* Sekcja Archetypów - zaktualizowana dla v4.2.0 */}
        <Accordion
          expanded={expandedAccordion === 'archetypes'}
          onChange={handleAccordionChange('archetypes')}
          sx={{ mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
              <PsychologyIcon color="primary" fontSize="small" />
              Customer Archetypes
              {customerArchetype && isStrategiaReady && (
                <Badge badgeContent="1" color="primary" />
              )}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {!isStrategiaReady ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 2 }}>
                <CircularProgress size={20} />
                <Typography variant="body2" color="text.secondary">
                  Analizuję profil klienta...
                </Typography>
              </Box>
            ) : (
              <Stack spacing={2}>
                <Card 
                  variant="outlined" 
                  sx={{ 
                    position: 'relative',
                    bgcolor: 'primary.lighter'
                  }}
                >
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="h6" component="span">
                          {getArchetypeIcon(customerArchetype.archetype_name)}
                        </Typography>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                          {customerArchetype.archetype_name}
                        </Typography>
                        <Chip 
                          label="Primary" 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                        />
                      </Box>
                      <Chip
                        label={`${activeConfidence.toFixed(0)}%`}
                        size="small"
                        color={getConfidenceColor(activeConfidence)}
                      />
                    </Box>

                    <LinearProgress
                      variant="determinate"
                      value={activeConfidence}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        mb: 1
                      }}
                      color={getConfidenceColor(activeConfidence)}
                    />

                    {customerArchetype.description && (
                      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                        {customerArchetype.description}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Stack>
            )}
          </AccordionDetails>
        </Accordion>

        {/* 🧠⚡ PSYCHOMETRIC SECTION - Customer DNA Big Five Analysis */}
        <Accordion 
          expanded={expandedAccordion === 'psychometric'} 
          onChange={handleAccordionChange('psychometric')}
          sx={{ mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
              <PsychologyIcon color="secondary" fontSize="small" />
              📊 Profil Psychometryczny - Big Five
              {(isDnaReady && surowePsychology?.big_five) && (
                <Badge badgeContent="🧬 DNA" color="primary" />
              )}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {!isDnaReady ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 2 }}>
                <CircularProgress size={20} />
                <Typography variant="body2" color="text.secondary">
                  Analizuję profil psychometryczny Big Five...
                </Typography>
              </Box>
            ) : (
              <Box>
                {surowePsychology?.big_five ? (
                  <BigFiveRadarChart data={surowePsychology.big_five} />
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                      Dane Big Five nie są jeszcze dostępne. Kontynuuj konwersację aby wygenerować szczegółowy profil psychometryczny.
                    </Typography>
                  </Box>
                )}
              </Box>
            )}
          </AccordionDetails>
        </Accordion>

        {/* 🧠⚡ ULTRA MÓZG v4.2.0: Strategic Insights - DNA KLIENTA */}
        <Accordion 
          expanded={expandedAccordion === 'insights'} 
          onChange={handleAccordionChange('insights')}
          sx={{ mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
              <LightbulbIcon color="warning" fontSize="small" />
              Strategic Insights - DNA Klienta
              {isDnaReady && (
                <Badge badgeContent="🧬 DNA" color="primary" />
              )}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {!isDnaReady ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 2 }}>
                <CircularProgress size={20} />
                <Typography variant="body2" color="text.secondary">
                  Ultra Mózg analizuje profil psychologiczny klienta... DNA zostanie wygenerowane wkrótce.
                </Typography>
              </Box>
            ) : (
              <Stack spacing={2}>
                {/* Main Drive */}
                <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'primary.lighter' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'primary.main', mb: 0.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                    🎯 Główny Motor Napędowy:
                  </Typography>
                  <Typography variant="body2" sx={{ fontSize: '0.9rem' }}>
                    {getMainDrive()}
                  </Typography>
                </Paper>
                
                {/* Communication Style */}
                {getCommunicationStyle().recommended_tone && (
                  <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'success.lighter' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'success.main', mb: 1 }}>
                      💬 Styl Komunikacji:
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1, fontSize: '0.85rem' }}>
                      <strong>Ton:</strong> {getCommunicationStyle().recommended_tone}
                    </Typography>
                    
                    {getCommunicationStyle().keywords_to_use?.length > 0 && (
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="caption" sx={{ fontWeight: 600, color: 'success.dark' }}>
                          ✅ UŻYWAJ:
                        </Typography>
                        <Box sx={{ mt: 0.5 }}>
                          {getCommunicationStyle().keywords_to_use.map((keyword, i) => (
                            <Chip key={i} label={keyword} size="small" variant="outlined" color="success" sx={{ m: 0.25, fontSize: '0.7rem' }} />
                          ))}
                        </Box>
                      </Box>
                    )}
                    
                    {getCommunicationStyle().keywords_to_avoid?.length > 0 && (
                      <Box>
                        <Typography variant="caption" sx={{ fontWeight: 600, color: 'error.main' }}>
                          ❌ UNIKAJ:
                        </Typography>
                        <Box sx={{ mt: 0.5 }}>
                          {getCommunicationStyle().keywords_to_avoid.map((keyword, i) => (
                            <Chip key={i} label={keyword} size="small" variant="outlined" color="error" sx={{ m: 0.25, fontSize: '0.7rem' }} />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </Paper>
                )}
                
                {/* Key Levers */}
                {getKeyLevers().length > 0 && (
                  <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'warning.lighter' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'warning.main', mb: 1 }}>
                      🔑 Kluczowe Dźwignie:
                    </Typography>
                    <List dense>
                      {getKeyLevers().map((lever, index) => (
                        <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 24 }}>
                            <Typography sx={{ fontSize: '0.9rem' }}>⚡</Typography>
                          </ListItemIcon>
                          <ListItemText 
                            primary={lever}
                            primaryTypographyProps={{ fontSize: '0.85rem', fontWeight: 500 }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                )}
                
                {/* Red Flags */}
                {getRedFlags().length > 0 && (
                  <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'error.lighter' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'error.main', mb: 1 }}>
                      🚩 Czerwone Flagi:
                    </Typography>
                    <List dense>
                      {getRedFlags().map((flag, index) => (
                        <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 24 }}>
                            <Typography sx={{ fontSize: '0.9rem' }}>⚠️</Typography>
                          </ListItemIcon>
                          <ListItemText 
                            primary={flag}
                            primaryTypographyProps={{ fontSize: '0.85rem', fontWeight: 500 }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                )}
              </Stack>
            )}
          </AccordionDetails>
        </Accordion>

        {/* 🧠⚡ NOWA SEKCJA v4.2.0 - Dynamiczne Dane Analizy AI */}
        {analysis?.aiResponse && analysis?.lastInteraction && (
          <Accordion 
            expanded={expandedAccordion === 'analysis'} 
            onChange={handleAccordionChange('analysis')}
            elevation={1}
            sx={{ mb: 1 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                <AssessmentIcon color="info" fontSize="small" />
                📊 Analiza AI - Live Data v4.2.0
                <Badge 
                  badgeContent="LIVE" 
                  color="success" 
                  sx={{ fontSize: '0.6rem' }}
                />
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Stack spacing={2}>
                {/* Metryki AI */}
                {(analysis.sentimentScore || analysis.potentialScore || analysis.urgencyLevel) && (
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'info.lighter' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'info.main' }}>
                      📈 Metryki Analizy
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      {analysis.sentimentScore && (
                        <Chip
                          label={`Sentyment: ${analysis.sentimentScore}/10`}
                          color={analysis.sentimentScore >= 7 ? 'success' : analysis.sentimentScore >= 4 ? 'warning' : 'error'}
                          variant="outlined"
                          size="small"
                        />
                      )}
                      {analysis.potentialScore && (
                        <Chip
                          label={`Potencjał: ${analysis.potentialScore}/10`}
                          color={analysis.potentialScore >= 7 ? 'success' : analysis.potentialScore >= 4 ? 'warning' : 'error'}
                          variant="outlined"
                          size="small"
                        />
                      )}
                      {analysis.urgencyLevel && (
                        <Chip
                          label={`Pilność: ${analysis.urgencyLevel}`}
                          color={analysis.urgencyLevel === 'high' ? 'error' : analysis.urgencyLevel === 'medium' ? 'warning' : 'success'}
                          variant="outlined"
                          size="small"
                        />
                      )}
                    </Box>
                  </Paper>
                )}

                {/* Sygnały */}
                {(analysis.buySignals?.length > 0 || analysis.riskSignals?.length > 0) && (
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'warning.lighter' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'warning.main' }}>
                      🎯 Zidentyfikowane Sygnały
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {analysis.buySignals?.map((signal, index) => (
                        <Chip
                          key={`buy-${index}`}
                          icon={<TrendingUpIcon />}
                          label={signal}
                          color="success"
                          variant="outlined"
                          size="small"
                        />
                      ))}
                      {analysis.riskSignals?.map((signal, index) => (
                        <Chip
                          key={`risk-${index}`}
                          icon={<TrendingDownIcon />}
                          label={signal}
                          color="error"
                          variant="outlined"
                          size="small"
                        />
                      ))}
                    </Box>
                  </Paper>
                )}

                {/* Następny krok */}
                {analysis.nextBestAction && (
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'success.lighter' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'success.main' }}>
                      🚀 Następny Krok
                    </Typography>
                    <Typography variant="body2" sx={{ fontSize: '0.9rem', fontStyle: 'italic' }}>
                      {analysis.nextBestAction}
                    </Typography>
                  </Paper>
                )}

                {/* Sugerowane pytania */}
                {analysis.suggestedQuestions?.length > 0 && (
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'primary.lighter' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'primary.main' }}>
                      ❓ Sugerowane Pytania ({analysis.suggestedQuestions.length})
                    </Typography>
                    <Stack spacing={1}>
                      {analysis.suggestedQuestions.slice(0, 3).map((question, index) => (
                        <Typography key={index} variant="body2" sx={{ fontSize: '0.85rem', pl: 1 }}>
                          • {typeof question === 'object' ? question.text : question}
                        </Typography>
                      ))}
                    </Stack>
                  </Paper>
                )}
              </Stack>
            </AccordionDetails>
          </Accordion>
        )}

        {/* Sekcja Knowledge Base */}
        <Accordion 
          expanded={expandedAccordion === 'knowledge'} 
          onChange={handleAccordionChange('knowledge')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
              <SupportAgentIcon color="success" fontSize="small" />
              Knowledge Base
              {knowledgeItems.length > 0 && (
                <Badge badgeContent={knowledgeItems.length} color="success" />
              )}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {loadingKnowledge ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 2 }}>
                <CircularProgress sx={{ flexGrow: 1 }} />
                <Typography variant="caption" color="text.secondary">
                  Loading insights...
                </Typography>
              </Box>
            ) : knowledgeItems.length === 0 ? (
              <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
                Relevant knowledge tips will appear here based on identified archetypes
              </Alert>
            ) : (
              <Stack spacing={1.5}>
                {knowledgeItems.map((item, index) => (
                  <Paper 
                    key={item.id || index}
                    variant="outlined"
                    sx={{ p: 2, bgcolor: 'success.lighter' }}
                  >
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      💡 {item.title || 'Strategic Tip'}
                    </Typography>
                    <Typography variant="body2" sx={{ fontSize: '0.8rem', lineHeight: 1.4 }}>
                      {item.content || item.description || 'Knowledge content...'}
                    </Typography>
                    {item.knowledge_type && (
                      <Chip 
                        label={item.knowledge_type} 
                        size="small" 
                        variant="outlined"
                        sx={{ mt: 1, fontSize: '0.7rem', height: 20 }}
                      />
                    )}
                  </Paper>
                ))}
              </Stack>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Status Footer */}
        <Box sx={{ mt: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <InfoIcon fontSize="small" />
            {currentSession ? `Session Active` : 'Waiting for session...'}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default StrategicPanel;
