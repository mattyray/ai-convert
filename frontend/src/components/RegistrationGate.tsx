import React from 'react';
import { X, Crown, Sparkles, Users, Infinity } from 'lucide-react';
import type { UsageData } from '../types/index';

interface RegistrationGateProps {
  isOpen: boolean;
  onClose: () => void;
  onSignUp: () => void;
  onLogin: () => void;
  usage?: UsageData | null;
  lastFeatureAttempted?: 'match' | 'randomize';
}

const RegistrationGate: React.FC<RegistrationGateProps> = ({
  isOpen,
  onClose,
  onSignUp,
  onLogin,
  usage,
  lastFeatureAttempted
}) => {
  if (!isOpen) return null;

  const getFeatureIcon = (feature?: string) => {
    switch (feature) {
      case 'match': return <Users className="w-6 h-6" />;
      case 'randomize': return <Sparkles className="w-6 h-6" />;
      default: return <Crown className="w-6 h-6" />;
    }
  };

  const getFeatureName = (feature?: string) => {
    switch (feature) {
      case 'match': return 'face matching';
      case 'randomize': return 'randomize feature';
      default: return 'premium features';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-2xl">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white hover:text-gray-200 transition-colors"
          >
            <X size={24} />
          </button>
          
          <div className="text-center">
            <div className="flex items-center justify-center mb-3">
              <Crown className="w-8 h-8 text-yellow-300 mr-2" />
              <h2 className="text-2xl font-bold">Unlock Full Access</h2>
            </div>
            <p className="text-blue-100">
              You've reached your free limit! Join to continue exploring.
            </p>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Usage Status */}
          {usage && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                {getFeatureIcon(lastFeatureAttempted)}
                Your Usage Summary
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Face Matches:</span>
                  <span className={`font-medium ${usage.can_match ? 'text-green-600' : 'text-red-600'}`}>
                    {usage.matches_used}/{usage.matches_limit}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Randomizes:</span>
                  <span className={`font-medium ${usage.can_randomize ? 'text-green-600' : 'text-red-600'}`}>
                    {usage.randomizes_used}/{usage.randomizes_limit}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Attempted Feature Message */}
          {lastFeatureAttempted && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-2 text-amber-800">
                {getFeatureIcon(lastFeatureAttempted)}
                <span className="font-medium">
                  You tried to use {getFeatureName(lastFeatureAttempted)}
                </span>
              </div>
              <p className="text-amber-700 text-sm mt-1">
                Sign up now to continue and get unlimited access!
              </p>
            </div>
          )}

          {/* Benefits */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 mb-4 text-center">
              ✨ What you'll get with an account:
            </h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-gray-700">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <Infinity className="w-4 h-4 text-green-600" />
                </div>
                <span>Unlimited face matching</span>
              </div>
              <div className="flex items-center gap-3 text-gray-700">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-purple-600" />
                </div>
                <span>Unlimited randomize feature</span>
              </div>
              <div className="flex items-center gap-3 text-gray-700">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <Users className="w-4 h-4 text-blue-600" />
                </div>
                <span>Access to all historical figures</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={onSignUp}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              🚀 Create Free Account
            </button>
            
            <button
              onClick={onLogin}
              className="w-full bg-white hover:bg-gray-50 text-gray-700 font-semibold py-3 px-6 rounded-lg border border-gray-300 hover:border-gray-400 transition-all duration-200"
            >
              Already have an account? Sign In
            </button>
          </div>

          {/* Footer */}
          <div className="text-center mt-6 pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Free to join • No credit card required • Start creating immediately
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegistrationGate;