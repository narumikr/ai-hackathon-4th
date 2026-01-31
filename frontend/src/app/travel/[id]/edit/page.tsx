'use client';
import { Container } from '@/components/layout';
import { Button, TextField, Tooltip } from '@/components/ui';
import {
  ARIA_LABELS,
  BUTTON_LABELS,
  FORM_LABELS,
  HELP_TEXTS,
  MESSAGES,
  PAGE_TITLES,
  PLACEHOLDERS,
  TOOLTIP_MESSAGES,
} from '@/constants';
import { createApiClientFromEnv, toApiError } from '@/lib/api';
import type { TravelPlanResponse } from '@/types';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useId, useState } from 'react';

export default function TravelEditPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;
  const componentId = useId();

  const [travel, setTravel] = useState<TravelPlanResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    destination: '',
    spots: [] as { id: string; name: string }[],
  });
  const [spotIdCounter, setSpotIdCounter] = useState(0);
  const [showTitleError, setShowTitleError] = useState(false);
  const [showDestinationError, setShowDestinationError] = useState(false);

  useEffect(() => {
    const fetchTravelPlan = async () => {
      if (!id) return;

      setIsLoading(true);
      setError(null);

      try {
        const apiClient = createApiClientFromEnv();
        const response = await apiClient.getTravelPlan({ planId: id });
        setTravel(response);

        // フォームデータを初期化
        setFormData({
          title: response.title,
          destination: response.destination,
          spots: response.spots.map((s, i) => ({
            id: `${componentId}-spot-${i}`,
            name: s.name,
          })),
        });
        setSpotIdCounter(response.spots.length);
      } catch (err) {
        const apiError = toApiError(err);
        setError(apiError.message || MESSAGES.ERROR);
        console.error('Failed to fetch travel plan:', apiError);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTravelPlan();
  }, [id, componentId]);

  const handleBack = () => {
    router.push('/travel');
  };

  const handleUpdate = async () => {
    let isValid = true;

    if (!formData.title.trim()) {
      setShowTitleError(true);
      isValid = false;
    } else {
      setShowTitleError(false);
    }

    if (!formData.destination.trim()) {
      setShowDestinationError(true);
      isValid = false;
    } else {
      setShowDestinationError(false);
    }

    if (!isValid) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const apiClient = createApiClientFromEnv();

      // スポットリストを整形（空の値を除外）
      const filteredSpots = formData.spots
        .filter(spot => spot.name.trim())
        .map(spot => ({ name: spot.name.trim() }));

      // 1. 旅行計画を更新
      const response = await apiClient.updateTravelPlan({
        planId: id,
        request: {
          title: formData.title.trim(),
          destination: formData.destination.trim(),
          spots: filteredSpots.length > 0 ? filteredSpots : undefined,
        },
      });

      // 2. 旅行ガイドを生成
      await apiClient.generateTravelGuide({
        request: {
          planId: response.id,
        },
      });

      // 3. 更新成功後、旅行一覧ページにリダイレクト
      router.push('/travel');
    } catch (err) {
      const apiError = toApiError(err);
      setError(apiError.message || MESSAGES.ERROR);
      console.error('Failed to update travel plan or generate guide:', apiError);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSpotChange = (id: string, value: string) => {
    const newSpots = formData.spots.map(spot => (spot.id === id ? { ...spot, name: value } : spot));
    setFormData({ ...formData, spots: newSpots });
  };

  const handleAddSpot = () => {
    const newId = `${componentId}-spot-${spotIdCounter}`;
    setSpotIdCounter(spotIdCounter + 1);
    setFormData({ ...formData, spots: [...formData.spots, { id: newId, name: '' }] });
  };

  const handleRemoveSpot = (id: string) => {
    const newSpots = formData.spots.filter(spot => spot.id !== id);
    setFormData({ ...formData, spots: newSpots });
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

  return (
    <div className="py-8">
      <Container variant="standard">
        <div className="mx-auto max-w-2xl">
          <div className="mb-8">
            <h1 className="mb-2 font-bold text-3xl text-neutral-900">{PAGE_TITLES.TRAVEL_EDIT}</h1>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-8 shadow-sm">
            {/* エラーメッセージ */}
            {error && (
              <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            <form className="space-y-6" onSubmit={e => e.preventDefault()}>
              {/* Title */}
              <div>
                <Tooltip
                  content={TOOLTIP_MESSAGES.TITLE_REQUIRED}
                  isOpen={showTitleError}
                  position="top"
                >
                  <TextField
                    label={FORM_LABELS.TRAVEL_TITLE}
                    value={formData.title}
                    onChange={value => {
                      setFormData({ ...formData, title: value });
                      if (showTitleError) setShowTitleError(false);
                    }}
                    placeholder={PLACEHOLDERS.TRAVEL_TITLE}
                    fullWidth
                    required
                  />
                </Tooltip>
              </div>

              {/* Destination */}
              <div>
                <Tooltip
                  content={TOOLTIP_MESSAGES.DESTINATION_REQUIRED}
                  isOpen={showDestinationError}
                  position="top"
                >
                  <TextField
                    label={FORM_LABELS.DESTINATION}
                    value={formData.destination}
                    onChange={value => {
                      setFormData({ ...formData, destination: value });
                      if (showDestinationError) setShowDestinationError(false);
                    }}
                    placeholder={PLACEHOLDERS.DESTINATION}
                    helpText={HELP_TEXTS.DESTINATION}
                    fullWidth
                    required
                  />
                </Tooltip>
              </div>

              {/* Spots */}
              <div>
                <div className="mb-2 block font-medium text-neutral-700 text-sm">
                  {FORM_LABELS.SPOTS}
                </div>
                <div className="space-y-3">
                  {formData.spots.map(spot => (
                    <div key={spot.id} className="flex gap-2">
                      <div className="flex-1">
                        <TextField
                          value={spot.name}
                          onChange={value => handleSpotChange(spot.id, value)}
                          placeholder={PLACEHOLDERS.SPOT_1}
                          fullWidth
                        />
                      </div>
                      <Button
                        variant="ghost"
                        onClick={() => handleRemoveSpot(spot.id)}
                        disabled={formData.spots.length <= 1}
                        title={ARIA_LABELS.REMOVE_SPOT}
                      >
                        ✕
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Add Spot Button */}
              <div>
                <Button variant="ghost" fullWidth onClick={handleAddSpot} type="button">
                  {BUTTON_LABELS.ADD_SPOT}
                </Button>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4">
                <Button
                  variant="ghost"
                  className="flex-1"
                  onClick={handleBack}
                  type="button"
                  disabled={isSubmitting}
                >
                  {BUTTON_LABELS.BACK}
                </Button>
                <Button
                  variant="primary"
                  className="flex-1"
                  onClick={handleUpdate}
                  type="button"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? MESSAGES.LOADING : BUTTON_LABELS.UPDATE}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </Container>
    </div>
  );
}
