'use client';

import { TextArea } from '@/components/ui';
import { BUTTON_LABELS, FORM_LABELS, HELP_TEXTS, PLACEHOLDERS, STATUS_LABELS } from '@/constants';
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
        <ImageUploader images={spot.photoPreviews} onImagesChange={handleImagesChange} />
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
