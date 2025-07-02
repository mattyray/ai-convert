import React, { useEffect, useRef, useState } from 'react';

declare global {
  interface Window {
    google: any;
    FB: any;
    fbReady?: boolean;
    fbSkipped?: boolean;
  }
}

interface SocialAuthProps {
  onGoogleSuccess: (token: string, userInfo: any) => void;
  onFacebookSuccess: (token: string, userInfo: any) => void;
  onError: (error: string) => void;
  disabled?: boolean;
}

const SocialAuth: React.FC<SocialAuthProps> = ({ 
  onGoogleSuccess, 
  onFacebookSuccess, 
  onError,
  disabled = false
}) => {
  const googleButtonRef = useRef<HTMLDivElement>(null);
  const [googleReady, setGoogleReady] = useState(false);
  const [facebookReady, setFacebookReady] = useState(false);
  const [loadingGoogle, setLoadingGoogle] = useState(true);

  // 🔥 FIXED: Proper VITE_ prefix
  const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const FACEBOOK_APP_ID = import.meta.env.VITE_FACEBOOK_APP_ID;
  
  const isLocalhost = window.location.hostname === 'localhost';
  const isHTTPS = window.location.protocol === 'https:';
  const facebookAllowed = isHTTPS || isLocalhost;

  console.log('🔧 SSO Debug:', {
    googleClientId: GOOGLE_CLIENT_ID ? `${GOOGLE_CLIENT_ID.substring(0, 20)}...` : 'MISSING',
    facebookAppId: FACEBOOK_APP_ID || 'MISSING',
    protocol: window.location.protocol,
    facebookAllowed,
    googleButtonRef: !!googleButtonRef.current
  });

  // 🔥 FIXED: Better Google initialization
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) {
      console.error('❌ VITE_GOOGLE_CLIENT_ID missing');
      setLoadingGoogle(false);
      return;
    }

    let attempts = 0;
    const maxAttempts = 50;

    const initGoogle = () => {
      attempts++;
      
      if (window.google?.accounts?.id) {
        try {
          console.log('🔧 Initializing Google OAuth...');
          
          window.google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleResponse,
            auto_select: false,
            cancel_on_tap_outside: true,
          });

          // 🔥 FIXED: Force render after a delay to ensure DOM is ready
          setTimeout(() => {
            if (googleButtonRef.current) {
              try {
                window.google.accounts.id.renderButton(googleButtonRef.current, {
                  theme: 'outline',
                  size: 'large',
                  width: '100%',
                  text: 'continue_with',
                  shape: 'rectangular',
                  logo_alignment: 'left'
                });
                setGoogleReady(true);
                setLoadingGoogle(false);
                console.log('✅ Google button rendered');
              } catch (renderError) {
                console.error('❌ Google button render error:', renderError);
                setLoadingGoogle(false);
              }
            } else {
              console.error('❌ Google button ref not available');
              setLoadingGoogle(false);
            }
          }, 100);

          console.log('✅ Google OAuth initialized');
          return;
        } catch (error) {
          console.error('❌ Google init error:', error);
          setLoadingGoogle(false);
        }
      }

      if (attempts < maxAttempts) {
        setTimeout(initGoogle, 100);
      } else {
        console.error('❌ Google SDK failed to load after 5 seconds');
        setLoadingGoogle(false);
        onError('Google authentication unavailable');
      }
    };

    initGoogle();
  }, [GOOGLE_CLIENT_ID]);

  // Initialize Facebook
  useEffect(() => {
    if (!facebookAllowed) {
      console.log('⚠️ Facebook disabled - requires HTTPS');
      return;
    }

    let attempts = 0;
    const checkFB = () => {
      attempts++;
      
      if (window.fbReady && window.FB) {
        setFacebookReady(true);
        console.log('✅ Facebook ready');
        return;
      }

      if (window.fbSkipped) {
        console.log('⚠️ Facebook SDK was skipped');
        return;
      }

      if (attempts < 50) {
        setTimeout(checkFB, 100);
      }
    };

    checkFB();
  }, [facebookAllowed]);

  const handleGoogleResponse = (response: any) => {
    try {
      console.log('🔑 Google response:', response);
      
      if (!response.credential) {
        throw new Error('No credential from Google');
      }

      // Parse JWT payload
      const payload = JSON.parse(
        atob(response.credential.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))
      );
      
      console.log('👤 Google user:', payload);
      onGoogleSuccess(response.credential, payload);
    } catch (error) {
      console.error('❌ Google auth error:', error);
      onError('Google authentication failed');
    }
  };

  const handleGoogleClick = () => {
    if (disabled) return;
    
    try {
      if (window.google?.accounts?.id) {
        window.google.accounts.id.prompt();
      } else {
        throw new Error('Google SDK not loaded');
      }
    } catch (error) {
      console.error('❌ Google prompt error:', error);
      onError('Failed to show Google login');
    }
  };

  const handleFacebookClick = () => {
    if (disabled || !facebookReady) return;
    
    if (!facebookAllowed) {
      onError('Facebook login requires HTTPS. Please use Google login instead.');
      return;
    }

    try {
      window.FB.login((response: any) => {
        console.log('🔑 Facebook response:', response);
        
        if (response.authResponse) {
          window.FB.api('/me', { fields: 'name,email,first_name,last_name' }, (userInfo: any) => {
            console.log('👤 Facebook user:', userInfo);
            onFacebookSuccess(response.authResponse.accessToken, userInfo);
          });
        } else {
          console.log('❌ Facebook login cancelled or failed');
          onError('Facebook login cancelled');
        }
      }, { scope: 'email,public_profile' });
    } catch (error) {
      console.error('❌ Facebook error:', error);
      onError('Facebook authentication failed');
    }
  };

  if (!GOOGLE_CLIENT_ID && !FACEBOOK_APP_ID) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800 text-sm">
          ⚠️ Social authentication not configured
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Google Login */}
      {GOOGLE_CLIENT_ID && (
        <div className={disabled ? 'opacity-50 pointer-events-none' : ''}>
          {/* 🔥 FIXED: Always show the div, but conditionally render Google button or fallback */}
          <div ref={googleButtonRef} className="w-full min-h-[48px]" />
          
          {/* 🔥 FIXED: Fallback button if Google button doesn't render */}
          {!googleReady && !loadingGoogle && (
            <button
              onClick={handleGoogleClick}
              className="w-full flex items-center justify-center gap-3 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </button>
          )}

          {/* Loading state */}
          {loadingGoogle && (
            <div className="w-full flex items-center justify-center py-3 text-gray-500">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-400 mr-2"></div>
              Loading Google...
            </div>
          )}
        </div>
      )}
      
      {/* Facebook Login - Simplified */}
      {FACEBOOK_APP_ID && (
        <button
          onClick={handleFacebookClick}
          disabled={!facebookAllowed || disabled}
          className="w-full flex items-center justify-center gap-3 bg-[#1877F2] hover:bg-[#166FE5] text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
          {!facebookAllowed ? 'Facebook (HTTPS Required)' : 'Continue with Facebook'}
        </button>
      )}

      {/* Development warning */}
      {!facebookAllowed && (
        <p className="text-xs text-amber-600 text-center">
          ⚠️ Facebook requires HTTPS. Google login works on localhost.
        </p>
      )}
    </div>
  );
};

export default SocialAuth;