import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import BigFiveRadarChart from '../BigFiveRadarChart';

// Mock Recharts components
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div data-testid="responsive-container">{children}</div>,
  RadarChart: ({ children }) => <div data-testid="radar-chart">{children}</div>,
  PolarGrid: () => <div data-testid="polar-grid" />,
  PolarAngleAxis: () => <div data-testid="polar-angle-axis" />,
  PolarRadiusAxis: () => <div data-testid="polar-radius-axis" />,
  Radar: () => <div data-testid="radar" />,
  Legend: () => <div data-testid="legend" />,
  Tooltip: () => <div data-testid="tooltip" />
}));

describe('BigFiveRadarChart', () => {
  const mockData = {
    openness: { score: 7, rationale: "High openness", strategy: "Innovative approach" },
    conscientiousness: { score: 8, rationale: "Very conscientious", strategy: "Detailed planning" },
    extraversion: { score: 5, rationale: "Moderate extraversion", strategy: "Balance social and solitary work" },
    agreeableness: { score: 6, rationale: "Moderately agreeable", strategy: "Focus on mutual benefits" },
    neuroticism: { score: 3, rationale: "Low neuroticism", strategy: "Provide clear, stable information" }
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders chart with complete data', () => {
    render(<BigFiveRadarChart data={mockData} />);
    
    // Check that Recharts components are rendered
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('radar-chart')).toBeInTheDocument();
    expect(screen.getByTestId('polar-grid')).toBeInTheDocument();
    expect(screen.getByTestId('polar-angle-axis')).toBeInTheDocument();
    expect(screen.getByTestId('polar-radius-axis')).toBeInTheDocument();
    expect(screen.getByTestId('radar')).toBeInTheDocument();
    expect(screen.getByTestId('legend')).toBeInTheDocument();
    expect(screen.getByTestId('tooltip')).toBeInTheDocument();
  });

  it('renders with partial data', () => {
    const partialData = {
      openness: { score: 7, rationale: "High openness", strategy: "Innovative approach" },
      conscientiousness: { score: 8, rationale: "Very conscientious", strategy: "Detailed planning" }
    };
    
    render(<BigFiveRadarChart data={partialData} />);
    
    // Should still render even with partial data
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('radar-chart')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    render(<BigFiveRadarChart data={{}} />);
    
    // Should still render even with empty data
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('radar-chart')).toBeInTheDocument();
  });

  it('renders with null data', () => {
    render(<BigFiveRadarChart data={null} />);
    
    // Should show no data message
    expect(screen.getByText('Brak danych do wyświetlenia')).toBeInTheDocument();
  });

  it('renders with undefined data', () => {
    render(<BigFiveRadarChart data={undefined} />);
    
    // Should show no data message
    expect(screen.getByText('Brak danych do wyświetlenia')).toBeInTheDocument();
  });
});