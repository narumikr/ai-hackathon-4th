'use client';

import { Container } from '@/components/layout';
import { SpotAdder } from '@/components/reflection/SpotAdder';
import { SpotReflectionForm } from '@/components/reflection/SpotReflectionForm';
import { Button, TextArea } from '@/components/ui';
import {
  BUTTON_LABELS,
  FORM_LABELS,
  HINTS,
  LABELS,
  MESSAGES,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  PLACEHOLDERS,
  SECTION_TITLES,
} from '@/constants';
import { createApiClientFromEnv, toApiError } from '@/lib/api';
import type { TravelPlanResponse } from '@/types';
import type { ReflectionSpot } from '@/types/reflection';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function ReflectionDetailPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;

  const [travel, setTravel] = useState<TravelPlanResponse | null>(null);
  const [spots, setSpots] = useState<ReflectionSpot[]>([]);
  const [overallComment, setOverallComment] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTravelPlan = async () => {
      if (!id) return;

      setIsLoading(true);
      setError(null);

      try {
        const apiClient = createApiClientFromEnv();
        const response = await apiClient.getTravelPlan({ planId: id });
        setTravel(response);

        // 既に振り返りがある場合は閲覧ページにリダイレクト
        if (response.reflection) {
          router.push(`/reflection/${id}/view`);
          return;
        }

        // スポットリストを初期化
        const initialSpots: ReflectionSpot[] = response.spots.map(s => ({
          id: s.id || `spot-${s.name}`,
          name: s.name,
          photos: [],
          comment: '',
          isAdded: false,
        }));
        setSpots(initialSpots);
      } catch (err) {
        const apiError = toApiError(err);
        setError(apiError.message || MESSAGES.ERROR);
        console.error('Failed to fetch travel plan:', apiError);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTravelPlan();
  }, [id, router]);

  if (!travel && !isLoading) {
    return (
      <div className="py-8">
        <Container>
          <div className="mb-6 rounded-lg border border-danger-200 bg-danger-50 p-4 text-danger-800">
            {error || MESSAGES.TRAVEL_NOT_FOUND}
          </div>
          <Link href="/reflection">
            <Button>{BUTTON_LABELS.BACK}</Button>
          </Link>
        </Container>
      </div>
    );
  }

  if (isLoading) {
    return <div className="py-20 text-center">{MESSAGES.LOADING}</div>;
  }

  const handleSpotUpdate = (spotId: string, updates: Partial<ReflectionSpot>) => {
    setSpots(prev => prev.map(s => (s.id === spotId ? { ...s, ...updates } : s)));
  };

  const handleAddSpot = (name: string) => {
    const newSpot: ReflectionSpot = {
      id: `added-${Date.now()}`,
      name,
      photos: [],
      comment: '',
      isAdded: true,
    };
    setSpots(prev => [...prev, newSpot]);
  };

  const handleRemoveSpot = (spotId: string) => {
    setSpots(prev => prev.filter(s => s.id !== spotId));
  };

  const handleSubmit = () => {
    // TODO: 実際の実装ではここでAPIリクエストを送信し、
    // 成功時に適切なUIフィードバック（トースト表示や画面遷移など）を行う
    alert(MESSAGES.REFLECTION_GENERATED);
  };

  return (
    <div className="py-8">
      <Container>
        <div className="mx-auto max-w-4xl">
          <div className="mb-8 flex items-start justify-between">
            <div>
              <h1 className="mb-2 font-bold text-3xl text-neutral-900">
                {PAGE_TITLES.REFLECTION_CREATE}
              </h1>
              <p className="text-neutral-600">{PAGE_DESCRIPTIONS.REFLECTION_CREATE}</p>
            </div>
            <Link href="/reflection">
              <Button variant="ghost">{BUTTON_LABELS.BACK}</Button>
            </Link>
          </div>

          {/* 旅行情報 */}
          {travel && (
            <div className="mb-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
              <h2 className="mb-1 font-semibold text-lg text-neutral-900">{travel.title}</h2>
              <div className="flex gap-4 text-neutral-600 text-sm">
                <span>
                  {LABELS.COMPLETED_DATE} {new Date(travel.updatedAt).toLocaleDateString('ja-JP')}
                </span>
                <span>{travel.destination}</span>
              </div>
            </div>
          )}

          {/* スポットごとの振り返り */}
          <div className="mb-8 space-y-6">
            <h2 className="border-b pb-2 font-bold text-neutral-900 text-xl">
              {SECTION_TITLES.SPOT_REFLECTIONS}
            </h2>
            {spots.map(spot => (
              <SpotReflectionForm
                key={spot.id}
                spot={spot}
                onUpdate={handleSpotUpdate}
                onRemove={spot.isAdded ? handleRemoveSpot : undefined}
              />
            ))}
          </div>

          {/* スポット追加 */}
          <div className="mb-8">
            <SpotAdder onAdd={handleAddSpot} />
          </div>

          {/* 全体的な感想 */}
          <section className="mb-8 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 font-bold text-neutral-900 text-xl">
              {FORM_LABELS.OVERALL_IMPRESSION}
            </h2>
            <TextArea
              value={overallComment}
              onChange={setOverallComment}
              placeholder={PLACEHOLDERS.OVERALL_COMMENT}
              rows={6}
              fullWidth
              maxLength={1000}
              showCount
            />
          </section>

          {/* アクションボタン */}
          <div className="flex flex-col gap-4 sm:flex-row">
            <Link href="/reflection" className="flex-1">
              <Button variant="ghost" size="lg" fullWidth>
                {BUTTON_LABELS.CANCEL}
              </Button>
            </Link>
            <Button variant="primary" size="lg" className="flex-1" onClick={handleSubmit}>
              {BUTTON_LABELS.GENERATE_REFLECTION}
            </Button>
          </div>

          {/* 注意事項 */}
          <div className="mt-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
            <h3 className="mb-2 font-semibold text-primary-900 text-sm">{LABELS.HINT_TITLE}</h3>
            <ul className="space-y-1 text-primary-800 text-sm">
              {HINTS.REFLECTION_CREATE.map(hint => (
                <li key={hint}>• {hint}</li>
              ))}
            </ul>
          </div>
        </div>
      </Container>
    </div>
  );
}
