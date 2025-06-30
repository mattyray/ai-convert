import axios from 'axios';
import type { FaceSwapResult, ApiError } from '../types/index';

// Read from environment variables (from Netlify environment variables)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8002';
const API_TOKEN = import.meta.env.VITE_API_TOKEN;

// Debug environment variables
console.log('🔧 Environment check:');
console.log('  - API_BASE_URL:', API_BASE_URL);
console.log('  - NODE_ENV:', import.meta.env.MODE);
console.log('  - API_TOKEN present:', !!API_TOKEN);

// Debug: Check if token is loaded
if (!API_TOKEN) {
  console.error('❌ API Token not found! Make sure environment variables are set with VITE_API_TOKEN');
} else {
  console.log('✅ API Token loaded:', API_TOKEN.substring(0, 8) + '...');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': API_TOKEN ? `Token ${API_TOKEN}` : '',
  },
  timeout: 60000, // Default 1 minute timeout for most requests
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
      throw new Error('API token not configured. Please set VITE_API_TOKEN in environment variables.');
    }

    const formData = new FormData();
    formData.append('selfie', selfieFile);

    try {
      console.log(`📤 Uploading file: ${selfieFile.name} (${(selfieFile.size / 1024 / 1024).toFixed(1)}MB)`);
      
      // 🔥 UPDATED: Extended timeout and better error handling for large uploads
      const response = await api.post<FaceSwapResult>('/api/imagegen/generate/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 180000, // 3 minutes for face swap processing
        validateStatus: function (status) {
          return status < 500; // Don't throw on 4xx errors, only 5xx
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
        console.error('❌ Axios error details:', {
          message: error.message,
          status: error.response?.status,
          statusText: error.response?.statusText,
          url: error.config?.url,
          method: error.config?.method,
          code: error.code
        });

        // Handle timeout specifically
        if (error.code === 'ECONNABORTED') {
          throw new Error('Request timed out. Large images may take up to 3 minutes to process. Please try a smaller image or try again.');
        }

        if (error.code === 'ECONNREFUSED') {
          throw new Error('Cannot connect to server. Make sure the backend is running.');
        }
        
        if (error.code === 'ERR_NETWORK') {
          throw new Error('Network error - check CORS settings and backend connectivity.');
        }
        
        if (error.response?.status === 401) {
          throw new Error('Authentication failed. Check your API token in environment variables.');
        }
        
        if (error.response?.status === 404) {
          throw new Error('API endpoint not found. Check the backend URL configuration.');
        }
        
        if (error.response?.status === 413) {
          throw new Error('File too large. Please use an image under 10MB.');
        }

        if (error.response?.status === 503) {
          throw new Error('Server is busy processing other requests. Please try again in 30 seconds.');
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
      // Test the health endpoint first
      const response = await api.get('/health/');
      console.log('✅ Health check passed:', response.data);
      return true;
    } catch (error) {
      console.error('❌ Connection test failed:', error);
      // Try the root endpoint as fallback
      try {
        const response = await api.get('/');
        console.log('✅ Root endpoint accessible:', response.data);
        return true;
      } catch (rootError) {
        console.error('❌ Root endpoint also failed:', rootError);
        return false;
      }
    }
  }
}

export default api;