import React, { useState } from 'react';
import { Download, RefreshCw, Share2, Star, Loader2, CheckCircle, Copy } from 'lucide-react';
import type { FaceSwapResult } from '../types/index';
import FacebookShareButton from './FacebookShareButton';

interface ResultDisplayProps {
  result: FaceSwapResult;
  onTryAgain: () => void;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, onTryAgain }) => {
  const [downloadState, setDownloadState] = useState<'idle' | 'downloading' | 'success' | 'error'>('idle');

  const handleDownload = async () => {
    try {
      setDownloadState('downloading');
      console.log('🔽 Starting download for:', result.output_image_url);
      
      // Fetch the image as a blob to bypass CORS restrictions
      const response = await fetch(result.output_image_url);
      if (!response.ok) {
        throw new Error(`Failed to fetch image: ${response.status}`);
      }
      
      const blob = await response.blob();
      console.log('✅ Image fetched as blob:', blob.size, 'bytes');
      
      // Create a temporary URL for the blob
      const blobUrl = URL.createObjectURL(blob);
      
      // Create download link
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = `historyface_${result.match_name.replace(/[^a-zA-Z0-9]/g, '_')}_transformation.jpg`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up the blob URL to free memory
      URL.revokeObjectURL(blobUrl);
      
      setDownloadState('success');
      console.log('✅ Download completed');
      
      // Reset state after 2 seconds
      setTimeout(() => setDownloadState('idle'), 2000);
      
    } catch (error) {
      console.error('❌ Download failed:', error);
      setDownloadState('error');
      
      // Reset state after 3 seconds
      setTimeout(() => setDownloadState('idle'), 3000);
      
      // Fallback: open in new tab
      setTimeout(() => {
        window.open(result.output_image_url, '_blank');
      }, 1000);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `I transformed into ${result.match_name}!`,
          text: `Check out my AI transformation into ${result.match_name}`,
          url: window.location.href,
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // Fallback: copy to clipboard
      try {
        await navigator.clipboard.writeText(window.location.href);
        alert('Link copied to clipboard!');
      } catch (error) {
        alert('Could not copy link');
      }
    }
  };

  const handleCopyImageUrl = async () => {
    try {
      await navigator.clipboard.writeText(result.output_image_url);
      alert('✅ Image URL copied! Paste it into any social media post.');
    } catch (error) {
      alert('📋 Copy this URL: ' + result.output_image_url);
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600 bg-green-50';
    if (score >= 0.8) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getDownloadButtonContent = () => {
    switch (downloadState) {
      case 'downloading':
        return (
          <>
            <Loader2 className="animate-spin" size={20} />
            Downloading...
          </>
        );
      case 'success':
        return (
          <>
            <CheckCircle size={20} />
            Downloaded!
          </>
        );
      case 'error':
        return (
          <>
            <Download size={20} />
            Failed - Try Again
          </>
        );
      default:
        return (
          <>
            <Download size={20} />
            Download Result
          </>
        );
    }
  };

  return (
    <div className="space-y-8">
      {/* Success Message */}
      <div className="text-center bg-green-50 border border-green-200 rounded-xl p-6">
        <div className="flex items-center justify-center mb-4">
          <Star className="w-8 h-8 text-yellow-500 fill-current" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Transformation Complete! ✨
        </h2>
        <p className="text-gray-600">
          {result.message}
        </p>
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mt-3 ${getConfidenceColor(result.match_score)}`}>
          {(result.match_score * 100).toFixed(1)}% match confidence
        </div>
      </div>

      {/* Image Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Original Selfie */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-center text-gray-900">
            📸 Your Original
          </h3>
          <div className="relative overflow-hidden rounded-xl border-2 border-gray-200">
            <img
              src={result.original_selfie_url}
              alt="Your original selfie"
              className="w-full h-64 object-cover"
            />
          </div>
        </div>

        {/* Historical Figure */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-center text-gray-900">
            👑 {result.match_name}
          </h3>
          <div className="relative overflow-hidden rounded-xl border-2 border-yellow-300">
            <img
              src={result.historical_figure_url}
              alt={result.match_name}
              className="w-full h-64 object-cover"
            />
          </div>
        </div>

        {/* Final Result */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-center text-gray-900">
            ✨ Your Transformation
          </h3>
          <div className="relative overflow-hidden rounded-xl border-2 border-green-300">
            <img
              src={result.output_image_url}
              alt="Face swap result"
              className="w-full h-64 object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
            <div className="absolute bottom-3 left-3 right-3">
              <p className="text-white text-sm font-medium bg-black/50 rounded px-2 py-1">
                You as {result.match_name}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={handleDownload}
          disabled={downloadState === 'downloading'}
          className={`btn-primary flex items-center justify-center gap-2 ${
            downloadState === 'success' ? 'bg-green-500 hover:bg-green-600' : 
            downloadState === 'error' ? 'bg-red-500 hover:bg-red-600' : ''
          }`}
        >
          {getDownloadButtonContent()}
        </button>
        
        <button
          onClick={handleCopyImageUrl}
          className="btn-secondary flex items-center justify-center gap-2"
        >
          <Copy size={20} />
          Copy Image Link
        </button>
        
        <button
          onClick={handleShare}
          className="btn-secondary flex items-center justify-center gap-2"
        >
          <Share2 size={20} />
          Share Transformation
        </button>

        <FacebookShareButton 
          result={result}
          className="w-full sm:w-auto"
        />
        
        <button
          onClick={onTryAgain}
          className="btn-secondary flex items-center justify-center gap-2"
        >
          <RefreshCw size={20} />
          Try Another Photo
        </button>
      </div>

      {/* Download Error Message */}
      {downloadState === 'error' && (
        <div className="text-center">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            Download failed. Opening image in new tab instead...
          </div>
        </div>
      )}

      {/* Technical Details */}
      <div className="bg-gray-50 rounded-xl p-6">
        <h4 className="font-semibold text-gray-900 mb-3">Transformation Details</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Historical Match:</span>
            <span className="ml-2 text-gray-600">{result.match_name}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Confidence Score:</span>
            <span className="ml-2 text-gray-600">{(result.match_score * 100).toFixed(1)}%</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Transformation ID:</span>
            <span className="ml-2 text-gray-600">#{result.id}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Processing Time:</span>
            <span className="ml-2 text-gray-600">~30 seconds</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultDisplay;