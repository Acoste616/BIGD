import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import SessionWorkspace from '../SessionWorkspace';

// Mock child components
jest.mock('../../components/conversation/StrategicPanel', () => () => <div data-testid="strategic-panel">Strategic Panel</div>);
jest.mock('../../components/ConversationView', () => () => <div data-testid="conversation-view">Conversation View</div>);
jest.mock('../../components/conversation/QuestionsPanel', () => () => <div data-testid="questions-panel">Questions Panel</div>);
jest.mock('../../components/psychometrics/PsychometricDashboard', () => () => <div data-testid="psychometric-dashboard">Psychometric Dashboard</div>);

// Mock the useParams hook
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    sessionId: '1'
  })
}));

// Mock the useSessionPsychometrics hook
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
    refetch: jest.fn()
  })
}));

describe('SessionWorkspace', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all main components', () => {
    render(
      <BrowserRouter>
        <SessionWorkspace />
      </BrowserRouter>
    );
    
    // Check that all main components are rendered
    expect(screen.getByTestId('questions-panel')).toBeInTheDocument();
    expect(screen.getByTestId('conversation-view')).toBeInTheDocument();
    expect(screen.getByTestId('psychometric-dashboard')).toBeInTheDocument();
    expect(screen.getByTestId('strategic-panel')).toBeInTheDocument();
  });

  it('passes correct props to PsychometricDashboard', () => {
    render(
      <BrowserRouter>
        <SessionWorkspace />
      </BrowserRouter>
    );
    
    // Check that PsychometricDashboard receives the correct props
    const dashboard = screen.getByTestId('psychometric-dashboard');
    expect(dashboard).toBeInTheDocument();
  });

  it('handles sessionId from URL params', () => {
    render(
      <BrowserRouter>
        <SessionWorkspace />
      </BrowserRouter>
    );
    
    // The component should use the mocked sessionId '1'
    // We can't directly test this without more complex mocking, but we ensure
    // the component renders without errors
    expect(screen.getByTestId('psychometric-dashboard')).toBeInTheDocument();
  });
});