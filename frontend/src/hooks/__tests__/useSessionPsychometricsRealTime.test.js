import { renderHook, act } from '@testing-library/react';
import { useSessionPsychometrics } from '../usePsychometrics';
import * as api from '../../services/api';

// Mock the API module
jest.mock('../../services/api');

describe('useSessionPsychometrics - Real-time Updates', () => {
  const mockSessionId = 1;
  const initialPsychometricsData = {
    confidence_score: 85,
    summary: "Initial summary",
    big_five: {
      openness: { score: 7, rationale: "Initial", strategy: "Initial strategy" }
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

  const updatedPsychometricsData = {
    confidence_score: 90,
    summary: "Updated summary",
    big_five: {
      openness: { score: 8, rationale: "Updated", strategy: "Updated strategy" },
      conscientiousness: { score: 7, rationale: "New", strategy: "New strategy" }
    },
    archetype: {
      key: "analityk",
      name: "🔬 Analityk",
      confidence: 95,
      description: "Analytical customer - updated"
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

  it('should update data on refetch after interaction', async () => {
    // Mock initial API response
    api.default.get.mockResolvedValueOnce({ data: initialPsychometricsData });
    
    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    // Initial fetch
    await act(async () => {
      await result.current.refetch();
    });

    // Verify initial data
    expect(result.current.psychometricsData).toEqual(initialPsychometricsData);
    expect(result.current.psychometricsData.confidence_score).toBe(85);
    expect(result.current.psychometricsData.big_five.openness.score).toBe(7);

    // Mock updated API response
    api.default.get.mockResolvedValueOnce({ data: updatedPsychometricsData });

    // Second fetch (simulating update after interaction)
    await act(async () => {
      await result.current.refetch();
    });

    // Verify updated data
    expect(result.current.psychometricsData).toEqual(updatedPsychometricsData);
    expect(result.current.psychometricsData.confidence_score).toBe(90);
    expect(result.current.psychometricsData.big_five.openness.score).toBe(8);
    expect(result.current.psychometricsData.big_five.conscientiousness).toBeDefined();
    expect(result.current.psychometricsData.big_five.conscientiousness.score).toBe(7);
  });

  it('should handle rapid successive updates', async () => {
    // Mock API responses
    api.default.get
      .mockResolvedValueOnce({ data: initialPsychometricsData })
      .mockResolvedValueOnce({ data: updatedPsychometricsData })
      .mockResolvedValueOnce({ data: initialPsychometricsData });

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    // First fetch
    await act(async () => {
      await result.current.refetch();
    });
    expect(result.current.psychometricsData).toEqual(initialPsychometricsData);

    // Second fetch
    await act(async () => {
      await result.current.refetch();
    });
    expect(result.current.psychometricsData).toEqual(updatedPsychometricsData);

    // Third fetch (back to initial)
    await act(async () => {
      await result.current.refetch();
    });
    expect(result.current.psychometricsData).toEqual(initialPsychometricsData);

    // Verify API was called three times
    expect(api.default.get).toHaveBeenCalledTimes(3);
  });

  it('should maintain data consistency during updates', async () => {
    api.default.get.mockResolvedValue({ data: initialPsychometricsData });

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    // Initial fetch
    await act(async () => {
      await result.current.refetch();
    });

    // Store reference to initial data
    const initialDataRef = result.current.psychometricsData;

    // Verify data structure
    expect(initialDataRef).toHaveProperty('confidence_score');
    expect(initialDataRef).toHaveProperty('summary');
    expect(initialDataRef).toHaveProperty('big_five');
    expect(initialDataRef).toHaveProperty('archetype');
    expect(initialDataRef).toHaveProperty('disc_profile');
    expect(initialDataRef).toHaveProperty('schwartz_values');
    expect(initialDataRef).toHaveProperty('evolution_trend');

    // Refetch
    await act(async () => {
      await result.current.refetch();
    });

    // Verify updated data still has same structure
    const updatedDataRef = result.current.psychometricsData;
    expect(updatedDataRef).toHaveProperty('confidence_score');
    expect(updatedDataRef).toHaveProperty('summary');
    expect(updatedDataRef).toHaveProperty('big_five');
    expect(updatedDataRef).toHaveProperty('archetype');
    expect(updatedDataRef).toHaveProperty('disc_profile');
    expect(updatedDataRef).toHaveProperty('schwartz_values');
    expect(updatedDataRef).toHaveProperty('evolution_trend');
  });

  it('should handle update with partial data', async () => {
    const partialUpdateData = {
      confidence_score: 88,
      big_five: {
        openness: { score: 7, rationale: "Updated", strategy: "Updated strategy" }
      }
      // Missing other fields
    };

    api.default.get
      .mockResolvedValueOnce({ data: initialPsychometricsData })
      .mockResolvedValueOnce({ data: partialUpdateData });

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    // Initial fetch
    await act(async () => {
      await result.current.refetch();
    });
    expect(result.current.psychometricsData).toEqual(initialPsychometricsData);

    // Update with partial data
    await act(async () => {
      await result.current.refetch();
    });
    expect(result.current.psychometricsData).toEqual(partialUpdateData);
  });

  it('should handle update errors gracefully', async () => {
    api.default.get
      .mockResolvedValueOnce({ data: initialPsychometricsData })
      .mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useSessionPsychometrics(mockSessionId));

    // Initial fetch
    await act(async () => {
      await result.current.refetch();
    });
    expect(result.current.psychometricsData).toEqual(initialPsychometricsData);
    expect(result.current.error).toBeNull();

    // Failed update
    await act(async () => {
      await result.current.refetch();
    });
    // Data should remain unchanged
    expect(result.current.psychometricsData).toEqual(initialPsychometricsData);
    // Error should be set
    expect(result.current.error).toBe('Network error');
  });
});