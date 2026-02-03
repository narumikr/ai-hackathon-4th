import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  BUTTON_LABELS,
  HINTS,
  LABELS,
  MESSAGES,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  STATUS_LABELS,
} from '@/constants';
import type { TravelPlanListResponse } from '@/types';

import ReflectionListPage from './page';

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
  status: 'completed',
  guideGenerationStatus: 'succeeded',
  reflectionGenerationStatus: 'not_started',
  ...overrides,
});

describe('ReflectionListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('初期表示', () => {
    it('ページタイトルと説明が表示される', async () => {
      // 準備: APIが空の配列を返す
      mockListTravelPlans.mockResolvedValue([]);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: タイトルと説明が表示される
      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: PAGE_TITLES.REFLECTION_LIST })
        ).toBeInTheDocument();
      });
      expect(screen.getByText(PAGE_DESCRIPTIONS.REFLECTION_LIST)).toBeInTheDocument();
    });

    it('更新ボタンが表示される', async () => {
      // 準備: APIが空の配列を返す
      mockListTravelPlans.mockResolvedValue([]);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: 更新ボタンが表示される
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.UPDATE })).toBeInTheDocument();
      });
    });

    it('ヒントセクションが表示される', async () => {
      // 準備: APIが空の配列を返す
      mockListTravelPlans.mockResolvedValue([]);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: ヒントが表示される
      await waitFor(() => {
        expect(screen.getByText(LABELS.ABOUT_REFLECTION)).toBeInTheDocument();
      });
      for (const hint of HINTS.REFLECTION) {
        expect(screen.getByText(`• ${hint}`)).toBeInTheDocument();
      }
    });
  });

  describe('ローディング状態', () => {
    it('データ取得中はローディングメッセージが表示される', () => {
      // 準備: APIが解決しないPromiseを返す
      mockListTravelPlans.mockImplementation(() => new Promise(() => {}));

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: ローディングメッセージが表示される
      expect(screen.getByText(MESSAGES.LOADING)).toBeInTheDocument();
    });
  });

  describe('空状態', () => {
    it('完了した旅行がない場合は空メッセージが表示される', async () => {
      // 準備: APIが空の配列を返す（または計画中のみ）
      mockListTravelPlans.mockResolvedValue([createMockTravelPlan({ status: 'planning' })]);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: 空メッセージが表示される
      await waitFor(() => {
        expect(screen.getByText(MESSAGES.NO_REFLECTIONS)).toBeInTheDocument();
      });
    });

    it('空状態で旅行一覧へのリンクが表示される', async () => {
      // 準備: APIが空の配列を返す
      mockListTravelPlans.mockResolvedValue([]);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: 旅行一覧リンクが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.VIEW_TRAVEL_LIST_ALT })
        ).toBeInTheDocument();
      });
    });
  });

  describe('振り返り一覧表示', () => {
    it('完了した旅行のみが表示される', async () => {
      // 準備: APIが計画中と完了の旅行を返す
      const mockTravels = [
        createMockTravelPlan({
          id: 'plan-1',
          title: '京都歴史探訪の旅',
          status: 'completed',
        }),
        createMockTravelPlan({
          id: 'plan-2',
          title: '計画中の旅行',
          status: 'planning',
        }),
      ];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: 完了した旅行のみ表示される
      await waitFor(() => {
        expect(screen.getByText('京都歴史探訪の旅')).toBeInTheDocument();
      });
      expect(screen.queryByText('計画中の旅行')).not.toBeInTheDocument();
    });

    it('振り返り未作成の場合は作成ボタンが表示される', async () => {
      // 準備: 振り返り未作成の旅行
      const mockTravels = [
        createMockTravelPlan({
          reflectionGenerationStatus: 'not_started',
        }),
      ];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: 作成ボタンが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.CREATE_REFLECTION })
        ).toBeInTheDocument();
      });
    });

    it('振り返り作成済みの場合は表示ボタンが表示される', async () => {
      // 準備: 振り返り作成済みの旅行
      const mockTravels = [
        createMockTravelPlan({
          reflectionGenerationStatus: 'succeeded',
        }),
      ];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: 表示ボタンと作成済みバッジが表示される
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.VIEW_REFLECTION })
        ).toBeInTheDocument();
      });
      expect(screen.getByText(STATUS_LABELS.REFLECTION_CREATED)).toBeInTheDocument();
    });

    it('振り返り生成中の場合は生成中表示される', async () => {
      // 準備: 振り返り生成中の旅行
      const mockTravels = [
        createMockTravelPlan({
          reflectionGenerationStatus: 'processing',
        }),
      ];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: 生成中表示される
      await waitFor(() => {
        const processingElements = screen.getAllByText(STATUS_LABELS.REFLECTION_PROCESSING);
        expect(processingElements.length).toBeGreaterThan(0);
      });
    });

    it('振り返り生成失敗の場合はエラーバッジが表示される', async () => {
      // 準備: 振り返り生成失敗の旅行
      const mockTravels = [
        createMockTravelPlan({
          reflectionGenerationStatus: 'failed',
        }),
      ];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: 失敗バッジが表示される
      await waitFor(() => {
        expect(screen.getByText(STATUS_LABELS.GENERATION_FAILED)).toBeInTheDocument();
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
      render(<ReflectionListPage />);

      // 検証: 初期データが表示される
      await waitFor(() => {
        expect(screen.getByText('初期の旅行')).toBeInTheDocument();
      });

      // 実行: 更新ボタンをクリック
      const updateButton = screen.getByRole('button', {
        name: BUTTON_LABELS.UPDATE,
      });
      fireEvent.click(updateButton);

      // 検証: 更新後のデータが表示される
      await waitFor(() => {
        expect(screen.getByText('更新後の旅行')).toBeInTheDocument();
      });
      expect(mockListTravelPlans).toHaveBeenCalledTimes(2);
    });
  });

  describe('ナビゲーション', () => {
    it('振り返り作成リンクが正しいパスを持つ', async () => {
      // 準備: 振り返り未作成の旅行
      const mockTravels = [
        createMockTravelPlan({
          id: 'test-plan-id',
          reflectionGenerationStatus: 'not_started',
        }),
      ];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: 作成リンクが正しいパスを持つ
      await waitFor(() => {
        const createLink = screen
          .getByRole('button', { name: BUTTON_LABELS.CREATE_REFLECTION })
          .closest('a');
        expect(createLink).toHaveAttribute('href', '/reflection/test-plan-id');
      });
    });

    it('振り返り表示リンクが正しいパスを持つ', async () => {
      // 準備: 振り返り作成済みの旅行
      const mockTravels = [
        createMockTravelPlan({
          id: 'test-plan-id',
          reflectionGenerationStatus: 'succeeded',
        }),
      ];
      mockListTravelPlans.mockResolvedValue(mockTravels);

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: 表示リンクが正しいパスを持つ
      await waitFor(() => {
        const viewLink = screen
          .getByRole('button', { name: BUTTON_LABELS.VIEW_REFLECTION })
          .closest('a');
        expect(viewLink).toHaveAttribute('href', '/reflection/test-plan-id/view');
      });
    });
  });

  describe('エラー状態', () => {
    it('API呼び出しが失敗した場合エラーダイアログが表示される', async () => {
      // 準備: APIがエラーをスローする
      mockListTravelPlans.mockRejectedValue(new Error('ネットワークエラー'));

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: エラーダイアログが表示される
      await waitFor(() => {
        expect(screen.getByText('ネットワークエラー')).toBeInTheDocument();
      });
    });

    it('エラーダイアログを閉じることができる', async () => {
      // 準備: APIがエラーをスローする
      mockListTravelPlans.mockRejectedValue(new Error('ネットワークエラー'));

      // 実行: コンポーネントをレンダリング
      render(<ReflectionListPage />);

      // 検証: エラーダイアログが表示される
      await waitFor(() => {
        expect(screen.getByText('ネットワークエラー')).toBeInTheDocument();
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
