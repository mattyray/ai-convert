import { useState, useEffect, useCallback } from 'react';
import { FaceSwapAPI } from '../services/api';
import type { UsageData, UsageLimitError } from '../types/index';

interface UseUsageReturn {
  usage: UsageData | null;
  loading: boolean;
  error: string | null;
  isLimited: boolean;
  canUseFeature: (feature: 'match' | 'randomize') => boolean;
  checkUsage: () => Promise<void>;
  handleUsageLimitError: (error: UsageLimitError) => void;
  resetUsage: () => void;
}

export const useUsage = (): UseUsageReturn => {
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user has hit all limits
  const isLimited = usage ? usage.is_limited && !usage.unlimited : false;

  // Check if user can use a specific feature
  const canUseFeature = useCallback((feature: 'match' | 'randomize'): boolean => {
    if (!usage) return false;
    if (usage.unlimited) return true;
    
    return feature === 'match' ? usage.can_match : usage.can_randomize;
  }, [usage]);

  // Fetch current usage status
  const checkUsage = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const usageData = await FaceSwapAPI.getUsageStatus();
      setUsage(usageData);
    } catch (err) {
      console.error('Failed to check usage:', err);
      setError(err instanceof Error ? err.message : 'Failed to check usage');
    } finally {
      setLoading(false);
    }
  }, []);

  // Handle usage limit errors from API calls
  const handleUsageLimitError = useCallback((error: UsageLimitError) => {
    console.log('Usage limit reached:', error);
    if (error.usage) {
      setUsage(error.usage);
    }
    setError(error.message || 'Usage limit reached');
  }, []);

  // Reset usage state (for testing or after login)
  const resetUsage = useCallback(() => {
    setUsage(null);
    setError(null);
    checkUsage();
  }, [checkUsage]);

  // Load usage on mount
  useEffect(() => {
    checkUsage();
  }, [checkUsage]);

  return {
    usage,
    loading,
    error,
    isLimited,
    canUseFeature,
    checkUsage,
    handleUsageLimitError,
    resetUsage,
  };
};