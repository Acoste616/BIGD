import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

const QuestionsPanel = ({ sessionId }) => {
    return (
        <Paper elevation={2} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
                Arsenał Pytań
            </Typography>
            
            <Box sx={{ mt: 2, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                <Typography variant="subtitle2" color="text.secondary">Pytania DO KLIENTA:</Typography>
                {/* TODO: Tutaj będą wyświetlane dynamiczne pytania do klienta */}
            </Box>

            <Box sx={{ mt: 4 }}>
                <Typography variant="subtitle2" color="text.secondary">Pytania DO MNIE (dla AI):</Typography>
                {/* TODO: Tutaj będą wyświetlane pytania klaryfikujące od AI */}
            </Box>
        </Paper>
    );
};

export default QuestionsPanel;