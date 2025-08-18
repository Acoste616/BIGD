import React from 'react';
import MainLayout from '../components/MainLayout';
import { Typography, Container, Paper, Box } from '@mui/material';

function Settings() {
  return (
    <MainLayout>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper sx={{ p: 4 }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              Ustawienia
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Panel ustawień aplikacji Tesla Co-Pilot. Funkcjonalność w trakcie rozwoju.
            </Typography>
          </Box>
        </Paper>
      </Container>
    </MainLayout>
  );
}

export default Settings;
