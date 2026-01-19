'use client';

import { Emoji } from '@/components/ui';
import { HELP_TEXTS, PLACEHOLDERS } from '@/constants';
import type React from 'react';
import { useRef, useState } from 'react';

interface ImageUploaderProps {
  images: string[]; // プレビュー用のURL
  onImagesChange: (files: File[], previews: string[]) => void;
  maxImages?: number;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  images,
  onImagesChange,
  maxImages = 5,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

    if (imageFiles.length === 0) return;

    // 現在の枚数チェック
    if (images.length + imageFiles.length > maxImages) {
      alert(`写真は最大${maxImages}枚までアップロードできます`);
      return;
    }

    // プレビュー生成
    const newPreviews = imageFiles.map(file => URL.createObjectURL(file));

    // 親コンポーネントに通知（本来は既存のファイルと合わせる必要があるが、
    // ここでは簡易的に追加分だけ処理するか、親でマージするかを決める。
    // 今回は親で管理しているリストに追加する形を想定して、Fileオブジェクトを渡す）

    // 注意: ここでは既存のimagesはURL(string)のみ受け取っているため、
    // 完全なFileオブジェクトのリストを維持するには親側での管理が重要。
    // このコンポーネントは「新しく追加されたファイル」を通知する。

    onImagesChange(imageFiles, newPreviews);
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
      <div
        className={`mb-4 flex h-48 w-full cursor-pointer items-center justify-center rounded-lg border-2 border-dashed transition-colors ${isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-neutral-300 bg-neutral-50 hover:border-primary-400'
          }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        aria-label={PLACEHOLDERS.UPLOAD_INSTRUCTION}
      >
        <div className="text-center">
          <div className="mb-2 text-4xl">
            <Emoji symbol="📤" label="アップロード" />
          </div>
          <p className="mb-1 font-medium text-neutral-700">{PLACEHOLDERS.UPLOAD_INSTRUCTION}</p>
          <p className="text-neutral-500 text-xs">{HELP_TEXTS.UPLOAD_FORMAT}</p>
        </div>
      </div>

      {/* プレビューエリア */}
      {images.length > 0 && (
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-5">
          {images.map((src, index) => (
            <div
              key={`${src}-${index}`}
              className="group relative aspect-square overflow-hidden rounded-lg bg-neutral-100 border border-neutral-200"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={src} alt={`Uploaded ${index + 1}`} className="h-full w-full object-cover" />
              <button
                type="button"
                // 削除機能は別途実装が必要 (Props拡張が必要)
                // onClick={() => handleRemove(index)}
                className="absolute top-1 right-1 flex h-5 w-5 items-center justify-center rounded-full bg-black/50 text-white text-xs opacity-0 transition-opacity group-hover:opacity-100"
                aria-label="削除"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
