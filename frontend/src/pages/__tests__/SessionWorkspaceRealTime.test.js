import React from 'react';
import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import SessionWorkspace from '../SessionWorkspace';

// Mock child components
jest.mock('../../components/conversation/StrategicPanel', () => ({ 
  __esModule: true,
  default: ({ sessionId }) => <div data-testid="strategic-panel">Strategic Panel for session {sessionId}</div>
}));

jest.mock('../../components/ConversationView', () => ({ 
  __esModule: true,
  default: ({ sessionId, onInteractionAdded }) => (
    <div data-testid="conversation-view">
      Conversation View for session {sessionId}
      <button onClick={() => onInteractionAdded()}>Add Interaction</button>
    </div>
  )
}));

jest.mock('../../components/conversation/QuestionsPanel', () => ({ 
  __esModule: true,
  default: ({ sessionId }) => <div data-testid="questions-panel">Questions Panel for session {sessionId}</div>
}));

jest.mock('../../components/psychometrics/PsychometricDashboard', () => ({ 
  __esModule: true,
  default: ({ sessionId, psychometricsData }) => (
    <div data-testid="psychometric-dashboard">
      Psychometric Dashboard for session {sessionId}
      {psychometricsData && <div data-testid="psychometrics-content">Psychometrics loaded</div>}
    </div>
  )
}));

// Mock the useParams hook
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    sessionId: '1'
  })
}));

// Mock the useSessionPsychometrics hook
const mockRefetch = jest.fn();
jest.mock('../../hooks/usePsychometrics', () => ({
  useSessionPsychometrics: () => ({
    psychometricsData: {
      confidence_score: 85,
      summary: "Test summary",
      big_five: {
        openness: { score: 7, rationale: "Test", strategy: "Test strategy" }
      },
      archetype: {
        key: "analityk",
        name: "🔬 Analityk",
        confidence: 90,
        description: "Analytical customer"
      },
      disc_profile: {},
      schwartz_values: [],
      evolution_trend: {
        big_five_trends: {},
        disc_trends: {},
        schwartz_trends: {}
      }
    },
    loading: false,
    error: null,
    refetch: mockRefetch
  })
}));

describe('SessionWorkspace Real-time Updates', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('triggers psychometrics refetch when interaction is added', async () => {
    render(
      <BrowserRouter>
        <SessionWorkspace />
      </BrowserRouter>
    );
    
    // Find the "Add Interaction" button and click it
    const addButton = screen.getByText('Add Interaction');
    
    await act(async () => {
      addButton.click();
    });
    
    // Verify that refetch was called
    expect(mockRefetch).toHaveBeenCalledTimes(1);
  });

  it('passes sessionId to all child components', () => {
    render(
      <BrowserRouter>
        <SessionWorkspace />
      </BrowserRouter>
    );
    
    // Check that sessionId is passed to all components
    expect(screen.getByTestId('strategic-panel')).toHaveTextContent('session 1');
    expect(screen.getByTestId('conversation-view')).toHaveTextContent('session 1');
    expect(screen.getByTestId('questions-panel')).toHaveTextContent('session 1');
    expect(screen.getByTestId('psychometric-dashboard')).toHaveTextContent('session 1');
  });

  it('passes psychometricsData to PsychometricDashboard', () => {
    render(
      <BrowserRouter>
        <SessionWorkspace />
      </BrowserRouter>
    );
    
    // Check that psychometricsData is passed and rendered
    expect(screen.getByTestId('psychometrics-content')).toBeInTheDocument();
  });

  it('handles psychometrics loading state', () => {
    // Mock loading state
    jest.mock('../../hooks/usePsychometrics', () => ({
      useSessionPsychometrics: () => ({
        psychometricsData: null,
        loading: true,
        error: null,
        refetch: mockRefetch
      })
    }));
    
    render(
      <BrowserRouter>
        <SessionWorkspace />
      </BrowserRouter>
    );
    
    // Check that loading state is handled (component should still render)
    expect(screen.getByTestId('psychometric-dashboard')).toBeInTheDocument();
  });

  it('handles psychometrics error state', () => {
    // Mock error state
    jest.mock('../../hooks/usePsychometrics', () => ({
      useSessionPsychometrics: () => ({
        psychometricsData: null,
        loading: false,
        error: 'Failed to load data',
        refetch: mockRefetch
      })
    }));
    
    render(
      <BrowserRouter>
        <SessionWorkspace />
      </BrowserRouter>
    );
    
    // Check that error state is handled (component should still render)
    expect(screen.getByTestId('psychometric-dashboard')).toBeInTheDocument();
  });
});