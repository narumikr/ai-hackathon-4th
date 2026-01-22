'use client';

import { Emoji } from '@/components/ui';
import { EMOJI_LABELS, FORM_LABELS, LABELS, SECTION_TITLES } from '@/constants';
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
          {SECTION_TITLES.SPOT_MEMORIES}
        </h3>
        <div className="space-y-8">
          {reflection.photos.map(photo => (
            <div
              key={photo.id}
              className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm"
            >
              <div className="flex flex-col gap-6 md:flex-row">
                <div className="w-full shrink-0 md:w-1/3">
                  <div className="flex aspect-video w-full items-center justify-center rounded-lg bg-neutral-200 text-neutral-400">
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
                    {SECTION_TITLES.MEMORY_SCENE(photo.id)}
                  </h4>
                  <p className="whitespace-pre-wrap text-neutral-700 leading-relaxed">
                    {photo.comment}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 全体的な感想 */}
      <section className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 font-bold text-neutral-900 text-xl">
          {FORM_LABELS.OVERALL_IMPRESSION_PLAIN}
        </h3>
        <p className="whitespace-pre-wrap text-neutral-700 leading-relaxed">
          {reflection.overallComment}
        </p>
      </section>
    </div>
  );
};
