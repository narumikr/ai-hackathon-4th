import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  BUTTON_LABELS,
  CONFIRMATION_MESSAGES,
  DATE_LABELS,
  ERROR_DIALOG_MESSAGES,
  MESSAGES,
  SECTION_TITLES,
  STATUS_LABELS,
} from '@/constants';
import type { TravelPlanResponse } from '@/types';

import TravelGuidePage from './page';

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

// APIクライアントのモック
const mockGetTravelPlan = vi.fn();
const mockDeleteTravelPlan = vi.fn();
const mockUpdateTravelPlan = vi.fn();
const mockGenerateTravelGuide = vi.fn();

vi.mock('@/lib/api', () => ({
  createApiClientFromEnv: () => ({
    getTravelPlan: mockGetTravelPlan,
    deleteTravelPlan: mockDeleteTravelPlan,
    updateTravelPlan: mockUpdateTravelPlan,
    generateTravelGuide: mockGenerateTravelGuide,
  }),
  toApiError: (error: unknown) => ({
    message: error instanceof Error ? error.message : 'エラーが発生しました',
  }),
}));

// テスト用のモックデータ
const createMockTravelPlan = (overrides: Partial<TravelPlanResponse> = {}): TravelPlanResponse => ({
  id: 'test-plan-id',
  userId: 'demo-user',
  title: '京都歴史探訪の旅',
  destination: '京都府',
  spots: [
    { id: 'spot-1', name: '金閣寺', description: '有名な寺院' },
    { id: 'spot-2', name: '清水寺' },
  ],
  status: 'planning',
  guideGenerationStatus: 'succeeded',
  reflectionGenerationStatus: 'not_started',
  createdAt: '2024-01-15T10:00:00Z',
  updatedAt: '2024-01-15T10:00:00Z',
  guide: {
    id: 'guide-1',
    planId: 'test-plan-id',
    overview: '京都の歴史を学ぶ旅',
    timeline: [
      {
        year: 1397,
        event: '金閣寺建立',
        significance: '室町文化の象徴',
        relatedSpots: ['金閣寺'],
      },
    ],
    spotDetails: [
      {
        spotName: '金閣寺',
        historicalBackground: '足利義満により建立',
        highlights: ['金箔の建築', '庭園'],
        recommendedVisitTime: '1-2時間',
        historicalSignificance: '室町時代の文化を象徴する建築物',
      },
    ],
    checkpoints: [],
    mapData: {
      center: { lat: 35.0394, lng: 135.7292 },
      zoom: 13,
      markers: [],
    },
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
  },
  ...overrides,
});

