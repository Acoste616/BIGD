/**
 * Komponent do wyświetlania pojedynczej interakcji z analizą AI
 * Wyróżnia quick_response dla natychmiastowego użycia przez sprzedawcę
 */
import React, { useState } from 'react';
import { useInteractionFeedback } from '../hooks/useInteractionFeedback';
import FeedbackButtons from './FeedbackButtons';
import SuggestedQuestions from './SuggestedQuestions';
// import SystemInsights from './ComprehensiveAnalysis/SystemInsights';
// import FullAnalysisModal from './ComprehensiveAnalysis/FullAnalysisModal';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Alert,
  Paper,
  Box,
  Chip,
  IconButton,
  Collapse,
  Divider,
  Stack,
  Button,
  Tooltip,
  Rating,
  CircularProgress
} from '@mui/material';
import {
  ChatBubbleOutline as ChatBubbleOutlineIcon,
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  ContentCopy as ContentCopyIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  Assessment as AssessmentIcon,
  QuestionAnswer as QuestionAnswerIcon,
  Lightbulb as LightbulbIcon,
  SupportAgent as SupportAgentIcon,
  ThumbUpOffAlt as ThumbUpOffAltIcon,
  ThumbDownOffAlt as ThumbDownOffAltIcon,
  ThumbUpAlt as ThumbUpAltIcon,
  ThumbDownAlt as ThumbDownAltIcon
} from '@mui/icons-material';

// Mapowanie pilności na kolory
const urgencyColors = {
  'low': 'success',
  'medium': 'warning', 
  'high': 'error'
};

// Mapowanie pilności na etykiety polskie
const urgencyLabels = {
  'low': 'Niska',
  'medium': 'Średnia',
  'high': 'Wysoka'
};

