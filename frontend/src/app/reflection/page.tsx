import { Container } from '@/components/layout';
import { Button, Emoji } from '@/components/ui';
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
import { completedTravels } from '@/data';
import Link from 'next/link';

export default function ReflectionListPage() {
  const hasTravels = completedTravels.length > 0;

  return (
    <div className="py-8">
      <Container>
        <div className="mb-8">
          <h1 className="mb-2 font-bold text-3xl text-neutral-900">
            {PAGE_TITLES.REFLECTION_LIST}
          </h1>
          <p className="text-neutral-600">{PAGE_DESCRIPTIONS.REFLECTION_LIST}</p>
        </div>

        {!hasTravels ? (
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
            {completedTravels.map(travel => (
              <div
                key={travel.id}
                className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="mb-4">
                  <div className="mb-2 flex items-start justify-between">
                    <h2 className="font-semibold text-neutral-900 text-xl">{travel.title}</h2>
                    {travel.hasReflection && (
                      <span className="rounded-full bg-success px-3 py-1 font-medium text-white text-xs">
                        {STATUS_LABELS.REFLECTION_CREATED}
                      </span>
                    )}
                  </div>
                  <p className="text-neutral-500 text-sm">{travel.destination}</p>
                </div>

                <div className="mb-4 flex items-center gap-4 text-neutral-600 text-sm">
                  <span>
                    <Emoji symbol="✅" label={EMOJI_LABELS.CHECKMARK} /> {LABELS.COMPLETED_DATE}{' '}
                    {travel.completedAt}
                  </span>
                  {travel.photosCount > 0 && (
                    <span>
                      <Emoji symbol="📸" label={EMOJI_LABELS.CAMERA} /> {travel.photosCount}
                      {LABELS.PHOTOS_COUNT}
                    </span>
                  )}
                </div>

                <div className="flex gap-2">
                  {travel.hasReflection ? (
                    <Link href={`/reflection/${travel.id}`} className="flex-1">
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
            ))}
          </div>
        )}

        {/* ヒント */}
        <div className="mt-8 rounded-lg border border-primary-200 bg-primary-50 p-4">
          <h3 className="mb-2 font-semibold text-primary-900 text-sm">{LABELS.ABOUT_REFLECTION}</h3>
          <ul className="space-y-1 text-primary-800 text-sm">
            {HINTS.REFLECTION.map((hint, index) => (
              <li key={`hint-${index}`}>• {hint}</li>
            ))}
          </ul>
        </div>
      </Container>
    </div>
  );
}
