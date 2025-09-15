import { renderHook, act } from '@testing-library/react';
import { useSessionPsychometrics } from '../usePsychometrics';
import * as api from '../../services/api';

// Mock the API module
jest.mock('../../services/api');

describe('useSessionPsychometrics - Extended Tests', () => {
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

  it('should handle empty data response', async () => {
    // Mock the API response with empty data
    api.default.get.mockResolvedValue({ data: {} });

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    await act(async () => {
      await result.current.refetch();
    });

    // After fetching, data should be populated with empty object
    expect(result.current.psychometricsData).toEqual({});
    expect(result.current.loading).toBe(false);
    expect(result.current.hasData).toBe(true); // Empty object is still data
    expect(api.default.get).toHaveBeenCalledWith(`/sessions/${mockSessionId}/psychometrics`);
  });

  it('should handle partial data response', async () => {
    const partialData = {
      confidence_score: 60,
      big_five: {
        openness: { score: 7, rationale: "Test", strategy: "Test strategy" }
      }
    };
    
    // Mock the API response with partial data
    api.default.get.mockResolvedValue({ data: partialData });

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    await act(async () => {
      await result.current.refetch();
    });

    // After fetching, data should be populated with partial data
    expect(result.current.psychometricsData).toEqual(partialData);
    expect(result.current.loading).toBe(false);
    expect(result.current.hasData).toBe(true);
    expect(api.default.get).toHaveBeenCalledWith(`/sessions/${mockSessionId}/psychometrics`);
  });

  it('should handle loading state transitions', async () => {
    // Mock the API to delay response
    api.default.get.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ data: mockPsychometricsData }), 100))
    );

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    // Initially should not be loading
    expect(result.current.loading).toBe(false);
    
    // Start fetching
    let fetchPromise;
    act(() => {
      fetchPromise = result.current.refetch();
    });

    // Should be loading during fetch
    expect(result.current.loading).toBe(true);
    
    // Wait for fetch to complete
    await act(async () => {
      await fetchPromise;
    });

    // Should not be loading after fetch
    expect(result.current.loading).toBe(false);
    expect(result.current.psychometricsData).toEqual(mockPsychometricsData);
  });

  it('should handle multiple refetch calls', async () => {
    api.default.get.mockResolvedValue({ data: mockPsychometricsData });

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    // First fetch
    await act(async () => {
      await result.current.refetch();
    });

    expect(api.default.get).toHaveBeenCalledTimes(1);
    expect(result.current.psychometricsData).toEqual(mockPsychometricsData);

    // Second fetch
    await act(async () => {
      await result.current.refetch();
    });

    expect(api.default.get).toHaveBeenCalledTimes(2);
    expect(result.current.psychometricsData).toEqual(mockPsychometricsData);
  });

  it('should handle network error', async () => {
    // Mock the API to throw a network error
    api.default.get.mockRejectedValue(new Error('Network Error'));

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    await act(async () => {
      await result.current.refetch();
    });

    // Check that error state is set
    expect(result.current.error).toBe('Network Error');
    expect(result.current.psychometricsData).toBeNull();
    expect(result.current.loading).toBe(false);
  });

  it('should handle HTTP error response', async () => {
    // Mock the API to return an error response
    api.default.get.mockRejectedValue({
      response: {
        status: 404,
        data: { detail: 'Session not found' }
      }
    });

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    await act(async () => {
      await result.current.refetch();
    });

    // Check that error state is set
    expect(result.current.error).toBe('Session not found');
    expect(result.current.psychometricsData).toBeNull();
    expect(result.current.loading).toBe(false);
  });

  it('should not fetch when autoFetch is false and no manual refetch', async () => {
    api.default.get.mockResolvedValue({ data: mockPsychometricsData });

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId, { autoFetch: false }));

    // Wait a bit to ensure no auto fetch happened
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    // API should not be called
    expect(api.default.get).not.toHaveBeenCalled();
    expect(result.current.psychometricsData).toBeNull();
  });

  it('should handle onError callback', async () => {
    const errorMessage = 'Failed to fetch';
    api.default.get.mockRejectedValue(new Error(errorMessage));
    
    const onErrorMock = jest.fn();

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId, { onError: onErrorMock }));

    await act(async () => {
      await result.current.refetch();
    });

    // Check that onError callback was called
    expect(onErrorMock).toHaveBeenCalledWith(new Error(errorMessage));
    expect(result.current.error).toBe(errorMessage);
  });
});