// src/hooks/useRegistrationGate.ts

import { useState, useCallback } from 'react';
import type { UsageLimitError, UsageData } from '../types/index';

// 📝 TypeScript: Define what this hook returns
interface UseRegistrationGateReturn {
  isOpen: boolean;
  lastFeatureAttempted: 'match' | 'randomize' | undefined;
  showRegistrationGate: (error: UsageLimitError) => void;
  hideRegistrationGate: () => void;
  handleSignUp: () => void;
  handleLogin: () => void;
  canUseFeature: (feature: 'match' | 'randomize', usage?: UsageData | null) => boolean;
}

export const useRegistrationGate = (
  onRefreshUsage?: () => void
): UseRegistrationGateReturn => {
  // 🎯 State: Track registration gate
  const [isOpen, setIsOpen] = useState(false);
  const [lastFeatureAttempted, setLastFeatureAttempted] = useState<'match' | 'randomize' | undefined>();

  // 🎯 Function: Show registration gate when usage limit hit
  const showRegistrationGate = useCallback((error: UsageLimitError) => {
    console.log('🚪 Showing registration gate for:', error.feature_type);
    setLastFeatureAttempted(error.feature_type);
    setIsOpen(true);
  }, []);

  // 🎯 Function: Hide registration gate
  const hideRegistrationGate = useCallback(() => {
    console.log('🚪 Hiding registration gate');
    setIsOpen(false);
    setLastFeatureAttempted(undefined);
  }, []);

  // 🎯 Function: Handle signup click
  const handleSignUp = useCallback(() => {
    console.log('📝 Sign up clicked');
    // TODO: Implement actual signup functionality
    // For now, just close the gate and refresh usage
    hideRegistrationGate();
    if (onRefreshUsage) {
      onRefreshUsage();
    }
    
    // In a real app, you might:
    // - Navigate to signup page
    // - Open signup modal
    // - Call authentication service
    alert('Signup functionality coming soon! For now, you can continue using the app.');
  }, [hideRegistrationGate, onRefreshUsage]);

  // 🎯 Function: Handle login click  
  const handleLogin = useCallback(() => {
    console.log('🔑 Login clicked');
    // TODO: Implement actual login functionality
    // For now, just close the gate and refresh usage
    hideRegistrationGate();
    if (onRefreshUsage) {
      onRefreshUsage();
    }
    
    // In a real app, you might:
    // - Navigate to login page
    // - Open login modal
    // - Call authentication service
    alert('Login functionality coming soon! For now, you can continue using the app.');
  }, [hideRegistrationGate, onRefreshUsage]);

  // 🎯 Function: Check if user can use a specific feature
  const canUseFeature = useCallback((
    feature: 'match' | 'randomize', 
    usage?: UsageData | null
  ): boolean => {
    // If no usage data, assume they can use it (first time user)
    if (!usage) {
      console.log(`✅ No usage data, allowing ${feature}`);
      return true;
    }

    // If user has unlimited access (authenticated), allow everything
    if (usage.unlimited) {
      console.log(`✅ Unlimited access, allowing ${feature}`);
      return true;
    }

    // Check specific feature limits
    const canUse = feature === 'match' ? usage.can_match : usage.can_randomize;
    console.log(`${canUse ? '✅' : '❌'} Can use ${feature}:`, {
      feature,
      canUse,
      usage_summary: {
        matches: `${usage.matches_used}/${usage.matches_limit}`,
        randomizes: `${usage.randomizes_used}/${usage.randomizes_limit}`,
      }
    });

    return canUse;
  }, []);

  // 📤 Return everything the component needs
  return {
    isOpen,
    lastFeatureAttempted,
    showRegistrationGate,
    hideRegistrationGate,
    handleSignUp,
    handleLogin,
    canUseFeature,
  };
};