// src/components/UserMenu.tsx
import React, { useState, useRef, useEffect } from 'react';
import { LogOut, Settings, History, ChevronDown } from 'lucide-react';
import { FaceSwapAPI } from '../services/api';

interface UserData {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

interface UserMenuProps {
  onShowRegistrationGate: () => void;
  onUserStateChange?: () => void;
}

const UserMenu: React.FC<UserMenuProps> = ({ onShowRegistrationGate, onUserStateChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setLoading(false);
        return;
      }

      // Try to get user info to verify token is valid
      const userData = await FaceSwapAPI.refreshUserSession();
      setUser(userData);
    } catch (error) {
      console.log('User not authenticated:', error);
      // Clear invalid token
      localStorage.removeItem('authToken');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSignIn = () => {
    onShowRegistrationGate();
    setIsOpen(false);
  };

  const handleLogout = async () => {
    try {
      await FaceSwapAPI.logout();
      setUser(null);
      setIsOpen(false);
      
      // Notify parent about user state change
      if (onUserStateChange) {
        onUserStateChange();
      }
      
      // Refresh page to reset any cached user data
      window.location.reload();
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if API call fails
      localStorage.removeItem('authToken');
      setUser(null);
      window.location.reload();
    }
  };

  const getUserInitials = (user: UserData): string => {
    const first = user.first_name?.charAt(0) || '';
    const last = user.last_name?.charAt(0) || '';
    return (first + last).toUpperCase() || user.email?.charAt(0).toUpperCase() || '?';
  };

  const getUserDisplayName = (user: UserData): string => {
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    if (user.first_name) {
      return user.first_name;
    }
    return user.email;
  };

  // Loading state
  if (loading) {
    return (
      <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse"></div>
    );
  }

  // Logged out state
  if (!user) {
    return (
      <button
        onClick={handleSignIn}
        className="bg-white hover:bg-gray-50 text-gray-700 font-semibold py-2 px-4 rounded-lg border border-gray-300 hover:border-gray-400 transition-all duration-200 text-sm"
      >
        Sign In
      </button>
    );
  }

  // Logged in state
  return (
    <div className="relative" ref={dropdownRef}>
      {/* User Avatar Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
          {getUserInitials(user)}
        </div>
        <ChevronDown 
          size={16} 
          className={`text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
          {/* User Info */}
          <div className="px-4 py-3 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">
                {getUserInitials(user)}
              </div>
              <div>
                <div className="font-medium text-gray-900">{getUserDisplayName(user)}</div>
                <div className="text-sm text-gray-500">{user.email}</div>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div className="py-1">
            <button
              onClick={() => {
                setIsOpen(false);
                // TODO: Navigate to account settings
                alert('Account settings coming soon!');
              }}
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <Settings size={16} />
              Account Settings
            </button>
            
            <button
              onClick={() => {
                setIsOpen(false);
                // TODO: Navigate to transformation history
                alert('Transformation history coming soon!');
              }}
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <History size={16} />
              My Transformations
            </button>
          </div>

          {/* Logout */}
          <div className="border-t border-gray-100 py-1">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut size={16} />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;