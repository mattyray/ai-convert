import React from 'react';
import type { FaceSwapResult } from '../types/index';

interface FacebookShareButtonProps {
  result: FaceSwapResult;
  className?: string;
}

const FacebookShareButton: React.FC<FacebookShareButtonProps> = ({ 
  result, 
  className = "" 
}) => {
  const handleFacebookShare = () => {
    // Check if Facebook SDK is loaded
    if (typeof window.FB === 'undefined') {
      console.error('Facebook SDK not loaded');
      // Fallback to simple sharer for development
      const shareUrl = window.location.origin;
      const shareText = result.is_randomized 
        ? `🎭 I just got randomly transformed into ${result.match_name} using AI! Try HistoryFace!`
        : `🎭 Amazing! AI matched my face with ${result.match_name} with ${(result.match_score * 100).toFixed(0)}% confidence! Try HistoryFace!`;
      
      const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareText)}`;
      window.open(facebookUrl, 'facebook-share', 'width=600,height=500');
      return;
    }

    // Modern FB.ui Share Dialog (2024/2025 standard)
    window.FB.ui({
      method: 'share',
      href: window.location.origin, // The URL to share
      display: 'popup'
    }, (response: any) => {
      if (response && !response.error_message) {
        console.log('✅ Facebook share successful:', response);
        // Optional: Track successful shares
        // analytics.track('facebook_share_success', { figure: result.match_name });
      } else {
        console.log('❌ Facebook share cancelled or failed:', response);
      }
    });

    console.log('🔗 Facebook share initiated for:', result.match_name);
  };

  return (
    <button
      onClick={handleFacebookShare}
      className={`flex items-center justify-center gap-2 bg-[#1877F2] hover:bg-[#166FE5] text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 ${className}`}
    >
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
      </svg>
      Share on Facebook
    </button>
  );
};

export default FacebookShareButton;