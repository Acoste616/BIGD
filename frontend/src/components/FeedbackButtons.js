import React, { useState } from 'react';
import { Box, IconButton, Tooltip, Chip, CircularProgress } from '@mui/material';
import { ThumbUp, ThumbDown, CheckCircle } from '@mui/icons-material';
import { feedbackApi } from '../services';

/**
 * Komponent do oceniania pojedynczych sugestii AI
 * Zgodnie z Blueprint Granularnego Systemu Ocen
 */
const FeedbackButtons = ({ 
  interactionId, 
  suggestionId, 
  suggestionType,
  onFeedbackSent = null 
}) => {
  const [feedback, setFeedback] = useState(null); // null, 1, -1
  const [loading, setLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleFeedback = async (score) => {
    if (loading || feedback === score) return;
    
    setLoading(true);
    try {
      const feedbackData = {
        interaction_id: interactionId,
        suggestion_id: suggestionId,
        suggestion_type: suggestionType,
        score: score
      };

      await feedbackApi.createFeedback(interactionId, feedbackData);
      setFeedback(score);
      
      // Show success message
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
      
      if (onFeedbackSent) {
        onFeedbackSent(suggestionId, score);
      }
      
    } catch (error) {
      console.error('❌ Błąd podczas wysyłania feedback:', error);
      // Show error message
    } finally {
      setLoading(false);
    }
  };

  if (showSuccess) {
    return (
      <Chip
        icon={<CheckCircle />}
        label="Dziękujemy, uczę się!"
        color="success"
        size="small"
        variant="filled"
      />
    );
  }

  if (feedback !== null) {
    return (
      <Chip
        icon={<CheckCircle />}
        label={feedback === 1 ? "Przydatne" : "Nie przydatne"}
        color={feedback === 1 ? "success" : "error"}
        size="small"
        variant="filled"
      />
    );
  }

  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <Tooltip title="Przydatna sugestia">
        <IconButton
          size="small"
          onClick={() => handleFeedback(1)}
          disabled={loading}
          sx={{
            color: 'success.main',
            '&:hover': { backgroundColor: 'success.lighter' }
          }}
        >
          <ThumbUp fontSize="small" />
        </IconButton>
      </Tooltip>
      
      <Tooltip title="Nie przydatna sugestia">
        <IconButton
          size="small"
          onClick={() => handleFeedback(-1)}
          disabled={loading}
          sx={{
            color: 'error.main',
            '&:hover': { backgroundColor: 'error.lighter' }
          }}
        >
          <ThumbDown fontSize="small" />
        </IconButton>
      </Tooltip>
      
      {loading && <CircularProgress size={20} />}
    </Box>
  );
};

export default FeedbackButtons;