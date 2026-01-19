'use client';

import { Emoji } from '@/components/ui';
import { EMOJI_LABELS, LABELS } from '@/constants';
import type { ReflectionContent } from '@/data/sampleReflections';
import type { SampleTravel } from '@/data/sampleTravels';
import type React from 'react';

interface ReflectionViewerProps {
  travel: SampleTravel;
  reflection: ReflectionContent;
}

export const ReflectionViewer: React.FC<ReflectionViewerProps> = ({ travel, reflection }) => {
  return (
    <div className="space-y-8">
      {/* 旅行概要 */}
      <div className="rounded-lg border border-primary-200 bg-primary-50 p-6">
        <h2 className="mb-2 font-bold text-2xl text-neutral-900">{travel.title}</h2>
        <div className="flex gap-6 text-neutral-700">
          <span>
            <Emoji symbol="📍" label={EMOJI_LABELS.PIN} /> {travel.destination}
          </span>
          <span>
            <Emoji symbol="✅" label={EMOJI_LABELS.CHECKMARK} /> {LABELS.COMPLETED_DATE}{' '}
            {travel.completedAt}
          </span>
        </div>
      </div>

      {/* スポットごとの振り返り */}
      <section>
        <h3 className="mb-6 border-b pb-2 font-bold text-neutral-900 text-xl">
          観光スポットの思い出
        </h3>
        <div className="space-y-8">
          {reflection.photos.map(photo => {
            // Note: In a real app, we would link photos to spot details more explicitly.
            // Here, `photo` in sample data has `id` and `comment` but lacks spot name directly.
            // However, the new data structure `ReflectionSpot` links them better.
            // For this viewer which uses `ReflectionContent` (legacy sample data structure),
            // we might need to adjust or map it.
            // But since we are building a NEW viewer, we should probably stick to the NEW types if possible,
            // or adapt the sample data.
            // Let's assume we display what we have in `ReflectionContent` for now,
            // which is a list of photos with comments.
            // Wait, the design says "Spot-based photo upload".
            // `ReflectionContent` in `sampleReflections.ts` has `photos: {id, comment}[]`.
            // It doesn't explicitly group by spot.
            // BUT, the new `ReflectionSpot` structure does.
            // If we are viewing a *newly created* reflection, we should use the new structure.
            // If we are viewing *legacy sample* reflection, we use the old structure.
            // To unify, I will assume we are viewing data that conforms to the *concept* of the design.
            // Let's render the list of photos/comments as they are in the sample for now,
            // or better, try to simulate the spot-based view if data allows.
            // The sample data just has a flat list of photos.
            // Let's just render them nicely.

            return (
              <div
                key={photo.id}
                className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm"
              >
                <div className="flex flex-col gap-6 md:flex-row">
                  <div className="w-full flex-shrink-0 md:w-1/3">
                    <div className="flex aspect-video w-full items-center justify-center rounded-lg bg-neutral-200 text-neutral-400">
                      {/* Placeholder for actual image since we don't have real URLs in sample */}
                      <div className="text-center">
                        <span className="mb-2 block text-4xl">
                          <Emoji symbol="🖼️" label={EMOJI_LABELS.PICTURE} />
                        </span>
                        <span className="text-sm">Photo {photo.id}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h4 className="mb-2 font-bold text-lg text-neutral-800">
                      {/* In real data, this would be the spot name */}
                      思い出の場面 #{photo.id}
                    </h4>
                    <p className="whitespace-pre-wrap text-neutral-700 leading-relaxed">
                      {photo.comment}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 全体的な感想 */}
      <section className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 font-bold text-neutral-900 text-xl">全体的な感想</h3>
        <p className="whitespace-pre-wrap text-neutral-700 leading-relaxed">
          {reflection.overallComment}
        </p>
      </section>
    </div>
  );
};
