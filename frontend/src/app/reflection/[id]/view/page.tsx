'use client';

import { Container } from '@/components/layout';
import { Button } from '@/components/ui';
import { BUTTON_LABELS } from '@/constants';
import { sampleReflectionContents, sampleTravels } from '@/data';
import { notFound, useParams } from 'next/navigation';
import Link from 'next/link';
import { ReflectionViewer } from '@/components/reflection/ReflectionViewer';

export default function ReflectionViewPage() {
    const params = useParams();
    const id = params?.id as string;

    const travel = sampleTravels.find(t => t.id === id);

    if (!travel) {
        return <div className="py-20 text-center">Travel not found</div>;
    }

    // 実際のアプリではAPIから取得。ここではサンプルデータから検索。
    const reflection = sampleReflectionContents.find(r => r.travelId === id);

    if (!reflection) {
        return <div className="py-20 text-center">Reflection not found</div>;
    }

    return (
        <div className="py-8">
            <Container>
                <div className="maybe-8 flex items-center justify-between mb-6">
                    <h1 className="text-2xl font-bold text-neutral-900">振り返りパンフレット</h1>
                    <div className="flex gap-2">
                        <Button variant="secondary">{BUTTON_LABELS.PRINT}</Button>
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
