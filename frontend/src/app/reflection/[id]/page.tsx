

import { Container } from '@/components/layout';
import { Button, Emoji, TextArea } from '@/components/ui';
import {
  BUTTON_LABELS,
  EMOJI_LABELS,
  FORM_LABELS,
  HELP_TEXTS,
  HINTS,
  LABELS,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  PLACEHOLDERS,
} from '@/constants';
import { samplePreLearningInfo, sampleReflectionContents, sampleTravels } from '@/data';
import Link from 'next/link';
import { notFound } from 'next/navigation';

export default async function ReflectionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const travel = sampleTravels.find(t => t.id === id);

  if (!travel) {
    notFound();
  }

  const isCompleted = travel.hasReflection;
  const reflectionContent = isCompleted
    ? sampleReflectionContents.find(r => r.travelId === id)
    : undefined;

  // 閲覧モード（完了済み）
  if (isCompleted && reflectionContent) {
    return (
      <div className="py-8">
        <Container>
          <div className="mx-auto max-w-4xl">
            <div className="mb-8 flex items-start justify-between">
              <div>
                <h1 className="mb-2 font-bold text-3xl text-neutral-900">
                  {PAGE_TITLES.REFLECTION_CREATE}
                </h1>
                <p className="text-neutral-600">{PAGE_DESCRIPTIONS.REFLECTION_LIST}</p>
              </div>
              <Link href="/reflection">
                <Button variant="ghost">{BUTTON_LABELS.BACK}</Button>
              </Link>
            </div>

            {/* 旅行情報 */}
            <div className="mb-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
              <h2 className="mb-1 font-semibold text-lg text-neutral-900">{travel.title}</h2>
              <p className="text-neutral-600 text-sm">
                {LABELS.COMPLETED_DATE} {travel.completedAt}
              </p>
            </div>

            {/* 写真と感想（閲覧のみ） */}
            <section className="mb-8 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 font-bold text-neutral-900 text-xl">
                {FORM_LABELS.PHOTO_COMMENTS}
              </h2>
              <div className="space-y-6">
                {reflectionContent.photos.map(photo => (
                  <div
                    key={photo.id}
                    className="border-neutral-200 border-b pb-6 last:border-0 last:pb-0"
                  >
                    <div className="mb-3 flex items-start gap-4">
                      <div className="flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-lg bg-neutral-200">
                        <span className="text-2xl">
                          <Emoji symbol="🖼️" label={EMOJI_LABELS.PICTURE} />
                        </span>
                      </div>
                      <div className="flex-1">
                        <h3 className="mb-2 font-semibold text-neutral-700 text-sm">
                          {LABELS.PHOTO_NUMBER} {photo.id}
                        </h3>
                        <p className="whitespace-pre-wrap text-neutral-800">{photo.comment}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* 全体的な感想（閲覧のみ） */}
            <section className="mb-8 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 font-bold text-neutral-900 text-xl">
                {FORM_LABELS.OVERALL_IMPRESSION}
              </h2>
              <p className="whitespace-pre-wrap text-neutral-800">
                {reflectionContent.overallComment}
              </p>
            </section>
          </div>
        </Container>
      </div>
    );
  }

  // 作成モード（未完了）
  return (
    <div className="py-8">
      <Container>
        <div className="mx-auto max-w-4xl">
          <div className="mb-8">
            <h1 className="mb-2 font-bold text-3xl text-neutral-900">
              {PAGE_TITLES.REFLECTION_CREATE}
            </h1>
            <p className="text-neutral-600">{PAGE_DESCRIPTIONS.REFLECTION_CREATE}</p>
          </div>

          {/* 旅行情報 */}
          <div className="mb-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
            <h2 className="mb-1 font-semibold text-lg text-neutral-900">{travel.title}</h2>
            <p className="text-neutral-600 text-sm">
              {LABELS.COMPLETED_DATE} {travel.completedAt}
            </p>
          </div>

          {/* 写真アップロード */}
          <section className="mb-8 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 font-bold text-neutral-900 text-xl">{FORM_LABELS.PHOTO_UPLOAD}</h2>

            {/* ドロップゾーン */}
            <button
              type="button"
              className="mb-6 flex h-64 w-full cursor-pointer items-center justify-center rounded-lg border-2 border-neutral-300 border-dashed bg-neutral-50 transition-colors hover:border-primary-400"
              aria-label={PLACEHOLDERS.UPLOAD_INSTRUCTION}
            >
              <div className="text-center">
                <div className="mb-2 text-6xl">
                  <Emoji symbol="📤" label="アップロード" />
                </div>
                <p className="mb-2 font-medium text-neutral-700">
                  {PLACEHOLDERS.UPLOAD_INSTRUCTION}
                </p>
                <p className="text-neutral-500 text-sm">{HELP_TEXTS.UPLOAD_FORMAT}</p>
              </div>
            </button>

            {/* アップロード済み写真プレビュー（サンプル） */}
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
              {[1, 2, 3].map(i => (
                <div
                  key={i}
                  className="group relative aspect-square overflow-hidden rounded-lg bg-neutral-200"
                >
                  <div className="absolute inset-0 flex items-center justify-center bg-neutral-300">
                    <span className="text-4xl text-neutral-500">
                      <Emoji symbol="🖼️" label={EMOJI_LABELS.PICTURE} />
                    </span>
                  </div>
                  <button
                    type="button"
                    className="absolute top-2 right-2 flex h-6 w-6 items-center justify-center rounded-full bg-danger text-white text-xs opacity-0 transition-opacity group-hover:opacity-100"
                    aria-label="削除"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </section>

          {/* 各写真への感想 */}
          <section className="mb-8 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 font-bold text-neutral-900 text-xl">
              {FORM_LABELS.PHOTO_COMMENTS}
            </h2>
            <div className="space-y-6">
              {[1, 2, 3].map(i => (
                <div key={i} className="border-neutral-200 border-b pb-6 last:border-0 last:pb-0">
                  <div className="mb-3 flex items-start gap-4">
                    <div className="flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-lg bg-neutral-200">
                      <span className="text-2xl">
                        <Emoji symbol="🖼️" label={EMOJI_LABELS.PICTURE} />
                      </span>
                    </div>
                    <div className="flex-1">
                      <h3 className="mb-2 font-semibold text-neutral-700 text-sm">
                        {LABELS.PHOTO_NUMBER} {i}
                      </h3>
                      <TextArea placeholder={PLACEHOLDERS.PHOTO_COMMENT} rows={3} fullWidth />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 全体的な感想 */}
          <section className="mb-8 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 font-bold text-neutral-900 text-xl">
              {FORM_LABELS.OVERALL_IMPRESSION}
            </h2>
            <TextArea
              placeholder={PLACEHOLDERS.OVERALL_COMMENT}
              rows={6}
              fullWidth
              maxLength={1000}
              showCount
            />
          </section>

          {/* 事前学習情報の表示（参考用） */}
          <section className="mb-8 rounded-lg border border-neutral-200 bg-neutral-50 p-6">
            <h2 className="mb-4 font-bold text-neutral-900 text-xl">{FORM_LABELS.PRE_LEARNING}</h2>
            <div className="space-y-3 text-sm">
              {samplePreLearningInfo.map(info => (
                <div key={info.spotName} className="rounded border border-neutral-200 bg-white p-3">
                  <h3 className="mb-1 font-semibold text-neutral-900">{info.spotName}</h3>
                  <p className="text-neutral-600">{info.description}</p>
                </div>
              ))}
            </div>
          </section>

          {/* アクションボタン */}
          <div className="flex flex-col gap-4 sm:flex-row">
            <Button variant="ghost" size="lg" className="flex-1">
              {BUTTON_LABELS.CANCEL}
            </Button>
            <Button variant="primary" size="lg" className="flex-1">
              {BUTTON_LABELS.GENERATE_REFLECTION}
            </Button>
          </div>

          {/* 注意事項 */}
          <div className="mt-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
            <h3 className="mb-2 font-semibold text-primary-900 text-sm">{LABELS.HINT_TITLE}</h3>
            <ul className="space-y-1 text-primary-800 text-sm">
              {HINTS.REFLECTION_CREATE.map(hint => (
                <li key={hint}>• {hint}</li>
              ))}
            </ul>
          </div>
        </div>
      </Container>
    </div>
  );
}
