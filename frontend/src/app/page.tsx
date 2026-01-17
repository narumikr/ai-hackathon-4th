import { Container } from '@/components/layout';
import { Button } from '@/components/ui';
import { APP_DESCRIPTION, APP_NAME } from '@/constants';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="bg-gradient-to-b from-primary-50 to-white">
      {/* Hero Section */}
      <section className="py-16 lg:py-24">
        <Container>
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="mb-6 font-bold text-4xl text-neutral-900 lg:text-5xl">{APP_NAME}</h1>
            <p className="mb-8 text-lg text-neutral-600 lg:text-xl">{APP_DESCRIPTION}</p>
            <p className="mb-12 text-base text-neutral-500">
              旅行前に歴史的背景を学び、旅行後に写真と共に振り返る。
              <br />
              AIが生成する歴史学習特化型の旅行ガイドで、より深い旅の体験を。
            </p>
            <div className="flex flex-col justify-center gap-4 sm:flex-row">
              <Link href="/travel/new">
                <Button size="lg">新しい旅行を作成</Button>
              </Link>
              <Link href="/travel">
                <Button variant="secondary" size="lg">
                  旅行一覧を見る
                </Button>
              </Link>
            </div>
          </div>
        </Container>
      </section>

      {/* Features Section */}
      <section className="bg-white py-16">
        <Container>
          <h2 className="mb-12 text-center font-bold text-3xl text-neutral-900">主な機能</h2>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <div className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
              <div className="mb-4 text-4xl">📚</div>
              <h3 className="mb-2 font-semibold text-neutral-900 text-xl">事前学習ガイド生成</h3>
              <p className="text-neutral-600">
                訪問予定の観光スポットの歴史的背景や見どころを、AIが分かりやすくまとめた旅行ガイドを自動生成。
              </p>
            </div>

            {/* Feature 2 */}
            <div className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
              <div className="mb-4 text-4xl">🗺️</div>
              <h3 className="mb-2 font-semibold text-neutral-900 text-xl">歴史年表と地図</h3>
              <p className="text-neutral-600">
                時系列で整理された歴史年表と、歴史的コンテキスト付きの地図で、訪問地の理解を深めます。
              </p>
            </div>

            {/* Feature 3 */}
            <div className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
              <div className="mb-4 text-4xl">📸</div>
              <h3 className="mb-2 font-semibold text-neutral-900 text-xl">旅行後の振り返り</h3>
              <p className="text-neutral-600">
                旅行写真と感想をアップロードすると、AIが事前学習との比較を含めた振り返りパンフレットを生成。
              </p>
            </div>
          </div>
        </Container>
      </section>

      {/* How to Use Section */}
      <section className="bg-neutral-50 py-16">
        <Container>
          <h2 className="mb-12 text-center font-bold text-3xl text-neutral-900">使い方</h2>
          <div className="mx-auto max-w-3xl space-y-8">
            {/* Step 1 */}
            <div className="flex gap-4">
              <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-primary-400 font-bold text-lg text-primary-950">
                1
              </div>
              <div>
                <h3 className="mb-2 font-semibold text-neutral-900 text-xl">旅行計画を作成</h3>
                <p className="text-neutral-600">
                  訪問予定の目的地と観光スポットを入力します。地図上からスポットを選択することもできます。
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-4">
              <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-primary-400 font-bold text-lg text-primary-950">
                2
              </div>
              <div>
                <h3 className="mb-2 font-semibold text-neutral-900 text-xl">旅行ガイドを確認</h3>
                <p className="text-neutral-600">
                  AIが生成した歴史的背景や見どころ、チェックポイントを含む旅行ガイドを確認・印刷できます。
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-4">
              <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-primary-400 font-bold text-lg text-primary-950">
                3
              </div>
              <div>
                <h3 className="mb-2 font-semibold text-neutral-900 text-xl">旅行を楽しむ</h3>
                <p className="text-neutral-600">
                  生成されたガイドを参考に、歴史的な背景を理解しながら旅行を楽しみます。
                </p>
              </div>
            </div>

            {/* Step 4 */}
            <div className="flex gap-4">
              <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-primary-400 font-bold text-lg text-primary-950">
                4
              </div>
              <div>
                <h3 className="mb-2 font-semibold text-neutral-900 text-xl">振り返りを作成</h3>
                <p className="text-neutral-600">
                  旅行後、写真と感想をアップロードすると、AIが学習体験を振り返るパンフレットを生成します。
                </p>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-100 py-16">
        <Container>
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="mb-4 font-bold text-3xl text-neutral-900">
              さあ、歴史を学ぶ旅を始めましょう
            </h2>
            <p className="mb-8 text-lg text-neutral-600">
              次の旅行をより深い学びの体験に変えてみませんか？
            </p>
            <Link href="/travel/new">
              <Button size="lg">今すぐ始める</Button>
            </Link>
          </div>
        </Container>
      </section>
    </div>
  );
}
