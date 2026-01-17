import { Container } from '@/components/layout';
import { Button, TextField } from '@/components/ui';
import { BUTTON_LABELS, PAGE_TITLES } from '@/constants';

export default function TravelNewPage() {
  return (
    <div className="py-8">
      <Container variant="standard">
        <div className="mx-auto max-w-2xl">
          <div className="mb-8">
            <h1 className="mb-2 font-bold text-3xl text-neutral-900">{PAGE_TITLES.TRAVEL_NEW}</h1>
            <p className="text-neutral-600">旅行先と訪問予定の観光スポットを入力してください</p>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-8 shadow-sm">
            <form className="space-y-6">
              {/* 旅行タイトル */}
              <div>
                <TextField
                  label="旅行タイトル"
                  placeholder="例: 京都 歴史探訪の旅"
                  fullWidth
                  required
                />
              </div>

              {/* 目的地 */}
              <div>
                <TextField
                  label="目的地"
                  placeholder="例: 京都府"
                  helpText="訪問する都道府県や地域を入力してください"
                  fullWidth
                  required
                />
              </div>

              {/* 観光スポット */}
              <div>
                <div className="mb-2 block font-medium text-neutral-700 text-sm">
                  観光スポット
                  <span className="ml-1 text-danger">*</span>
                </div>
                <div className="space-y-3">
                  <TextField placeholder="例: 金閣寺" fullWidth />
                  <TextField placeholder="例: 清水寺" fullWidth />
                  <TextField placeholder="例: 伏見稲荷大社" fullWidth />
                </div>
                <p className="mt-2 text-neutral-500 text-sm">
                  訪問予定の観光スポットを入力してください（複数可）
                </p>
              </div>

              {/* スポット追加ボタン */}
              <div>
                <Button variant="ghost" fullWidth>
                  ＋ スポットを追加
                </Button>
              </div>

              {/* 地図選択エリア（プレースホルダー） */}
              <div>
                <div className="mb-2 block font-medium text-neutral-700 text-sm">地図から選択</div>
                <div className="flex h-64 items-center justify-center rounded-lg border-2 border-neutral-300 border-dashed bg-neutral-100">
                  <div className="text-center">
                    <div className="mb-2 text-4xl">🗺️</div>
                    <p className="text-neutral-500">地図機能は今後実装予定</p>
                  </div>
                </div>
              </div>

              {/* アクションボタン */}
              <div className="flex gap-4 pt-4">
                <Button variant="ghost" className="flex-1">
                  {BUTTON_LABELS.CANCEL}
                </Button>
                <Button variant="primary" className="flex-1">
                  旅行ガイドを生成
                </Button>
              </div>
            </form>
          </div>

          {/* 注意事項 */}
          <div className="mt-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
            <h3 className="mb-2 font-semibold text-primary-900 text-sm">💡 ヒント</h3>
            <ul className="space-y-1 text-primary-800 text-sm">
              <li>• 観光スポットは具体的な名称を入力してください</li>
              <li>• 歴史的な建造物や史跡がおすすめです</li>
              <li>• ガイド生成には1-2分程度かかる場合があります</li>
            </ul>
          </div>
        </div>
      </Container>
    </div>
  );
}
