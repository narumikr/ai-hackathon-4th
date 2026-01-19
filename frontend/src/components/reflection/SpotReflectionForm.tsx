'use client';

import { TextArea } from '@/components/ui';
import type { ReflectionSpot } from '@/types/reflection';
import type React from 'react';
import { ImageUploader } from '../upload/ImageUploader';

interface SpotReflectionFormProps {
  spot: ReflectionSpot;
  onUpdate: (id: string, updates: Partial<ReflectionSpot>) => void;
  onRemove?: (id: string) => void;
}

export const SpotReflectionForm: React.FC<SpotReflectionFormProps> = ({
  spot,
  onUpdate,
  onRemove,
}) => {
  const handleImagesChange = (files: File[], previews: string[]) => {
    // 新しい画像を追加
    const newPhotos = [...spot.photos, ...files];
    const newPreviews = [...spot.photoPreviews, ...previews];
    onUpdate(spot.id, { photos: newPhotos, photoPreviews: newPreviews });
  };

  const handleCommentChange = (value: string) => {
    onUpdate(spot.id, { comment: value });
  };

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-lg text-neutral-900">{spot.name}</h3>
            {spot.isAdded && (
              <span className="rounded-full bg-primary-100 px-2 py-0.5 font-medium text-primary-700 text-xs">
                追加スポット
              </span>
            )}
          </div>
          {spot.isAdded && (
            <p className="mt-1 text-neutral-500 text-xs">振り返りで追加したスポットです</p>
          )}
        </div>
        {spot.isAdded && onRemove && (
          <button
            type="button"
            onClick={() => onRemove(spot.id)}
            className="text-danger text-sm hover:underline"
          >
            削除
          </button>
        )}
      </div>

      <div className="mb-6">
        <div className="mb-2 block font-semibold text-neutral-700 text-sm">写真</div>
        <ImageUploader images={spot.photoPreviews} onImagesChange={handleImagesChange} />
      </div>

      <div>
        <div className="mb-2 block font-semibold text-neutral-700 text-sm">感想</div>
        <TextArea
          value={spot.comment}
          onChange={handleCommentChange}
          placeholder={`${spot.name}での思い出や感想を書いてみましょう...`}
          rows={3}
          fullWidth
        />
      </div>
    </div>
  );
};
