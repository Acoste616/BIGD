import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import PsychometricDashboard from '../PsychometricDashboard';

// Mock child components
jest.mock('../BigFiveRadarChart', () => () => <div data-testid="big-five-chart">Big Five Chart</div>);
jest.mock('../DiscProfileDisplay', () => () => <div data-testid="disc-profile">DISC Profile</div>);
jest.mock('../SchwartzValuesList', () => () => <div data-testid="schwartz-values">Schwartz Values</div>);
jest.mock('../ClarifyingQuestions', () => () => <div data-testid="clarifying-questions">Clarifying Questions</div>);

describe('PsychometricDashboard', () => {
  const mockAnalysisData = {
    cumulative_psychology: {
      big_five: {
        openness: { score: 7, rationale: "High openness", strategy: "Innovative approach" },
        conscientiousness: { score: 8, rationale: "Very conscientious", strategy: "Detailed planning" }
      },
      disc: {
        dominance: { score: 6, rationale: "Moderate dominance", strategy: "Allow leadership opportunities" }
      },
      schwartz_values: [
        { value_name: "Security", strength: 8, rationale: "Values safety", strategy: "Emphasize reliability", is_present: true }
      ]
    },
    psychology_confidence: 85,
    customer_archetype: {
      key: "analityk",
      name: "🔬 Analityk",
      confidence: 90,
      description: "Analytical customer profile"
    }
  };

  const mockPsychometricsData = {
    confidence_score: 85,
    summary: "Test summary",
    big_five: {
      openness: { score: 7, rationale: "High openness", strategy: "Innovative approach" },
      conscientiousness: { score: 8, rationale: "Very conscientious", strategy: "Detailed planning" }
    },
    archetype: {
      key: "analityk",
      name: "🔬 Analityk",
      confidence: 90,
      description: "Analytical customer profile"
    },
    disc_profile: {
      dominance: { score: 6, rationale: "Moderate dominance", strategy: "Allow leadership opportunities" }
    },
    schwartz_values: [
      { value_name: "Security", strength: 8, rationale: "Values safety", strategy: "Emphasize reliability", is_present: true }
    ],
    evolution_trend: {
      big_five_trends: {},
      disc_trends: {},
      schwartz_trends: {}
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state when loading prop is true', () => {
    render(
      <PsychometricDashboard 
        loading={true} 
        psychometricsLoading={false}
      />
    );
    
    expect(screen.getByText('Analiza Psychometryczna w Toku...')).toBeInTheDocument();
  });

  it('renders loading state when psychometricsLoading prop is true', () => {
    render(
      <PsychometricDashboard 
        loading={false} 
        psychometricsLoading={true}
      />
    );
    
    expect(screen.getByText('Analiza Psychometryczna w Toku...')).toBeInTheDocument();
  });

  it('renders with psychometricsData from new endpoint', () => {
    render(
      <PsychometricDashboard 
        psychometricsData={mockPsychometricsData}
        psychometricsLoading={false}
        loading={false}
      />
    );
    
    // Check that header is rendered
    expect(screen.getByText('Profil Psychometryczny Klienta')).toBeInTheDocument();
    
    // Check that Ultra Mózg badge is rendered
    expect(screen.getByText('🧠⚡ ULTRA MÓZG')).toBeInTheDocument();
    
    // Check that confidence score is displayed
    expect(screen.getByText('🔍 Pewność analizy: 85%')).toBeInTheDocument();
    
    // Check that all visualization components are rendered
    expect(screen.getByTestId('big-five-chart')).toBeInTheDocument();
    expect(screen.getByTestId('disc-profile')).toBeInTheDocument();
    expect(screen.getByTestId('schwartz-values')).toBeInTheDocument();
  });

  it('renders with legacy analysisData', () => {
    render(
      <PsychometricDashboard 
        analysisData={mockAnalysisData}
        loading={false}
        psychometricsLoading={false}
      />
    );
    
    // Check that header is rendered
    expect(screen.getByText('Profil Psychometryczny Klienta')).toBeInTheDocument();
    
    // Check that Ultra Mózg badge is NOT rendered for legacy data
    expect(screen.queryByText('🧠⚡ ULTRA MÓZG')).not.toBeInTheDocument();
    
    // Check that confidence score is displayed
    expect(screen.getByText('🔍 Pewność analizy: 85%')).toBeInTheDocument();
    
    // Check that all visualization components are rendered
    expect(screen.getByTestId('big-five-chart')).toBeInTheDocument();
    expect(screen.getByTestId('disc-profile')).toBeInTheDocument();
    expect(screen.getByTestId('schwartz-values')).toBeInTheDocument();
  });

  it('renders clarifying questions when needs clarification', () => {
    const mockAnalysisDataWithQuestions = {
      ...mockAnalysisData,
      needs_clarification: true,
      clarifying_questions: [
        {
          id: "q1",
          question: "Does the client value security?",
          option_a: "Yes",
          option_b: "No",
          psychological_target: "security"
        }
      ]
    };
    
    render(
      <PsychometricDashboard 
        analysisData={mockAnalysisDataWithQuestions}
        loading={false}
        psychometricsLoading={false}
      />
    );
    
    // Check that clarifying questions component is rendered
    expect(screen.getByTestId('clarifying-questions')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    render(
      <PsychometricDashboard 
        loading={false}
        psychometricsLoading={false}
      />
    );
    
    // Should show loading message when no data
    expect(screen.getByText('Analiza Psychometryczna w Toku...')).toBeInTheDocument();
  });

  it('renders with partial data (only Big Five)', () => {
    const partialData = {
      confidence_score: 60,
      big_five: {
        openness: { score: 7, rationale: "High openness", strategy: "Innovative approach" }
      },
      disc_profile: {},
      schwartz_values: []
    };
    
    render(
      <PsychometricDashboard 
        psychometricsData={partialData}
        psychometricsLoading={false}
        loading={false}
      />
    );
    
    // Check that header is rendered
    expect(screen.getByText('Profil Psychometryczny Klienta')).toBeInTheDocument();
    
    // Check that Big Five chart is rendered
    expect(screen.getByTestId('big-five-chart')).toBeInTheDocument();
    
    // Check that other components are not rendered when no data
    expect(screen.queryByTestId('disc-profile')).not.toBeInTheDocument();
    expect(screen.queryByTestId('schwartz-values')).not.toBeInTheDocument();
  });
});