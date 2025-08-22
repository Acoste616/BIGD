/**
 * useDojoChat Hook - Zarządzanie stanem konwersacji treningowej AI Dojo
 * 
 * Moduł 3: Interaktywne AI Dojo "Sparing z Mistrzem"
 * 
 * Hook zarządza:
 * - Stanem konwersacji (wiadomości, loading, błędy)
 * - Wysyłaniem wiadomości do AI
 * - Potwierdzaniem zapisu wiedzy
 * - Historią konwersacji i sesji treningowej
 */
import { useState, useCallback, useEffect, useRef } from 'react';
import {
  sendDojoMessage,
  confirmKnowledgeWrite,
  getSessionSummary,
  validateDojoMessage,
  formatDojoResponse,
  generateSessionId,
  TRAINING_MODES,
  RESPONSE_TYPES
} from '../services/dojoApi';

/**
 * Hook główny - useDojoChat
 * 
 * @param {Object} options - Opcje konfiguracji
 * @param {string} [options.expertName='Administrator'] - Nazwa eksperta
 * @param {string} [options.trainingMode='knowledge_update'] - Tryb treningu
 * @param {boolean} [options.autoFocus=true] - Auto focus na input po wysłaniu
 * @param {Function} [options.onError] - Callback dla błędów
 * @param {Function} [options.onSuccess] - Callback dla sukcesu
 * @returns {Object} Stan i funkcje do zarządzania chatem
 * 
 * @example
 * const {
 *   messages, sendMessage, isLoading, error,
 *   sessionId, clearChat, confirmKnowledge
 * } = useDojoChat({
 *   expertName: 'Product Expert',
 *   trainingMode: 'knowledge_update'
 * });
 */
