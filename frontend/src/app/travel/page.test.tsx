import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  BUTTON_LABELS,
  MESSAGES,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  STATUS_LABELS,
} from '@/constants';
import type { TravelPlanListResponse } from '@/types';

import TravelListPage from './page';

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
const mockListTravelPlans = vi.fn();

vi.mock('@/lib/api', () => ({
  createApiClientFromEnv: () => ({
    listTravelPlans: mockListTravelPlans,
  }),
  toApiError: (error: unknown) => ({
    message: error instanceof Error ? error.message : 'エラーが発生しました',
  }),
}));

// テスト用のモックデータ
const createMockTravelPlan = (
  overrides: Partial<TravelPlanListResponse> = {}
): TravelPlanListResponse => ({
  id: 'plan-1',
  title: '京都歴史探訪の旅',
  destination: '京都府',
  status: 'planning',
  guideGenerationStatus: 'succeeded',
  reflectionGenerationStatus: 'not_started',
  ...overrides,
});

describe('TravelListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('初期表示', () => {
    it('ページタイトルと説明が表示される', async () => {
      // 準備: APIが空の配列を返す
      mockListTravelPlans.mockResolvedValue([]);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: タイトルと説明が表示される
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: PAGE_TITLES.TRAVEL_LIST })).toBeInTheDocument();
      });
      expect(screen.getByText(PAGE_DESCRIPTIONS.TRAVEL_LIST)).toBeInTheDocument();
    });

    it('新規作成ボタンが表示される', async () => {
      // 準備: APIが空の配列を返す
      mockListTravelPlans.mockResolvedValue([]);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 新規作成ボタンが表示される
      await waitFor(() => {
        const buttons = screen.getAllByRole('button', {
          name: BUTTON_LABELS.CREATE_NEW_TRAVEL,
        });
        expect(buttons.length).toBeGreaterThan(0);
      });
    });
  });

  describe('ローディング状態', () => {
    it('データ取得中はローディングメッセージが表示される', () => {
      // 準備: APIが解決しないPromiseを返す（ローディング状態を維持）
      mockListTravelPlans.mockImplementation(() => new Promise(() => {}));

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: ローディングメッセージが表示される（複数箇所に表示されるため getAllByText を使用）
      const loadingElements = screen.getAllByText(MESSAGES.LOADING);
      expect(loadingElements.length).toBeGreaterThan(0);
    });
  });

  describe('空状態', () => {
    it('旅行計画がない場合は空メッセージが表示される', async () => {
      // 準備: APIが空の配列を返す
      mockListTravelPlans.mockResolvedValue([]);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 空メッセージと新規作成ボタンが表示される
      await waitFor(() => {
        expect(screen.getByText(MESSAGES.NO_TRAVELS)).toBeInTheDocument();
      });
    });
  });

  describe('旅行一覧表示', () => {
    it('旅行計画の一覧が表示される', async () => {
      // 準備: APIが旅行計画の配列を返す
      const mockTravels: TravelPlanListResponse[] = [
        createMockTravelPlan({
          id: 'plan-1',
          title: '京都歴史探訪の旅',
          destination: '京都府',
          status: 'planning',
        }),
        createMockTravelPlan({
          id: 'plan-2',
          title: '奈良古都めぐり',
          destination: '奈良県',
          status: 'completed',
        }),
      ];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 各旅行計画のタイトルと目的地が表示される
      await waitFor(() => {
        expect(screen.getByText('京都歴史探訪の旅')).toBeInTheDocument();
      });
      expect(screen.getByText('京都府')).toBeInTheDocument();
      expect(screen.getByText('奈良古都めぐり')).toBeInTheDocument();
      expect(screen.getByText('奈良県')).toBeInTheDocument();
    });

    it('計画中ステータスのラベルが正しく表示される', async () => {
      // 準備: 計画中の旅行計画を返す
      const mockTravels = [createMockTravelPlan({ status: 'planning' })];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 計画中ラベルが表示される
      await waitFor(() => {
        expect(screen.getByText(STATUS_LABELS.PLANNING)).toBeInTheDocument();
      });
    });

    it('完了ステータスのラベルが正しく表示される', async () => {
      // 準備: 完了した旅行計画を返す
      const mockTravels = [createMockTravelPlan({ status: 'completed' })];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 完了ラベルが表示される
      await waitFor(() => {
        expect(screen.getByText(STATUS_LABELS.COMPLETED)).toBeInTheDocument();
      });
    });

    it('生成失敗バッジが表示される', async () => {
      // 準備: 生成失敗の旅行計画を返す
      const mockTravels = [createMockTravelPlan({ guideGenerationStatus: 'failed' })];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 生成失敗バッジが表示される
      await waitFor(() => {
        expect(screen.getByText(STATUS_LABELS.GENERATION_FAILED)).toBeInTheDocument();
      });
    });

    it('生成中の場合は詳細ボタンが無効になる', async () => {
      // 準備: 生成中の旅行計画を返す
      const mockTravels = [createMockTravelPlan({ guideGenerationStatus: 'processing' })];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 生成中メッセージが表示され、ボタンが無効
      await waitFor(() => {
        expect(screen.getByText(MESSAGES.GENERATING)).toBeInTheDocument();
      });
      const generatingButton = screen.getByRole('button', {
        name: MESSAGES.GENERATING,
      });
      expect(generatingButton).toBeDisabled();
    });

    it('完了した旅行には編集ボタンが表示されない', async () => {
      // 準備: 完了した旅行計画のみを返す
      const mockTravels = [
        createMockTravelPlan({
          id: 'completed-plan',
          status: 'completed',
          guideGenerationStatus: 'succeeded',
        }),
      ];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 詳細ボタンは表示されるが、編集ボタンは表示されない
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.VIEW_DETAILS })
        ).toBeInTheDocument();
      });
      // 編集ボタンがないことを確認（リンク内のボタンも含めて）
      const editButtons = screen.queryAllByRole('button', {
        name: BUTTON_LABELS.EDIT,
      });
      expect(editButtons.length).toBe(0);
    });
  });

  describe('エラー状態', () => {
    it('API呼び出しが失敗した場合エラーダイアログが表示される', async () => {
      // 準備: APIがエラーをスローする
      mockListTravelPlans.mockRejectedValue(new Error('ネットワークエラー'));

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: エラーダイアログが表示される
      await waitFor(() => {
        expect(screen.getByText('ネットワークエラー')).toBeInTheDocument();
      });
    });
  });

  describe('一覧更新', () => {
    it('更新ボタンをクリックすると一覧が再取得される', async () => {
      // 準備: APIが旅行計画を返す
      const initialTravels = [createMockTravelPlan({ title: '初期の旅行' })];
      const updatedTravels = [createMockTravelPlan({ title: '更新後の旅行' })];
      mockListTravelPlans
        .mockResolvedValueOnce(initialTravels)
        .mockResolvedValueOnce(updatedTravels);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 初期データが表示される
      await waitFor(() => {
        expect(screen.getByText('初期の旅行')).toBeInTheDocument();
      });

      // 実行: 更新ボタンをクリック
      const refreshButton = screen.getByRole('button', {
        name: BUTTON_LABELS.REFRESH_LIST,
      });
      fireEvent.click(refreshButton);

      // 検証: 更新後のデータが表示される
      await waitFor(() => {
        expect(screen.getByText('更新後の旅行')).toBeInTheDocument();
      });
      expect(mockListTravelPlans).toHaveBeenCalledTimes(2);
    });
  });

  describe('ナビゲーション', () => {
    it('詳細ボタンのリンクが正しいパスを持つ', async () => {
      // 準備: APIが旅行計画を返す
      const mockTravels = [createMockTravelPlan({ id: 'test-plan-id' })];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 詳細リンクが正しいパスを持つ
      await waitFor(() => {
        const detailLink = screen
          .getByRole('button', { name: BUTTON_LABELS.VIEW_DETAILS })
          .closest('a');
        expect(detailLink).toHaveAttribute('href', '/travel/test-plan-id');
      });
    });

    it('編集ボタンのリンクが正しいパスを持つ', async () => {
      // 準備: 計画中の旅行計画を返す
      const mockTravels = [
        createMockTravelPlan({
          id: 'test-plan-id',
          status: 'planning',
          guideGenerationStatus: 'succeeded',
        }),
      ];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 編集リンクが正しいパスを持つ
      await waitFor(() => {
        const editLink = screen.getByRole('button', { name: BUTTON_LABELS.EDIT }).closest('a');
        expect(editLink).toHaveAttribute('href', '/travel/test-plan-id/edit');
      });
    });

    it('新規作成リンクが正しいパスを持つ', async () => {
      // 準備: APIが空の配列を返す
      mockListTravelPlans.mockResolvedValue([]);

      // 実行: コンポーネントをレンダリング
      render(<TravelListPage />);

      // 検証: 新規作成リンクが正しいパスを持つ
      await waitFor(() => {
        const createLinks = screen.getAllByRole('link');
        const newTravelLink = createLinks.find(link =>
          link.getAttribute('href')?.includes('/travel/new')
        );
        expect(newTravelLink).toHaveAttribute('href', '/travel/new');
      });
    });
  });
});
