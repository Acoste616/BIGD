import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import PromptSandbox from '../components/dojo/PromptSandbox'; // Import nowego komponentu

const DojoAdminPage = () => {
    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
                AI Dojo & Prompt Sandbox
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
                Zarządzaj, testuj i wdrażaj nowe wersje "mózgu" Twojego Co-Pilota.
            </Typography>
            
            <Paper elevation={3} sx={{ p: 2 }}>
                <PromptSandbox />
            </Paper>
        </Box>
    );
};

export default DojoAdminPage;