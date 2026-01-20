'use client';

import { Emoji } from '@/components/ui';
import { ERROR_MESSAGES, HELP_TEXTS, LABELS, PLACEHOLDERS } from '@/constants';
import type { PhotoData } from '@/types/reflection';
import type React from 'react';
import { useEffect, useRef, useState } from 'react';

interface ImageUploaderProps {
  photos: PhotoData[]; // 写真データ配列
  onPhotosChange: (newPhotos: PhotoData[]) => void;
  onRemovePhoto?: (index: number) => void;
  maxImages?: number;
  maxSizeMB?: number;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  photos,
  onPhotosChange,
  onRemovePhoto,
  maxImages = 5,
  maxSizeMB = 10,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // メモリリーク防止: コンポーネントアンマウント時にオブジェクトURLを解放
  useEffect(() => {
    return () => {
      photos.forEach(photo => {
        if (photo.url.startsWith('blob:')) {
          URL.revokeObjectURL(photo.url);
        }
      });
    };
  }, [photos]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(Array.from(e.target.files));
    }
  };

  const processFiles = (newFiles: File[]) => {
    // 画像のみフィルタリング
    const imageFiles = newFiles.filter(file => file.type.startsWith('image/'));

    if (imageFiles.length === 0) {
      alert(ERROR_MESSAGES.INVALID_FILE_TYPE);
      return;
    }

    // 現在の枚数チェック
    if (photos.length + imageFiles.length > maxImages) {
      alert(ERROR_MESSAGES.MAX_IMAGES_EXCEEDED(maxImages));
      return;
    }

    // ファイルサイズチェック
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    const oversizedFiles = imageFiles.filter(file => file.size > maxSizeBytes);
    if (oversizedFiles.length > 0) {
      oversizedFiles.forEach(file => {
        alert(ERROR_MESSAGES.FILE_SIZE_EXCEEDED(file.name, maxSizeMB));
      });
      return;
    }

    // PhotoDataオブジェクトを生成
    const newPhotos: PhotoData[] = imageFiles.map(file => ({
      url: URL.createObjectURL(file),
      file,
    }));

    // 親コンポーネントに新しく追加された写真データを通知
    onPhotosChange(newPhotos);
  };

  const handleRemove = (index: number) => {
    // オブジェクトURLを解放
    const photo = photos[index];
    if (photo.url.startsWith('blob:')) {
      URL.revokeObjectURL(photo.url);
    }
    onRemovePhoto?.(index);
  };

  return (
    <div>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept="image/*"
        multiple
      />

      {/* ドロップゾーン */}
      <button
        type="button"
        className={`mb-4 flex h-48 w-full cursor-pointer items-center justify-center rounded-lg border-2 border-dashed transition-colors ${
          isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-neutral-300 bg-neutral-50 hover:border-primary-400'
        }`}
        onKeyDown={e => {
          if (e.key === 'Enter' || e.key === ' ') {
            fileInputRef.current?.click();
          }
        }}
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        aria-label={PLACEHOLDERS.UPLOAD_INSTRUCTION}
      >
        <div className="text-center">
          <div className="mb-2 text-4xl">
            <Emoji symbol="📤" label="アップロード" />
          </div>
          <p className="mb-1 font-medium text-neutral-700">{PLACEHOLDERS.UPLOAD_INSTRUCTION}</p>
          <p className="text-neutral-500 text-xs">{HELP_TEXTS.UPLOAD_FORMAT}</p>
        </div>
      </button>

      {/* プレビューエリア */}
      {photos.length > 0 && (
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-5">
          {photos.map((photo, index) => (
            <div
              key={photo.id || photo.url}
              className="group relative aspect-square overflow-hidden rounded-lg border border-neutral-200 bg-neutral-100"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={photo.url}
                alt={`Uploaded ${index + 1}`}
                className="h-full w-full object-cover"
              />
              {onRemovePhoto && (
                <button
                  type="button"
                  onClick={() => handleRemove(index)}
                  className="absolute top-1 right-1 flex h-5 w-5 items-center justify-center rounded-full bg-black/50 text-white text-xs opacity-0 transition-opacity group-hover:opacity-100"
                  aria-label={LABELS.REMOVE_IMAGE}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