export const useDojoChat = (options = {}) => {
  const {
    expertName = 'Administrator',
    trainingMode = TRAINING_MODES.KNOWLEDGE_UPDATE,
    autoFocus = true,
    onError = null,
    onSuccess = null
  } = options;

  // === CORE STATE ===
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  
  // === EXTENDED STATE ===
  const [sessionSummary, setSessionSummary] = useState(null);
  const [pendingConfirmation, setPendingConfirmation] = useState(null);
  const [isConfirming, setIsConfirming] = useState(false);

  // === REFS ===
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  /**
   * CORE FUNCTIONS
   */

  /**
   * Wyślij wiadomość do AI
   * 
   * @param {string} messageText - Tekst wiadomości
   * @param {Object} [options={}] - Dodatkowe opcje
   * @returns {Promise<void>}
   */
  const sendMessage = useCallback(async (messageText, options = {}) => {
    try {
      // Walidacja wejścia
      const validation = validateDojoMessage({ message: messageText });
      if (!validation.isValid) {
        const errorMessage = validation.errors.join(', ');
        setError(errorMessage);
        if (onError) onError(new Error(errorMessage));
        return;
      }

      setIsLoading(true);
      setError(null);

      // Przygotuj payload
      const payload = {
        message: messageText,
        training_mode: options.trainingMode || trainingMode,
        conversation_history: messages.map(msg => ({
          timestamp: msg.timestamp,
          message: msg.type === 'user' ? msg.text : msg.response,
          sender: msg.type === 'user' ? 'expert' : 'ai'
        })),
        client_context: options.clientContext || null
      };

      // Dodaj wiadomość użytkownika do stanu
      const userMessage = {
        id: `user_${Date.now()}`,
        type: 'user',
        text: messageText,
        timestamp: new Date().toISOString(),
        expertName: expertName
      };

      setMessages(prev => [...prev, userMessage]);

      console.log('🎓 useDojoChat: Wysyłam wiadomość do AI', {
        messageLength: messageText.length,
        sessionId: sessionId,
        trainingMode: payload.training_mode
      });

      // Wywołaj API
      const response = await sendDojoMessage(payload, sessionId, expertName);

      // Jeśli to pierwsza wiadomość, ustaw sessionId
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
      }

      // Sformatuj odpowiedź AI
      const formattedResponse = formatDojoResponse(response);

      // Dodaj odpowiedź AI do stanu
      const aiMessage = {
        id: `ai_${Date.now()}`,
        type: 'ai',
        ...formattedResponse,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);

      // Obsłuż specjalne typy odpowiedzi
      if (response.response_type === RESPONSE_TYPES.CONFIRMATION) {
        setPendingConfirmation({
          sessionId: sessionId,
          structuredData: response.structured_data,
          messageId: aiMessage.id
        });
      }

      // Callback sukcesu
      if (onSuccess) {
        onSuccess(response);
      }

      console.log('✅ useDojoChat: Odpowiedź AI otrzymana', {
        responseType: response.response_type,
        confidence: response.confidence_level
      });

    } catch (error) {
      console.error('❌ useDojoChat: Błąd podczas wysyłania:', error);
      
      setError(error.message || 'Błąd podczas wysyłania wiadomości');
      
      if (onError) {
        onError(error);
      }
    } finally {
      setIsLoading(false);
      
      // Auto-scroll do dołu
      setTimeout(() => {
        scrollToBottom();
      }, 100);
      
      // Auto-focus na input
      if (autoFocus && inputRef.current) {
        setTimeout(() => {
          inputRef.current.focus();
        }, 200);
      }
    }
  }, [messages, sessionId, expertName, trainingMode, onError, onSuccess, autoFocus]);

  /**
   * Potwierdź zapis wiedzy do bazy
   * 
   * @param {boolean} [confirmed=true] - Czy zatwierdzić zapis
   * @returns {Promise<void>}
   */
  const confirmKnowledge = useCallback(async (confirmed = true) => {
    if (!pendingConfirmation) {
      console.warn('⚠️ useDojoChat: Brak oczekującej konfirmacji');
      return;
    }

    try {
      setIsConfirming(true);
      setError(null);

      console.log(`💾 useDojoChat: ${confirmed ? 'Zatwierdzam' : 'Anuluję'} zapis wiedzy`, {
        sessionId: pendingConfirmation.sessionId,
        dataTitle: pendingConfirmation.structuredData?.title
      });

      // Wywołaj API potwierdzenia
      const response = await confirmKnowledgeWrite(
        pendingConfirmation.sessionId,
        pendingConfirmation.structuredData,
        confirmed
      );

      // Dodaj wiadomość systemową o rezultacie
      const systemMessage = {
        id: `system_${Date.now()}`,
        type: 'system',
        text: response.response,
        timestamp: new Date().toISOString(),
        success: response.response_type === 'status' && confirmed,
        cancelled: !confirmed
      };

      setMessages(prev => [...prev, systemMessage]);

      // Wyczyść pending confirmation
      setPendingConfirmation(null);

      console.log(`✅ useDojoChat: Wiedza ${confirmed ? 'zapisana' : 'anulowana'}`);

    } catch (error) {
      console.error('❌ useDojoChat: Błąd podczas potwierdzania:', error);
      
      setError(error.message || 'Błąd podczas zapisywania wiedzy');
      
      if (onError) {
        onError(error);
      }
    } finally {
      setIsConfirming(false);
    }
  }, [pendingConfirmation, onError]);

  /**
   * UTILITY FUNCTIONS
   */

  /**
   * Wyczyść chat i rozpocznij nową sesję
   */
  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    setSessionId(null);
    setSessionSummary(null);
    setPendingConfirmation(null);
    setIsConfirming(false);
    
    console.log('🧹 useDojoChat: Chat wyczyszczony');
  }, []);

  /**
   * Przewiń do dołu konwersacji
   */
  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  /**
   * Pobierz podsumowanie aktualnej sesji
   */
  const refreshSessionSummary = useCallback(async () => {
    if (!sessionId) return;

    try {
      const summary = await getSessionSummary(sessionId);
      setSessionSummary(summary);
      
      console.log('📊 useDojoChat: Session summary odświeżone', {
        messages: summary.total_messages,
        knowledgeItems: summary.knowledge_items_added
      });
      
    } catch (error) {
      console.error('❌ useDojoChat: Błąd podczas pobierania podsumowania:', error);
      // Nie ustawiamy błędu globalnego dla podsumowania - to nie krytyczne
    }
  }, [sessionId]);

  /**
   * Usuń konkretną wiadomość z historii
   */
  const removeMessage = useCallback((messageId) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
    console.log('🗑️ useDojoChat: Usunięto wiadomość:', messageId);
  }, []);

  /**
   * EFFECTS
   */

  // Auto-scroll po dodaniu nowych wiadomości
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Odświeżaj podsumowanie sesji co 30 sekund
  useEffect(() => {
    if (!sessionId) return;

    const interval = setInterval(() => {
      refreshSessionSummary();
    }, 30000); // 30 sekund

    return () => clearInterval(interval);
  }, [sessionId, refreshSessionSummary]);

  // Generuj sessionId jeśli nie ma
  useEffect(() => {
    if (!sessionId && messages.length === 0) {
      const newSessionId = generateSessionId();
      setSessionId(newSessionId);
      console.log('🆔 useDojoChat: Wygenerowano nowe sessionId:', newSessionId);
    }
  }, [sessionId, messages.length]);

  /**
   * COMPUTED VALUES
   */

  const hasMessages = messages.length > 0;
  const hasPendingConfirmation = !!pendingConfirmation;
  const isSessionActive = !!sessionId;
  const lastAiMessage = messages.filter(m => m.type === 'ai').slice(-1)[0];
  const messageCount = messages.length;
  const userMessageCount = messages.filter(m => m.type === 'user').length;
  const aiMessageCount = messages.filter(m => m.type === 'ai').length;

  /**
   * RETURN OBJECT
   */
  return {
    // Core state
    messages,
    isLoading,
    error,
    sessionId,
    
    // Extended state  
    sessionSummary,
    pendingConfirmation,
    isConfirming,
    
    // Core functions
    sendMessage,
    confirmKnowledge,
    
    // Utility functions
    clearChat,
    scrollToBottom,
    refreshSessionSummary,
    removeMessage,
    
    // Computed values
    hasMessages,
    hasPendingConfirmation,
    isSessionActive,
    lastAiMessage,
    messageCount,
    userMessageCount,
    aiMessageCount,
    
    // Refs (do użycia w komponencie)
    messagesEndRef,
    inputRef,
    
    // Configuration
    expertName,
    trainingMode
  };
};

