'use client';

import { ErrorDialog } from '@/components/features/common';
import { Container } from '@/components/layout';
import { Button } from '@/components/ui';
import {
  BUTTON_LABELS,
  ERROR_DIALOG_MESSAGES,
  MESSAGES,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  STATUS_COLORS,
  STATUS_LABELS,
} from '@/constants';
import { useAuthContext } from '@/contexts/AuthContext';
import { createApiClientFromEnv } from '@/lib/api';
import type { TravelPlanListResponse, TravelPlanStatus } from '@/types';
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';

export default function TravelListPage() {
  const { user } = useAuthContext();
  const [travels, setTravels] = useState<TravelPlanListResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTravels = useCallback(async () => {
    if (!user) return;
    setIsLoading(true);
    setError(null);

    try {
      const apiClient = createApiClientFromEnv();

      const response = await apiClient.listTravelPlans({});
      setTravels(response);
    } catch (_err) {
      setError(ERROR_DIALOG_MESSAGES.TRAVEL_LIST_FETCH_FAILED);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

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
              {isLoading ? MESSAGES.LOADING : BUTTON_LABELS.REFRESH_LIST}
            </Button>
            <Link href="/travel/new">
              <Button>{BUTTON_LABELS.CREATE_NEW_TRAVEL}</Button>
            </Link>
          </div>
        </div>

        {isLoading ? (
          <div className="py-16 text-center">
            <p className="text-neutral-600">{MESSAGES.LOADING}</p>
          </div>
        ) : !hasTravels ? (
          <div className="py-16 text-center">
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
                    <div className="mb-1 flex items-center gap-2">
                      <h2 className="font-semibold text-neutral-900 text-xl">{travel.title}</h2>
                      {travel.guideGenerationStatus === 'failed' && (
                        <span className="rounded-full bg-danger px-2 py-0.5 font-medium text-white text-xs">
                          {STATUS_LABELS.GENERATION_FAILED}
                        </span>
                      )}
                    </div>
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
                        {MESSAGES.GENERATING}
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

      {/* エラーダイアログ */}
      <ErrorDialog
        isOpen={!!error}
        onClose={() => setError(null)}
        title={MESSAGES.ERROR}
        message={error || ''}
      />
    </div>
  );
}
