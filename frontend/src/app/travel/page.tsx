'use client';

import { Container } from '@/components/layout';
import { Button, Emoji } from '@/components/ui';
import {
  BUTTON_LABELS,
  EMOJI_LABELS,
  MESSAGES,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  STATUS_COLORS,
  STATUS_LABELS,
} from '@/constants';
import { createApiClientFromEnv, toApiError } from '@/lib/api';
import type { TravelPlanListResponse, TravelPlanStatus } from '@/types';
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';

export default function TravelListPage() {
  const [travels, setTravels] = useState<TravelPlanListResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTravels = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const apiClient = createApiClientFromEnv();
      // TODO: 実際のユーザーIDに置き換える（認証機能実装後）
      const userId = 'demo-user';

      const response = await apiClient.listTravelPlans({ userId });
      setTravels(response);
    } catch (err) {
      const apiError = toApiError(err);
      setError(apiError.message || MESSAGES.ERROR);
      console.error('Failed to fetch travel plans:', apiError);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTravels();
  }, [fetchTravels]);

  const hasTravels = travels.length > 0;

  const getStatusLabel = (status: TravelPlanStatus) => {
    switch (status) {
      case 'planning':
        return STATUS_LABELS.PLANNING;
      case 'completed':
        return STATUS_LABELS.COMPLETED;
    }
  };

  const getStatusColor = (status: TravelPlanStatus) => {
    switch (status) {
      case 'planning':
        return STATUS_COLORS.PLANNING;
      case 'completed':
        return STATUS_COLORS.COMPLETED;
    }
  };

  return (
    <div className="py-8">
      <Container>
        <div className="mb-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="mb-2 font-bold text-3xl text-neutral-900">{PAGE_TITLES.TRAVEL_LIST}</h1>
            <p className="text-neutral-600">{PAGE_DESCRIPTIONS.TRAVEL_LIST}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={fetchTravels} disabled={isLoading}>
              {isLoading ? MESSAGES.LOADING : '一覧を更新'}
            </Button>
            <Link href="/travel/new">
              <Button>{BUTTON_LABELS.CREATE_NEW_TRAVEL}</Button>
            </Link>
          </div>
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
              <Emoji symbol="📚" label={EMOJI_LABELS.BOOK} />
            </div>
            <p className="mb-6 text-neutral-600">{MESSAGES.NO_TRAVELS}</p>
            <Link href="/travel/new">
              <Button>{BUTTON_LABELS.CREATE_NEW_TRAVEL}</Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {travels.map(travel => (
              <div
                key={travel.id}
                className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="mb-4 flex items-start justify-between">
                  <div>
                    <h2 className="mb-1 font-semibold text-neutral-900 text-xl">{travel.title}</h2>
                    <p className="text-neutral-500 text-sm">{travel.destination}</p>
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 font-medium text-xs ${getStatusColor(travel.status)}`}
                  >
                    {getStatusLabel(travel.status)}
                  </span>
                </div>

                <div className="flex gap-2">
                  {travel.guideGenerationStatus === 'processing' ? (
                    <div className="flex-1">
                      <Button variant="primary" fullWidth disabled>
                        生成中...
                      </Button>
                    </div>
                  ) : (
                    <Link href={`/travel/${travel.id}`} className="flex-1">
                      <Button variant="primary" fullWidth>
                        {BUTTON_LABELS.VIEW_DETAILS}
                      </Button>
                    </Link>
                  )}
                  {travel.status !== 'completed' &&
                    (travel.guideGenerationStatus === 'processing' ? (
                      <Button variant="ghost" disabled>
                        {BUTTON_LABELS.EDIT}
                      </Button>
                    ) : (
                      <Link href={`/travel/${travel.id}/edit`}>
                        <Button variant="ghost">{BUTTON_LABELS.EDIT}</Button>
                      </Link>
                    ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </Container>
    </div>
  );
}
