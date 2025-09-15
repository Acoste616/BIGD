import { renderHook, act } from '@testing-library/react';
import { useSessionPsychometrics } from '../usePsychometrics';
import * as api from '../../services/api';

// Mock the API module
jest.mock('../../services/api');

describe('useSessionPsychometrics', () => {
  const mockSessionId = 1;
  const mockPsychometricsData = {
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
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch psychometrics data successfully', async () => {
    // Mock the API response
    api.default.get.mockResolvedValue({ data: mockPsychometricsData });

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    // Initially loading should be false, and data should be null
    expect(result.current.loading).toBe(false);
    expect(result.current.psychometricsData).toBeNull();

    // Wait for the hook to fetch data
    await act(async () => {
      await result.current.refetch();
    });

    // After fetching, data should be populated
    expect(result.current.psychometricsData).toEqual(mockPsychometricsData);
    expect(result.current.loading).toBe(false);
    expect(result.current.hasData).toBe(true);
    expect(api.default.get).toHaveBeenCalledWith(`/sessions/${mockSessionId}/psychometrics`);
  });

  it('should handle API error', async () => {
    // Mock the API to throw an error
    const errorMessage = 'Failed to fetch';
    api.default.get.mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    await act(async () => {
      await result.current.refetch();
    });

    // Check that error state is set
    expect(result.current.error).toBe(errorMessage);
    expect(result.current.psychometricsData).toBeNull();
    expect(result.current.loading).toBe(false);
  });

  it('should not fetch data when sessionId is null', async () => {
    const { result } = renderHook(() => useSessionPsychometrics(null));

    await act(async () => {
      await result.current.refetch();
    });

    // API should not be called
    expect(api.default.get).not.toHaveBeenCalled();
  });

  it('should handle autoFetch option', async () => {
    api.default.get.mockResolvedValue({ data: mockPsychometricsData });

    // Test with autoFetch enabled (default)
    const { result: result1 } = renderHook(() => useSessionPsychometrics(mockSessionId, { autoFetch: true }));

    // Wait for initial fetch
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(api.default.get).toHaveBeenCalledWith(`/sessions/${mockSessionId}/psychometrics`);

    // Reset mock
    api.default.get.mockClear();

    // Test with autoFetch disabled
    const { result: result2 } = renderHook(() => useSessionPsychometrics(mockSessionId, { autoFetch: false }));

    // Wait a bit to ensure no auto fetch happened
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    // API should not be called when autoFetch is false
    expect(api.default.get).not.toHaveBeenCalled();

    // But manual fetch should still work
    await act(async () => {
      await result2.current.refetch();
    });

    expect(api.default.get).toHaveBeenCalledWith(`/sessions/${mockSessionId}/psychometrics`);
  });
});