import { History } from 'lucide-react';
import ProcessingStatus from './components/ProcessingStatus';
import ResultDisplay from './components/ResultDisplay';
import RegistrationGate from './components/RegistrationGate';
import UploadSection from './components/UploadSection';
import ErrorDisplay from './components/ErrorDisplay';
import UserMenu from './components/UserMenu';
import { useUsage } from './hooks/useUsage';
import { useFileUpload } from './hooks/useFileUpload';
import { useProcessing } from './hooks/useProcessing';
import { useRegistrationGate } from './hooks/useRegistrationGate';
import { useAuth } from './hooks/useAuth';

function App() {
  // 🎯 Custom Hooks handle all the complexity
  const { usage, loading: usageLoading, checkUsage } = useUsage();
  const { isAuthenticated, checkAuthStatus } = useAuth();
  
  const { 
    selectedFile, 
    handleFileSelect, 
    handleClearFile, 
    error: fileError 
  } = useFileUpload();
  
  // 🔥 Updated: Enhanced registration gate callback
  const handleUsageLimitReached = (usageLimitError: any) => {
    // Only show registration gate if user is not authenticated
    if (!isAuthenticated) {
      showRegistrationGate(usageLimitError);
    }
  };
  
  const {
    isProcessing,
    processing,
    result,
    error: processingError,
    startProcessing,
    clearResult,
    clearError
  } = useProcessing(handleUsageLimitReached);
  
  const {
    isOpen: showRegistrationModal,
    lastFeatureAttempted,
    showRegistrationGate,
    hideRegistrationGate,
    handleSignUp,
    handleLogin,
    canUseFeature
  } = useRegistrationGate(() => {
    checkUsage();
    checkAuthStatus();
  });

  // 🎯 Unified error handling
  const currentError = fileError || processingError;

  // 🎯 Event Handlers
  const handleFileSelectWrapper = (file: File) => {
    handleFileSelect(file);
    if (currentError) {
      clearError();
    }
  };

  const handleClearFileWrapper = () => {
    handleClearFile();
    clearResult();
    clearError();
  };

  const handleStartProcessing = async (isRandomize = false) => {
    if (!selectedFile) return;
    
    try {
      await startProcessing(selectedFile, isRandomize);
      checkUsage(); // Refresh usage after successful operation
    } catch (error) {
      // Error handling is done in the useProcessing hook
      console.error('Processing failed:', error);
    }
  };

  const handleRegularMatch = () => handleStartProcessing(false);
  const handleRandomize = () => handleStartProcessing(true);

  const handleTryAgain = () => {
    handleClearFileWrapper();
  };

  // 🎯 Render main content based on processing state
  const renderContent = () => {
    if (isProcessing) {
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
    }

    if (result) {
      return (
        <div className="max-w-4xl mx-auto">
          <ResultDisplay
            result={result}
            onTryAgain={handleTryAgain}
          />
        </div>
      );
    }

    if (currentError) {
      return (
        <ErrorDisplay
          error={currentError}
          onTryAgain={handleTryAgain}
        />
      );
    }

    // Default: Upload screen
    return (
      <UploadSection
        selectedFile={selectedFile}
        onFileSelect={handleFileSelectWrapper}
        onClearFile={handleClearFileWrapper}
        onRegularMatch={handleRegularMatch}
        onRandomize={handleRandomize}
        onShowRegistrationGate={showRegistrationGate}
        canUseMatch={isAuthenticated ? true : canUseFeature('match', usage)}
        usage={usage}
        usageLoading={usageLoading}
      />
    );
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
            
            <div className="flex items-center gap-4">
              {/* Usage Summary - only show for non-authenticated users */}
              {!isAuthenticated && usage && !usage.unlimited && !usageLoading && (
                <div className="hidden sm:flex items-center gap-3 text-sm text-gray-600">
                  <span>Matches: {usage.matches_used}/{usage.matches_limit}</span>
                  <span>•</span>
                  <span>Randomizes: {usage.randomizes_used}/{usage.randomizes_limit}</span>
                </div>
              )}
              
              {/* Authenticated user gets unlimited indicator */}
              {isAuthenticated && (
                <div className="hidden sm:flex items-center gap-2 text-sm text-green-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  <span>Unlimited Access</span>
                </div>
              )}
              
              {(result || currentError) && (
                <button
                  onClick={handleTryAgain}
                  className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  ← Start Over
                </button>
              )}

              {/* User Menu */}
              <UserMenu 
                onShowRegistrationGate={() => showRegistrationGate({
                  error: 'Authentication required',
                  message: 'Sign up to unlock unlimited access',
                  feature_type: 'match',
                  registration_required: true,
                  usage: usage || {
                    matches_used: 0,
                    matches_limit: 1,
                    randomizes_used: 0,
                    randomizes_limit: 1,
                    can_match: true,
                    can_randomize: true,
                    is_limited: false,
                  }
                })}
                onUserStateChange={() => {
                  checkUsage();
                  checkAuthStatus();
                }}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderContent()}
      </main>

      {/* Registration Gate Modal */}
      <RegistrationGate
        isOpen={showRegistrationModal}
        onClose={hideRegistrationGate}
        onSignUp={handleSignUp}
        onLogin={handleLogin}
        usage={usage}
        lastFeatureAttempted={lastFeatureAttempted}
      />

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