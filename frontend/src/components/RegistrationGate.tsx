import React from 'react';
import { X, Crown, Sparkles, Users, Infinity } from 'lucide-react';
import type { UsageData } from '../types/index';
import SocialAuth from './SocialAuth';
import { FaceSwapAPI } from '../services/api';
import { useAuth } from '../hooks/useAuth';

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
  usage,
  lastFeatureAttempted
}) => {
  const { login } = useAuth();

  if (!isOpen) return null;

  const getFeatureIcon = (feature?: string) => {
    switch (feature) {
      case 'match': return <Users className="w-6 h-6" />;
      case 'randomize': return <Sparkles className="w-6 h-6" />;
      default: return <Crown className="w-6 h-6" />;
    }
  };

  const handleGoogleSuccess = async (credential: string, userInfo: any) => {
    try {
      console.log('🔑 Google auth success:', userInfo);
      const response = await FaceSwapAPI.googleAuth(credential, userInfo);
      
      // 🔥 FIXED: Store token and update auth state
      localStorage.setItem('authToken', response.token);
      login(response.token, response.user);
      
      // 🔥 FIXED: Close modal and show success
      onClose();
      
      // 🔥 FIXED: Reload page to refresh all state
      window.location.reload();
      
    } catch (error) {
      console.error('Google auth failed:', error);
      alert('Google authentication failed. Please try again.');
    }
  };

  const handleFacebookSuccess = async (accessToken: string, userInfo: any) => {
    try {
      console.log('🔑 Facebook auth success:', userInfo);
      const response = await FaceSwapAPI.facebookAuth(accessToken, userInfo);
      
      // 🔥 FIXED: Store token and update auth state
      localStorage.setItem('authToken', response.token);
      login(response.token, response.user);
      
      // 🔥 FIXED: Close modal and show success
      onClose();
      
      // 🔥 FIXED: Reload page to refresh all state
      window.location.reload();
      
    } catch (error) {
      console.error('Facebook auth failed:', error);
      alert('Facebook authentication failed. Please try again.');
    }
  };

  const handleSocialAuthError = (error: string) => {
    console.error('Social auth error:', error);
    alert(`Authentication error: ${error}`);
  };

  const handleEmailSignup = () => {
    alert('Email signup coming soon! For now, please use Google.');
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
              Join to get unlimited transformations!
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

          {/* Social Auth Buttons */}
          <div className="space-y-4">
            <SocialAuth 
              onGoogleSuccess={handleGoogleSuccess}
              onFacebookSuccess={handleFacebookSuccess}
              onError={handleSocialAuthError}
            />
            
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-2">or</div>
              <button
                onClick={handleEmailSignup}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Create account with email
              </button>
            </div>
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