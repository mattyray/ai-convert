import { AlertCircle } from 'lucide-react';

interface ErrorDisplayProps {
  error: string;
  onTryAgain: () => void;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onTryAgain }) => {
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
            onClick={onTryAgain}
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
};

export default ErrorDisplay;