// src/hooks/useAuth.ts
import { useState, useEffect, useCallback } from 'react';
import { FaceSwapAPI } from '../services/api';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  login: (token: string, userData: User) => void;
  logout: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
  clearError: () => void;
}

export const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkAuthStatus = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('authToken');
      if (!token) {
        setUser(null);
        return;
      }

      // Verify token is still valid by getting user info
      const userData = await FaceSwapAPI.refreshUserSession();
      setUser(userData);
    } catch (err) {
      console.log('Auth check failed:', err);
      // Clear invalid token
      localStorage.removeItem('authToken');
      setUser(null);
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  }, []);

  const login = useCallback((token: string, userData: User) => {
    localStorage.setItem('authToken', token);
    setUser(userData);
    setError(null);
    console.log('✅ User logged in:', userData.email);
  }, []);

  const logout = useCallback(async () => {
    try {
      await FaceSwapAPI.logout();
    } catch (err) {
      console.error('Logout API call failed:', err);
      // Continue with logout even if API call fails
    } finally {
      localStorage.removeItem('authToken');
      setUser(null);
      setError(null);
      console.log('✅ User logged out');
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Check auth status on mount
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  return {
    user,
    isAuthenticated: !!user,
    loading,
    error,
    login,
    logout,
    checkAuthStatus,
    clearError,
  };
};