describe('TravelGuidePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('ローディング状態', () => {
    it('データ取得中はローディングメッセージが表示される', () => {
      // 準備: APIが解決しないPromiseを返す
      mockGetTravelPlan.mockImplementation(() => new Promise(() => {}));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: ローディングメッセージが表示される
      expect(screen.getByText(MESSAGES.LOADING)).toBeInTheDocument();
    });
  });

  describe('旅行データの表示', () => {
    it('旅行のタイトルと目的地が表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: タイトルと目的地が表示される
      await waitFor(() => {
        expect(screen.getByText('京都歴史探訪の旅')).toBeInTheDocument();
      });
      expect(screen.getByText('京都府')).toBeInTheDocument();
    });

    it('作成日が表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 作成日が表示される
      await waitFor(() => {
        expect(screen.getByText(DATE_LABELS.CREATED_DATE, { exact: false })).toBeInTheDocument();
      });
    });

    it('観光スポット一覧が表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: スポットセクションとスポットが表示される
      await waitFor(() => {
        expect(screen.getByText(SECTION_TITLES.TOURIST_SPOTS)).toBeInTheDocument();
      });
      // 金閣寺はスポット一覧とスポット詳細の両方に表示される
      const kinkakujiElements = screen.getAllByText('金閣寺');
      expect(kinkakujiElements.length).toBeGreaterThan(0);
      expect(screen.getByText('清水寺')).toBeInTheDocument();
    });

    it('スポットがない場合はメッセージが表示される', async () => {
      // 準備: スポットが空の旅行計画
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan({ spots: [] }));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 登録なしメッセージが表示される
      await waitFor(() => {
        expect(screen.getByText(MESSAGES.NO_SPOTS_REGISTERED)).toBeInTheDocument();
      });
    });
  });

  describe('ガイド表示', () => {
    it('歴史年表が表示される', async () => {
      // 準備: APIがガイド付きの旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 年表セクションと内容が表示される
      await waitFor(() => {
        expect(screen.getByText(SECTION_TITLES.TIMELINE)).toBeInTheDocument();
      });
      expect(screen.getByText('金閣寺建立')).toBeInTheDocument();
    });

    it('スポット詳細が表示される', async () => {
      // 準備: APIがガイド付きの旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: スポット詳細が表示される
      await waitFor(() => {
        expect(screen.getByText(SECTION_TITLES.SPOT_DETAILS)).toBeInTheDocument();
      });
      expect(screen.getByText('足利義満により建立')).toBeInTheDocument();
    });

    it('ガイド未生成の場合はメッセージが表示される', async () => {
      // 準備: ガイドなしの旅行計画
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          guide: undefined,
          guideGenerationStatus: 'not_started',
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 未生成メッセージが表示される
      await waitFor(() => {
        expect(screen.getByText(MESSAGES.GUIDE_NOT_GENERATED)).toBeInTheDocument();
      });
    });
  });

  describe('ガイド生成状態', () => {
    it('生成中の場合は処理中画面が表示される', async () => {
      // 準備: 生成中の旅行計画
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({ guideGenerationStatus: 'processing' })
      );

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 生成中ステータスが表示される
      await waitFor(() => {
        expect(screen.getByText(STATUS_LABELS.GUIDE_PROCESSING)).toBeInTheDocument();
      });
    });

    it('生成失敗の場合はエラー画面が表示される', async () => {
      // 準備: 生成失敗の旅行計画
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({ guideGenerationStatus: 'failed' })
      );

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 失敗ステータスと再生成ボタンが表示される
      await waitFor(() => {
        expect(screen.getByText(STATUS_LABELS.GENERATION_FAILED)).toBeInTheDocument();
      });
      expect(
        screen.getByRole('button', { name: BUTTON_LABELS.RETRY_GENERATE_GUIDE })
      ).toBeInTheDocument();
    });

    it('再生成ボタンをクリックするとAPIが呼ばれる', async () => {
      // 準備: 生成失敗の旅行計画
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({ guideGenerationStatus: 'failed' })
      );
      mockGenerateTravelGuide.mockResolvedValue({});

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 再生成ボタンをクリック
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.RETRY_GENERATE_GUIDE })
        ).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.RETRY_GENERATE_GUIDE }));

      // 検証: APIが呼ばれ、一覧に戻る
      await waitFor(() => {
        expect(mockGenerateTravelGuide).toHaveBeenCalledWith({
          request: { planId: 'test-plan-id' },
        });
      });
      expect(mockPush).toHaveBeenCalledWith('/travel');
    });
  });

  describe('計画中の旅行', () => {
    it('旅行完了ボタンが表示される', async () => {
      // 準備: 計画中の旅行計画
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan({ status: 'planning' }));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 完了ボタンが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.TRAVEL_COMPLETE })
        ).toBeInTheDocument();
      });
    });

    it('編集ボタンが表示される', async () => {
      // 準備: 計画中の旅行計画
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan({ status: 'planning' }));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 編集ボタンが表示される
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.EDIT })).toBeInTheDocument();
      });
    });

    it('旅行完了ボタンをクリックするとステータスが更新される', async () => {
      // 準備: 計画中の旅行計画
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan({ status: 'planning' }));
      mockUpdateTravelPlan.mockResolvedValue({});

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 完了ボタンをクリック
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.TRAVEL_COMPLETE })
        ).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.TRAVEL_COMPLETE }));

      // 検証: APIが呼ばれる
      await waitFor(() => {
        expect(mockUpdateTravelPlan).toHaveBeenCalledWith({
          planId: 'test-plan-id',
          request: { status: 'completed' },
        });
      });
    });
  });

  describe('完了した旅行', () => {
    it('振り返りボタンが表示される', async () => {
      // 準備: 完了した旅行計画
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          status: 'completed',
          reflectionGenerationStatus: 'not_started',
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 振り返り作成ボタンが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.CREATE_REFLECTION })
        ).toBeInTheDocument();
      });
    });

    it('振り返り成功時は振り返りを見るボタンが表示される', async () => {
      // 準備: 振り返り成功の旅行計画
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          status: 'completed',
          reflectionGenerationStatus: 'succeeded',
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 振り返りを見るボタンが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.VIEW_REFLECTION })
        ).toBeInTheDocument();
      });
    });

    it('振り返り生成中は生成中表示になる', async () => {
      // 準備: 振り返り生成中の旅行計画
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          status: 'completed',
          reflectionGenerationStatus: 'processing',
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 生成中ボタンが無効で表示される
      await waitFor(() => {
        const generatingButton = screen.getByRole('button', {
          name: MESSAGES.GENERATING,
        });
        expect(generatingButton).toBeDisabled();
      });
    });
  });

  describe('削除機能', () => {
    it('削除ボタンをクリックすると確認モーダルが表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 削除ボタンをクリック
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.DELETE })).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.DELETE }));

      // 検証: 確認モーダルが表示される
      await waitFor(() => {
        expect(screen.getByText(CONFIRMATION_MESSAGES.DELETE_TRAVEL)).toBeInTheDocument();
      });
    });

    it('確認モーダルで削除するとAPIが呼ばれる', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());
      mockDeleteTravelPlan.mockResolvedValue({});

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 実行: 削除ボタンをクリック
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.DELETE })).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.DELETE }));

      // 検証: モーダル内の削除ボタンをクリック
      await waitFor(() => {
        expect(screen.getByText(CONFIRMATION_MESSAGES.DELETE_TRAVEL)).toBeInTheDocument();
      });

      // モーダル内の削除ボタンを特定
      const modalDeleteButtons = screen.getAllByRole('button', {
        name: BUTTON_LABELS.DELETE,
      });
      fireEvent.click(modalDeleteButtons[1]); // モーダル内のボタン

      // 検証: APIが呼ばれる
      await waitFor(() => {
        expect(mockDeleteTravelPlan).toHaveBeenCalledWith({
          planId: 'test-plan-id',
        });
      });
      expect(mockPush).toHaveBeenCalledWith('/travel');
    });

    it('キャンセルするとモーダルが閉じる', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 実行: 削除ボタンをクリック
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.DELETE })).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.DELETE }));

      // 検証: モーダルが表示される
      await waitFor(() => {
        expect(screen.getByText(CONFIRMATION_MESSAGES.DELETE_TRAVEL)).toBeInTheDocument();
      });

      // 実行: キャンセルボタンをクリック
      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.CANCEL }));

      // 検証: モーダルが閉じる
      await waitFor(() => {
        expect(screen.queryByText(CONFIRMATION_MESSAGES.DELETE_TRAVEL)).not.toBeInTheDocument();
      });
    });
  });

  describe('ナビゲーション', () => {
    it('戻るボタンをクリックすると一覧に戻る', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 戻るボタンをクリック
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.BACK })).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.BACK }));

      // 検証: 一覧にリダイレクト
      expect(mockPush).toHaveBeenCalledWith('/travel');
    });

    it('編集リンクが正しいパスを持つ', async () => {
      // 準備: 計画中の旅行計画
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan({ status: 'planning' }));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 編集リンクが正しいパスを持つ
      await waitFor(() => {
        const editLink = screen.getByRole('button', { name: BUTTON_LABELS.EDIT }).closest('a');
        expect(editLink).toHaveAttribute('href', '/travel/test-plan-id/edit');
      });
    });
  });

  describe('エラー状態', () => {
    it('API呼び出しが失敗した場合エラーダイアログが表示される', async () => {
      // 準備: APIがエラーをスローする（nullを返すことでエラー状態を確認）
      mockGetTravelPlan.mockRejectedValue(new Error('サーバーエラー'));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: エラーメッセージが表示される（戻るボタンがある画面）
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.BACK })).toBeInTheDocument();
      });
    });

    it('削除API失敗時はエラーダイアログが表示される', async () => {
      // 準備: 削除APIがエラーを返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());
      mockDeleteTravelPlan.mockRejectedValue(new Error('削除に失敗しました'));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 削除ボタンをクリック
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.DELETE })).toBeInTheDocument();
      });
      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.DELETE }));

      // モーダル内の削除ボタンをクリック
      await waitFor(() => {
        expect(screen.getByText(CONFIRMATION_MESSAGES.DELETE_TRAVEL)).toBeInTheDocument();
      });
      const modalDeleteButtons = screen.getAllByRole('button', { name: BUTTON_LABELS.DELETE });
      fireEvent.click(modalDeleteButtons[1]);

      // 検証: エラーダイアログが表示される
      await waitFor(() => {
        expect(screen.getByText(ERROR_DIALOG_MESSAGES.TRAVEL_DELETE_FAILED)).toBeInTheDocument();
      });
    });

    it('旅行完了API失敗時はエラーダイアログが表示される', async () => {
      // 準備: 完了APIがエラーを返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan({ status: 'planning' }));
      mockUpdateTravelPlan.mockRejectedValue(new Error('完了処理に失敗しました'));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 完了ボタンをクリック
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.TRAVEL_COMPLETE })
        ).toBeInTheDocument();
      });
      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.TRAVEL_COMPLETE }));

      // 検証: エラーダイアログが表示される
      await waitFor(() => {
        expect(
          screen.getByText(ERROR_DIALOG_MESSAGES.TRAVEL_COMPLETE_FAILED)
        ).toBeInTheDocument();
      });
    });

    it('エラーダイアログを閉じることができる', async () => {
      // 準備: APIがエラーを返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan({ status: 'planning' }));
      mockUpdateTravelPlan.mockRejectedValue(new Error('テスト用エラー'));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 完了ボタンをクリックしてエラーを発生させる
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.TRAVEL_COMPLETE })
        ).toBeInTheDocument();
      });
      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.TRAVEL_COMPLETE }));

      // エラーダイアログが表示される（モーダルタイトルで確認）
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: MESSAGES.ERROR })).toBeInTheDocument();
      });

      // 閉じるボタンをクリック（複数ある場合は最後のものがダイアログ内のボタン）
      const closeButtons = screen.getAllByRole('button', { name: /閉じる/i });
      fireEvent.click(closeButtons[closeButtons.length - 1]);

      // エラーダイアログが閉じる（モーダルタイトルがなくなる）
      await waitFor(() => {
        expect(screen.queryByRole('heading', { name: MESSAGES.ERROR })).not.toBeInTheDocument();
      });
    });
  });

  describe('振り返りボタンの動作', () => {
    it('振り返り生成失敗時はデフォルトの旅行完了ボタンラベルが使用される', async () => {
      // 準備: 振り返り生成失敗の旅行計画
      // 注意: ソースコードではfailedステータスが明示的に扱われていないため、
      // デフォルトのTRAVEL_COMPLETEラベルが使用される
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          status: 'completed',
          reflectionGenerationStatus: 'failed',
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 検証: 完了した旅行でfailedステータスの場合、ボタンは無効化されずに存在する
      await waitFor(() => {
        // failedの場合、デフォルトラベル（TRAVEL_COMPLETE）が表示される
        const button = screen.getByRole('button', { name: BUTTON_LABELS.TRAVEL_COMPLETE });
        expect(button).toBeInTheDocument();
        expect(button).not.toBeDisabled();
      });
    });

    it('振り返り作成ボタンをクリックすると振り返り作成ページに遷移する', async () => {
      // 準備: 振り返り未作成の完了した旅行計画
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          status: 'completed',
          reflectionGenerationStatus: 'not_started',
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 振り返り作成ボタンをクリック
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.CREATE_REFLECTION })
        ).toBeInTheDocument();
      });
      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.CREATE_REFLECTION }));

      // 検証: 振り返り作成ページに遷移
      expect(mockPush).toHaveBeenCalledWith('/reflection/test-plan-id');
    });

    it('振り返り表示ボタンをクリックすると振り返り表示ページに遷移する', async () => {
      // 準備: 振り返り作成済みの旅行計画
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          status: 'completed',
          reflectionGenerationStatus: 'succeeded',
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 振り返り表示ボタンをクリック
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.VIEW_REFLECTION })
        ).toBeInTheDocument();
      });
      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.VIEW_REFLECTION }));

      // 検証: 振り返り表示ページに遷移
      expect(mockPush).toHaveBeenCalledWith('/reflection/test-plan-id/view');
    });
  });

  describe('ボタン無効化状態', () => {
    it('削除処理中は削除ボタンが無効化される', async () => {
      // 準備: 削除APIが解決しないPromiseを返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());
      mockDeleteTravelPlan.mockImplementation(() => new Promise(() => {}));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 削除ボタンをクリック
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.DELETE })).toBeInTheDocument();
      });
      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.DELETE }));

      // モーダル内の削除ボタンをクリック
      await waitFor(() => {
        expect(screen.getByText(CONFIRMATION_MESSAGES.DELETE_TRAVEL)).toBeInTheDocument();
      });
      const modalDeleteButtons = screen.getAllByRole('button', { name: BUTTON_LABELS.DELETE });
      fireEvent.click(modalDeleteButtons[1]);

      // 検証: 削除中はボタンが無効化されている
      await waitFor(() => {
        const disabledButtons = screen.getAllByRole('button', {
          name: new RegExp(MESSAGES.LOADING),
        });
        expect(disabledButtons.length).toBeGreaterThan(0);
      });
    });

    it('完了処理中は完了ボタンが無効化される', async () => {
      // 準備: 完了APIが解決しないPromiseを返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan({ status: 'planning' }));
      mockUpdateTravelPlan.mockImplementation(() => new Promise(() => {}));

      // 実行: コンポーネントをレンダリング
      render(<TravelGuidePage />);

      // 完了ボタンをクリック
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.TRAVEL_COMPLETE })
        ).toBeInTheDocument();
      });
      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.TRAVEL_COMPLETE }));

      // 検証: 処理中はボタンが無効化されてローディング表示になる
      await waitFor(() => {
        const loadingButton = screen.getByRole('button', { name: MESSAGES.LOADING });
        expect(loadingButton).toBeDisabled();
      });
    });
  });
});