const InteractionCard = ({ 
  interaction, 
  showFullDetails = true, 
  onCopyQuickResponse = null,
  onFeedback = null 
}) => {
  const [expanded, setExpanded] = useState(false);
  const [copiedQuickResponse, setCopiedQuickResponse] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  
  // Hook do zarządzania feedback dla tej interakcji
  const { 
    isLoading: isFeedbackLoading, 
    submittedRating, 
    canVote, 
    isPositiveVote, 
    isNegativeVote, 
    submitFeedback 
  } = useInteractionFeedback(interaction?.id);

  if (!interaction) {
    return null;
  }

  const aiResponse = interaction.ai_response_json || {};
  const quickResponse = aiResponse.quick_response;
  const isAIAvailable = !aiResponse.is_fallback;
  
  // Obsługa nowego formatu quick_response z unikalnym ID (Blueprint Feedback Loop)
  const quickResponseText = typeof quickResponse === 'object' && quickResponse?.text 
    ? quickResponse.text 
    : typeof quickResponse === 'string' 
    ? quickResponse 
    : null;
  const quickResponseId = typeof quickResponse === 'object' ? quickResponse?.id : null;

  // Handler dla kopiowania quick response
  const handleCopyQuickResponse = async () => {
    if (quickResponseText) {
      try {
        await navigator.clipboard.writeText(quickResponseText);
        setCopiedQuickResponse(true);
        setTimeout(() => setCopiedQuickResponse(false), 2000);
        
        if (onCopyQuickResponse) {
          onCopyQuickResponse(quickResponseText);
        }
      } catch (err) {
        console.error('Nie udało się skopiować tekstu:', err);
      }
    }
  };

  // Handler dla przełączania rozwinięcia
  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  // Formatowanie znacznika czasu
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Nieznany czas';
    
    try {
      return new Date(timestamp).toLocaleString('pl-PL', {
        year: 'numeric',
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Nieprawidłowa data';
    }
  };

  return (
    <Card 
      variant="outlined" 
      sx={{ 
        mb: 2,
        border: isAIAvailable ? '1px solid' : '1px dashed',
        borderColor: isAIAvailable ? 'divider' : 'warning.main',
        position: 'relative'
      }}
    >
      {/* Nagłówek interakcji */}
      <CardContent sx={{ pb: quickResponse ? 1 : 2 }}>
        {/* Metadane interakcji */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PersonIcon color="primary" fontSize="small" />
            <Typography variant="body2" color="text.secondary">
              {formatTimestamp(interaction.timestamp)}
            </Typography>
            {interaction.confidence_score && (
              <Chip 
                size="small" 
                label={`Pewność: ${interaction.confidence_score}%`}
                color={interaction.confidence_score >= 80 ? 'success' : interaction.confidence_score >= 60 ? 'warning' : 'error'}
                variant="outlined"
              />
            )}
          </Box>
          
          {!isAIAvailable && (
            <Tooltip title="AI był niedostępny - użyto odpowiedzi awaryjnej">
              <WarningIcon color="warning" fontSize="small" />
            </Tooltip>
          )}
        </Box>

        {/* Wejście użytkownika */}
        <Paper 
          variant="outlined" 
          sx={{ 
            p: 2, 
            mb: quickResponse ? 2 : 1,
            bgcolor: 'grey.50',
            borderLeft: '4px solid',
            borderLeftColor: interaction.isOptimistic ? 'warning.main' : 'primary.main',
            opacity: interaction.isOptimistic ? 0.8 : 1
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: 0.5 }}>
              {interaction.isOptimistic ? 'Wysyłanie...' : 'Sytuacja zgłoszona przez sprzedawcę'}
            </Typography>
            {interaction.isOptimistic && (
              <CircularProgress size={12} color="warning" />
            )}
          </Box>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            {interaction.user_input}
          </Typography>
        </Paper>

        {/* QUICK RESPONSE - główny element z granularnym feedback! */}
        {quickResponseText && (
          <Alert 
            severity="info"
            sx={{ 
              mb: 2,
              border: '2px solid',
              borderColor: 'info.main',
              bgcolor: 'info.lighter',
              '& .MuiAlert-message': { 
                width: '100%',
                fontSize: '1rem',
                fontWeight: 500
              }
            }}
            icon={<ChatBubbleOutlineIcon sx={{ fontSize: '1.5rem' }} />}
            action={
              <Box sx={{ display: 'flex', gap: 1 }}>
                {/* Blueprint Feedback Loop - Przyciski oceny dla quick_response */}
                {quickResponseId && (
                  <FeedbackButtons
                    interactionId={interaction.id}
                    suggestionId={quickResponseId}
                    suggestionType="quick_response"
                  />
                )}
                <Tooltip title={copiedQuickResponse ? "Skopiowano!" : "Kopiuj do schowka"}>
                  <IconButton
                    color="info"
                    size="small"
                    onClick={handleCopyQuickResponse}
                    sx={{ mr: 1 }}
                  >
                    {copiedQuickResponse ? <CheckCircleIcon /> : <ContentCopyIcon />}
                  </IconButton>
                </Tooltip>
              </Box>
            }
          >
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5, mb: 0.5 }}>
                💬 Sugerowana Odpowiedź
              </Typography>
              <Typography variant="body1" sx={{ lineHeight: 1.4 }}>
                "{quickResponseText}"
              </Typography>
            </Box>
          </Alert>
        )}

        {/* Podstawowe metryki AI */}
        {aiResponse.sentiment_score && aiResponse.potential_score && (
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">Sentyment:</Typography>
              <Rating 
                value={aiResponse.sentiment_score} 
                max={10} 
                size="small" 
                readOnly 
                sx={{ '& .MuiRating-icon': { fontSize: '1rem' } }}
              />
              <Typography variant="body2" fontWeight="bold">
                {aiResponse.sentiment_score}/10
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">Potencjał:</Typography>
              <Rating 
                value={aiResponse.potential_score} 
                max={10} 
                size="small" 
                readOnly 
                sx={{ '& .MuiRating-icon': { fontSize: '1rem' } }}
              />
              <Typography variant="body2" fontWeight="bold">
                {aiResponse.potential_score}/10
              </Typography>
            </Box>

            {aiResponse.urgency_level && (
              <Chip 
                size="small"
                label={`Pilność: ${urgencyLabels[aiResponse.urgency_level] || aiResponse.urgency_level}`}
                color={urgencyColors[aiResponse.urgency_level] || 'default'}
                icon={<ScheduleIcon fontSize="small" />}
              />
            )}
          </Box>
        )}

        {/* FEEDBACK SECTION - Pętla Informacji Zwrotnej */}
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'flex-end', 
          p: 1, 
          gap: 1,
          borderTop: '1px solid',
          borderTopColor: 'divider',
          mt: 2,
          pt: 2
        }}>
          {submittedRating ? (
            <Typography variant="caption" color="text.secondary" sx={{ mr: 'auto' }}>
              Dziękujemy za ocenę! 
              {isPositiveVote && ' 👍'} 
              {isNegativeVote && ' 👎'}
            </Typography>
          ) : (
            <Typography variant="caption" color="text.secondary" sx={{ mr: 'auto' }}>
              Czy ta sugestia była pomocna?
            </Typography>
          )}
          
          <Tooltip title="Pomocna sugestia">
            <span>
              <IconButton
                size="small"
                onClick={() => submitFeedback(1)}
                disabled={isFeedbackLoading || !canVote}
                color={isPositiveVote ? 'success' : 'default'}
                sx={{ 
                  border: isPositiveVote ? '2px solid' : '1px solid transparent',
                  borderColor: isPositiveVote ? 'success.main' : 'transparent'
                }}
              >
                {isPositiveVote ? <ThumbUpAltIcon /> : <ThumbUpOffAltIcon />}
              </IconButton>
            </span>
          </Tooltip>
          
          <Tooltip title="Niepomocna sugestia">
            <span>
              <IconButton
                size="small"
                onClick={() => submitFeedback(-1)}
                disabled={isFeedbackLoading || !canVote}
                color={isNegativeVote ? 'error' : 'default'}
                sx={{ 
                  border: isNegativeVote ? '2px solid' : '1px solid transparent',
                  borderColor: isNegativeVote ? 'error.main' : 'transparent'
                }}
              >
                {isNegativeVote ? <ThumbDownAltIcon /> : <ThumbDownOffAltIcon />}
              </IconButton>
            </span>
          </Tooltip>
        </Box>

        {/* BLUEPRINT ZADANIE 1: SuggestedQuestions component with types and feedback */}
        {aiResponse.suggested_questions?.length > 0 && (
          <SuggestedQuestions
            questions={aiResponse.suggested_questions}
            interactionId={interaction.id}
            onQuestionFeedback={(questionId, score, type, text) => {
              console.log('Question feedback:', questionId, score, type, text);
              // Optional: Propagate to parent component
              if (onFeedback) {
                onFeedback({
                  type: 'question_feedback',
                  questionId,
                  score,
                  questionType: type,
                  questionText: text
                });
              }
            }}
            title="🤔 Suggested Questions to Deepen Understanding"
            maxVisible={5}
          />
        )}
      </CardContent>

      {/* Szczegółowa analiza (rozwijana) */}
      {showFullDetails && (
        <>
          <CardActions sx={{ px: 2, py: 1, bgcolor: 'grey.50' }}>
            <Button
              onClick={() => setModalOpen(true)}
              size="small"
              sx={{ textTransform: 'none', fontWeight: 500 }}
            >
              Pokaż pełną analizę AI
            </Button>
            
            <Button
              onClick={handleExpandClick}
              endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              size="small"
              sx={{ textTransform: 'none', fontWeight: 500, ml: 1 }}
            >
              {expanded ? 'Ukryj szczegóły' : 'Pokaż szczegóły'}
            </Button>
            
            {aiResponse.next_best_action && (
              <Chip 
                size="small"
                label={aiResponse.next_best_action}
                color="primary"
                variant="outlined"
                sx={{ ml: 'auto', maxWidth: 200 }}
              />
            )}
          </CardActions>

          <Collapse in={expanded} timeout="auto" unmountOnExit>
            <CardContent sx={{ pt: 2, bgcolor: 'grey.25' }}>
              {/* Główna analiza */}
              {aiResponse.main_analysis && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <AssessmentIcon color="primary" />
                    Analiza sytuacji
                  </Typography>
                  <Typography variant="body1" sx={{ fontStyle: 'italic', lineHeight: 1.6 }}>
                    {aiResponse.main_analysis}
                  </Typography>
                </Box>
              )}

              {/* Sugerowane akcje */}
              {aiResponse.suggested_actions?.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <LightbulbIcon color="primary" />
                    Sugerowane akcje
                  </Typography>
                  <Stack spacing={1}>
                    {aiResponse.suggested_actions.map((action, index) => (
                      <Paper key={index} variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="body1" fontWeight="bold" sx={{ mb: 0.5 }}>
                          {index + 1}. {action.action}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {action.reasoning}
                        </Typography>
                      </Paper>
                    ))}
                  </Stack>
                </Box>
              )}

              {/* Sygnały */}
              {(aiResponse.buy_signals?.length > 0 || aiResponse.risk_signals?.length > 0) && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <SupportAgentIcon color="primary" />
                    Zidentyfikowane sygnały
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    {aiResponse.buy_signals?.map((signal, index) => (
                      <Chip 
                        key={`buy-${index}`}
                        icon={<TrendingUpIcon />}
                        label={signal}
                        color="success"
                        variant="outlined"
                        size="small"
                      />
                    ))}
                    
                    {aiResponse.risk_signals?.map((signal, index) => (
                      <Chip 
                        key={`risk-${index}`}
                        icon={<TrendingDownIcon />}
                        label={signal}
                        color="warning"
                        variant="outlined"
                        size="small"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {/* Pytania kwalifikujące */}
              {aiResponse.qualifying_questions?.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <QuestionAnswerIcon color="primary" />
                    Sugerowane pytania
                  </Typography>
                  <Stack spacing={1}>
                    {aiResponse.qualifying_questions.map((question, index) => {
                      // Obsługa formatu question z unikalnym ID (Blueprint)
                      const questionText = typeof question === 'object' && question?.text 
                        ? question.text 
                        : typeof question === 'string' 
                        ? question 
                        : '';
                      const questionId = typeof question === 'object' ? question?.id : null;
                      
                      return (
                        <Box key={questionId || index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                          <Typography variant="body2" sx={{ pl: 2, position: 'relative', flex: 1 }}>
                            <Box component="span" sx={{ position: 'absolute', left: 0, color: 'primary.main', fontWeight: 'bold' }}>
                              Q:
                            </Box>
                            {questionText}
                          </Typography>
                          {/* Feedback buttons dla qualifying questions */}
                          {questionId && (
                            <FeedbackButtons
                              interactionId={interaction.id}
                              suggestionId={questionId}
                              suggestionType="qualifying_question"
                            />
                          )}
                        </Box>
                      );
                    })}
                  </Stack>
                </Box>
              )}

              {/* System Insights - wglądy w proces myślowy AI */}
              {/* {(aiResponse.knowledge_base_insights || aiResponse.strategic_insights) && (
                <SystemInsights 
                  data={{
                    knowledge_base_insights: aiResponse.knowledge_base_insights,
                    strategic_insights: aiResponse.strategic_insights
                  }}
                />
              )} */}
            </CardContent>
          </Collapse>
        </>
      )}
      
      {/* FullAnalysisModal - ZADANIE 4 BLUEPRINT v6.0 */}
      {/* <FullAnalysisModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        data={{
          product_recommendation: aiResponse.product_recommendation,
          sales_triggers: aiResponse.sales_triggers,
          strategy_dos_and_donts: aiResponse.strategy_dos_and_donts,
          next_steps_plan: aiResponse.next_steps_plan
        }}
      /> */}
    </Card>
  );
};

export default InteractionCard;
