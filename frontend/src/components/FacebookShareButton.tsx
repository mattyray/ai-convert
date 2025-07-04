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
      ? `🎭 I just got randomly transformed into ${result.match_name} using AI! The results are amazing! Try HistoryFace and see which historical figure you become! ✨`
      : `🎭 Amazing! AI matched my face with ${result.match_name} with ${(result.match_score * 100).toFixed(0)}% confidence! Try HistoryFace yourself and discover your historical twin! ✨`;

    const shareUrl = window.location.origin;

    console.log('🔗 Initiating Facebook share for:', result.match_name);

    // Option 1: Try Web Share API first (works great on mobile and includes images)
    if (navigator.share) {
      navigator.share({
        title: `I transformed into ${result.match_name}!`,
        text: shareText,
        url: shareUrl
      }).then(() => {
        console.log('✅ Web Share API successful');
      }).catch(err => {
        console.log('Web Share API failed, falling back to Facebook dialog:', err);
        openFacebookDialog();
      });
    } else {
      // Desktop or browsers without Web Share API
      openFacebookDialog();
    }

    function openFacebookDialog() {
      // Facebook Share Dialog with pre-filled text
      const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareText)}`;
      
      console.log('🌐 Opening Facebook share dialog');
      
      const popup = window.open(
        facebookUrl,
        'facebook-share',
        'width=600,height=500,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no'
      );
      
      if (popup) {
        popup.focus();
        
        // Auto-copy image URL to clipboard for easy pasting
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(result.output_image_url).then(() => {
            console.log('📋 Image URL copied to clipboard for easy pasting');
            
            // Optional: Show a brief notification to user
            showNotification();
          }).catch(err => {
            console.log('Clipboard copy failed:', err);
          });
        }
      } else {
        console.error('❌ Popup blocked or failed to open');
        // Fallback: redirect to Facebook in same tab
        window.location.href = facebookUrl;
      }
    }

    function showNotification() {
      // Create a subtle notification that the image URL is copied
      const notification = document.createElement('div');
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #1877F2;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        font-size: 14px;
        font-family: Arial, sans-serif;
        transform: translateX(100%);
        transition: transform 0.3s ease;
      `;
      notification.textContent = '📋 Image URL copied! Paste it in your Facebook post.';
      
      document.body.appendChild(notification);
      
      // Animate in
      setTimeout(() => {
        notification.style.transform = 'translateX(0)';
      }, 100);
      
      // Remove after 4 seconds
      setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
          if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        }, 300);
      }, 4000);
    }
  };

  return (
    <button
      onClick={handleFacebookShare}
      className={`flex items-center justify-center gap-2 bg-[#1877F2] hover:bg-[#166FE5] text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 ${className}`}
    >
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
      </svg>
      Share to Facebook
    </button>
  );
};

export default FacebookShareButton;