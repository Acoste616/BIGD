/**
 * Test cases for ConversationStream WebSocket functionality
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import ConversationStream from './ConversationStream';

// Mock the API services
jest.mock('../../services/interactionsApi', () => ({
  createInteraction: jest.fn()
}));

jest.mock('../../services/clientsApi', () => ({
  createClient: jest.fn()
}));

jest.mock('../../services/sessionsApi', () => ({
  createSession: jest.fn()
}));

// Mock WebSocket
const mockWebSocket = {
  close: jest.fn()
};

global.WebSocket = jest.fn(() => mockWebSocket);

describe('ConversationStream WebSocket', () => {
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
  });

  test('creates WebSocket connection when session ID is provided', () => {
    render(<ConversationStream {...defaultProps} />);
    
    // Check that WebSocket was created with correct URL
    expect(WebSocket).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/ws/123')
    );
  });

  test('shows connection status in UI', () => {
    render(<ConversationStream {...defaultProps} />);
    
    // Check that connection status is displayed
    expect(screen.getByText(/Session #123/)).toBeInTheDocument();
  });

  test('cleans up WebSocket connection on unmount', () => {
    const { unmount } = render(<ConversationStream {...defaultProps} />);
    
    // Mock the close method
    mockWebSocket.close.mockClear();
    
    // Unmount the component
    unmount();
    
    // Check that WebSocket was closed
    expect(mockWebSocket.close).toHaveBeenCalled();
  });
});