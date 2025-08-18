import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ConversationView from './components/ConversationView';
import KnowledgeAdmin from './pages/KnowledgeAdmin';
import Settings from './pages/Settings';

function App() {
  return (
    <Routes>
      <Route path="/" element={<ConversationView />} />
      <Route path="/admin/knowledge" element={<KnowledgeAdmin />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  );
}

export default App;