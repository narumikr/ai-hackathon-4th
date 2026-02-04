import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { BUTTON_LABELS, MESSAGES, PAGE_TITLES, STATUS_LABELS } from '@/constants';
import type { TravelPlanResponse } from '@/types';
import type { ReflectionPamphletResponse } from '@/types/reflection';

import ReflectionViewPage from './page';

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

// Next.js の useParams をモック
vi.mock('next/navigation', () => ({
  useParams: () => ({
    id: 'test-plan-id',
  }),
}));

// APIクライアントのモック
const mockGetTravelPlan = vi.fn();

vi.mock('@/lib/api', () => ({
  createApiClientFromEnv: () => ({
    getTravelPlan: mockGetTravelPlan,
  }),
  toApiError: (error: unknown) => ({
    message: error instanceof Error ? error.message : 'エラーが発生しました',
  }),
}));

// GenerationStatusView コンポーネントをモック
vi.mock('@/components/features/common', () => ({
  ErrorDialog: ({
    isOpen,
    onClose,
    message,
  }: {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    message: string;
  }) =>
    isOpen ? (
      <div data-testid="error-dialog">
        {message}
        <button type="button" onClick={onClose}>
          閉じる
        </button>
      </div>
    ) : null,
  GenerationStatusView: ({
    title,
    statusLabel,
    hintMessage,
    isRefreshing,
    onRefresh,
  }: {
    title: string;
    status: string;
    statusLabel: string;
    hintMessage: string;
    isRefreshing: boolean;
    onRefresh: () => void;
    backHref: string;
  }) => (
    <div data-testid="generation-status-view">
      <h1>{title}</h1>
      <span data-testid="status-label">{statusLabel}</span>
      <span data-testid="hint-message">{hintMessage}</span>
      <button
        type="button"
        onClick={onRefresh}
        disabled={isRefreshing}
        data-testid="refresh-button"
      >
        {isRefreshing ? '更新中...' : '更新'}
      </button>
    </div>
  ),
}));

// ReflectionViewer コンポーネントをモック
vi.mock('@/components/features/reflection', () => ({
  ReflectionViewer: ({
    travel,
    pamphlet,
  }: {
    travel: TravelPlanResponse;
    pamphlet: ReflectionPamphletResponse;
  }) => (
    <div data-testid="reflection-viewer">
      <span data-testid="travel-title">{travel.title}</span>
      <span data-testid="travel-summary">{pamphlet.travelSummary}</span>
      {pamphlet.spotReflections.map(spot => (
        <div key={spot.spotName} data-testid={`spot-${spot.spotName}`}>
          <span>{spot.spotName}</span>
          <span>{spot.reflection}</span>
        </div>
      ))}
      {pamphlet.nextTripSuggestions.map((suggestion, idx) => (
        <span key={suggestion} data-testid={`suggestion-${idx}`}>
          {suggestion}
        </span>
      ))}
    </div>
  ),
}));

// テスト用のモックデータ
const createMockPamphlet = (
  overrides: Partial<ReflectionPamphletResponse> = {}
): ReflectionPamphletResponse => ({
  travelSummary:
    '京都での素晴らしい歴史探訪でした。金閣寺と清水寺を巡り、日本の歴史と文化を深く学びました。',
  spotReflections: [
    {
      spotName: '金閣寺',
      reflection: '金箔の輝きが美しく、室町時代の栄華を感じました。',
    },
    {
      spotName: '清水寺',
      reflection: '舞台からの眺望は圧巻。清水の舞台から飛び降りる勇気を感じました。',
    },
  ],
  nextTripSuggestions: [
    '奈良の東大寺を訪れて大仏を見る',
    '姫路城で城郭建築を学ぶ',
    '伏見稲荷大社の千本鳥居を歩く',
  ],
  ...overrides,
});

const createMockTravelPlan = (overrides: Partial<TravelPlanResponse> = {}): TravelPlanResponse => ({
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
  reflectionGenerationStatus: 'succeeded',
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-15T00:00:00Z',
  guide: null,
  reflection: null,
  pamphlet: createMockPamphlet(),
  ...overrides,
});

