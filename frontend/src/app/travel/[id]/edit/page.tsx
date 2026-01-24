'use client';
import { useRouter } from 'next/navigation';
import { Container } from '@/components/layout';
import { Button, TextField, Emoji } from '@/components/ui';
import {
  BUTTON_LABELS,
  FORM_LABELS,
  PAGE_TITLES,
  PLACEHOLDERS,
} from '@/constants';
import { sampleGuide } from '@/data';
import { useState } from 'react';

export default function TravelEditPage() {
  const router = useRouter();
  // const params = useParams(); // status check not needed here for now as per instructions (or maybe needed later but unused now)
  // const id = params?.id as string; 

  // Initial state based on sampleGuide
  const [formData, setFormData] = useState({
    title: sampleGuide.title,
    destination: sampleGuide.destination,
    spots: sampleGuide.spots.map(s => s.name),
  });

  const handleBack = () => {
    router.push('/travel');
  };

  const handleUpdate = () => {
    // TODO: Update logic here
    console.log('Update:', formData);
    router.push('/travel');
  };

  const handleSpotChange = (index: number, value: string) => {
    const newSpots = [...formData.spots];
    newSpots[index] = value;
    setFormData({ ...formData, spots: newSpots });
  };

  const handleAddSpot = () => {
    setFormData({ ...formData, spots: [...formData.spots, ''] });
  };

  const handleRemoveSpot = (index: number) => {
    const newSpots = [...formData.spots];
    newSpots.splice(index, 1);
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
            <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
              {/* Title */}
              <div>
                <TextField
                  label={FORM_LABELS.TRAVEL_TITLE}
                  value={formData.title}
                  onChange={(value) => setFormData({ ...formData, title: value })}
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
                  onChange={(value) => setFormData({ ...formData, destination: value })}
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
                  {formData.spots.map((spot, index) => (
                    <div key={index} className="flex gap-2">
                        <div className="flex-1">
                            <TextField
                                value={spot}
                                onChange={(value) => handleSpotChange(index, value)}
                                placeholder={PLACEHOLDERS.SPOT_1}
                                fullWidth
                            />
                        </div>
                        <Button 
                            variant="ghost" 
                            onClick={() => handleRemoveSpot(index)}
                            disabled={formData.spots.length <= 1} // Prevent removing all spots if desired
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
                <Button variant="ghost" fullWidth onClick={handleAddSpot}>
                  {BUTTON_LABELS.ADD_SPOT}
                </Button>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4">
                <Button variant="ghost" className="flex-1" onClick={handleBack}>
                  {BUTTON_LABELS.BACK}
                </Button>
                <Button variant="primary" className="flex-1" onClick={handleUpdate}>
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
