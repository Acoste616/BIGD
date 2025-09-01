import React, { useState } from 'react';
import { Box, IconButton, Tooltip, Chip, Snackbar, Alert } from '@mui/material';
import { ThumbUp, ThumbDown, CheckCircle } from '@mui/icons-material';
import { createFeedback } from '../services/feedbackApi';

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
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  const handleFeedback = async (score) => {
    if (loading || feedback === score) return;
    
    // 🚀 NATYCHMIASTOWY FEEDBACK WIZUALNY
    setFeedback(score);
    setLoading(true);
    
    try {
      const feedbackData = {
        interaction_id: interactionId,
        suggestion_id: suggestionId,
        suggestion_type: suggestionType,
        score: score
      };

      console.log('📊 FeedbackButtons - wysyłam ocenę:', feedbackData);
      await createFeedback(interactionId, feedbackData);
      
      // ✅ POMYŚLNE ZAPISANIE - Pokaż potwierdzenie
      setSnackbarMessage('Dziękujemy, ocena została zapisana!');
      setSnackbarSeverity('success');
      setShowSnackbar(true);
      
      if (onFeedbackSent) {
        onFeedbackSent(suggestionId, score);
      }
      
    } catch (error) {
      console.error('❌ Błąd podczas wysyłania feedback:', error);
      
      // 🚨 BŁĄD - Cofnij stan i pokaż komunikat błędu
      setFeedback(null);
      setSnackbarMessage(`Błąd: ${error.message || 'Nie udało się zapisać oceny'}`);
      setSnackbarSeverity('error');
      setShowSnackbar(true);
    } finally {
      setLoading(false);
    }
  };

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
    <>
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
      </Box>
      
      {/* 🎯 SNACKBAR - Potwierdzenie oceny */}
      <Snackbar
        open={showSnackbar}
        autoHideDuration={3000}
        onClose={() => setShowSnackbar(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setShowSnackbar(false)} 
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </>
  );
};

export default FeedbackButtons;
