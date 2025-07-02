import React, { useEffect } from 'react';

// Extend Window interface for TypeScript
declare global {
  interface Window {
    google: any;
    FB: any;
  }
}

interface SocialAuthProps {
  onGoogleSuccess: (token: string, userInfo: any) => void;
  onFacebookSuccess: (token: string, userInfo: any) => void;
  onError: (error: string) => void;
}

const SocialAuth: React.FC<SocialAuthProps> = ({ 
  onGoogleSuccess, 
  onFacebookSuccess, 
  onError 
}) => {
  
  // Initialize Google OAuth when component mounts
  useEffect(() => {
    if (window.google) {
      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        callback: handleGoogleResponse,
      });
    }
  }, []);

  const handleGoogleResponse = async (response: any) => {
    try {
      // The response contains a JWT token, we need to decode it
      const credential = response.credential;
      
      // Parse the JWT to get user info (basic decode - in production use a proper JWT library)
      const base64Url = credential.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      
      const userInfo = JSON.parse(jsonPayload);
      
      // For Google Identity Services, we pass the credential token directly
      onGoogleSuccess(credential, userInfo);
    } catch (error) {
      console.error('Google auth error:', error);
      onError('Google authentication failed');
    }
  };

  const handleGoogleLogin = () => {
    if (window.google) {
      window.google.accounts.id.prompt();
    } else {
      onError('Google SDK not loaded');
    }
  };

  const handleFacebookLogin = () => {
    if (window.FB) {
      window.FB.login((response: any) => {
        if (response.authResponse) {
          // Get user profile information
          window.FB.api('/me', { fields: 'name,email,first_name,last_name' }, (userInfo: any) => {
            onFacebookSuccess(response.authResponse.accessToken, userInfo);
          });
        } else {
          onError('Facebook login was cancelled or failed');
        }
      }, { scope: 'email,public_profile' });
    } else {
      onError('Facebook SDK not loaded');
    }
  };

  return (
    <div className="space-y-3">
      {/* Google Login Button */}
      <button
        onClick={handleGoogleLogin}
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
      
      {/* Facebook Login Button */}
      <button
        onClick={handleFacebookLogin}
        className="w-full flex items-center justify-center gap-3 bg-[#1877F2] hover:bg-[#166FE5] text-white font-semibold py-3 px-6 rounded-lg transition-colors"
      >
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
        Continue with Facebook
      </button>
    </div>
  );
};

export default SocialAuth;