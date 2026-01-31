'use client';

import { Container } from '@/components/layout';
import { Button, Emoji, Modal } from '@/components/ui';
import { BUTTON_LABELS, EMOJI_LABELS, LABELS, MESSAGES, SECTION_TITLES } from '@/constants';
import { createApiClientFromEnv, toApiError } from '@/lib/api';
import type { TravelPlanResponse } from '@/types';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function TravelGuidePage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;

  const [travel, setTravel] = useState<TravelPlanResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);

  useEffect(() => {
    const fetchTravelPlan = async () => {
      if (!id) return;

      setIsLoading(true);
      setError(null);

      try {
        const apiClient = createApiClientFromEnv();
        const response = await apiClient.getTravelPlan({ planId: id });
        setTravel(response);
      } catch (err) {
        const apiError = toApiError(err);
        setError(apiError.message || MESSAGES.ERROR);
        console.error('Failed to fetch travel plan:', apiError);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTravelPlan();
  }, [id]);

  const isCompleted = travel?.status === 'completed';

  // reflectionGenerationStatus logic
  const reflectionStatus = travel?.reflectionGenerationStatus;

  const handleBack = () => {
    router.push('/travel');
  };

  const handleDeleteClick = () => {
    setIsDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!id) return;

    setIsDeleting(true);
    try {
      const apiClient = createApiClientFromEnv();
      await apiClient.deleteTravelPlan({ planId: id });
      setIsDeleteModalOpen(false);
      router.push('/travel');
    } catch (err) {
      const apiError = toApiError(err);
      alert(`削除に失敗しました: ${apiError.message}`);
      console.error('Failed to delete travel plan:', apiError);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setIsDeleteModalOpen(false);
  };

  const handleComplete = async () => {
    if (!id) return;

    setIsCompleting(true);
    try {
      const apiClient = createApiClientFromEnv();
      await apiClient.updateTravelPlan({
        planId: id,
        request: {
          status: 'completed',
        },
      });
      router.push('/travel');
    } catch (err) {
      const apiError = toApiError(err);
      alert(`完了処理に失敗しました: ${apiError.message}`);
      console.error('Failed to complete travel plan:', apiError);
    } finally {
      setIsCompleting(false);
    }
  };

  const handleReflectionAction = () => {
    if (!reflectionStatus) {
      // Fallback or "Planning" state -> Create Reflection (as original "Travel Complete" logic)
      router.push(`/reflection/${id}`);
      return;
    }

    if (reflectionStatus === 'succeeded') {
      router.push(`/reflection/${id}/view`);
    } else if (reflectionStatus === 'not_started') {
      router.push(`/reflection/${id}`);
    }
  };

  // Determine button props based on status
  let actionButtonLabel: string = BUTTON_LABELS.TRAVEL_COMPLETE;
  let isActionDisabled = false;

  if (reflectionStatus === 'succeeded') {
    actionButtonLabel = BUTTON_LABELS.VIEW_REFLECTION;
  } else if (reflectionStatus === 'processing') {
    actionButtonLabel = MESSAGES.GENERATING;
    isActionDisabled = true;
  } else if (reflectionStatus === 'not_started') {
    actionButtonLabel = BUTTON_LABELS.CREATE_REFLECTION;
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="py-8">
        <Container>
          <div className="py-16 text-center">
            <p className="text-neutral-600">{MESSAGES.LOADING}</p>
          </div>
        </Container>
      </div>
    );
  }

  if (error || !travel) {
    return (
      <div className="py-8">
        <Container>
          <div className="mb-6 rounded-lg border border-danger-200 bg-danger-50 p-4 text-danger-800">
            {error || MESSAGES.TRAVEL_NOT_FOUND}
          </div>
          <Button onClick={handleBack}>{BUTTON_LABELS.BACK}</Button>
        </Container>
      </div>
    );
  }

  const hasGuide = travel.guide && travel.guideGenerationStatus === 'succeeded';

  return (
    <div className="py-8">
      <Container variant="wide">
        {/* ヘッダー */}
        <div className="mb-8">
          <div className="mb-4 flex flex-col items-start justify-between gap-4 lg:flex-row lg:items-center">
            <div>
              <h1 className="mb-2 font-bold text-3xl text-neutral-900">{travel.title}</h1>
              <p className="text-lg text-neutral-600">{travel.destination}</p>
              <p className="mt-2 text-neutral-500 text-sm">
                作成日: {formatDate(travel.createdAt)}
              </p>
            </div>
            {!isCompleted && (
              <div className="flex gap-2">
                <Button variant="primary" onClick={handleComplete} disabled={isCompleting}>
                  {isCompleting ? MESSAGES.LOADING : BUTTON_LABELS.TRAVEL_COMPLETE}
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* 観光スポット一覧 */}
        <section className="mb-12 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
          <h2 className="mb-6 font-bold text-2xl text-neutral-900">
            <Emoji symbol="📍" label={EMOJI_LABELS.PIN} /> {SECTION_TITLES.TOURIST_SPOTS}
          </h2>
          {travel.spots.length === 0 ? (
            <p className="text-neutral-600">{MESSAGES.NO_SPOTS_REGISTERED}</p>
          ) : (
            <div className="space-y-4">
              {travel.spots.map((spot, index) => (
                <div
                  key={spot.id || index}
                  className="border-neutral-200 border-b pb-4 last:border-b-0"
                >
                  <div className="flex items-center gap-3">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-400 font-bold text-primary-950 text-sm">
                      {index + 1}
                    </span>
                    <div>
                      <h3 className="font-semibold text-neutral-900">{spot.name}</h3>
                      {spot.description && (
                        <p className="text-neutral-600 text-sm">{spot.description}</p>
                      )}
                      {spot.userNotes && (
                        <p className="mt-1 text-neutral-500 text-sm">
                          {LABELS.MEMO_PREFIX} {spot.userNotes}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* 旅行ガイド */}
        {hasGuide && travel.guide && (
          <>
            {/* 歴史年表 */}
            {travel.guide.timeline && travel.guide.timeline.length > 0 && (
              <section className="mb-12 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
                <h2 className="mb-6 font-bold text-2xl text-neutral-900">
                  <Emoji symbol="📅" label={EMOJI_LABELS.CALENDAR} /> {SECTION_TITLES.TIMELINE}
                </h2>
                <div className="space-y-4">
                  {travel.guide.timeline.map((item, index) => (
                    <div key={`timeline-${item.year}-${index}`} className="flex gap-4">
                      <div className="w-24 shrink-0 font-bold text-primary-700">
                        {item.year}
                        {LABELS.YEAR_SUFFIX}
                      </div>
                      <div className="flex-1">
                        <p className="text-neutral-700">{item.event}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* スポット詳細 */}
            {travel.guide.spotDetails && travel.guide.spotDetails.length > 0 && (
              <section className="mb-12">
                <h2 className="mb-6 font-bold text-2xl text-neutral-900">
                  <Emoji symbol="📍" label={EMOJI_LABELS.PIN} /> {SECTION_TITLES.SPOT_DETAILS}
                </h2>
                <div className="space-y-6">
                  {travel.guide.spotDetails.map((spot, index) => (
                    <div
                      key={`${spot.spotName}-${index}`}
                      className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm"
                    >
                      <div className="mb-4">
                        <div className="mb-2 flex items-center gap-3">
                          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-400 font-bold text-primary-950 text-sm">
                            {index + 1}
                          </span>
                          <h3 className="font-bold text-neutral-900 text-xl">{spot.spotName}</h3>
                        </div>
                        {spot.historicalBackground && (
                          <p className="text-neutral-600">{spot.historicalBackground}</p>
                        )}
                      </div>

                      {spot.historicalSignificance && (
                        <div className="mb-4">
                          <h4 className="mb-2 font-semibold text-neutral-700 text-sm">
                            <Emoji symbol="🏛️" label={EMOJI_LABELS.HISTORIC_BUILDING} />{' '}
                            {SECTION_TITLES.HISTORICAL_CONTEXT}
                          </h4>
                          <p className="text-neutral-700 leading-relaxed">
                            {spot.historicalSignificance}
                          </p>
                        </div>
                      )}

                      {spot.highlights && spot.highlights.length > 0 && (
                        <div>
                          <h4 className="mb-2 font-semibold text-neutral-700 text-sm">
                            <Emoji symbol="✅" label={EMOJI_LABELS.CHECKMARK} />{' '}
                            {SECTION_TITLES.HIGHLIGHTS}
                          </h4>
                          <ul className="space-y-1">
                            {spot.highlights.map((highlight: string, idx: number) => (
                              <li
                                key={`${spot.spotName}-highlight-${idx}`}
                                className="text-neutral-700"
                              >
                                {highlight}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}

        {/* ガイド未生成の場合 */}
        {!hasGuide && (
          <section className="mb-12 rounded-lg border border-primary-200 bg-primary-50 p-6">
            <p className="text-center text-primary-900">
              {MESSAGES.GUIDE_NOT_GENERATED}
              {travel.guideGenerationStatus === 'processing' && MESSAGES.GUIDE_GENERATING}
              {travel.guideGenerationStatus === 'failed' && MESSAGES.GUIDE_GENERATION_FAILED}
            </p>
          </section>
        )}

        {/* アクション */}
        <div className="flex flex-col justify-center gap-4 sm:flex-row">
          <Button variant="ghost" size="lg" onClick={handleBack}>
            {BUTTON_LABELS.BACK}
          </Button>
          {!isCompleted ? (
            // Case: In progress (Planning, etc) - Show original Edit button
            <Link href={`/travel/${id}/edit`}>
              <Button variant="primary" size="lg">
                {BUTTON_LABELS.EDIT}
              </Button>
            </Link>
          ) : (
            // Case: Completed travel - Show Reflection Logic Button
            <Button
              variant="primary"
              size="lg"
              onClick={handleReflectionAction}
              disabled={isActionDisabled}
            >
              {actionButtonLabel}
            </Button>
          )}

          {/* Delete Button (Always shown or only when editing? Plan said "next to edit/generate". Assuming always accessible for detail view) */}
          <Button variant="error" size="lg" onClick={handleDeleteClick}>
            {BUTTON_LABELS.DELETE}
          </Button>
        </div>

        {/* Delete Confirmation Modal */}
        <Modal isOpen={isDeleteModalOpen} onClose={handleDeleteCancel} title="確認" size="sm">
          <div className="space-y-6">
            <p className="text-neutral-600">この旅行計画を削除してもよろしいですか？</p>
            <div className="flex justify-end gap-3">
              <Button variant="ghost" onClick={handleDeleteCancel} disabled={isDeleting}>
                {BUTTON_LABELS.CANCEL}
              </Button>
              <Button variant="error" onClick={handleDeleteConfirm} disabled={isDeleting}>
                {isDeleting ? MESSAGES.LOADING : BUTTON_LABELS.DELETE}
              </Button>
            </div>
          </div>
        </Modal>
      </Container>
    </div>
  );
}
