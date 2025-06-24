import { Loader2, Search, Users, Sparkles, CheckCircle } from 'lucide-react';
import type { ProgressStep } from '../types/index';

interface ProcessingStatusProps {
  step: ProgressStep;
  progress: number;
  message: string;
  matchedFigure?: string;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  step,
  progress,
  message,
  matchedFigure
}) => {
  const steps = [
    {
      key: 'uploading',
      label: 'Uploading',
      icon: Loader2,
      description: 'Securely uploading your photo'
    },
    {
      key: 'analyzing',
      label: 'Analyzing',
      icon: Search,
      description: 'AI analyzing facial features'
    },
    {
      key: 'matching',
      label: 'Matching',
      icon: Users,
      description: 'Finding historical matches'
    },
    {
      key: 'swapping',
      label: 'Transforming',
      icon: Sparkles,
      description: 'Creating your transformation'
    },
  ];

  const getStepStatus = (stepKey: string) => {
    const stepIndex = steps.findIndex(s => s.key === stepKey);
    const currentStepIndex = steps.findIndex(s => s.key === step);
    
    if (stepIndex < currentStepIndex) return 'completed';
    if (stepIndex === currentStepIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-full p-3">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Creating Your Transformation
        </h2>
        <p className="text-gray-600">
          {message}
        </p>
        {matchedFigure && (
          <div className="mt-4 inline-block bg-green-50 border border-green-200 rounded-lg px-4 py-2">
            <p className="text-green-800 font-medium">
              ✨ Matched with {matchedFigure}!
            </p>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-4">
        {steps.map((stepItem) => {
          const status = getStepStatus(stepItem.key);
          const Icon = stepItem.icon;
          
          return (
            <div
              key={stepItem.key}
              className={`flex items-center p-4 rounded-lg transition-all duration-300 ${
                status === 'active'
                  ? 'bg-blue-50 border border-blue-200'
                  : status === 'completed'
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-gray-50 border border-gray-200'
              }`}
            >
              <div
                className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center mr-4 ${
                  status === 'active'
                    ? 'bg-blue-500 text-white'
                    : status === 'completed'
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}
              >
                {status === 'completed' ? (
                  <CheckCircle size={20} />
                ) : status === 'active' ? (
                  <Icon size={20} className="animate-spin" />
                ) : (
                  <Icon size={20} />
                )}
              </div>
              
              <div className="flex-grow">
                <div
                  className={`font-medium ${
                    status === 'active'
                      ? 'text-blue-900'
                      : status === 'completed'
                      ? 'text-green-900'
                      : 'text-gray-600'
                  }`}
                >
                  {stepItem.label}
                </div>
                <div
                  className={`text-sm ${
                    status === 'active'
                      ? 'text-blue-700'
                      : status === 'completed'
                      ? 'text-green-700'
                      : 'text-gray-500'
                  }`}
                >
                  {stepItem.description}
                </div>
              </div>
              
              <div className="flex-shrink-0">
                {status === 'active' && (
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                )}
                {status === 'completed' && (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Fun fact while waiting */}
      <div className="mt-8 p-4 bg-purple-50 border border-purple-200 rounded-lg">
        <p className="text-purple-800 text-sm text-center">
          💡 <strong>Did you know?</strong> Our AI analyzes over 100 facial landmarks to find your perfect historical match!
        </p>
      </div>
    </div>
  );
};

export default ProcessingStatus;