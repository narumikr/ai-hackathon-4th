import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  BUTTON_LABELS,
  FORM_LABELS,
  HINTS,
  LABELS,
  MESSAGES,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  SECTION_TITLES,
} from '@/constants';
import type { TravelPlanResponse } from '@/types';

import ReflectionDetailPage from './page';

// Next.js の Link コンポーネントをモック
vi.mock('next/link', () => ({
  default: ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => <a href={href}>{children}</a>,
}));

// Next.js の useRouter と useParams をモック
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useParams: () => ({
    id: 'test-plan-id',
  }),
}));

// APIクライアントのモック
const mockGetTravelPlan = vi.fn();
const mockUploadSpotReflection = vi.fn();
const mockCreateReflection = vi.fn();

vi.mock('@/lib/api', () => ({
  createApiClientFromEnv: () => ({
    getTravelPlan: mockGetTravelPlan,
    uploadSpotReflection: mockUploadSpotReflection,
    createReflection: mockCreateReflection,
  }),
  toApiError: (error: unknown) => ({
    message: error instanceof Error ? error.message : 'エラーが発生しました',
  }),
}));

// SpotReflectionForm と SpotAdder コンポーネントをシンプルにモック
vi.mock('@/components/features/reflection', () => ({
  SpotReflectionForm: ({
    spot,
  }: {
    spot: { id: string; name: string; isAdded: boolean };
  }) => (
    <div data-testid={`spot-form-${spot.id}`}>
      <span data-testid={`spot-name-${spot.id}`}>{spot.name}</span>
      {spot.isAdded && <span data-testid={`added-marker-${spot.id}`}>追加済み</span>}
    </div>
  ),
  SpotAdder: () => (
    <div data-testid="spot-adder">スポット追加エリア</div>
  ),
}));

// テスト用のモックデータ
const createMockTravelPlan = (
  overrides: Partial<TravelPlanResponse> = {}
): TravelPlanResponse => ({
  id: 'test-plan-id',
  userId: 'user-1',
  title: '京都歴史探訪の旅',
  destination: '京都府',
  spots: [
    { id: 'spot-1', name: '金閣寺', description: '有名な金箔のお寺' },
    { id: 'spot-2', name: '清水寺', description: '舞台で有名なお寺' },
  ],
  status: 'completed',
  guideGenerationStatus: 'succeeded',
  reflectionGenerationStatus: 'not_started',
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-15T00:00:00Z',
  guide: null,
  reflection: null,
  pamphlet: null,
  ...overrides,
});

