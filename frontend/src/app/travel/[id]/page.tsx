'use client';

import { Container } from '@/components/layout';
import { Button, Emoji, Modal } from '@/components/ui';
import { BUTTON_LABELS, EMOJI_LABELS, LABELS, SECTION_TITLES } from '@/constants';
import { sampleGuide, sampleTravels } from '@/data';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';

export default function TravelGuidePage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;
  const travel = sampleTravels.find(t => t.id === id);
  const isCompleted = travel?.status === 'completed';

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  // reflectionGenerationStatus logic
  const reflectionStatus = travel?.reflectionGenerationStatus;

  const handleBack = () => {
    router.push('/travel');
  };

  const handleDeleteClick = () => {
    setIsDeleteModalOpen(true);
  };

  const handleDeleteConfirm = () => {
    setIsDeleteModalOpen(false);
    alert('削除しました（モック）');
    router.push('/travel');
  };

  const handleDeleteCancel = () => {
    setIsDeleteModalOpen(false);
  };

  const handleReflectionAction = () => {
    if (!reflectionStatus) {
      // Fallback or "Planning" state -> Create Reflection (as original "Travel Complete" logic)
      router.push(`/reflection/${id}`);
      return;
    }

    if (reflectionStatus === 'completed') {
      router.push(`/reflection/${id}/view`);
    } else if (reflectionStatus === 'not_started') {
      router.push(`/reflection/${id}`);
    }
    // 'processing' is disabled, so no action needed here strictly, but good to handle.
  };

  // Determine button props based on status
  let actionButtonLabel: string = BUTTON_LABELS.TRAVEL_COMPLETE;
  let isActionDisabled = false;

  if (reflectionStatus === 'completed') {
    actionButtonLabel = BUTTON_LABELS.VIEW_REFLECTION;
  } else if (reflectionStatus === 'processing') {
    actionButtonLabel = '生成中...';
    isActionDisabled = true;
  } else if (reflectionStatus === 'not_started') {
    actionButtonLabel = BUTTON_LABELS.CREATE_REFLECTION;
  }

  return (
    <div className="py-8">
      <Container variant="wide">
        {/* ヘッダー */}
        <div className="mb-8">
          <div className="mb-4 flex flex-col items-start justify-between gap-4 lg:flex-row lg:items-center">
            <div>
              <h1 className="mb-2 font-bold text-3xl text-neutral-900">{sampleGuide.title}</h1>
              <p className="text-lg text-neutral-600">{sampleGuide.destination}</p>
            </div>
            {!isCompleted && (
              <div className="flex gap-2">
                <Button variant="primary">{BUTTON_LABELS.TRAVEL_COMPLETE}</Button>
              </div>
            )}
          </div>
        </div>

        {/* 歴史年表 */}
        <section className="mb-12 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
          <h2 className="mb-6 font-bold text-2xl text-neutral-900">
            <Emoji symbol="📅" label={EMOJI_LABELS.CALENDAR} /> {SECTION_TITLES.TIMELINE}
          </h2>
          <div className="space-y-4">
            {sampleGuide.timeline.map((item, index) => (
              <div key={`timeline-${item.year}-${index}`} className="flex gap-4">
                <div className="w-24 flex-shrink-0 font-bold text-primary-700">
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

        {/* スポット詳細 */}
        <section className="mb-12">
          <h2 className="mb-6 font-bold text-2xl text-neutral-900">
            <Emoji symbol="📍" label={EMOJI_LABELS.PIN} /> {SECTION_TITLES.SPOT_DETAILS}
          </h2>
          <div className="space-y-6">
            {sampleGuide.spots.map((spot, index) => (
              <div
                key={spot.id}
                className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm"
              >
                <div className="mb-4">
                  <div className="mb-2 flex items-center gap-3">
                    <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-primary-400 font-bold text-primary-950 text-sm">
                      {index + 1}
                    </span>
                    <h3 className="font-bold text-neutral-900 text-xl">{spot.name}</h3>
                  </div>
                  <p className="text-neutral-600">{spot.description}</p>
                </div>

                <div className="mb-4">
                  <h4 className="mb-2 font-semibold text-neutral-700 text-sm">
                    <Emoji symbol="🏛️" label={EMOJI_LABELS.HISTORIC_BUILDING} />{' '}
                    {SECTION_TITLES.HISTORICAL_CONTEXT}
                  </h4>
                  <p className="text-neutral-700 leading-relaxed">{spot.historicalContext}</p>
                </div>

                <div>
                  <h4 className="mb-2 font-semibold text-neutral-700 text-sm">
                    <Emoji symbol="✅" label={EMOJI_LABELS.CHECKMARK} />{' '}
                    {SECTION_TITLES.CHECKPOINTS}
                  </h4>
                  <ul className="space-y-1">
                    {spot.checkpoints.map(checkpoint => (
                      <li key={checkpoint} className="text-neutral-700">
                        {checkpoint}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </section>

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
              <Button variant="ghost" onClick={handleDeleteCancel}>
                {BUTTON_LABELS.CANCEL}
              </Button>
              <Button variant="error" onClick={handleDeleteConfirm}>
                {BUTTON_LABELS.DELETE}
              </Button>
            </div>
          </div>
        </Modal>
      </Container>
    </div>
  );
}
