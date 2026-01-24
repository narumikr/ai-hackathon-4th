'use client';
import { Container } from '@/components/layout';
import { Button, Emoji, TextField } from '@/components/ui';
import { BUTTON_LABELS, FORM_LABELS, PAGE_TITLES, PLACEHOLDERS } from '@/constants';
import { sampleGuide } from '@/data';
import { useRouter } from 'next/navigation';
import { useId, useState } from 'react';

export default function TravelEditPage() {
  const router = useRouter();
  const componentId = useId();
  // const params = useParams(); // status check not needed here for now as per instructions (or maybe needed later but unused now)
  // const id = params?.id as string;

  // Initial state based on sampleGuide
  const [formData, setFormData] = useState({
    title: sampleGuide.title,
    destination: sampleGuide.destination,
    spots: sampleGuide.spots.map((s, i) => ({ id: `${componentId}-spot-${i}`, name: s.name })),
  });
  const [spotIdCounter, setSpotIdCounter] = useState(sampleGuide.spots.length);

  const handleBack = () => {
    router.push('/travel');
  };

  const handleUpdate = () => {
    router.push('/travel');
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

  return (
    <div className="py-8">
      <Container variant="standard">
        <div className="mx-auto max-w-2xl">
          <div className="mb-8">
            <h1 className="mb-2 font-bold text-3xl text-neutral-900">{PAGE_TITLES.TRAVEL_EDIT}</h1>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-8 shadow-sm">
            <form className="space-y-6" onSubmit={e => e.preventDefault()}>
              {/* Title */}
              <div>
                <TextField
                  label={FORM_LABELS.TRAVEL_TITLE}
                  value={formData.title}
                  onChange={value => setFormData({ ...formData, title: value })}
                  placeholder={PLACEHOLDERS.TRAVEL_TITLE}
                  fullWidth
                  required
                />
              </div>

              {/* Destination */}
              <div>
                <TextField
                  label={FORM_LABELS.DESTINATION}
                  value={formData.destination}
                  onChange={value => setFormData({ ...formData, destination: value })}
                  placeholder={PLACEHOLDERS.DESTINATION}
                  fullWidth
                  required
                />
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
                        title="Remove spot"
                      >
                        <Emoji symbol="🗑️" label="Delete" />
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
                <Button variant="ghost" className="flex-1" onClick={handleBack} type="button">
                  {BUTTON_LABELS.BACK}
                </Button>
                <Button variant="primary" className="flex-1" onClick={handleUpdate} type="button">
                  {BUTTON_LABELS.UPDATE}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </Container>
    </div>
  );
}
