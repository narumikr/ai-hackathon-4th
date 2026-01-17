import { Container } from '@/components/layout';
import { Button } from '@/components/ui';
import { BUTTON_LABELS } from '@/constants';

// サンプルデータ
const sampleGuide = {
  id: '1',
  title: '京都 歴史探訪の旅',
  destination: '京都府',
  spots: [
    {
      id: 's1',
      name: '金閣寺（鹿苑寺）',
      description: '室町時代の北山文化を代表する寺院',
      historicalContext:
        '1397年、足利義満により建立された山荘を起源とし、義満の死後に禅寺となった。金箔で覆われた舎利殿「金閣」は、北山文化の象徴として知られる。',
      checkpoints: [
        '金閣（舎利殿）の建築様式を観察',
        '鏡湖池に映る金閣の美しさを鑑賞',
        '庭園の回遊式構造を体験',
      ],
    },
    {
      id: 's2',
      name: '清水寺',
      description: '京都を代表する古刹、清水の舞台で有名',
      historicalContext:
        '778年（奈良時代）に開山された古刹。現在の本堂は1633年の再建。「清水の舞台から飛び降りる」の語源となった舞台は、釘を一本も使わない懸造り（かけづくり）で建てられている。',
      checkpoints: [
        '本堂の懸造り構造を観察',
        '音羽の滝で三筋の水の意味を学ぶ',
        '仁王門から二寧坂へ続く歴史的景観を楽しむ',
      ],
    },
    {
      id: 's3',
      name: '伏見稲荷大社',
      description: '千本鳥居で有名な稲荷神社の総本宮',
      historicalContext:
        '711年（和銅4年）に創建された日本全国に約3万社ある稲荷神社の総本宮。商売繁盛・五穀豊穣の神として信仰を集め、江戸時代以降、商人たちによって奉納された朱色の鳥居が山全体に立ち並ぶ。',
      checkpoints: [
        '千本鳥居のトンネルを歩く',
        '稲荷山への参道を登る',
        '各時代の鳥居の奉納銘を観察',
      ],
    },
  ],
  timeline: [
    { year: 711, event: '伏見稲荷大社創建' },
    { year: 778, event: '清水寺開山' },
    { year: 1397, event: '金閣寺（北山殿）建立' },
    { year: 1633, event: '清水寺本堂再建' },
  ],
};

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
              <Button variant="ghost">印刷</Button>
              <Button variant="secondary">PDF出力</Button>
              <Button variant="primary">旅行完了</Button>
            </div>
          </div>
        </div>

        {/* 歴史年表 */}
        <section className="mb-12 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
          <h2 className="mb-6 font-bold text-2xl text-neutral-900">📅 歴史年表</h2>
          <div className="space-y-4">
            {sampleGuide.timeline.map(item => (
              <div key={`timeline-${item.year}`} className="flex gap-4">
                <div className="w-24 flex-shrink-0 font-bold text-primary-700">{item.year}年</div>
                <div className="flex-1">
                  <p className="text-neutral-700">{item.event}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 地図エリア（プレースホルダー） */}
        <section className="mb-12 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
          <h2 className="mb-6 font-bold text-2xl text-neutral-900">🗺️ 観光マップ</h2>
          <div className="flex h-96 items-center justify-center rounded-lg border-2 border-neutral-300 border-dashed bg-neutral-100">
            <div className="text-center">
              <div className="mb-2 text-6xl">🗺️</div>
              <p className="text-neutral-500">地図機能は今後実装予定</p>
              <p className="text-neutral-400 text-sm">各スポットの位置と歴史的コンテキストを表示</p>
            </div>
          </div>
        </section>

        {/* スポット詳細 */}
        <section className="mb-12">
          <h2 className="mb-6 font-bold text-2xl text-neutral-900">📍 観光スポット詳細</h2>
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
                  <h4 className="mb-2 font-semibold text-neutral-700 text-sm">🏛️ 歴史的背景</h4>
                  <p className="text-neutral-700 leading-relaxed">{spot.historicalContext}</p>
                </div>

                <div>
                  <h4 className="mb-2 font-semibold text-neutral-700 text-sm">
                    ✅ チェックポイント
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
            旅行を完了してフィードバックを作成
          </Button>
        </div>
      </Container>
    </div>
  );
}
