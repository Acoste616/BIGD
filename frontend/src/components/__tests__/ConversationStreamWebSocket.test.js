import React from 'react';
import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import ConversationStream from '../components/conversation/ConversationStream';

// Mock WebSocket
const mockWebSocket = {
  close: jest.fn(),
  send: jest.fn()
};

global.WebSocket = jest.fn(() => mockWebSocket);

// Mock API services
jest.mock('../services/interactionsApi', () => ({
  createInteraction: jest.fn()
}));

jest.mock('../services/clientsApi', () => ({
  createClient: jest.fn()
}));

jest.mock('../services/sessionsApi', () => ({
  createSession: jest.fn()
}));

describe('ConversationStream WebSocket Integration', () => {
  const defaultProps = {
    currentClientId: 1,
    currentSessionId: 123,
    currentSession: {},
    interactions: [],
    isLoading: false,
    onNewInteraction: jest.fn(),
    onSessionUpdate: jest.fn(),
    onClientIdUpdate: jest.fn(),
    onSessionIdUpdate: jest.fn(),
    onArchetypesUpdate: jest.fn(),
    onInsightsUpdate: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    WebSocket.mockClear();
  });

  it('creates WebSocket connection when session ID is provided', () => {
    render(<ConversationStream {...defaultProps} />);
    
    // Check that WebSocket was created with correct URL
    expect(WebSocket).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/ws/123')
    );
  });

  it('handles WebSocket connection events', () => {
    render(<ConversationStream {...defaultProps} />);
    
    // Simulate connection open
    const connectionEvent = { data: JSON.stringify({ event: 'connected', message: 'WebSocket connection established' }) };
    mockWebSocket.onopen();
    mockWebSocket.onmessage(connectionEvent);
    
    // Verify connection state
    expect(screen.queryByText('Connecting...')).not.toBeInTheDocument();
  });

  it('handles analysis_complete WebSocket messages', async () => {
    const mockOnNewInteraction = jest.fn();
    const mockOnArchetypesUpdate = jest.fn();
    const mockOnInsightsUpdate = jest.fn();
    
    render(
      <ConversationStream 
        {...defaultProps}
        onNewInteraction={mockOnNewInteraction}
        onArchetypesUpdate={mockOnArchetypesUpdate}
        onInsightsUpdate={mockOnInsightsUpdate}
      />
    );
    
    // Simulate analysis_complete message
    const analysisMessage = {
      data: JSON.stringify({
        event: 'analysis_complete',
        session_id: 123,
        data: {
          interaction_id: 456,
          ai_response: {
            main_analysis: 'Test analysis',
            likely_archetypes: ['analityk'],
            strategic_notes: ['Test note']
          }
        },
        timestamp: new Date().toISOString()
      })
    };
    
    await act(async () => {
      mockWebSocket.onmessage(analysisMessage);
    });
    
    // Verify callbacks were called with correct data
    expect(mockOnNewInteraction).toHaveBeenCalledWith({
      id: 456,
      ai_response_json: {
        main_analysis: 'Test analysis',
        likely_archetypes: ['analityk'],
        strategic_notes: ['Test note']
      },
      timestamp: expect.any(String)
    });
    
    expect(mockOnArchetypesUpdate).toHaveBeenCalledWith(['analityk']);
    expect(mockOnInsightsUpdate).toHaveBeenCalledWith(['Test note']);
  });

  it('handles WebSocket error messages', async () => {
    render(<ConversationStream {...defaultProps} />);
    
    // Simulate error message
    const errorMessage = {
      data: JSON.stringify({
        event: 'error',
        data: 'Connection error'
      })
    };
    
    await act(async () => {
      mockWebSocket.onmessage(errorMessage);
    });
    
    // Verify error is displayed
    expect(screen.getByText('Connection error: Connection error')).toBeInTheDocument();
  });

  it('handles WebSocket disconnection', () => {
    render(<ConversationStream {...defaultProps} />);
    
    // Simulate disconnection
    mockWebSocket.onclose();
    
    // Verify connection status
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
  });

  it('attempts reconnection on disconnection', () => {
    jest.useFakeTimers();
    
    render(<ConversationStream {...defaultProps} />);
    
    // Simulate disconnection
    mockWebSocket.onclose();
    
    // Fast-forward time to trigger reconnection
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    
    // Verify reconnection attempt
    expect(WebSocket).toHaveBeenCalledTimes(2);
    
    jest.useRealTimers();
  });
});