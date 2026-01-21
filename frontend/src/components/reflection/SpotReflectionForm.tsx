'use client';

import { TextArea } from '@/components/ui';
import { BUTTON_LABELS, FORM_LABELS, HELP_TEXTS, PLACEHOLDERS, STATUS_LABELS } from '@/constants';
import type { PhotoData, ReflectionSpot } from '@/types/reflection';
import type React from 'react';
import { ImageUploader } from '../ui/ImageUploader';

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
  const handlePhotosChange = (newPhotos: PhotoData[]) => {
    // 新しい写真を追加
    const updatedPhotos = [...spot.photos, ...newPhotos];
    onUpdate(spot.id, { photos: updatedPhotos });
  };

  const handleRemovePhoto = (index: number) => {
    const updatedPhotos = spot.photos.filter((_, i) => i !== index);
    onUpdate(spot.id, { photos: updatedPhotos });
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
                {STATUS_LABELS.ADDED_SPOT}
              </span>
            )}
          </div>
          {spot.isAdded && <p className="mt-1 text-neutral-500 text-xs">{HELP_TEXTS.ADDED_SPOT}</p>}
        </div>
        {spot.isAdded && onRemove && (
          <button
            type="button"
            onClick={() => onRemove(spot.id)}
            className="text-danger text-sm hover:underline"
          >
            {BUTTON_LABELS.REMOVE}
          </button>
        )}
      </div>

      <div className="mb-6">
        <div className="mb-2 block font-semibold text-neutral-700 text-sm">
          {FORM_LABELS.PHOTOS}
        </div>
        <ImageUploader
          photos={spot.photos}
          onPhotosChange={handlePhotosChange}
          onRemovePhoto={handleRemovePhoto}
        />
      </div>

      <div>
        <div className="mb-2 block font-semibold text-neutral-700 text-sm">
          {FORM_LABELS.COMMENT}
        </div>
        <TextArea
          value={spot.comment}
          onChange={handleCommentChange}
          placeholder={PLACEHOLDERS.SPOT_COMMENT(spot.name)}
          rows={3}
          fullWidth
        />
      </div>
    </div>
  );
};