/**
 * Hook do zarządzania wieloma sesjami treningowymi
 * 
 * @returns {Object} Stan i funkcje dla multi-session management
 */
export const useDojoSessions = () => {
  const [activeSessions, setActiveSessions] = useState(new Map());
  const [currentSessionId, setCurrentSessionId] = useState(null);
  
  const createSession = useCallback((sessionId, options = {}) => {
    const session = {
      id: sessionId,
      expertName: options.expertName || 'Administrator',
      trainingMode: options.trainingMode || TRAINING_MODES.KNOWLEDGE_UPDATE,
      createdAt: new Date().toISOString(),
      messages: [],
      isActive: true
    };
    
    setActiveSessions(prev => new Map(prev).set(sessionId, session));
    setCurrentSessionId(sessionId);
    
    return session;
  }, []);
  
  const switchToSession = useCallback((sessionId) => {
    if (activeSessions.has(sessionId)) {
      setCurrentSessionId(sessionId);
      return activeSessions.get(sessionId);
    }
    return null;
  }, [activeSessions]);
  
  const closeSession = useCallback((sessionId) => {
    setActiveSessions(prev => {
      const updated = new Map(prev);
      if (updated.has(sessionId)) {
        const session = updated.get(sessionId);
        updated.set(sessionId, { ...session, isActive: false });
      }
      return updated;
    });
  }, []);
  
  const currentSession = currentSessionId ? activeSessions.get(currentSessionId) : null;
  
  return {
    activeSessions: Array.from(activeSessions.values()),
    currentSession,
    currentSessionId,
    createSession,
    switchToSession,
    closeSession,
    sessionCount: activeSessions.size
  };
};

/**
 * Hook do statystyk AI Dojo
 * 
 * @param {Object} options - Opcje
 * @param {boolean} [options.autoRefresh=true] - Auto odświeżanie
 * @param {number} [options.refreshInterval=60000] - Interwał odświeżania (ms)
 * @returns {Object} Statystyki i funkcje
 */
export const useDojoAnalytics = (options = {}) => {
  const { autoRefresh = true, refreshInterval = 60000 } = options;
  
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Import dynamiczny żeby uniknąć circular imports
      const { getDojoAnalytics } = await import('../services/dojoApi');
      const data = await getDojoAnalytics();
      
      setAnalytics(data);
      
    } catch (err) {
      console.error('❌ useDojoAnalytics: Error fetching data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);
  
  // Auto refresh
  useEffect(() => {
    fetchAnalytics(); // Initial fetch
    
    if (autoRefresh) {
      const interval = setInterval(fetchAnalytics, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchAnalytics, autoRefresh, refreshInterval]);
  
  return {
    analytics,
    loading,
    error,
    refresh: fetchAnalytics
  };
};

// Export hooks
export default useDojoChat;