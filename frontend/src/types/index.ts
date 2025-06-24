export interface FaceSwapResult {
  id: number;
  match_name: string;
  match_score: number;
  message: string;
  output_image_url: string;
  original_selfie_url: string;
  historical_figure_url: string;
}

export interface ApiError {
  error: string;
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