import axios from 'axios';
import type { FaceSwapResult, ApiError, UsageData, UsageLimitError } from '../types/index';

// Read from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8002';

console.log('🔧 Environment check:');
console.log('  - API_BASE_URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
  withCredentials: true, // Include cookies for session management
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error(`❌ API Error: ${error.response?.status}`, error.response?.data);
    return Promise.reject(error);
  }
);

export class FaceSwapAPI {
  static async generateFaceSwap(
    selfieFile: File,
    onProgress?: (progress: number) => void
  ): Promise<FaceSwapResult> {
    const formData = new FormData();
    formData.append('selfie', selfieFile);

    try {
      const response = await api.post<FaceSwapResult>('/api/imagegen/generate/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total && onProgress) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleApiError(error);
    }
  }

  static async randomizeFaceSwap(
    selfieFile: File,
    onProgress?: (progress: number) => void
  ): Promise<FaceSwapResult> {
    const formData = new FormData();
    formData.append('selfie', selfieFile);

    try {
      const response = await api.post<FaceSwapResult>('/api/imagegen/randomize/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total && onProgress) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleApiError(error);
    }
  }

  static async getUsageStatus(): Promise<UsageData> {
    try {
      const response = await api.get<UsageData>('/api/imagegen/usage/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to check usage status');
    }
  }

  static async getImageStatus(id: number): Promise<FaceSwapResult> {
    try {
      const response = await api.get<FaceSwapResult>(`/api/imagegen/status/${id}/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to check image status');
    }
  }

  static async testConnection(): Promise<boolean> {
    try {
      await api.get('/health/');
      return true;
    } catch (error) {
      return false;
    }
  }

  private static handleApiError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNREFUSED') {
        throw new Error('Cannot connect to server. Make sure the backend is running.');
      }
      
      if (error.response?.status === 429) {
        const errorData = error.response.data as UsageLimitError;
        const usageLimitError = new Error(errorData.message || 'Usage limit reached') as Error & UsageLimitError;
        usageLimitError.usage = errorData.usage;
        usageLimitError.registration_required = errorData.registration_required;
        usageLimitError.feature_type = errorData.feature_type;
        throw usageLimitError;
      }
      
      if (error.response?.data) {
        const apiError = error.response.data as ApiError;
        throw new Error(apiError.error || `Server error: ${error.response.status}`);
      }
    }
    
    throw new Error('Network error. Please check your connection and try again.');
  }
}

export default api;