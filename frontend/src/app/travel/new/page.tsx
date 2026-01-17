import { Container } from '@/components/layout';
import { Button, TextField } from '@/components/ui';
import {
  BUTTON_LABELS,
  FORM_LABELS,
  HELP_TEXTS,
  HINTS,
  LABELS,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  PLACEHOLDERS,
  PLACEHOLDER_MESSAGES,
} from '@/constants';

export default function TravelNewPage() {
  return (
    <div className="py-8">
      <Container variant="standard">
        <div className="mx-auto max-w-2xl">
          <div className="mb-8">
            <h1 className="mb-2 font-bold text-3xl text-neutral-900">{PAGE_TITLES.TRAVEL_NEW}</h1>
            <p className="text-neutral-600">{PAGE_DESCRIPTIONS.TRAVEL_NEW}</p>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-8 shadow-sm">
            <form className="space-y-6">
              {/* 旅行タイトル */}
              <div>
                <TextField
                  label={FORM_LABELS.TRAVEL_TITLE}
                  placeholder={PLACEHOLDERS.TRAVEL_TITLE}
                  fullWidth
                  required
                />
              </div>

              {/* 目的地 */}
              <div>
                <TextField
                  label={FORM_LABELS.DESTINATION}
                  placeholder={PLACEHOLDERS.DESTINATION}
                  helpText={HELP_TEXTS.DESTINATION}
                  fullWidth
                  required
                />
              </div>

              {/* 観光スポット */}
              <div>
                <div className="mb-2 block font-medium text-neutral-700 text-sm">
                  {FORM_LABELS.SPOTS}
                  <span className="ml-1 text-danger">*</span>
                </div>
                <div className="space-y-3">
                  <TextField placeholder={PLACEHOLDERS.SPOT_1} fullWidth />
                  <TextField placeholder={PLACEHOLDERS.SPOT_2} fullWidth />
                  <TextField placeholder={PLACEHOLDERS.SPOT_3} fullWidth />
                </div>
                <p className="mt-2 text-neutral-500 text-sm">{HELP_TEXTS.SPOTS}</p>
              </div>

              {/* スポット追加ボタン */}
              <div>
                <Button variant="ghost" fullWidth>
                  {BUTTON_LABELS.ADD_SPOT}
                </Button>
              </div>

              {/* 地図選択エリア（プレースホルダー） */}
              <div>
                <div className="mb-2 block font-medium text-neutral-700 text-sm">
                  {FORM_LABELS.SELECT_FROM_MAP}
                </div>
                <div className="flex h-64 items-center justify-center rounded-lg border-2 border-neutral-300 border-dashed bg-neutral-100">
                  <div className="text-center">
                    <div className="mb-2 text-4xl">🗺️</div>
                    <p className="text-neutral-500">{PLACEHOLDER_MESSAGES.MAP_COMING_SOON}</p>
                  </div>
                </div>
              </div>

              {/* アクションボタン */}
              <div className="flex gap-4 pt-4">
                <Button variant="ghost" className="flex-1">
                  {BUTTON_LABELS.CANCEL}
                </Button>
                <Button variant="primary" className="flex-1">
                  {BUTTON_LABELS.GENERATE_GUIDE}
                </Button>
              </div>
            </form>
          </div>

          {/* 注意事項 */}
          <div className="mt-6 rounded-lg border border-primary-200 bg-primary-50 p-4">
            <h3 className="mb-2 font-semibold text-primary-900 text-sm">{LABELS.HINT_TITLE}</h3>
            <ul className="space-y-1 text-primary-800 text-sm">
              {HINTS.TRAVEL_NEW.map((hint, index) => (
                <li key={`hint-${index}`}>• {hint}</li>
              ))}
            </ul>
          </div>
        </div>
      </Container>
    </div>
  );
}
