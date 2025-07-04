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
    // Create engaging share text
    const shareText = result.is_randomized 
      ? `🎭 I just got randomly transformed into ${result.match_name} using AI! The results are amazing! Try HistoryFace and see which historical figure you become!`
      : `🎭 Amazing! AI matched my face with ${result.match_name} with ${(result.match_score * 100).toFixed(0)}% confidence! Try HistoryFace yourself and discover your historical twin!`;
    
    // Use Facebook's Feed Dialog instead of basic sharer for better control
    const shareUrl = window.location.origin;
    const imageUrl = result.output_image_url;
    
    // Facebook Feed Dialog URL with parameters
    const facebookUrl = new URL('https://www.facebook.com/dialog/feed');
    facebookUrl.searchParams.set('app_id', '1430950704695809'); // Your Facebook App ID
    facebookUrl.searchParams.set('link', shareUrl);
    facebookUrl.searchParams.set('picture', imageUrl);
    facebookUrl.searchParams.set('name', `I transformed into ${result.match_name}!`);
    facebookUrl.searchParams.set('caption', 'HistoryFace - AI Historical Transformation');
    facebookUrl.searchParams.set('description', shareText);
    facebookUrl.searchParams.set('redirect_uri', shareUrl);
    facebookUrl.searchParams.set('display', 'popup');
    
    // Open in popup window
    const popup = window.open(
      facebookUrl.toString(),
      'facebook-share',
      'width=600,height=400,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no'
    );
    
    if (popup) {
      popup.focus();
    }
    
    console.log('🔗 Facebook share clicked for:', result.match_name);
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