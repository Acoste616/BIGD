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
  Badge
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Psychology as PsychologyIcon,
  Lightbulb as LightbulbIcon,
  TrendingUp as TrendingUpIcon,
  Star as StarIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  QuestionAnswer as QuestionAnswerIcon,
  SupportAgent as SupportAgentIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { getKnowledgeList } from '../../services/knowledgeApi';
import PsychometricDashboard from '../psychometrics/PsychometricDashboard';
import CustomerArchetypeDisplay from '../psychometrics/CustomerArchetypeDisplay';
import SalesIndicatorsDashboard from '../indicators/SalesIndicatorsDashboard';
import { useUltraBrain } from '../../hooks/useUltraBrain';  // ULTRA MÓZG v4.0

const StrategicPanel = ({ 
  archetypes = [], 
  insights = [], 
  currentSession, 
  currentInteractionId = null,
  isLoading 
}) => {
  const [knowledgeItems, setKnowledgeItems] = useState([]);
  const [loadingKnowledge, setLoadingKnowledge] = useState(false);
  const [expandedAccordion, setExpandedAccordion] = useState('psychometric'); // Domyślnie otwórz psychometric

  // 🧠⚡ ULTRA MÓZG zastępuje usePsychometrics - wszystkie dane z jednego źródła

  // 🧠⚡ ULTRA MÓZG v4.0: CENTRALNE ŹRÓDŁO PRAWDY ===
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
    isPolling: ultraBrainPolling,
    getArchetypeName,
    getMainDrive,
    getCommunicationStyle,
    getKeyLevers,
    getRedFlags,
    getStrategicRecommendation,
    getQuickResponse,
    getSuggestedQuestions,
    getProactiveGuidance
  } = useUltraBrain(currentInteractionId, {
    autoFetch: !!currentInteractionId,
    enablePolling: true,
    debug: true  // 🔧 WŁĄCZ debug dla diagnozy
  });

  // 🧠⚡ ULTRA MÓZG - TYLKO JEDNA CENTRALNA PRAWDA
  const activeData = ultraBrainLegacy.analysisData;  // Dla kompatybilności z wykresami
  const activeArchetype = getArchetypeName();
  const activeConfidence = ultraBrainConfidence;
  const activeLoading = ultraBrainLoading || isLoading;

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
        {/* 🧠⚡ ULTRA MÓZG v4.0: REKOMENDACJE TAKTYCZNE - NAJWYŻSZY PRIORYTET */}
        {isStrategiaReady && (
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
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'success.main', mb: 0.5 }}>
                💬 Sugerowana Odpowiedź:
              </Typography>
              <Typography variant="body2" sx={{ fontSize: '0.9rem', lineHeight: 1.5, fontStyle: 'italic' }}>
                "{getQuickResponse()}"
              </Typography>
            </Box>
            
            {/* Suggested Questions */}
            {getSuggestedQuestions().length > 0 && (
              <Box sx={{ mb: 1.5 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'warning.main', mb: 1 }}>
                  ❓ Pytania Pogłębiające:
                </Typography>
                <Stack spacing={0.5}>
                  {getSuggestedQuestions().slice(0, 3).map((question, index) => (
                    <Chip 
                      key={question.id || index}
                      label={question.text}
                      variant="outlined"
                      size="small"
                      sx={{ 
                        justifyContent: 'flex-start', 
                        fontSize: '0.8rem',
                        '& .MuiChip-label': { textAlign: 'left', whiteSpace: 'normal' }
                      }}
                    />
                  ))}
                </Stack>
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

        {/* ETAP 5 v3.0: Customer Archetype Display - DRUGI W HIERARCHII */}
        <CustomerArchetypeDisplay 
          customerArchetype={activeArchetype}
          psychologyConfidence={activeConfidence}
          loading={activeLoading}
          dnaKlienta={dnaKlienta}  // NOWY PROP dla Ultra Mózgu
          isDnaReady={isDnaReady}  // NOWY PROP
        />

        {/* MODUŁ 4: Zaawansowane Wskaźniki Sprzedażowe - ULTRA MÓZG v4.0 */}
        {activeData?.sales_indicators && (
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
                  indicatorsData={activeData?.sales_indicators}
                  customerArchetype={activeArchetype}
                  psychologyConfidence={activeConfidence}
                  cumulativePsychology={activeData?.cumulative_psychology}
                  loading={activeLoading}
                  // NOWE PROPSY dla Ultra Mózgu
                  dnaKlienta={dnaKlienta}
                  isDnaReady={isDnaReady}
                  strategia={strategia}
                />
              </Box>
            </AccordionDetails>
          </Accordion>
        )}
        
        {/* Sekcja Archetypów */}
        <Accordion 
          expanded={expandedAccordion === 'archetypes'} 
          onChange={handleAccordionChange('archetypes')}
          sx={{ mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
              <PsychologyIcon color="primary" fontSize="small" />
              Customer Archetypes
              {archetypes.length > 0 && (
                <Badge badgeContent={archetypes.length} color="primary" />
              )}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {archetypes.length === 0 ? (
              <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
                Start a conversation to identify customer archetypes
              </Alert>
            ) : (
              <Stack spacing={2}>
                {archetypes.slice(0, 2).map((archetype, index) => (
                  <Card 
                    key={index}
                    variant="outlined" 
                    sx={{ 
                      position: 'relative',
                      bgcolor: index === 0 ? 'primary.lighter' : 'background.paper'
                    }}
                  >
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="h6" component="span">
                            {getArchetypeIcon(archetype.name)}
                          </Typography>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {archetype.name}
                          </Typography>
                          {index === 0 && (
                            <Chip 
                              label="Primary" 
                              size="small" 
                              color="primary" 
                              variant="outlined"
                            />
                          )}
                        </Box>
                        <Chip 
                          label={`${archetype.confidence || 0}%`}
                          size="small"
                          color={getConfidenceColor(archetype.confidence || 0)}
                        />
                      </Box>
                      
                      <LinearProgress 
                        variant="determinate" 
                        value={archetype.confidence || 0} 
                        sx={{ 
                          height: 6, 
                          borderRadius: 3,
                          mb: 1
                        }}
                        color={getConfidenceColor(archetype.confidence || 0)}
                      />
                      
                      {archetype.description && (
                        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                          {archetype.description}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Sekcja Profil Psychometryczny (Moduł 2) */}
        <Accordion 
          expanded={expandedAccordion === 'psychometric'} 
          onChange={handleAccordionChange('psychometric')}
          sx={{ mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
              <PsychologyIcon color="secondary" fontSize="small" />
              Szczegółowy Profil Psychometryczny
              <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                (Wykresy radarowe, Interactive Q&A)
              </Typography>
              {isDnaReady && (
                <Badge badgeContent="🧠⚡ ULTRA MÓZG" color="secondary" />
              )}
              {ultraBrainLoading && (
                <Badge badgeContent="..." color="info" />
              )}
              {ultraBrainPolling && (
                <Badge badgeContent="🔄 POLLING" color="warning" />
              )}
            </Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 0 }}>
            <Box sx={{ width: '100%' }}>
              <PsychometricDashboard 
                analysisData={activeData} 
                surowePsychology={surowePsychology}
                isUltraBrainReady={isUltraBrainReady}
                loading={activeLoading}
                isPolling={ultraBrainPolling}
                interactionId={currentInteractionId}
                onClarificationAnswered={handleClarificationAnswered}
              />
            </Box>
          </AccordionDetails>
        </Accordion>



        {/* 🧠⚡ ULTRA MÓZG v4.0: Strategic Insights - DNA KLIENTA */}
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
              <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
                Ultra Mózg analizuje profil psychologiczny klienta... DNA zostanie wygenerowane wkrótce.
              </Alert>
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
                <LinearProgress sx={{ flexGrow: 1 }} />
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
