import { Container } from '@/components/layout';
import { Button } from '@/components/ui';
import { BUTTON_LABELS, MESSAGES, PAGE_TITLES } from '@/constants';
import Link from 'next/link';

// サンプルデータ
const sampleTravels = [
  {
    id: '1',
    title: '京都 歴史探訪の旅',
    destination: '京都府',
    status: 'planning' as const,
    spotsCount: 5,
    createdAt: '2026-01-10',
  },
  {
    id: '2',
    title: '奈良 古代史の旅',
    destination: '奈良県',
    status: 'traveling' as const,
    spotsCount: 4,
    createdAt: '2026-01-08',
  },
  {
    id: '3',
    title: '広島 平和学習の旅',
    destination: '広島県',
    status: 'completed' as const,
    spotsCount: 3,
    createdAt: '2025-12-20',
  },
];

const statusLabels = {
  planning: '計画中',
  traveling: '旅行中',
  completed: '完了',
};

const statusColors = {
  planning: 'bg-info text-white',
  traveling: 'bg-warning text-white',
  completed: 'bg-success text-white',
};

export default function TravelListPage() {
  const hasTravels = sampleTravels.length > 0;

  return (
    <div className="py-8">
      <Container>
        <div className="mb-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="mb-2 font-bold text-3xl text-neutral-900">{PAGE_TITLES.TRAVEL_LIST}</h1>
            <p className="text-neutral-600">作成した旅行計画を管理できます</p>
          </div>
          <Link href="/travel/new">
            <Button>{BUTTON_LABELS.CREATE_NEW_TRAVEL}</Button>
          </Link>
        </div>

        {!hasTravels ? (
          <div className="py-16 text-center">
            <div className="mb-4 text-6xl">🗺️</div>
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
                    className={`rounded-full px-3 py-1 font-medium text-xs ${statusColors[travel.status]}`}
                  >
                    {statusLabels[travel.status]}
                  </span>
                </div>

                <div className="mb-4 flex items-center gap-4 text-neutral-600 text-sm">
                  <span>📍 {travel.spotsCount}スポット</span>
                  <span>📅 {travel.createdAt}</span>
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
