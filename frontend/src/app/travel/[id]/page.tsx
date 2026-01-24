import { Container } from '@/components/layout';
import { Button, Emoji } from '@/components/ui';
import {
  BUTTON_LABELS,
  EMOJI_LABELS,
  LABELS,
  SECTION_TITLES,
} from '@/constants';
import { sampleGuide } from '@/data';

export default function TravelGuidePage() {
  return (
    <div className="py-8">
      <Container variant="wide">
        {/* ヘッダー */}
        <div className="mb-8">
          <div className="mb-4 flex flex-col items-start justify-between gap-4 lg:flex-row lg:items-center">
            <div>
              <h1 className="mb-2 font-bold text-3xl text-neutral-900">{sampleGuide.title}</h1>
              <p className="text-lg text-neutral-600">{sampleGuide.destination}</p>
            </div>
            <div className="flex gap-2">
              <Button variant="ghost">{BUTTON_LABELS.PRINT}</Button>
              <Button variant="secondary">{BUTTON_LABELS.PDF_EXPORT}</Button>
              <Button variant="primary">{BUTTON_LABELS.TRAVEL_COMPLETE}</Button>
            </div>
          </div>
        </div>

        {/* 歴史年表 */}
        <section className="mb-12 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
          <h2 className="mb-6 font-bold text-2xl text-neutral-900">
            <Emoji symbol="📅" label={EMOJI_LABELS.CALENDAR} /> {SECTION_TITLES.TIMELINE}
          </h2>
          <div className="space-y-4">
            {sampleGuide.timeline.map((item, index) => (
              <div key={`timeline-${item.year}-${index}`} className="flex gap-4">
                <div className="w-24 flex-shrink-0 font-bold text-primary-700">
                  {item.year}
                  {LABELS.YEAR_SUFFIX}
                </div>
                <div className="flex-1">
                  <p className="text-neutral-700">{item.event}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* スポット詳細 */}
        <section className="mb-12">
          <h2 className="mb-6 font-bold text-2xl text-neutral-900">
            <Emoji symbol="📍" label={EMOJI_LABELS.PIN} /> {SECTION_TITLES.SPOT_DETAILS}
          </h2>
          <div className="space-y-6">
            {sampleGuide.spots.map((spot, index) => (
              <div
                key={spot.id}
                className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm"
              >
                <div className="mb-4">
                  <div className="mb-2 flex items-center gap-3">
                    <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-primary-400 font-bold text-primary-950 text-sm">
                      {index + 1}
                    </span>
                    <h3 className="font-bold text-neutral-900 text-xl">{spot.name}</h3>
                  </div>
                  <p className="text-neutral-600">{spot.description}</p>
                </div>

                <div className="mb-4">
                  <h4 className="mb-2 font-semibold text-neutral-700 text-sm">
                    <Emoji symbol="🏛️" label={EMOJI_LABELS.HISTORIC_BUILDING} />{' '}
                    {SECTION_TITLES.HISTORICAL_CONTEXT}
                  </h4>
                  <p className="text-neutral-700 leading-relaxed">{spot.historicalContext}</p>
                </div>

                <div>
                  <h4 className="mb-2 font-semibold text-neutral-700 text-sm">
                    <Emoji symbol="✅" label={EMOJI_LABELS.CHECKMARK} />{' '}
                    {SECTION_TITLES.CHECKPOINTS}
                  </h4>
                  <ul className="space-y-1">
                    {spot.checkpoints.map(checkpoint => (
                      <li key={checkpoint} className="text-neutral-700">
                        {checkpoint}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* アクション */}
        <div className="flex flex-col justify-center gap-4 sm:flex-row">
          <Button variant="ghost" size="lg">
            {BUTTON_LABELS.BACK}
          </Button>
          <Button variant="primary" size="lg">
            {BUTTON_LABELS.COMPLETE_TRAVEL_AND_CREATE_FEEDBACK}
          </Button>
        </div>
      </Container>
    </div>
  );
}
