export interface FaceSwapResult {
  id: number;
  match_name: string;
  match_score: number;
  message: string;
  output_image_url: string;
  original_selfie_url: string;
  historical_figure_url: string;
  is_randomized?: boolean;
  usage?: UsageData | null;
}

export interface ApiError {
  error: string;
  message?: string;
  feature_type?: 'match' | 'randomize';
  usage?: UsageData;
  registration_required?: boolean;
}

export type ProgressStep = 'uploading' | 'analyzing' | 'matching' | 'swapping' | 'complete';

export interface UploadProgress {
  step: ProgressStep;
  progress: number;
  message: string;
}

export interface HistoricalFigure {
  name: string;
  description: string;
  imageUrl: string;
  confidence?: number;
}

// NEW - Usage tracking types
export interface UsageData {
  matches_used: number;
  matches_limit: number;
  randomizes_used: number;
  randomizes_limit: number;
  can_match: boolean;
  can_randomize: boolean;
  is_limited: boolean;
  unlimited?: boolean;
  user_authenticated?: boolean;
}

export interface UsageLimitError extends ApiError {
  usage: UsageData;
  registration_required: true;
}