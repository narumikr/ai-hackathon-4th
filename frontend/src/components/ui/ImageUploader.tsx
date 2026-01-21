'use client';

import { Emoji } from '@/components/ui';
import { ERROR_MESSAGES, HELP_TEXTS, LABELS, PLACEHOLDERS } from '@/constants';
import type React from 'react';
import { useEffect, useRef, useState } from 'react';

interface ImageUploaderProps {
  images: string[]; // プレビュー用のURL
  onImagesChange: (files: File[], previews: string[]) => void;
  onRemoveImage?: (index: number) => void;
  maxImages?: number;
  maxSizeMB?: number;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  images,
  onImagesChange,
  onRemoveImage,
  maxImages = 5,
  maxSizeMB = 10,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // メモリリーク防止: コンポーネントアンマウント時にオブジェクトURLを解放
  useEffect(() => {
    return () => {
      images.forEach(url => {
        if (url.startsWith('blob:')) {
          URL.revokeObjectURL(url);
        }
      });
    };
  }, []);

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

  const isImageFile = (file: File): boolean => {
    if (file.type.startsWith('image/')) return true;
    // HEIC/HEIF はブラウザによってMIMEタイプが空になる場合があるため拡張子でもチェック
    const extension = file.name.toLowerCase().split('.').pop();
    return extension === 'heic' || extension === 'heif';
  };

  const processFiles = (newFiles: File[]) => {
    // 画像のみフィルタリング
    const imageFiles = newFiles.filter(isImageFile);

    if (imageFiles.length === 0) {
      alert(ERROR_MESSAGES.INVALID_FILE_TYPE);
      return;
    }

    // 現在の枚数チェック
    if (images.length + imageFiles.length > maxImages) {
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

    // プレビュー生成
    const newPreviews = imageFiles.map(file => URL.createObjectURL(file));

    // 親コンポーネントに新しく追加されたファイルとそのプレビューのみを通知
    onImagesChange(imageFiles, newPreviews);
  };

  const handleRemove = (index: number) => {
    // オブジェクトURLを解放
    const urlToRevoke = images[index];
    if (urlToRevoke.startsWith('blob:')) {
      URL.revokeObjectURL(urlToRevoke);
    }
    onRemoveImage?.(index);
  };

  return (
    <div>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept="image/*,.heic,.heif"
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
      {images.length > 0 && (
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-5">
          {images.map((src, index) => (
            <div
              key={src}
              className="group relative aspect-square overflow-hidden rounded-lg border border-neutral-200 bg-neutral-100"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={src} alt={`Uploaded ${index + 1}`} className="h-full w-full object-cover" />
              {onRemoveImage && (
                <button
                  type="button"
                  onClick={() => handleRemove(index)}
                  className="absolute top-1 right-1 flex h-6 w-6 items-center justify-center rounded-full bg-black/60 text-white text-xs transition-colors hover:bg-danger"
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
