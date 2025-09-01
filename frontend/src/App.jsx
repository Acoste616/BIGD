import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';

// Import komponentów zgodnie z CHANGELOG
import Dashboard from './pages/Dashboard';
import ClientDetail from './pages/ClientDetail';
import NewSession from './pages/NewSession';
import SessionDetail from './pages/SessionDetail';
import InteractionDemo from './pages/InteractionDemo';
import KnowledgeAdmin from './pages/KnowledgeAdmin';
import AdminBrainInterface from './pages/AdminBrainInterface';  // AI Dojo - Moduł 3
import Settings from './pages/Settings';
import ConversationView from './components/ConversationView';  // Nowy workflow analizy

// Import motywu
import theme from './theme';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        {/* Główne ścieżki aplikacji */}
        <Route path="/" element={<Dashboard />} />
        
        {/* Nowy workflow analizy (AI-driven) */}
        <Route path="/analysis/new" element={<ConversationView />} />
        
        {/* Zarządzanie klientami */}
        <Route path="/clients/:clientId" element={<ClientDetail />} />
        
        {/* Sesje */}
        <Route path="/clients/:clientId/sessions/new" element={<NewSession />} />
        <Route path="/sessions/:sessionId" element={<SessionDetail />} />
        
        {/* Demo i narzędzia */}
        <Route path="/demo/interactions" element={<InteractionDemo />} />
        
        {/* Panel administracyjny */}
        <Route path="/admin/knowledge" element={<KnowledgeAdmin />} />
        <Route path="/admin/dojo" element={<AdminBrainInterface />} />  {/* AI Dojo - Moduł 3 */}
        
        {/* Ustawienia */}
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </ThemeProvider>
  );
}

export default App;