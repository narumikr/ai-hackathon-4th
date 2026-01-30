'use client';

import { Container } from '@/components/layout';
import { Button, Emoji, LoadingSpinner } from '@/components/ui';
import {
  BUTTON_LABELS,
  EMOJI_LABELS,
  HINTS,
  LABELS,
  MESSAGES,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  STATUS_LABELS,
} from '@/constants';
import { createApiClientFromEnv, toApiError } from '@/lib/api';
import type { TravelPlanListResponse } from '@/types';
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';

export default function ReflectionListPage() {
  const [travels, setTravels] = useState<TravelPlanListResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTravels = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    try {
      const apiClient = createApiClientFromEnv();
      // TODO: 実際のユーザーIDに置き換える（認証機能実装後）
      const userId = 'demo-user';

      const response = await apiClient.listTravelPlans({ userId });
      // ステータスが completed のもののみをフィルタ
      const completedTravels = response.filter(t => t.status === 'completed');
      setTravels(completedTravels);
    } catch (err) {
      const apiError = toApiError(err);
      setError(apiError.message || MESSAGES.ERROR);
      console.error('Failed to fetch travel plans:', apiError);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchTravels(false);
  }, [fetchTravels]);

  const handleRefresh = () => {
    fetchTravels(true);
  };

  const hasTravels = travels.length > 0;

  return (
    <div className="py-8">
      <Container>
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="mb-2 font-bold text-3xl text-neutral-900">
              {PAGE_TITLES.REFLECTION_LIST}
            </h1>
            <p className="text-neutral-600">{PAGE_DESCRIPTIONS.REFLECTION_LIST}</p>
          </div>
          <Button variant="secondary" onClick={handleRefresh} disabled={isRefreshing}>
            {isRefreshing ? (
              <>
                <LoadingSpinner size="sm" variant="secondary" className="mr-2" />
                更新中...
              </>
            ) : (
              '更新'
            )}
          </Button>
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-danger-200 bg-danger-50 p-4 text-danger-800">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="py-16 text-center">
            <p className="text-neutral-600">{MESSAGES.LOADING}</p>
          </div>
        ) : !hasTravels ? (
          <div className="py-16 text-center">
            <div className="mb-4 text-6xl">
              <Emoji symbol="📸" label={EMOJI_LABELS.CAMERA} />
            </div>
            <p className="mb-6 text-neutral-600">{MESSAGES.NO_REFLECTIONS}</p>
            <Link href="/travel">
              <Button>{BUTTON_LABELS.VIEW_TRAVEL_LIST_ALT}</Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {travels.map(travel => {
              const hasReflection = travel.reflectionGenerationStatus === 'succeeded';

              return (
                <div
                  key={travel.id}
                  className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="mb-4">
                    <div className="mb-2 flex items-start justify-between">
                      <h2 className="font-semibold text-neutral-900 text-xl">{travel.title}</h2>
                      {travel.reflectionGenerationStatus === 'processing' ? (
                        <span className="rounded-full bg-warning px-3 py-1 font-medium text-white text-xs">
                          {STATUS_LABELS.REFLECTION_PROCESSING}
                        </span>
                      ) : (
                        hasReflection && (
                          <span className="rounded-full bg-success px-3 py-1 font-medium text-white text-xs">
                            {STATUS_LABELS.REFLECTION_CREATED}
                          </span>
                        )
                      )}
                    </div>
                    <p className="text-neutral-500 text-sm">{travel.destination}</p>
                  </div>

                  <div className="flex gap-2">
                    {travel.reflectionGenerationStatus === 'processing' ? (
                      <Button variant="secondary" fullWidth disabled className="flex-1">
                        <LoadingSpinner size="sm" variant="secondary" className="mr-2" />
                        {STATUS_LABELS.REFLECTION_PROCESSING}
                      </Button>
                    ) : hasReflection ? (
                      <Link href={`/reflection/${travel.id}/view`} className="flex-1">
                        <Button variant="primary" fullWidth>
                          {BUTTON_LABELS.VIEW_REFLECTION}
                        </Button>
                      </Link>
                    ) : (
                      <Link href={`/reflection/${travel.id}`} className="flex-1">
                        <Button variant="secondary" fullWidth>
                          {BUTTON_LABELS.CREATE_REFLECTION}
                        </Button>
                      </Link>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ヒント */}
        <div className="mt-8 rounded-lg border border-primary-200 bg-primary-50 p-4">
          <h3 className="mb-2 font-semibold text-primary-900 text-sm">{LABELS.ABOUT_REFLECTION}</h3>
          <ul className="space-y-1 text-primary-800 text-sm">
            {HINTS.REFLECTION.map(hint => (
              <li key={hint}>• {hint}</li>
            ))}
          </ul>
        </div>
      </Container>
    </div>
  );
}
