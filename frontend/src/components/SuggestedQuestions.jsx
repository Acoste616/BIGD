/**
 * SuggestedQuestions - ZADANIE 1 BLUEPRINT v6.0
 * 
 * Przebudowany komponent zgodny z wymaganiami Blueprint Naprawczy:
 * - Props z typami: questions: [{ type: 'clarifying' | 'psychometric', text: '...' }]
 * - Dynamiczne ikony/etykiety w zależności od type
 * - FeedbackButtons w pętli map() - każde pytanie z własnym niezależnym komponentem oceny
 * 
 * BLUEPRINT LOKALIZACJA: frontend/src/components/conversation/ConversationStream.js
 */
import React from 'react';
import {
  Box,
  Typography,
  Stack,
  Paper,
  Chip,
  Tooltip
} from '@mui/material';
import {
  QuestionAnswer as QuestionAnswerIcon,
  Psychology as PsychologyIcon,
  Search as SearchIcon,
  TrendingUp as StrategicIcon,
  HelpOutline as ClarifyingIcon
} from '@mui/icons-material';
import FeedbackButtons from './FeedbackButtons';

// Mapowanie typów pytań na ikony i kolory (NOWE WYMAGANIE BLUEPRINT)
const questionTypeConfig = {
  'clarifying': {
    icon: ClarifyingIcon,
    label: 'Pytanie pogłębiające',
    color: 'primary',
    bgColor: 'primary.lighter',
    borderColor: 'primary.main',
    description: 'Pomaga lepiej zrozumieć potrzeby klienta'
  },
  'psychometric': {
    icon: PsychologyIcon,
    label: 'Analiza psychometryczna', 
    color: 'secondary',
    bgColor: 'secondary.lighter',
    borderColor: 'secondary.main',
    description: 'Określa profil osobowości klienta'
  },
  'strategic': {
    icon: StrategicIcon,
    label: 'Pytanie strategiczne',
    color: 'success',
    bgColor: 'success.lighter', 
    borderColor: 'success.main',
    description: 'Pomaga w planowaniu strategii sprzedaży'
  }
};

const SuggestedQuestions = ({ 
  questions = [], 
  interactionId,
  onQuestionFeedback,
  title = "Sugerowane pytania",
  maxVisible = 5
}) => {
  // Walidacja danych wejściowych
  if (!questions || questions.length === 0) {
    return null;
  }

  // Ogranicz liczbę wyświetlanych pytań
  const visibleQuestions = questions.slice(0, maxVisible);

  const getQuestionConfig = (type) => {
    return questionTypeConfig[type] || questionTypeConfig['clarifying'];
  };

  return (
    <Paper 
      variant="outlined"
      sx={{ 
        p: 2,
        mb: 2,
        bgcolor: 'background.default',
        border: '2px solid',
        borderColor: 'divider',
        borderRadius: 2
      }}
    >
      {/* Header z tytułem */}
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <QuestionAnswerIcon color="primary" />
        <Typography 
          variant="subtitle2" 
          sx={{ 
            fontWeight: 600,
            color: 'primary.main',
            textTransform: 'uppercase',
            letterSpacing: 0.5,
            fontSize: '0.8rem'
          }}
        >
          {title}
        </Typography>
        <Chip 
          size="small" 
          label={visibleQuestions.length} 
          color="primary" 
          variant="outlined"
          sx={{ ml: 'auto', fontSize: '0.7rem' }}
        />
      </Box>

      {/* Lista pytań z dynamicznymi ikonami i feedback buttons */}
      <Stack spacing={1.5}>
        {visibleQuestions.map((question, index) => {
          // Obsługa różnych formatów question object
          const questionId = question.id || `q_${index}`;
          const questionText = question.text || question.question || '';
          const questionType = question.type || 'clarifying';
          const questionRationale = question.rationale || '';
          
          const config = getQuestionConfig(questionType);
          const IconComponent = config.icon;

          return (
            <Paper
              key={questionId}
              variant="outlined"
              sx={{
                p: 2,
                bgcolor: config.bgColor,
                borderLeft: '4px solid',
                borderLeftColor: config.borderColor,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  boxShadow: 2,
                  borderLeftWidth: '6px'
                }
              }}
            >
              {/* Header pytania z typem i ikoną */}
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, mb: 1 }}>
                <Tooltip title={config.description}>
                  <IconComponent 
                    sx={{ 
                      color: `${config.color}.main`,
                      fontSize: '1.2rem',
                      mt: 0.1
                    }} 
                  />
                </Tooltip>
                
                <Box sx={{ flex: 1 }}>
                  {/* Typ pytania jako label */}
                  <Chip
                    size="small"
                    label={config.label}
                    color={config.color}
                    variant="outlined"
                    sx={{ 
                      mb: 1,
                      fontSize: '0.7rem',
                      height: '20px'
                    }}
                  />
                  
                  {/* Tekst pytania */}
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontStyle: 'italic',
                      lineHeight: 1.4,
                      color: 'text.primary',
                      fontWeight: 500
                    }}
                  >
                    "{questionText}"
                  </Typography>
                  
                  {/* Uzasadnienie (jeśli dostępne) */}
                  {questionRationale && (
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        display: 'block',
                        mt: 0.5,
                        color: 'text.secondary',
                        fontSize: '0.75rem',
                        fontStyle: 'normal'
                      }}
                    >
                      💡 {questionRationale}
                    </Typography>
                  )}
                </Box>
              </Box>

              {/* BLUEPRINT WYMAGANIE: FeedbackButtons w pętli map() */}
              {/* Każde pytanie ma własny niezależny komponent oceny */}
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'flex-end',
                alignItems: 'center',
                mt: 1.5,
                pt: 1,
                borderTop: '1px solid',
                borderTopColor: 'divider'
              }}>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    mr: 'auto',
                    color: 'text.secondary',
                    fontSize: '0.75rem'
                  }}
                >
                  Czy to pytanie jest pomocne?
                </Typography>
                
                <FeedbackButtons
                  interactionId={interactionId}
                  suggestionId={questionId}
                  suggestionType={`suggested_question_${questionType}`}
                  onFeedbackSent={(id, score) => {
                    // Callback do parent component
                    if (onQuestionFeedback) {
                      onQuestionFeedback(id, score, questionType, questionText);
                    }
                  }}
                />
              </Box>
            </Paper>
          );
        })}
      </Stack>

      {/* Footer z informacją o ukrytych pytaniach */}
      {questions.length > maxVisible && (
        <Box sx={{ 
          mt: 2, 
          pt: 1, 
          borderTop: '1px solid', 
          borderTopColor: 'divider',
          textAlign: 'center'
        }}>
          <Typography variant="caption" color="text.secondary">
            Pokazano {maxVisible} z {questions.length} pytań
          </Typography>
        </Box>
      )}
      
      {/* Debug info (tylko w development) */}
      {import.meta.env.DEV && (
        <Box sx={{ 
          mt: 2, 
          p: 1, 
          bgcolor: 'grey.100', 
          borderRadius: 1,
          fontSize: '0.7rem'
        }}>
          <Typography variant="caption" color="text.secondary">
            DEBUG: {questions.length} questions, interactionId: {interactionId}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default SuggestedQuestions;
