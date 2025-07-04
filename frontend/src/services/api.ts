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

// 🔥 FIXED: Add request interceptor to include auth token in headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
      console.log('🔑 Adding auth token to request:', config.url);
    }
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

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

  // 🔥 NEW: Google Authentication
  static async googleAuth(credential: string, userInfo: any) {
    try {
      console.log('🔑 Sending Google auth request...');
      const response = await api.post('/api/accounts/auth/google/', { 
        credential: credential,
        user_info: userInfo
      });
      console.log('✅ Google auth successful:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Google auth failed:', error);
      throw this.handleApiError(error);
    }
  }

  // 🔥 NEW: Facebook Authentication
  static async facebookAuth(accessToken: string, userInfo: any) {
    try {
      console.log('🔑 Sending Facebook auth request...');
      const response = await api.post('/api/accounts/auth/facebook/', { 
        access_token: accessToken,
        user_info: userInfo
      });
      console.log('✅ Facebook auth successful:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Facebook auth failed:', error);
      throw this.handleApiError(error);
    }
  }

  // 🔥 NEW: Refresh User Session
  static async refreshUserSession() {
    try {
      const response = await api.get('/api/accounts/me/');
      return response.data;
    } catch (error) {
      throw this.handleApiError(error);
    }
  }

  // 🔥 NEW: Email/Password Signup (for future use)
  static async signUp(email: string, password: string, firstName?: string, lastName?: string) {
    try {
      const response = await api.post('/api/accounts/signup/', {
        email,
        password,
        first_name: firstName || '',
        last_name: lastName || ''
      });
      return response.data;
    } catch (error) {
      throw this.handleApiError(error);
    }
  }

  // 🔥 NEW: Email/Password Login (for future use)
  static async login(email: string, password: string) {
    try {
      const response = await api.post('/api/accounts/login/', {
        email,
        password
      });
      return response.data;
    } catch (error) {
      throw this.handleApiError(error);
    }
  }

  // 🔥 NEW: Logout
  static async logout() {
    try {
      await api.post('/api/accounts/logout/');
      // Clear local storage
      localStorage.removeItem('authToken');
      return true;
    } catch (error) {
      console.error('Logout error:', error);
      // Clear local storage even if API call fails
      localStorage.removeItem('authToken');
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
      
      // Handle authentication errors
      if (error.response?.status === 401) {
        const errorData = error.response.data as ApiError;
        throw new Error(errorData.error || 'Authentication failed');
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
