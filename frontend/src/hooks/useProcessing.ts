// src/hooks/useProcessing.ts

import { useState } from 'react';
import { FaceSwapAPI } from '../services/api';
import type { FaceSwapResult, ProgressStep, UsageLimitError } from '../types/index';

// 📝 TypeScript: Define the processing state
interface ProcessingState {
  step: ProgressStep;
  progress: number;
  message: string;
  matchedFigure?: string;
}

// 📝 TypeScript: Define what this hook returns
interface UseProcessingReturn {
  isProcessing: boolean;
  processing: ProcessingState;
  result: FaceSwapResult | null;
  error: string | null;
  startProcessing: (file: File, isRandomize?: boolean) => Promise<void>;
  clearResult: () => void;
  clearError: () => void;
}

export const useProcessing = (
  onUsageLimitReached: (error: UsageLimitError) => void
): UseProcessingReturn => {
  // 🎯 State: Track processing status
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<FaceSwapResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState<ProcessingState>({
    step: 'uploading',
    progress: 0,
    message: 'Preparing your transformation...',
  });

  // 🎯 Helper: Update processing state
  const updateProgress = (
    step: ProgressStep, 
    progress: number, 
    message: string, 
    matchedFigure?: string
  ) => {
    setProcessing({ step, progress, message, matchedFigure });
  };

  // 🎯 Main function: Start the face swap process
  const startProcessing = async (file: File, isRandomize = false) => {
    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      // Step 1: Uploading
      updateProgress('uploading', 10, 'Uploading your selfie securely...');
      
      // Step 2: Analysis
      const analysisMessage = isRandomize 
        ? 'AI is preparing a random transformation...' 
        : 'AI is analyzing your facial features...';
      updateProgress('analyzing', 25, analysisMessage);
      
      // 🚀 Start the API call
      const apiPromise = isRandomize
        ? FaceSwapAPI.randomizeFaceSwap(file, (uploadProgress) => {
            updateProgress('uploading', Math.min(uploadProgress, 20), 'Uploading your selfie securely...');
          })
        : FaceSwapAPI.generateFaceSwap(file, (uploadProgress) => {
            updateProgress('uploading', Math.min(uploadProgress, 20), 'Uploading your selfie securely...');
          });
      
      // Simulate analysis step for better UX
      setTimeout(() => {
        const progressMessage = isRandomize 
          ? 'Spinning the wheel of history...' 
          : 'Identifying unique facial characteristics...';
        updateProgress('analyzing', 45, progressMessage);
      }, 1000);
      
      // Simulate matching step
      setTimeout(() => {
        const matchingMessage = isRandomize 
          ? 'Selecting your random historical twin...' 
          : 'Searching through historical figures...';
        updateProgress('matching', 65, matchingMessage);
      }, 2500);
      
      // 📡 Wait for API response
      const apiResult = await apiPromise;
      
      // Step 3: Show match found
      const matchMessage = isRandomize 
        ? `Random selection: ${apiResult.match_name}!` 
        : `Perfect match found: ${apiResult.match_name}!`;
      updateProgress('matching', 80, matchMessage, apiResult.match_name);
      
      // Step 4: Face swapping
      setTimeout(() => {
        updateProgress('swapping', 95, `Transforming you into ${apiResult.match_name}...`, apiResult.match_name);
      }, 1000);
      
      // Step 5: Complete
      setTimeout(() => {
        setResult(apiResult);
        setIsProcessing(false);
      }, 2000);
      
    } catch (err) {
      console.error('Face swap error:', err);
      
      // 🚨 Check if it's a usage limit error
      if (err && typeof err === 'object' && 'usage' in err) {
        const usageLimitError = err as UsageLimitError;
        console.log('Usage limit reached:', usageLimitError);
        onUsageLimitReached(usageLimitError);
        setIsProcessing(false);
        return; // Don't set error state, let registration gate handle it
      }
      
      // 🚨 Regular error handling
      const errorMessage = err instanceof Error ? err.message : 'Something went wrong. Please try again.';
      setError(errorMessage);
      setIsProcessing(false);
    }
  };

  // 🎯 Function: Clear result and go back to upload
  const clearResult = () => {
    setResult(null);
    setError(null);
    setProcessing({
      step: 'uploading',
      progress: 0,
      message: 'Preparing your transformation...',
    });
  };

  // 🎯 Function: Clear error state
  const clearError = () => {
    setError(null);
  };

  // 📤 Return everything the component needs
  return {
    isProcessing,
    processing,
    result,
    error,
    startProcessing,
    clearResult,
    clearError,
  };
};