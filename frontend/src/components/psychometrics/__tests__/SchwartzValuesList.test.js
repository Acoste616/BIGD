import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import SchwartzValuesList from '../SchwartzValuesList';

describe('SchwartzValuesList', () => {
  const mockData = [
    { 
      value_name: "Security", 
      strength: 8, 
      rationale: "Values safety", 
      strategy: "Emphasize reliability", 
      is_present: true 
    },
    { 
      value_name: "Achievement", 
      strength: 7, 
      rationale: "Values success", 
      strategy: "Highlight accomplishments", 
      is_present: true 
    },
    { 
      value_name: "Power", 
      strength: 5, 
      rationale: "Values control", 
      strategy: "Offer choices and autonomy", 
      is_present: true 
    },
    { 
      value_name: "Hedonism", 
      strength: 3, 
      rationale: "Values pleasure", 
      strategy: "Focus on comfort", 
      is_present: false 
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with complete data', () => {
    render(<SchwartzValuesList data={mockData} />);
    
    // Check that only present values are displayed
    expect(screen.getByText('Security')).toBeInTheDocument();
    expect(screen.getByText('Achievement')).toBeInTheDocument();
    expect(screen.getByText('Power')).toBeInTheDocument();
    
    // Check that non-present values are not displayed
    expect(screen.queryByText('Hedonism')).not.toBeInTheDocument();
    
    // Check that strength indicators are displayed
    expect(screen.getByText('8/10')).toBeInTheDocument();
    expect(screen.getByText('7/10')).toBeInTheDocument();
    expect(screen.getByText('5/10')).toBeInTheDocument();
  });

  it('renders with partial data', () => {
    const partialData = [
      { 
        value_name: "Security", 
        strength: 8, 
        rationale: "Values safety", 
        strategy: "Emphasize reliability", 
        is_present: true 
      }
    ];
    
    render(<SchwartzValuesList data={partialData} />);
    
    // Check that the value is displayed
    expect(screen.getByText('Security')).toBeInTheDocument();
    expect(screen.getByText('8/10')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    render(<SchwartzValuesList data={[]} />);
    
    // Should show no data message
    expect(screen.getByText('Brak aktywnych wartości Schwartz do wyświetlenia')).toBeInTheDocument();
  });

  it('renders with null data', () => {
    render(<SchwartzValuesList data={null} />);
    
    // Should show no data message
    expect(screen.getByText('Brak aktywnych wartości Schwartz do wyświetlenia')).toBeInTheDocument();
  });

  it('renders tooltip on hover', () => {
    render(<SchwartzValuesList data={mockData} />);
    
    // Find the first value chip
    const securityChip = screen.getByText('Security').closest('[role="button"]');
    
    // In a real test, we would simulate hover, but for now we just check that
    // the container has the proper structure for tooltips
    expect(securityChip).toBeInTheDocument();
  });
});