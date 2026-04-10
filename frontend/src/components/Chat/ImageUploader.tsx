import { useState, useCallback, useRef } from 'react';

interface ImageFile {
  id: string;
  file: File;
  preview: string;
  dataUrl: string;
}

interface ImageUploaderProps {
  onImagesUploaded: (images: { url: string; type: string; alt_text: string | null }[]) => void;
  disabled?: boolean;
  maxImages?: number;
}

export function ImageUploader({ 
  onImagesUploaded, 
  disabled,
  maxImages = 5 
}: ImageUploaderProps) {
  const [images, setImages] = useState<ImageFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      return 'File type not supported. Use JPEG, PNG, WebP, or GIF.';
    }

    if (file.size > maxSize) {
      return 'File too large. Maximum size is 10MB.';
    }

    return null;
  };

  const processFile = useCallback((file: File): Promise<ImageFile> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string;
        const imageFile: ImageFile = {
          id: crypto.randomUUID(),
          file,
          preview: dataUrl,
          dataUrl,
        };
        resolve(imageFile);
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(file);
    });
  }, []);

  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files) return;

    setError(null);
    const newImages: ImageFile[] = [];
    const errors: string[] = [];

    for (const file of Array.from(files)) {
      if (images.length + newImages.length >= maxImages) {
        errors.push(`Maximum ${maxImages} images allowed.`);
        break;
      }

      const validationError = validateFile(file);
      if (validationError) {
        errors.push(`${file.name}: ${validationError}`);
        continue;
      }

      try {
        const imageFile = await processFile(file);
        newImages.push(imageFile);
      } catch {
        errors.push(`${file.name}: Failed to process file`);
      }
    }

    if (errors.length > 0) {
      setError(errors.join(' '));
    }

    if (newImages.length > 0) {
      setImages((prev) => [...prev, ...newImages]);
    }
  }, [images.length, maxImages, processFile]);

  const handleRemove = useCallback((id: string) => {
    setImages((prev) => {
      const image = prev.find((img) => img.id === id);
      if (image) {
        // Revoke the object URL to avoid memory leaks
        URL.revokeObjectURL(image.preview);
      }
      return prev.filter((img) => img.id !== id);
    });
  }, []);

  const handleUpload = useCallback(async () => {
    if (images.length === 0) return;

    setIsUploading(true);
    setError(null);

    try {
      const uploadedImages = images.map((img) => ({
        url: img.dataUrl,
        type: img.file.type,
        alt_text: img.file.name,
      }));
      onImagesUploaded(uploadedImages);
      setImages([]);
    } catch {
      setError('Failed to upload images');
    } finally {
      setIsUploading(false);
    }
  }, [images, onImagesUploaded]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  return (
    <div className="space-y-3">
      {/* Image previews */}
      {images.length > 0 && (
        <div className="flex flex-wrap gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
          {images.map((img) => (
            <div key={img.id} className="relative group">
              <img
                src={img.preview}
                alt={img.file.name}
                className="w-16 h-16 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
              />
              <button
                type="button"
                onClick={() => handleRemove(img.id)}
                className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className={`border-2 border-dashed rounded-lg p-4 text-center ${
          disabled || images.length >= maxImages
            ? 'border-gray-200 dark:border-gray-700 cursor-not-allowed'
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 cursor-pointer'
        }`}
        onClick={() => !disabled && images.length < maxImages && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          multiple
          onChange={(e) => handleFiles(e.target.files)}
          className="hidden"
          disabled={disabled}
        />
        
        {images.length >= maxImages ? (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Maximum {maxImages} images reached
          </p>
        ) : (
          <>
            <svg className="w-8 h-8 mx-auto text-gray-400 dark:text-gray-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Drop images here or click to upload
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              JPEG, PNG, WebP, GIF up to 10MB
            </p>
          </>
        )}
      </div>

      {/* Error message */}
      {error && (
        <p className="text-sm text-red-500 dark:text-red-400">{error}</p>
      )}

      {/* Actions */}
      {images.length > 0 && (
        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={() => setImages([])}
            className="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
          >
            Clear
          </button>
          <button
            type="button"
            onClick={handleUpload}
            disabled={isUploading}
            className="px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {isUploading ? 'Adding...' : 'Add Images'}
          </button>
        </div>
      )}
    </div>
  );
}
