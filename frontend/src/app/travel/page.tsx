import { Container } from '@/components/layout';
import { Button, Emoji } from '@/components/ui';
import {
  BUTTON_LABELS,
  EMOJI_LABELS,
  LABELS,
  MESSAGES,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  STATUS_COLORS,
  STATUS_LABELS,
} from '@/constants';
import { type TravelStatus, sampleTravels } from '@/data';
import Link from 'next/link';

export default function TravelListPage() {
  const hasTravels = sampleTravels.length > 0;

  const getStatusLabel = (status: TravelStatus) => {
    switch (status) {
      case 'planning':
        return STATUS_LABELS.PLANNING;
      case 'traveling':
        return STATUS_LABELS.TRAVELING;
      case 'completed':
        return STATUS_LABELS.COMPLETED;
    }
  };

  const getStatusColor = (status: TravelStatus) => {
    switch (status) {
      case 'planning':
        return STATUS_COLORS.PLANNING;
      case 'traveling':
        return STATUS_COLORS.TRAVELING;
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
          <Link href="/travel/new">
            <Button>{BUTTON_LABELS.CREATE_NEW_TRAVEL}</Button>
          </Link>
        </div>

        {!hasTravels ? (
          <div className="py-16 text-center">
            <div className="mb-4 text-6xl">
              <Emoji symbol="🗺️" label={EMOJI_LABELS.MAP} />
            </div>
            <p className="mb-6 text-neutral-600">{MESSAGES.NO_TRAVELS}</p>
            <Link href="/travel/new">
              <Button>{BUTTON_LABELS.CREATE_NEW_TRAVEL}</Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {sampleTravels.map(travel => (
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

                <div className="mb-4 flex items-center gap-4 text-neutral-600 text-sm">
                  <span>
                    <Emoji symbol="📍" label={EMOJI_LABELS.PIN} /> {travel.spotsCount}
                    {LABELS.SPOTS_COUNT}
                  </span>
                  <span>
                    <Emoji symbol="📅" label={EMOJI_LABELS.CALENDAR} /> {travel.createdAt}
                  </span>
                </div>

                <div className="flex gap-2">
                  <Link href={`/travel/${travel.id}`} className="flex-1">
                    <Button variant="primary" fullWidth>
                      {BUTTON_LABELS.VIEW_DETAILS}
                    </Button>
                  </Link>
                  <Button variant="ghost">{BUTTON_LABELS.EDIT}</Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Container>
    </div>
  );
}
