import React, { useState } from 'react';
import { Share2, CheckCircle } from 'lucide-react';
import type { FaceSwapResult } from '../types/index';

interface FacebookShareButtonProps {
  result: FaceSwapResult;
  className?: string;
}

const FacebookShareButton: React.FC<FacebookShareButtonProps> = ({ 
  result, 
  className = "" 
}) => {
  const [copyState, setCopyState] = useState<'idle' | 'copying' | 'copied'>('idle');

  const shareText = result.is_randomized 
    ? `🎭 I just transformed into ${result.match_name} using AI! Check out HistoryFace and see which historical figure you become! ✨`
    : `🎭 AI matched my face with ${result.match_name} (${(result.match_score * 100).toFixed(0)}% confidence)! Try HistoryFace and discover your historical twin! ✨`;

  const shareUrl = window.location.origin;
  const fullShareText = `${shareText}\n\n🌐 Try it: ${shareUrl}\n📸 My result: ${result.output_image_url}`;

  const handleShare = async () => {
    // 🔥 METHOD 1: Try Web Share API first (modern, works great on mobile)
    if (navigator.share) {
      try {
        await navigator.share({
          title: `I transformed into ${result.match_name}!`,
          text: shareText,
          url: shareUrl,
        });
        return; // Success, we're done
      } catch (error) {
        console.log('Web Share cancelled or failed, trying fallback');
      }
    }

    // 🔥 METHOD 2: Copy comprehensive text + open Facebook
    try {
      setCopyState('copying');
      await navigator.clipboard.writeText(fullShareText);
      setCopyState('copied');
      
      // Open Facebook after brief delay
      setTimeout(() => {
        const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
        window.open(facebookUrl, '_blank', 'width=600,height=500');
      }, 500);
      
      // Reset after 3 seconds
      setTimeout(() => setCopyState('idle'), 3000);
      
    } catch (error) {
      // 🔥 METHOD 3: Fallback - just open Facebook
      console.error('Clipboard failed, opening Facebook directly');
      const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
      window.open(facebookUrl, '_blank');
    }
  };

  const getButtonContent = () => {
    switch (copyState) {
      case 'copying':
        return (
          <>
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            Preparing...
          </>
        );
      case 'copied':
        return (
          <>
            <CheckCircle size={20} />
            Text Copied! Opening Facebook...
          </>
        );
      default:
        return (
          <>
            <Share2 size={20} />
            Share to Facebook
          </>
        );
    }
  };

  return (
    <div className="space-y-2">
      <button
        onClick={handleShare}
        disabled={copyState === 'copying'}
        className={`flex items-center justify-center gap-2 bg-[#1877F2] hover:bg-[#166FE5] text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-75 disabled:hover:scale-100 ${className}`}
      >
        {getButtonContent()}
      </button>
      
      {copyState === 'copied' && (
        <div className="text-xs text-gray-600 text-center animate-pulse">
          📋 Share text copied! Paste it in Facebook and add your image.
        </div>
      )}
    </div>
  );
};

export default FacebookShareButton;
