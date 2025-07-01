import React from 'react';
import { Shuffle, Lock } from 'lucide-react';
import type { UsageData } from '../types/index';

interface RandomizeButtonProps {
  onRandomize: () => void;
  disabled?: boolean;
  loading?: boolean;
  usage?: UsageData | null;
  hasSelectedFile: boolean;
}

const RandomizeButton: React.FC<RandomizeButtonProps> = ({
  onRandomize,
  disabled = false,
  loading = false,
  usage,
  hasSelectedFile
}) => {
  const canRandomize = usage ? (usage.unlimited || usage.can_randomize) : true;
  const isDisabled = disabled || loading || !hasSelectedFile || !canRandomize;
  
  const getButtonText = () => {
    if (loading) return 'Randomizing...';
    if (!hasSelectedFile) return 'Upload Photo First';
    if (!canRandomize && usage) {
      return `Randomize (${usage.randomizes_used}/${usage.randomizes_limit} used)`;
    }
    return '🎲 Surprise Me!';
  };

  const getButtonSubtext = () => {
    if (!hasSelectedFile) return 'Select a selfie to get started';
    if (!canRandomize && usage) return 'Upgrade to randomize more';
    return 'Get matched with a random historical figure';
  };

  return (
    <div className="text-center">
      <button
        onClick={onRandomize}
        disabled={isDisabled}
        className={`
          relative px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 flex items-center justify-center gap-3 mx-auto
          ${isDisabled 
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
            : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
          }
        `}
      >
        {!canRandomize && usage ? (
          <Lock size={20} />
        ) : (
          <Shuffle size={20} className={loading ? 'animate-spin' : ''} />
        )}
        {getButtonText()}
      </button>
      
      <p className={`text-sm mt-2 ${!canRandomize && usage ? 'text-red-600' : 'text-gray-600'}`}>
        {getButtonSubtext()}
      </p>
      
      {usage && !usage.unlimited && (
        <div className="mt-3 text-xs text-gray-500">
          Randomizes remaining: {usage.can_randomize ? usage.randomizes_limit - usage.randomizes_used : 0}
        </div>
      )}
    </div>
  );
};

export default RandomizeButton;