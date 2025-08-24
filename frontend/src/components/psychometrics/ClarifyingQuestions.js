import React, { useState } from 'react';
import { 
    Box, 
    Card, 
    CardContent, 
    Typography, 
    Button,
    ButtonGroup,
    Alert,
    Stack,
    Chip,
    LinearProgress,
    Fade
} from '@mui/material';
import { 
    QuestionAnswer as QuestionIcon,
    Psychology as PsychologyIcon,
    CheckCircle as CheckIcon,
    Lightbulb as InsightIcon
} from '@mui/icons-material';
import { sendClarifyingAnswer } from '../../services';

const ClarifyingQuestions = ({ 
    questions = [], 
    sessionId,        // NOWY v3.0: sessionId zamiast interactionId
    interactionId,    // DEPRECATED: zachowane dla backwards compatibility
    onAnswerSubmitted,
    loading = false 
}) => {
    const [selectedAnswers, setSelectedAnswers] = useState({});
    const [submittedQuestions, setSubmittedQuestions] = useState(new Set());
    const [submitting, setSubmitting] = useState(false);

    const handleAnswerSelection = async (questionId, selectedOption, questionData) => {
        try {
            setSubmitting(true);
            console.log('🎯 ClarifyingQuestions - odpowiadam na pytanie:', questionId, selectedOption);
            
            // Przygotuj odpowiedź dla backend
            const clarifyingAnswer = {
                question_id: questionId,
                question: questionData.question,
                selected_option: selectedOption,
                psychological_target: questionData.psychological_target,
                timestamp: new Date().toISOString()
            };
            
            // Wyślij do backend
            await sendClarifyingAnswer(interactionId, clarifyingAnswer);
            
            // Aktualizuj stan UI
            setSelectedAnswers(prev => ({
                ...prev,
                [questionId]: selectedOption
            }));
            
            setSubmittedQuestions(prev => new Set([...prev, questionId]));
            
            // Callback dla parent component
            if (onAnswerSubmitted) {
                onAnswerSubmitted(questionId, selectedOption, clarifyingAnswer);
            }
            
            console.log('✅ ClarifyingQuestions - odpowiedź wysłana pomyślnie');
            
        } catch (error) {
            console.error('❌ ClarifyingQuestions - błąd wysyłania odpowiedzi:', error);
        } finally {
            setSubmitting(false);
        }
    };

    if (!questions || questions.length === 0) {
        return null;
    }

    const allAnswered = questions.every(q => submittedQuestions.has(q.id));
    const answeredCount = submittedQuestions.size;

    return (
        <Box>
            {/* Header z postępem */}
            <Card elevation={2} sx={{ mb: 2, bgcolor: 'info.main', color: 'info.contrastText' }}>
                <CardContent sx={{ py: 2 }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box display="flex" alignItems="center" gap={2}>
                            <QuestionIcon sx={{ fontSize: 32 }} />
                            <Box>
                                <Typography variant="h6">
                                    🤔 AI Potrzebuje Więcej Informacji
                                </Typography>
                                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                                    Odpowiedz na obserwacje aby AI mógł precyzyjnie określić psychologię klienta
                                </Typography>
                            </Box>
                        </Box>
                        
                        <Chip 
                            label={`${answeredCount}/${questions.length}`}
                            color="secondary"
                            sx={{ fontWeight: 'bold' }}
                        />
                    </Box>
                    
                    {/* Progress Bar */}
                    <LinearProgress 
                        variant="determinate" 
                        value={(answeredCount / questions.length) * 100} 
                        sx={{ 
                            mt: 1, 
                            bgcolor: 'rgba(255,255,255,0.3)',
                            '& .MuiLinearProgress-bar': { bgcolor: 'secondary.main' }
                        }}
                    />
                </CardContent>
            </Card>

            {/* Lista pytań */}
            <Stack spacing={2}>
                {questions.map((question, index) => {
                    const isAnswered = submittedQuestions.has(question.id);
                    const selectedAnswer = selectedAnswers[question.id];
                    
                    return (
                        <Fade key={question.id} in={true} timeout={300 + index * 100}>
                            <Card 
                                variant="outlined"
                                sx={{ 
                                    border: '2px solid',
                                    borderColor: isAnswered ? 'success.main' : 'grey.300',
                                    bgcolor: isAnswered ? 'success.lighter' : 'background.paper'
                                }}
                            >
                                <CardContent sx={{ pb: 2 }}>
                                    {/* Header pytania */}
                                    <Box display="flex" alignItems="flex-start" gap={2} mb={2}>
                                        <Chip 
                                            label={`Q${index + 1}`} 
                                            color="primary" 
                                            size="small"
                                            sx={{ mt: 0.5 }}
                                        />
                                        <Box flexGrow={1}>
                                            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                                                {question.question}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                <InsightIcon sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'text-bottom' }} />
                                                Cel: {question.psychological_target}
                                            </Typography>
                                        </Box>
                                        
                                        {isAnswered && (
                                            <CheckIcon color="success" sx={{ mt: 0.5 }} />
                                        )}
                                    </Box>
                                    
                                    {/* Opcje odpowiedzi A/B */}
                                    {!isAnswered ? (
                                        <ButtonGroup 
                                            fullWidth 
                                            variant="outlined" 
                                            disabled={submitting}
                                            sx={{ mt: 1 }}
                                        >
                                            <Button
                                                onClick={() => handleAnswerSelection(question.id, question.option_a, question)}
                                                startIcon={<Typography sx={{ fontWeight: 'bold' }}>A</Typography>}
                                                sx={{ 
                                                    justifyContent: 'flex-start',
                                                    textTransform: 'none',
                                                    py: 1.5
                                                }}
                                            >
                                                {question.option_a}
                                            </Button>
                                            <Button
                                                onClick={() => handleAnswerSelection(question.id, question.option_b, question)}
                                                startIcon={<Typography sx={{ fontWeight: 'bold' }}>B</Typography>}
                                                sx={{ 
                                                    justifyContent: 'flex-start',
                                                    textTransform: 'none',
                                                    py: 1.5
                                                }}
                                            >
                                                {question.option_b}
                                            </Button>
                                        </ButtonGroup>
                                    ) : (
                                        <Alert 
                                            severity="success" 
                                            variant="outlined"
                                            sx={{ mt: 1 }}
                                        >
                                            <Typography variant="body2">
                                                <strong>Wybrano:</strong> {selectedAnswer}
                                                <br />
                                                <em>AI aktualizuje profil psychometryczny...</em>
                                            </Typography>
                                        </Alert>
                                    )}
                                </CardContent>
                            </Card>
                        </Fade>
                    );
                })}
            </Stack>

            {/* Status wszystkich odpowiedzi */}
            {allAnswered && (
                <Fade in={true} timeout={500}>
                    <Alert severity="success" sx={{ mt: 3 }}>
                        <Box display="flex" alignItems="center" gap={1}>
                            <PsychologyIcon />
                            <Typography variant="body2">
                                <strong>🎉 Wszystkie pytania odpowiedziane!</strong>
                                <br />
                                AI aktualizuje profil psychometryczny klienta na podstawie Twoich obserwacji.
                                Pełny profil pojawi się w ~15-30 sekund.
                            </Typography>
                        </Box>
                    </Alert>
                </Fade>
            )}

            {/* Loading overlay podczas submitting */}
            {submitting && (
                <Box 
                    sx={{ 
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        bgcolor: 'rgba(255,255,255,0.8)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 10
                    }}
                >
                    <LinearProgress sx={{ width: '50%' }} />
                </Box>
            )}
        </Box>
    );
};

export default ClarifyingQuestions;