describe('ReflectionDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('初期表示', () => {
    it('ページタイトルと説明が表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: タイトルと説明が表示される
      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: PAGE_TITLES.REFLECTION_CREATE })
        ).toBeInTheDocument();
      });
      expect(
        screen.getByText(PAGE_DESCRIPTIONS.REFLECTION_CREATE)
      ).toBeInTheDocument();
    });

    it('戻るボタンが表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: 戻るボタンが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.BACK })
        ).toBeInTheDocument();
      });
    });

    it('旅行情報が表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: 旅行タイトルと目的地が表示される
      await waitFor(() => {
        expect(screen.getByText('京都歴史探訪の旅')).toBeInTheDocument();
      });
      expect(screen.getByText('京都府')).toBeInTheDocument();
    });

    it('完了日ラベルが表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: 完了日ラベルが表示される
      await waitFor(() => {
        expect(screen.getByText(new RegExp(LABELS.COMPLETED_DATE))).toBeInTheDocument();
      });
    });

    it('ヒントセクションが表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: ヒントタイトルが表示される
      await waitFor(() => {
        expect(screen.getByText(LABELS.HINT_TITLE)).toBeInTheDocument();
      });
      // 各ヒントが表示される
      for (const hint of HINTS.REFLECTION_CREATE) {
        expect(screen.getByText(`• ${hint}`)).toBeInTheDocument();
      }
    });

    it('振り返り生成ボタンが表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: 生成ボタンが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.GENERATE_REFLECTION })
        ).toBeInTheDocument();
      });
    });

    it('キャンセルボタンが表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: キャンセルボタンが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.CANCEL })
        ).toBeInTheDocument();
      });
    });
  });

  describe('ローディング状態', () => {
    it('データ取得中はローディングメッセージが表示される', () => {
      // 準備: APIが解決しないPromiseを返す
      mockGetTravelPlan.mockImplementation(() => new Promise(() => {}));

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: ローディングメッセージが表示される
      expect(screen.getByText(MESSAGES.LOADING)).toBeInTheDocument();
    });
  });

  describe('エラー状態', () => {
    it('API呼び出しが失敗した場合エラーダイアログが表示される', async () => {
      // 準備: APIがエラーをスローする
      mockGetTravelPlan.mockRejectedValue(new Error('旅行計画が見つかりません'));

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: エラーダイアログが表示され、戻るボタンがある
      await waitFor(() => {
        expect(screen.getByText('旅行計画が見つかりません')).toBeInTheDocument();
      });
      expect(
        screen.getByRole('button', { name: BUTTON_LABELS.BACK })
      ).toBeInTheDocument();
    });
  });

  describe('リダイレクト', () => {
    it('既に振り返りがある場合は閲覧ページにリダイレクトされる', async () => {
      // 準備: 既に振り返りがある旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          reflection: {
            id: 'reflection-1',
            planId: 'test-plan-id',
            userId: 'user-1',
            photos: [],
            spotNotes: {},
            createdAt: '2024-01-20T00:00:00Z',
          },
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: 閲覧ページにリダイレクトされる
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/reflection/test-plan-id/view');
      });
    });
  });

  describe('スポット管理', () => {
    it('旅行計画のスポットが初期化される', async () => {
      // 準備: スポットを持つ旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: 各スポットのフォームが表示される
      await waitFor(() => {
        expect(screen.getByTestId('spot-name-spot-1')).toHaveTextContent('金閣寺');
      });
      expect(screen.getByTestId('spot-name-spot-2')).toHaveTextContent('清水寺');
    });

    it('スポットごとの振り返りセクションが表示される', async () => {
      // 準備: 旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: セクションタイトルが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: SECTION_TITLES.SPOT_REFLECTIONS })
        ).toBeInTheDocument();
      });
    });

    it('スポット追加エリアが表示される', async () => {
      // 準備: 旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: スポット追加エリアが表示される
      await waitFor(() => {
        expect(screen.getByTestId('spot-adder')).toBeInTheDocument();
      });
    });
  });

  describe('全体コメント', () => {
    it('全体的な感想セクションが表示される', async () => {
      // 準備: 旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: 全体的な感想セクションが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: new RegExp(FORM_LABELS.OVERALL_IMPRESSION) })
        ).toBeInTheDocument();
      });
    });

    it('コメント入力欄が表示される', async () => {
      // 準備: 旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: テキストエリアが表示される
      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });
    });

    it('コメントを入力できる', async () => {
      // 準備: 旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      // 実行: コメントを入力
      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: '素晴らしい旅でした' } });

      // 検証: 入力値が反映される
      expect(textarea).toHaveValue('素晴らしい旅でした');
    });
  });

  describe('ナビゲーション', () => {
    it('戻るボタンのリンクが正しいパスを持つ', async () => {
      // 準備: 旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: 戻るボタンが正しいパスを持つ
      await waitFor(() => {
        const backLink = screen
          .getByRole('button', { name: BUTTON_LABELS.BACK })
          .closest('a');
        expect(backLink).toHaveAttribute('href', '/reflection');
      });
    });

    it('キャンセルボタンのリンクが正しいパスを持つ', async () => {
      // 準備: 旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: キャンセルボタンが正しいパスを持つ
      await waitFor(() => {
        const cancelLink = screen
          .getByRole('button', { name: BUTTON_LABELS.CANCEL })
          .closest('a');
        expect(cancelLink).toHaveAttribute('href', '/reflection');
      });
    });
  });

  describe('API呼び出し', () => {
    it('正しいプランIDでAPIが呼び出される', async () => {
      // 準備: 旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionDetailPage />);

      // 検証: 正しい引数でAPIが呼び出される
      await waitFor(() => {
        expect(mockGetTravelPlan).toHaveBeenCalledWith({ planId: 'test-plan-id' });
      });
    });
  });
});
