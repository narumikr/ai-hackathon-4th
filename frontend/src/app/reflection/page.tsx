import { Container } from '@/components/layout';
import { Button } from '@/components/ui';
import { MESSAGES, PAGE_TITLES } from '@/constants';
import Link from 'next/link';

// サンプルデータ
const completedTravels = [
  {
    id: '3',
    title: '広島 平和学習の旅',
    destination: '広島県',
    completedAt: '2025-12-25',
    hasReflection: true,
    photosCount: 8,
  },
  {
    id: '4',
    title: '鎌倉 武家文化の旅',
    destination: '神奈川県',
    completedAt: '2025-11-15',
    hasReflection: false,
    photosCount: 0,
  },
];

export default function ReflectionListPage() {
  const hasTravels = completedTravels.length > 0;

  return (
    <div className="py-8">
      <Container>
        <div className="mb-8">
          <h1 className="mb-2 font-bold text-3xl text-neutral-900">
            {PAGE_TITLES.REFLECTION_LIST}
          </h1>
          <p className="text-neutral-600">完了した旅行の振り返りを作成・確認できます</p>
        </div>

        {!hasTravels ? (
          <div className="py-16 text-center">
            <div className="mb-4 text-6xl">📸</div>
            <p className="mb-6 text-neutral-600">{MESSAGES.NO_REFLECTIONS}</p>
            <Link href="/travel">
              <Button>旅行一覧へ</Button>
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
                        作成済み
                      </span>
                    )}
                  </div>
                  <p className="text-neutral-500 text-sm">{travel.destination}</p>
                </div>

                <div className="mb-4 flex items-center gap-4 text-neutral-600 text-sm">
                  <span>✅ 完了: {travel.completedAt}</span>
                  {travel.photosCount > 0 && <span>📸 {travel.photosCount}枚</span>}
                </div>

                <div className="flex gap-2">
                  {travel.hasReflection ? (
                    <Link href={`/reflection/${travel.id}`} className="flex-1">
                      <Button variant="primary" fullWidth>
                        振り返りを見る
                      </Button>
                    </Link>
                  ) : (
                    <Link href={`/reflection/${travel.id}`} className="flex-1">
                      <Button variant="secondary" fullWidth>
                        振り返りを作成
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
          <h3 className="mb-2 font-semibold text-primary-900 text-sm">💡 振り返りについて</h3>
          <ul className="space-y-1 text-primary-800 text-sm">
            <li>• 旅行の写真をアップロードして感想を入力してください</li>
            <li>• AIが事前学習との比較を含めた振り返りパンフレットを生成します</li>
            <li>• 生成されたパンフレットは保存・印刷できます</li>
          </ul>
        </div>
      </Container>
    </div>
  );
}
