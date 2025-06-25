import axios from 'axios';
import type { FaceSwapResult, ApiError } from '../types/index';

// Read from environment variables (from .env.local file)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8002';
const API_TOKEN = import.meta.env.VITE_API_TOKEN;

// Debug: Check if token is loaded
if (!API_TOKEN) {
  console.error('❌ API Token not found! Make sure Netlify environment variables are set with VITE_API_TOKEN');
} else {
  console.log('✅ API Token loaded:', API_TOKEN.substring(0, 8) + '...');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': API_TOKEN ? `Token ${API_TOKEN}` : '',
  },
  timeout: 300000, // 5 minutes for face swap processing
});

// Add request interceptor for debugging
api.interceptors.request.use((config) => {
  console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.baseURL}${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.baseURL}${error.config?.url}`, error.response?.data);
    return Promise.reject(error);
  }
);

export class FaceSwapAPI {
  static async generateFaceSwap(
    selfieFile: File,
    onProgress?: (progress: number) => void
  ): Promise<FaceSwapResult> {
    if (!API_TOKEN) {
      throw new Error('API token not configured. Please set VITE_API_TOKEN in Netlify environment variables.');
    }

    const formData = new FormData();
    formData.append('selfie', selfieFile);

    try {
      console.log(`📤 Uploading file: ${selfieFile.name} (${(selfieFile.size / 1024 / 1024).toFixed(1)}MB)`);
      
      const response = await api.post<FaceSwapResult>('/api/imagegen/generate/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total && onProgress) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      });

      console.log('✅ Face swap successful:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Face swap failed:', error);
      
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNREFUSED') {
          throw new Error('Cannot connect to server. Make sure the backend is running.');
        }
        
        if (error.response?.status === 401) {
          throw new Error('Authentication failed. Check your API token in Netlify environment variables.');
        }
        
        if (error.response?.status === 413) {
          throw new Error('File too large. Please use an image under 10MB.');
        }
        
        if (error.response?.data) {
          const apiError = error.response.data as ApiError;
          throw new Error(apiError.error || `Server error: ${error.response.status}`);
        }
      }
      
      throw new Error('Network error. Please check your connection and try again.');
    }
  }

  static async getImageStatus(id: number): Promise<FaceSwapResult> {
    try {
      const response = await api.get<FaceSwapResult>(`/api/imagegen/status/${id}/`);
      return response.data;
    } catch (error) {
      console.error('❌ Status check failed:', error);
      throw new Error('Failed to check image status');
    }
  }

  static async testConnection(): Promise<boolean> {
    try {
      await api.get('/health/');
      return true;
    } catch (error) {
      console.error('❌ Connection test failed:', error);
      return false;
    }
  }
}

export default api;