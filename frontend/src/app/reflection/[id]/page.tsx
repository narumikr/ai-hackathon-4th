import { Container } from '@/components/layout';
import { Button, TextArea } from '@/components/ui';
import { BUTTON_LABELS } from '@/constants';

export default function ReflectionCreatePage() {
  return (
    <div className="py-8">
      <Container>
        <div className="mx-auto max-w-4xl">
          <div className="mb-8">
            <h1 className="mb-2 font-bold text-3xl text-neutral-900">振り返り作成</h1>
            <p className="text-neutral-600">旅行の写真と感想をアップロードしてください</p>
          </div>

          {/* 旅行情報 */}
          <div className="mb-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
            <h2 className="mb-1 font-semibold text-lg text-neutral-900">広島 平和学習の旅</h2>
            <p className="text-neutral-600 text-sm">完了日: 2025-12-25</p>
          </div>

          {/* 写真アップロード */}
          <section className="mb-8 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 font-bold text-neutral-900 text-xl">📸 写真をアップロード</h2>

            {/* ドロップゾーン */}
            <div className="mb-6 flex h-64 cursor-pointer items-center justify-center rounded-lg border-2 border-neutral-300 border-dashed bg-neutral-50 transition-colors hover:border-primary-400">
              <div className="text-center">
                <div className="mb-2 text-6xl">📤</div>
                <p className="mb-2 font-medium text-neutral-700">
                  クリックまたはドラッグ&ドロップで写真を追加
                </p>
                <p className="text-neutral-500 text-sm">JPG, PNG形式に対応（最大10MB）</p>
              </div>
            </div>

            {/* アップロード済み写真プレビュー（サンプル） */}
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
              {[1, 2, 3].map(i => (
                <div
                  key={i}
                  className="group relative aspect-square overflow-hidden rounded-lg bg-neutral-200"
                >
                  <div className="absolute inset-0 flex items-center justify-center bg-neutral-300">
                    <span className="text-4xl text-neutral-500">🖼️</span>
                  </div>
                  <button
                    type="button"
                    className="absolute top-2 right-2 flex h-6 w-6 items-center justify-center rounded-full bg-danger text-white text-xs opacity-0 transition-opacity group-hover:opacity-100"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </section>

          {/* 各写真への感想 */}
          <section className="mb-8 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 font-bold text-neutral-900 text-xl">✍️ 写真ごとの感想</h2>
            <div className="space-y-6">
              {[1, 2, 3].map(i => (
                <div key={i} className="border-neutral-200 border-b pb-6 last:border-0 last:pb-0">
                  <div className="mb-3 flex items-start gap-4">
                    <div className="flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-lg bg-neutral-200">
                      <span className="text-2xl">🖼️</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="mb-2 font-semibold text-neutral-700 text-sm">写真 {i}</h3>
                      <TextArea
                        placeholder="この写真についての感想を入力してください..."
                        rows={3}
                        fullWidth
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 全体的な感想 */}
          <section className="mb-8 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 font-bold text-neutral-900 text-xl">📝 旅行全体の感想</h2>
            <TextArea
              placeholder="旅行全体を通しての感想を入力してください。事前学習との違いや、新たな発見などを記入すると、より充実した振り返りができます..."
              rows={6}
              fullWidth
              maxLength={1000}
              showCount
            />
          </section>

          {/* 事前学習情報の表示（参考用） */}
          <section className="mb-8 rounded-lg border border-neutral-200 bg-neutral-50 p-6">
            <h2 className="mb-4 font-bold text-neutral-900 text-xl">
              📚 事前学習で学んだこと（参考）
            </h2>
            <div className="space-y-3 text-sm">
              <div className="rounded border border-neutral-200 bg-white p-3">
                <h3 className="mb-1 font-semibold text-neutral-900">原爆ドーム</h3>
                <p className="text-neutral-600">
                  1945年8月6日の原子爆弾投下により被爆した建物。広島平和記念碑として世界遺産に登録。
                </p>
              </div>
              <div className="rounded border border-neutral-200 bg-white p-3">
                <h3 className="mb-1 font-semibold text-neutral-900">平和記念資料館</h3>
                <p className="text-neutral-600">
                  原爆の惨禍を伝える資料館。被爆の実相を後世に伝える重要な施設。
                </p>
              </div>
            </div>
          </section>

          {/* アクションボタン */}
          <div className="flex flex-col gap-4 sm:flex-row">
            <Button variant="ghost" size="lg" className="flex-1">
              {BUTTON_LABELS.CANCEL}
            </Button>
            <Button variant="primary" size="lg" className="flex-1">
              振り返りパンフレットを生成
            </Button>
          </div>

          {/* 注意事項 */}
          <div className="mt-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
            <h3 className="mb-2 font-semibold text-primary-900 text-sm">💡 ヒント</h3>
            <ul className="space-y-1 text-primary-800 text-sm">
              <li>• 写真は訪問した場所が分かるものがおすすめです</li>
              <li>• 事前学習との違いや新たな発見を記入すると効果的です</li>
              <li>• パンフレット生成には1-2分程度かかる場合があります</li>
            </ul>
          </div>
        </div>
      </Container>
    </div>
  );
}
