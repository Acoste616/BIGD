/**
 * ConversationView - Główny interfejs konwersacyjny aplikacji
 * 
 * Layout podzielony na dwie części:
 * - Lewa strona (70%): Strumień konwersacji z formularzem i historią
 * - Prawa strona (30%): Panel strategiczny z archetypami i wiedzą
 */
import React, { useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import MainLayout from './MainLayout';
import ConversationStream from './conversation/ConversationStream';
import StrategicPanel from './conversation/StrategicPanel';

const ConversationView = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('lg'));
  
  // Stan bieżącej sesji - nowa logika z clientId i sessionId
  const [currentClientId, setCurrentClientId] = useState(null);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [currentSession, setCurrentSession] = useState(null);
  const [interactions, setInteractions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Stan panelu strategicznego
  const [archetypes, setArchetypes] = useState([]);
  const [strategicInsights, setStrategicInsights] = useState([]);

  return (
    <MainLayout title="AI Sales Co-Pilot - Live Session">
      <Box sx={{ height: 'calc(100vh - 140px)', overflow: 'hidden' }}>
        <Grid container spacing={2} sx={{ height: '100%' }}>
          {/* Lewa strona: Strumień konwersacji (70%) */}
          <Grid 
            item 
            xs={12} 
            lg={8.5} 
            sx={{ 
              height: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Paper 
              elevation={1}
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid',
                borderColor: 'divider'
              }}
            >
              <ConversationStream
                currentClientId={currentClientId}
                currentSessionId={currentSessionId}
                currentSession={currentSession}
                interactions={interactions}
                isLoading={isLoading}
                onNewInteraction={(interaction) => {
                  setInteractions(prev => [...prev, interaction]);
                }}
                onSessionUpdate={setCurrentSession}
                onClientIdUpdate={setCurrentClientId}
                onSessionIdUpdate={setCurrentSessionId}
                onArchetypesUpdate={setArchetypes}
                onInsightsUpdate={setStrategicInsights}
              />
            </Paper>
          </Grid>

          {/* Prawa strona: Panel strategiczny (30%) */}
          <Grid 
            item 
            xs={12} 
            lg={3.5} 
            sx={{ 
              height: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Paper 
              elevation={1}
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid',
                borderColor: 'divider',
                bgcolor: 'background.paper'
              }}
            >
              <StrategicPanel
                archetypes={archetypes}
                insights={strategicInsights}
                currentSession={currentSession}
                isLoading={isLoading}
              />
            </Paper>
          </Grid>
        </Grid>

        {/* Mobile: Stack vertically */}
        {isMobile && (
          <Box sx={{ 
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            zIndex: 1000,
            bgcolor: 'background.paper',
            borderTop: '1px solid',
            borderColor: 'divider',
            p: 2
          }}>
            {/* Mobile strategic panel collapsed */}
          </Box>
        )}
      </Box>
    </MainLayout>
  );
};

export default ConversationView;
