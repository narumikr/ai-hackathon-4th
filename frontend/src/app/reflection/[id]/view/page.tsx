'use client';

import { Container } from '@/components/layout';
import { ReflectionViewer } from '@/components/reflection/ReflectionViewer';
import { Button } from '@/components/ui';
import { BUTTON_LABELS, MESSAGES, PAGE_TITLES } from '@/constants';
import { sampleReflectionContents, sampleTravels } from '@/data';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function ReflectionViewPage() {
  const params = useParams();
  const id = params?.id as string;

  const travel = sampleTravels.find(t => t.id === id);

  if (!travel) {
    return <div className="py-20 text-center">{MESSAGES.TRAVEL_NOT_FOUND}</div>;
  }

  // 実際のアプリではAPIから取得。ここではサンプルデータから検索。
  const reflection = sampleReflectionContents.find(r => r.travelId === id);

  if (!reflection) {
    return <div className="py-20 text-center">{MESSAGES.REFLECTION_NOT_FOUND}</div>;
  }

  return (
    <div className="py-8">
      <Container>
        <div className="mb-6 flex items-center justify-between">
          <h1 className="font-bold text-2xl text-neutral-900">{PAGE_TITLES.REFLECTION_PAMPHLET}</h1>
          <div className="flex gap-2">
            <Link href="/reflection">
              <Button variant="ghost">{BUTTON_LABELS.BACK}</Button>
            </Link>
          </div>
        </div>

        <ReflectionViewer travel={travel} reflection={reflection} />
      </Container>
    </div>
  );
}
