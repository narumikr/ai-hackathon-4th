'use client';

import { ErrorDialog } from '@/components/features/common';
import { SpotAdder, SpotReflectionForm } from '@/components/features/reflection';
import { Container } from '@/components/layout';
import { Button, Dialog, Icon, TextArea, Tooltip } from '@/components/ui';
import {
  BUTTON_LABELS,
  EMOJI_LABELS,
  ERROR_DIALOG_MESSAGES,
  FORM_LABELS,
  HINTS,
  LABELS,
  MESSAGES,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  PLACEHOLDERS,
  SECTION_TITLES,
  TOOLTIP_MESSAGES,
} from '@/constants';
import { createApiClientFromEnv } from '@/lib/api';
import {
  clearReflectionSubmissionPending,
  markReflectionSubmissionPending,
} from '@/lib/reflectionSubmissionState';
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
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPhotoError, setShowPhotoError] = useState(false);

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
      } catch (_err) {
        setError(ERROR_DIALOG_MESSAGES.REFLECTION_TRAVEL_FETCH_FAILED);
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
          <Link href="/reflection">
            <Button>{BUTTON_LABELS.BACK}</Button>
          </Link>
        </Container>
        <ErrorDialog
          isOpen={!!error}
          onClose={() => setError(null)}
          title={MESSAGES.ERROR}
          message={error || MESSAGES.TRAVEL_NOT_FOUND}
        />
      </div>
    );
  }

  if (isLoading) {
    return <div className="py-20 text-center">{MESSAGES.LOADING}</div>;
  }

  const handleSpotUpdate = (spotId: string, updates: Partial<ReflectionSpot>) => {
    // ローカル状態を更新
    setSpots(prev => prev.map(s => (s.id === spotId ? { ...s, ...updates } : s)));
    // 写真が追加された場合、エラーを解除
    if (updates.photos && updates.photos.length > 0 && showPhotoError) {
      setShowPhotoError(false);
    }
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

  const handleSubmit = async () => {
    if (!travel || !id) return;

    // 写真が1枚以上アップロードされているかチェック
    const hasPhotos = spots.some(spot => spot.photos.length > 0);
    if (!hasPhotos) {
      setShowPhotoError(true);
      return;
    }
    setShowPhotoError(false);

    setIsSubmitting(true);

    try {
      const apiClient = createApiClientFromEnv();

      markReflectionSubmissionPending(id);
      void (async () => {
        try {
          // 1. 各スポットの写真をアップロード
          for (const spot of spots) {
            const files = spot.photos
              .filter(photo => photo.file !== undefined)
              .map(photo => photo.file as File);

            if (files.length > 0) {
              await apiClient.uploadSpotReflection({
                planId: id,
                spotId: spot.id,
                spotNote: spot.comment,
                files,
              });
            }
          }

          // 2. 振り返り生成APIを呼び出す
          await apiClient.createReflection({
            request: {
              planId: id,
              userNotes: overallComment || undefined,
            },
          });
        } catch (err) {
          console.error('Failed to submit reflection in background', err);
        } finally {
          clearReflectionSubmissionPending(id);
        }
      })();

      // 3. 処理を待たずに振り返り閲覧ページにリダイレクト
      router.push(`/reflection/${id}/view`);
    } catch (_err) {
      setIsSubmitting(false);
      setError(ERROR_DIALOG_MESSAGES.REFLECTION_CREATE_FAILED);
    }
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
            <h2 className="mb-4 flex items-center gap-2 font-bold text-neutral-900 text-xl">
              <Icon name="note" size="md" label={EMOJI_LABELS.NOTE} />
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
              <Button variant="ghost" size="lg" fullWidth disabled={isSubmitting}>
                {BUTTON_LABELS.CANCEL}
              </Button>
            </Link>
            <Tooltip
              content={TOOLTIP_MESSAGES.PHOTO_REQUIRED}
              isOpen={showPhotoError}
              position="top"
            >
              <Button
                variant="primary"
                size="lg"
                className="flex-1"
                onClick={handleSubmit}
                disabled={isSubmitting}
              >
                {BUTTON_LABELS.GENERATE_REFLECTION}
              </Button>
            </Tooltip>
          </div>

          {/* 処理中ダイアログ */}
          <Dialog
            isOpen={isSubmitting}
            title={MESSAGES.PROCESSING}
            message={MESSAGES.GENERATING_REFLECTION}
            showSpinner
            closable={false}
          />

          {/* エラーダイアログ */}
          <ErrorDialog
            isOpen={!!error}
            onClose={() => setError(null)}
            title={MESSAGES.ERROR}
            message={error || ''}
          />

          {/* 注意事項 */}
          <div className="mt-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
            <h3 className="mb-2 flex items-center gap-1 font-semibold text-primary-900 text-sm">
              <Icon name="hint" size="sm" label={EMOJI_LABELS.HINT} />
              {LABELS.HINT_TITLE}
            </h3>
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
