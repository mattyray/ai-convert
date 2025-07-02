// src/hooks/useFileUpload.ts

import { useState } from 'react';

// 📝 TypeScript: Define what our hook returns
interface UseFileUploadReturn {
  selectedFile: File | null;           // Either a File object or null
  isFileSelected: boolean;            // true/false if file exists
  handleFileSelect: (file: File) => void;  // Function that takes a File
  handleClearFile: () => void;        // Function that takes nothing
  error: string | null;               // Error message or null
}

// 📝 TypeScript: Define what file types we accept
const ACCEPTED_FILE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes

export const useFileUpload = (): UseFileUploadReturn => {
  // 🎯 State: Store the selected file
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 🎯 Function: Handle when user selects a file
  const handleFileSelect = (file: File) => {
    // Clear any previous errors
    setError(null);

    // 📋 Validate file type
    if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
      setError('Please select a valid image file (JPG, PNG, WebP)');
      return;
    }

    // 📋 Validate file size
    if (file.size > MAX_FILE_SIZE) {
      setError('File size must be less than 10MB');
      return;
    }

    // ✅ File is valid, store it
    setSelectedFile(file);
    console.log(`📁 File selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(1)}MB)`);
  };

  // 🎯 Function: Clear the selected file
  const handleClearFile = () => {
    setSelectedFile(null);
    setError(null);
    console.log('🗑️ File cleared');
  };

  // 🎯 Computed value: Check if we have a file
  const isFileSelected = selectedFile !== null;

  // 📤 Return everything the component needs
  return {
    selectedFile,
    isFileSelected,
    handleFileSelect,
    handleClearFile,
    error,
  };
};