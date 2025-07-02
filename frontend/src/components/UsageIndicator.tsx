import type { UsageData, UsageLimitError } from '../types/index';

interface UsageIndicatorProps {
  usage: UsageData;
  onShowRegistrationGate: (error: UsageLimitError) => void;
}

const UsageIndicator: React.FC<UsageIndicatorProps> = ({ usage, onShowRegistrationGate }) => {
  if (usage.unlimited) return null;

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <h3 className="font-medium text-blue-900 mb-2">Your Free Usage</h3>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="text-center">
          <div className={`text-lg font-bold ${usage.can_match ? 'text-green-600' : 'text-red-600'}`}>
            {usage.matches_used}/{usage.matches_limit}
          </div>
          <div className="text-gray-600">Face Matches</div>
        </div>
        <div className="text-center">
          <div className={`text-lg font-bold ${usage.can_randomize ? 'text-green-600' : 'text-red-600'}`}>
            {usage.randomizes_used}/{usage.randomizes_limit}
          </div>
          <div className="text-gray-600">Randomizes</div>
        </div>
      </div>
      {usage.is_limited && (
        <div className="mt-3 text-center">
          <button
            onClick={() => onShowRegistrationGate({ 
              feature_type: 'match', 
              usage, 
              registration_required: true,
              error: 'Usage limit reached',
              message: 'Get unlimited access'
            })}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Get unlimited access →
          </button>
        </div>
      )}
    </div>
  );
};

export default UsageIndicator;