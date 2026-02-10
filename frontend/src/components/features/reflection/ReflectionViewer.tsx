'use client';

import { Icon } from '@/components/ui';
import { DATE_LABELS, EMOJI_LABELS, FORM_LABELS, SECTION_TITLES } from '@/constants';
import { parseSourceFromMultilineText } from '@/lib/sourceUtil';
import type {
  ReflectionPamphletResponse,
  ReflectionPhotoResponse,
  TravelPlanResponse,
} from '@/types';
import Image from 'next/image';
import type React from 'react';
import { useMemo } from 'react';

interface ReflectionViewerProps {
  travel: TravelPlanResponse;
  pamphlet: ReflectionPamphletResponse;
}

export const ReflectionViewer: React.FC<ReflectionViewerProps> = ({ travel, pamphlet }) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  // スポット名からスポットIDを取得するマップを作成
  const spotNameToId = useMemo(() => {
    const map = new Map<string, string>();
    for (const spot of travel.spots) {
      if (spot.id) {
        map.set(spot.name, spot.id);
      }
    }
    return map;
  }, [travel.spots]);

  // スポットIDごとに写真をグループ化
  const photosBySpotId = useMemo(() => {
    const map = new Map<string, ReflectionPhotoResponse[]>();
    if (travel.reflection?.photos) {
      for (const photo of travel.reflection.photos) {
        const existing = map.get(photo.spotId) || [];
        existing.push(photo);
        map.set(photo.spotId, existing);
      }
    }
    return map;
  }, [travel.reflection?.photos]);

  // スポット名から写真を取得
  const getPhotosForSpot = (spotName: string): ReflectionPhotoResponse[] => {
    const spotId = spotNameToId.get(spotName);
    if (!spotId) return [];
    return photosBySpotId.get(spotId) || [];
  };

  return (
    <div className="space-y-8">
      {/* 旅行概要 */}
      <div className="rounded-lg border border-primary-200 bg-primary-50 p-6">
        <h2 className="mb-2 font-bold text-2xl text-neutral-900">{travel.title}</h2>
        <div className="flex gap-6 text-neutral-700">
          <span className="flex items-center gap-1">
            <Icon name="pin" size="sm" label={EMOJI_LABELS.PIN} /> {travel.destination}
          </span>
          <span className="flex items-center gap-1">
            <Icon name="calendar" size="sm" label={EMOJI_LABELS.CALENDAR} />{' '}
            {DATE_LABELS.CREATED_DATE} {formatDate(travel.createdAt)}
          </span>
        </div>
      </div>

      {/* 旅行サマリー */}
      <section className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 font-bold text-neutral-900 text-xl">
          {FORM_LABELS.OVERALL_IMPRESSION_PLAIN}
        </h3>
        {(() => {
          const parsed = parseSourceFromMultilineText(pamphlet.travelSummary || '');
          return (
            <div>
              <p className="whitespace-pre-wrap text-neutral-700 leading-relaxed">
                {parsed.content}
              </p>
              {parsed.source.url && (
                <p className="mt-2 text-sm">
                  <span className="mr-1 text-neutral-500">出典:</span>
                  <a
                    href={parsed.source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 underline hover:text-primary-700"
                  >
                    {parsed.source.label}
                  </a>
                </p>
              )}
            </div>
          );
        })()}
      </section>

      {/* スポットごとの振り返り */}
      <section>
        <h3 className="mb-6 border-b pb-2 font-bold text-neutral-900 text-xl">
          {SECTION_TITLES.SPOT_MEMORIES}
        </h3>
        <div className="space-y-8">
          {pamphlet.spotReflections.map((spotReflection, index) => {
            const photos = getPhotosForSpot(spotReflection.spotName);
            return (
              <div
                key={`${spotReflection.spotName}-${index}`}
                className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm"
              >
                <h4 className="mb-4 flex items-center gap-1 font-bold text-lg text-neutral-800">
                  <Icon name="pin" size="md" label={EMOJI_LABELS.PIN} /> {spotReflection.spotName}
                </h4>

                {/* 写真ギャラリー */}
                {photos.length > 0 && (
                  <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-3">
                    {photos.map(photo => (
                      <div
                        key={photo.id}
                        className="relative aspect-square overflow-hidden rounded-lg"
                      >
                        <Image
                          src={photo.url}
                          alt={photo.userDescription || spotReflection.spotName}
                          fill
                          className="object-cover"
                          sizes="(max-width: 768px) 50vw, 33vw"
                        />
                      </div>
                    ))}
                  </div>
                )}

                {(() => {
                  const parsed = parseSourceFromMultilineText(spotReflection.reflection || '');
                  return (
                    <div>
                      <p className="whitespace-pre-wrap text-neutral-700 leading-relaxed">
                        {parsed.content}
                      </p>
                      {parsed.source.url && (
                        <p className="mt-2 text-sm">
                          <span className="mr-1 text-neutral-500">出典:</span>
                          <a
                            href={parsed.source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary-600 underline hover:text-primary-700"
                          >
                            {parsed.source.label}
                          </a>
                        </p>
                      )}
                    </div>
                  );
                })()}
              </div>
            );
          })}
        </div>
      </section>

      {/* 次の旅行の提案 */}
      {pamphlet.nextTripSuggestions && pamphlet.nextTripSuggestions.length > 0 && (
        <section className="rounded-lg border border-primary-200 bg-primary-50 p-6 shadow-sm">
          <h3 className="mb-4 font-bold text-neutral-900 text-xl">
            {SECTION_TITLES.NEXT_TRIP_SUGGESTIONS}
          </h3>
          <ul className="space-y-2">
            {pamphlet.nextTripSuggestions.map(suggestion => {
              const parsed = parseSourceFromMultilineText(suggestion || '');
              return (
                <li key={suggestion} className="text-neutral-700">
                  • {parsed.content}
                  {parsed.source.url && (
                    <span className="ml-2 text-sm">
                      <a
                        href={parsed.source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 underline hover:text-primary-700"
                      >
                        {parsed.source.label}
                      </a>
                    </span>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      )}
    </div>
  );
};