describe('ReflectionViewPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('ローディング状態', () => {
    it('データ取得中はローディングメッセージが表示される', () => {
      // 準備: APIが解決しないPromiseを返す
      mockGetTravelPlan.mockImplementation(() => new Promise(() => {}));

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: ローディングメッセージが表示される
      expect(screen.getByText(MESSAGES.LOADING)).toBeInTheDocument();
    });
  });

  describe('エラー状態', () => {
    it('API呼び出しが失敗した場合エラーダイアログが表示される', async () => {
      // 準備: APIがエラーをスローする
      mockGetTravelPlan.mockRejectedValue(new Error('旅行計画が見つかりません'));

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: エラーダイアログが表示され、戻るボタンがある
      await waitFor(() => {
        expect(screen.getByTestId('error-dialog')).toHaveTextContent('旅行計画が見つかりません');
      });
      expect(screen.getByRole('button', { name: BUTTON_LABELS.BACK })).toBeInTheDocument();
    });

    it('振り返りが見つからない場合エラーダイアログが表示される', async () => {
      // 準備: pamphletがnullの旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          pamphlet: null,
          reflectionGenerationStatus: 'not_started',
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: エラーダイアログが表示される
      await waitFor(() => {
        expect(screen.getByTestId('error-dialog')).toHaveTextContent(MESSAGES.REFLECTION_NOT_FOUND);
      });
    });
  });

  describe('生成中状態', () => {
    it('振り返り生成中の場合は生成中ビューが表示される', async () => {
      // 準備: 生成中の旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          reflectionGenerationStatus: 'processing',
          pamphlet: null,
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: 生成中ビューが表示される
      await waitFor(() => {
        expect(screen.getByTestId('generation-status-view')).toBeInTheDocument();
      });
      expect(screen.getByText(PAGE_TITLES.REFLECTION_PAMPHLET)).toBeInTheDocument();
      expect(screen.getByTestId('status-label')).toHaveTextContent(
        STATUS_LABELS.REFLECTION_PROCESSING
      );
    });

    it('生成中ビューで更新ボタンをクリックするとAPIが再呼び出される', async () => {
      // 準備: 生成中の旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          reflectionGenerationStatus: 'processing',
          pamphlet: null,
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      await waitFor(() => {
        expect(screen.getByTestId('generation-status-view')).toBeInTheDocument();
      });

      // 実行: 更新ボタンをクリック
      const refreshButton = screen.getByTestId('refresh-button');
      fireEvent.click(refreshButton);

      // 検証: APIが2回呼び出される（初回 + 更新）
      await waitFor(() => {
        expect(mockGetTravelPlan).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('正常表示', () => {
    it('ページタイトルが表示される', async () => {
      // 準備: pamphletを持つ旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: タイトルが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: PAGE_TITLES.REFLECTION_PAMPHLET })
        ).toBeInTheDocument();
      });
    });

    it('戻るボタンが表示される', async () => {
      // 準備: pamphletを持つ旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: 戻るボタンが表示される
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.BACK })).toBeInTheDocument();
      });
    });

    it('ReflectionViewerコンポーネントが表示される', async () => {
      // 準備: pamphletを持つ旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: ReflectionViewerが表示される
      await waitFor(() => {
        expect(screen.getByTestId('reflection-viewer')).toBeInTheDocument();
      });
    });

    it('旅行タイトルが正しく渡される', async () => {
      // 準備: pamphletを持つ旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: 旅行タイトルが表示される
      await waitFor(() => {
        expect(screen.getByTestId('travel-title')).toHaveTextContent('京都歴史探訪の旅');
      });
    });

    it('旅行サマリーが表示される', async () => {
      // 準備: pamphletを持つ旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: サマリーが表示される
      await waitFor(() => {
        expect(screen.getByTestId('travel-summary')).toHaveTextContent(
          '京都での素晴らしい歴史探訪でした'
        );
      });
    });

    it('スポットごとの振り返りが表示される', async () => {
      // 準備: pamphletを持つ旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: 各スポットの振り返りが表示される
      await waitFor(() => {
        expect(screen.getByTestId('spot-金閣寺')).toBeInTheDocument();
      });
      expect(screen.getByTestId('spot-清水寺')).toBeInTheDocument();
    });

    it('次の旅行提案が表示される', async () => {
      // 準備: pamphletを持つ旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: 提案が表示される
      await waitFor(() => {
        expect(screen.getByTestId('suggestion-0')).toHaveTextContent(
          '奈良の東大寺を訪れて大仏を見る'
        );
      });
      expect(screen.getByTestId('suggestion-1')).toHaveTextContent('姫路城で城郭建築を学ぶ');
      expect(screen.getByTestId('suggestion-2')).toHaveTextContent('伏見稲荷大社の千本鳥居を歩く');
    });
  });

  describe('ナビゲーション', () => {
    it('戻るボタンのリンクが正しいパスを持つ', async () => {
      // 準備: pamphletを持つ旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: 戻るボタンが正しいパスを持つ
      await waitFor(() => {
        const backLink = screen.getByRole('button', { name: BUTTON_LABELS.BACK }).closest('a');
        expect(backLink).toHaveAttribute('href', '/reflection');
      });
    });
  });

  describe('API呼び出し', () => {
    it('正しいプランIDでAPIが呼び出される', async () => {
      // 準備: pamphletを持つ旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: 正しい引数でAPIが呼び出される
      await waitFor(() => {
        expect(mockGetTravelPlan).toHaveBeenCalledWith({ planId: 'test-plan-id' });
      });
    });
  });

  describe('エラーダイアログ操作', () => {
    it('エラーダイアログを閉じることができる', async () => {
      // 準備: APIがエラーをスローする
      mockGetTravelPlan.mockRejectedValue(new Error('旅行計画が見つかりません'));

      // 実行: コンポーネントをレンダリング
      render(<ReflectionViewPage />);

      // 検証: エラーダイアログが表示される
      await waitFor(() => {
        expect(screen.getByText('旅行計画が見つかりません')).toBeInTheDocument();
      });

      // 実行: 閉じるボタンをクリック
      const closeButtons = screen.getAllByRole('button', { name: /閉じる/i });
      fireEvent.click(closeButtons[closeButtons.length - 1]);

      // 検証: エラーダイアログが閉じる
      await waitFor(() => {
        expect(screen.queryByRole('heading', { name: MESSAGES.ERROR })).not.toBeInTheDocument();
      });
    });
  });
});
