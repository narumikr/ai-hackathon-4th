'use client';

import { GenerationStatusView } from '@/components/features/common';
import { ReflectionViewer } from '@/components/features/reflection';
import { Container } from '@/components/layout';
import { Button } from '@/components/ui';
import { BUTTON_LABELS, MESSAGES, PAGE_TITLES, STATUS_LABELS } from '@/constants';
import { createApiClientFromEnv, toApiError } from '@/lib/api';
import type { TravelPlanResponse } from '@/types';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';

export default function ReflectionViewPage() {
  const params = useParams();
  const id = params?.id as string;

  const [travel, setTravel] = useState<TravelPlanResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTravelPlan = useCallback(
    async (isRefresh = false) => {
      if (!id) return;

      if (isRefresh) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      setError(null);

      try {
        const apiClient = createApiClientFromEnv();
        const response = await apiClient.getTravelPlan({ planId: id });
        setTravel(response);

        // 振り返りがまだ作成されていない場合（processing以外）
        if (!response.pamphlet && response.reflectionGenerationStatus !== 'processing') {
          setError(MESSAGES.REFLECTION_NOT_FOUND);
        }
      } catch (err) {
        const apiError = toApiError(err);
        setError(apiError.message || MESSAGES.ERROR);
        console.error('Failed to fetch travel plan:', apiError);
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    },
    [id]
  );

  useEffect(() => {
    fetchTravelPlan(false);
  }, [fetchTravelPlan]);

  const handleRefresh = () => {
    fetchTravelPlan(true);
  };

  if (isLoading) {
    return <div className="py-20 text-center">{MESSAGES.LOADING}</div>;
  }

  if (error || !travel) {
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

  // 生成中の場合
  if (travel.reflectionGenerationStatus === 'processing') {
    return (
      <GenerationStatusView
        title={PAGE_TITLES.REFLECTION_PAMPHLET}
        status="processing"
        statusLabel={STATUS_LABELS.REFLECTION_PROCESSING}
        hintMessage={MESSAGES.GENERATING_REFLECTION_HINT}
        isRefreshing={isRefreshing}
        onRefresh={handleRefresh}
        backHref="/reflection"
      />
    );
  }

  if (!travel.pamphlet) {
    return (
      <div className="py-8">
        <Container>
          <div className="mb-6 rounded-lg border border-warning-200 bg-warning-50 p-4 text-warning-800">
            {MESSAGES.REFLECTION_NOT_FOUND}
          </div>
          <Link href="/reflection">
            <Button>{BUTTON_LABELS.BACK}</Button>
          </Link>
        </Container>
      </div>
    );
  }

  return (
    <div className="py-8">
      <Container>
        <div className="mb-6 flex items-center justify-between">
          <h1 className="font-bold text-2xl text-neutral-900">{PAGE_TITLES.REFLECTION_PAMPHLET}</h1>
          <div className="flex gap-2">
            <Link href="/reflection">
              <Button variant="ghost">{BUTTON_LABELS.BACK}</Button>
            </Link>
          </div>
        </div>

        <ReflectionViewer travel={travel} pamphlet={travel.pamphlet} />
      </Container>
    </div>
  );
}
