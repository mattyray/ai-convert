import React, { useState } from 'react';
import { Sparkles, AlertCircle, History } from 'lucide-react';
import FileUpload from './components/FileUpload';
import ProcessingStatus from './components/ProcessingStatus';
import ResultDisplay from './components/ResultDisplay';
import { FaceSwapAPI } from './services/api';
import type { FaceSwapResult } from './types/index';

type AppState = 'upload' | 'processing' | 'result' | 'error';

function App() {
  const [state, setState] = useState<AppState>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<FaceSwapResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState({
    step: 'uploading' as const,
    progress: 0,
    message: 'Preparing your transformation...',
    matchedFigure: undefined as string | undefined,
  });

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setError(null);
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setError(null);
  };

  const handleStartProcessing = async () => {
    if (!selectedFile) return;

    setState('processing');
    setError(null);
    
    try {
      // Simulate processing steps for better UX
      const updateProgress = (step: typeof processing.step, progress: number, message: string, matchedFigure?: string) => {
        setProcessing({ step, progress, message, matchedFigure });
      };

      // Step 1: Uploading
      updateProgress('uploading', 10, 'Uploading your selfie securely...');
      
      // Step 2: Start the API call
      updateProgress('analyzing', 25, 'AI is analyzing your facial features...');
      
      const apiPromise = FaceSwapAPI.generateFaceSwap(selectedFile, (uploadProgress) => {
        updateProgress('uploading', Math.min(uploadProgress, 20), 'Uploading your selfie securely...');
      });
      
      // Simulate analysis step
      setTimeout(() => {
        updateProgress('analyzing', 45, 'Identifying unique facial characteristics...');
      }, 1000);
      
      // Simulate matching step
      setTimeout(() => {
        updateProgress('matching', 65, 'Searching through historical figures...');
      }, 2500);
      
      // Wait for API response
      const apiResult = await apiPromise;
      
      // Step 3: Show match found
      updateProgress('matching', 80, `Perfect match found: ${apiResult.match_name}!`, apiResult.match_name);
      
      // Step 4: Face swapping
      setTimeout(() => {
        updateProgress('swapping', 95, `Transforming you into ${apiResult.match_name}...`, apiResult.match_name);
      }, 1000);
      
      // Step 5: Complete
      setTimeout(() => {
        setResult(apiResult);
        setState('result');
      }, 2000);
      
    } catch (err) {
      console.error('Face swap error:', err);
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
      setState('error');
    }
  };

  const handleTryAgain = () => {
    setState('upload');
    setSelectedFile(null);
    setResult(null);
    setError(null);
    setProcessing({
      step: 'uploading',
      progress: 0,
      message: 'Preparing your transformation...',
      matchedFigure: undefined,
    });
  };

  const renderContent = () => {
    switch (state) {
      case 'upload':
        return (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-full p-3">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
              </div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                AI Historical Face Swap
              </h1>
              <p className="text-xl text-gray-600 mb-6">
                Discover which historical figure you resemble and see yourself transformed!
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
                <p className="text-blue-800 text-sm">
                  🎭 Our AI will analyze your facial features and match you with historical figures like Napoleon, Cleopatra, Leonardo da Vinci, and more!
                </p>
              </div>
            </div>

            <FileUpload
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              onClear={handleClearFile}
            />

            {selectedFile && (
              <div className="mt-8 text-center">
                <button
                  onClick={handleStartProcessing}
                  className="btn-primary text-lg px-8 py-4"
                >
                  🔮 Find My Historical Twin
                </button>
                <p className="text-sm text-gray-500 mt-3">
                  This will take about 30 seconds
                </p>
              </div>
            )}

            {/* Historical Figures Preview */}
            <div className="mt-12 text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">
                Meet Some Historical Figures
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
                {[
                  { name: 'Napoleon', emoji: '👑' },
                  { name: 'Cleopatra', emoji: '🏺' },
                  { name: 'Leonardo da Vinci', emoji: '🎨' },
                  { name: 'Marie Antoinette', emoji: '👸' },
                  { name: 'JFK', emoji: '🇺🇸' },
                  { name: 'Frida Kahlo', emoji: '🌺' },
                ].map((figure) => (
                  <div key={figure.name} className="text-center p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
                    <div className="text-2xl mb-2">{figure.emoji}</div>
                    <div className="text-xs text-gray-600 font-medium">{figure.name}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'processing':
        return (
          <div className="max-w-xl mx-auto">
            <ProcessingStatus
              step={processing.step}
              progress={processing.progress}
              message={processing.message}
              matchedFigure={processing.matchedFigure}
            />
          </div>
        );

      case 'result':
        return result ? (
          <div className="max-w-4xl mx-auto">
            <ResultDisplay
              result={result}
              onTryAgain={handleTryAgain}
            />
          </div>
        ) : null;

      case 'error':
        return (
          <div className="max-w-xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
              <div className="flex items-center justify-center mb-4">
                <AlertCircle className="w-12 h-12 text-red-500" />
              </div>
              <h3 className="text-xl font-semibold text-red-900 mb-4">
                Oops! Something went wrong
              </h3>
              <p className="text-red-700 mb-6">
                {error}
              </p>
              <div className="space-y-3">
                <button
                  onClick={handleTryAgain}
                  className="btn-primary w-full"
                >
                  Try Again
                </button>
                <p className="text-sm text-red-600">
                  Make sure your photo shows a clear face and is under 10MB
                </p>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg p-2">
                <History className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">HistoryFace</h1>
                <p className="text-sm text-gray-500">AI Historical Transformation</p>
              </div>
            </div>
            
            {state !== 'upload' && (
              <button
                onClick={handleTryAgain}
                className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                ← Start Over
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="bg-gray-50 border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-gray-600 text-sm">
              Powered by AI face recognition and historical figure matching
            </p>
            <p className="text-gray-500 text-xs mt-2">
              Your photos are processed securely and not stored permanently
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;