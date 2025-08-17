import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import ConversationView from './components/ConversationView';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ConversationView />
    </ThemeProvider>
  );
}

export default App;
