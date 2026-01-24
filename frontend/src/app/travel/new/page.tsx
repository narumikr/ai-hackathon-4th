'use client';
import { Container } from '@/components/layout';
import { Button, Emoji, TextField, Tooltip } from '@/components/ui';
import {
  BUTTON_LABELS,
  FORM_LABELS,
  HELP_TEXTS,
  HINTS,
  LABELS,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  PLACEHOLDERS,
  TOOLTIP_MESSAGES,
} from '@/constants';
import { useRouter } from 'next/navigation';
import { useId, useState } from 'react';

export default function TravelNewPage() {
  const router = useRouter();
  const componentId = useId();
  const [title, setTitle] = useState('');
  const [destination, setDestination] = useState('');
  const [spots, setSpots] = useState([
    { id: `${componentId}-spot-0`, name: '' },
    { id: `${componentId}-spot-1`, name: '' },
    { id: `${componentId}-spot-2`, name: '' },
  ]);
  const [spotIdCounter, setSpotIdCounter] = useState(3);

  const handleSpotChange = (id: string, value: string) => {
    const newSpots = spots.map(spot => (spot.id === id ? { ...spot, name: value } : spot));
    setSpots(newSpots);
  };

  const handleAddSpot = () => {
    const newId = `${componentId}-spot-${spotIdCounter}`;
    setSpotIdCounter(spotIdCounter + 1);
    setSpots([...spots, { id: newId, name: '' }]);
  };

  const handleRemoveSpot = (id: string) => {
    const newSpots = spots.filter(spot => spot.id !== id);
    setSpots(newSpots);
  };

  const [showTitleError, setShowTitleError] = useState(false);
  const [showDestinationError, setShowDestinationError] = useState(false);

  const handleCancel = () => {
    router.push('/travel');
  };

  const handleCreate = () => {
    let isValid = true;

    if (!title.trim()) {
      setShowTitleError(true);
      isValid = false;
    } else {
      setShowTitleError(false);
    }

    if (!destination.trim()) {
      setShowDestinationError(true);
      isValid = false;
    } else {
      setShowDestinationError(false);
    }

    if (!isValid) return;
    alert('作成ボタンが押されました（API未実装）');
  };

  return (
    <div className="py-8">
      <Container variant="standard">
        <div className="mx-auto max-w-2xl">
          <div className="mb-8">
            <h1 className="mb-2 font-bold text-3xl text-neutral-900">{PAGE_TITLES.TRAVEL_NEW}</h1>
            <p className="text-neutral-600">{PAGE_DESCRIPTIONS.TRAVEL_NEW}</p>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-8 shadow-sm">
            <form className="space-y-6" onSubmit={e => e.preventDefault()}>
              {/* 旅行タイトル */}
              <div>
                <Tooltip
                  content={TOOLTIP_MESSAGES.TITLE_REQUIRED}
                  isOpen={showTitleError}
                  position="top"
                >
                  <TextField
                    label={FORM_LABELS.TRAVEL_TITLE}
                    placeholder={PLACEHOLDERS.TRAVEL_TITLE}
                    fullWidth
                    required
                    value={title}
                    onChange={value => {
                      setTitle(value);
                      if (showTitleError) setShowTitleError(false);
                    }}
                  />
                </Tooltip>
              </div>

              {/* 目的地 */}
              <div>
                <Tooltip
                  content={TOOLTIP_MESSAGES.DESTINATION_REQUIRED}
                  isOpen={showDestinationError}
                  position="top"
                >
                  <TextField
                    label={FORM_LABELS.DESTINATION}
                    placeholder={PLACEHOLDERS.DESTINATION}
                    helpText={HELP_TEXTS.DESTINATION}
                    fullWidth
                    required
                    value={destination}
                    onChange={value => {
                      setDestination(value);
                      if (showDestinationError) setShowDestinationError(false);
                    }}
                  />
                </Tooltip>
              </div>

              {/* 観光スポット */}
              <div>
                <div className="mb-2 block font-medium text-neutral-700 text-sm">
                  {FORM_LABELS.SPOTS}
                </div>
                <div className="space-y-3">
                  {spots.map(spot => (
                    <div key={spot.id} className="flex gap-2">
                      <div className="flex-1">
                        <TextField
                          placeholder={PLACEHOLDERS.SPOT_1}
                          fullWidth
                          value={spot.name}
                          onChange={value => handleSpotChange(spot.id, value)}
                        />
                      </div>
                      <Button
                        variant="ghost"
                        onClick={() => handleRemoveSpot(spot.id)}
                        disabled={spots.length <= 1}
                        title="Remove spot"
                        type="button"
                      >
                        <Emoji symbol="🗑️" label="Delete" />
                      </Button>
                    </div>
                  ))}
                </div>
                <p className="mt-2 text-neutral-500 text-sm">{HELP_TEXTS.SPOTS}</p>
              </div>

              {/* スポット追加ボタン */}
              <div>
                <Button variant="ghost" fullWidth type="button" onClick={handleAddSpot}>
                  {BUTTON_LABELS.ADD_SPOT}
                </Button>
              </div>

              {/* アクションボタン */}
              <div className="flex gap-4 pt-4">
                <Button variant="ghost" className="flex-1" onClick={handleCancel} type="button">
                  {BUTTON_LABELS.CANCEL}
                </Button>
                <Button variant="primary" className="flex-1" onClick={handleCreate} type="button">
                  {BUTTON_LABELS.GENERATE_GUIDE}
                </Button>
              </div>
            </form>
          </div>

          {/* 注意事項 */}
          <div className="mt-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
            <h3 className="mb-2 font-semibold text-primary-900 text-sm">{LABELS.HINT_TITLE}</h3>
            <ul className="space-y-1 text-primary-800 text-sm">
              {HINTS.TRAVEL_NEW.map(hint => (
                <li key={hint}>• {hint}</li>
              ))}
            </ul>
          </div>
        </div>
      </Container>
    </div>
  );
}
