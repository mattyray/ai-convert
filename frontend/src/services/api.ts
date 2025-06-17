import axios from 'axios';
import { FaceSwapResult, ApiError } from '../types';

const API_BASE_URL = 'http://127.0.0.1:8002/api';
const API_TOKEN = '90cc43ca30091f85a96b4ce3647ffa7b0f46e8f3';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Token ${API_TOKEN}`,
  },
});

export class FaceSwapAPI {
  static async generateFaceSwap(
    selfieFile: File,
    onProgress?: (progress: number) => void
  ): Promise<FaceSwapResult> {
    const formData = new FormData();
    formData.append('selfie', selfieFile);

    try {
      const response = await api.post<FaceSwapResult>('/imagegen/generate/', formData, {
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

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.data) {
        const apiError = error.response.data as ApiError;
        throw new Error(apiError.error || 'Face swap failed');
      }
      throw new Error('Network error. Please try again.');
    }
  }

  static async getImageStatus(id: number): Promise<FaceSwapResult> {
    const response = await api.get<FaceSwapResult>(`/imagegen/status/${id}/`);
    return response.data;
  }
}

export default api;