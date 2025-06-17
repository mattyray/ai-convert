import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Image as ImageIcon } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
  disabled?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  selectedFile,
  onClear,
  disabled = false
}) => {
  const [preview, setPreview] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      onFileSelect(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxFiles: 1,
    disabled
  });

  const handleClear = () => {
    onClear();
    setPreview(null);
  };

  if (selectedFile && preview) {
    return (
      <div className="relative">
        <div className="relative overflow-hidden rounded-xl border-2 border-gray-200">
          <img
            src={preview}
            alt="Selected selfie"
            className="w-full h-64 object-cover"
          />
          {!disabled && (
            <button
              onClick={handleClear}
              className="absolute top-3 right-3 bg-red-500 hover:bg-red-600 text-white rounded-full p-2 transition-colors"
            >
              <X size={16} />
            </button>
          )}
        </div>
        <div className="mt-3 text-center">
          <p className="text-sm text-gray-600">
            📸 <strong>{selectedFile.name}</strong>
          </p>
          <p className="text-xs text-gray-500">
            {(selectedFile.size / 1024 / 1024).toFixed(1)} MB
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200
        ${isDragActive 
          ? 'border-primary-500 bg-primary-50' 
          : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input {...getInputProps()} />
      
      <div className="space-y-4">
        <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
          {isDragActive ? (
            <Upload className="w-8 h-8 text-primary-500" />
          ) : (
            <ImageIcon className="w-8 h-8 text-gray-400" />
          )}
        </div>
        
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {isDragActive ? 'Drop your selfie here!' : 'Upload Your Selfie'}
          </h3>
          <p className="text-gray-500 mb-4">
            Drag and drop your photo, or click to browse
          </p>
          <div className="text-xs text-gray-400">
            Supports: JPG, PNG, WebP • Max size: 10MB
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;