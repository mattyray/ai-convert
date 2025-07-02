import { Sparkles } from 'lucide-react';
import FileUpload from './FileUpload';
import RandomizeButton from './RandomizeButton';
import UsageIndicator from './UsageIndicator';
import HistoricalPreview from './HistoricalPreview';
import type { UsageData, UsageLimitError } from '../types/index';

interface UploadSectionProps {
  selectedFile: File | null;
  onFileSelect: (file: File) => void;
  onClearFile: () => void;
  onRegularMatch: () => void;
  onRandomize: () => void;
  onShowRegistrationGate: (error: UsageLimitError) => void;
  canUseMatch: boolean;
  usage: UsageData | null;
  usageLoading: boolean;
}

const UploadSection: React.FC<UploadSectionProps> = ({
  selectedFile,
  onFileSelect,
  onClearFile,
  onRegularMatch,
  onRandomize,
  onShowRegistrationGate,
  canUseMatch,
  usage,
  usageLoading
}) => {
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

      {/* Usage Indicator */}
      {!usageLoading && usage && !usage.unlimited && (
        <UsageIndicator 
          usage={usage} 
          onShowRegistrationGate={onShowRegistrationGate} 
        />
      )}

      <FileUpload
        onFileSelect={onFileSelect}
        selectedFile={selectedFile}
        onClear={onClearFile}
      />

      {selectedFile && (
        <div className="mt-8 space-y-4">
          {/* Regular Match Button */}
          <div className="text-center">
            <button
              onClick={onRegularMatch}
              disabled={!canUseMatch}
              className={`text-lg px-8 py-4 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-3 mx-auto ${
                canUseMatch
                  ? 'btn-primary'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              <Sparkles size={20} />
              🔮 Find My Historical Twin
            </button>
            <p className="text-sm text-gray-500 mt-2">
              AI analyzes your face to find the best match
            </p>
          </div>

          {/* OR Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">OR</span>
            </div>
          </div>

          {/* Randomize Button */}
          <RandomizeButton
            onRandomize={onRandomize}
            hasSelectedFile={!!selectedFile}
            usage={usage}
          />
        </div>
      )}

      <HistoricalPreview />
    </div>
  );
};

export default UploadSection;