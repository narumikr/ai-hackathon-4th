import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  ARIA_LABELS,
  BUTTON_LABELS,
  FORM_LABELS,
  MESSAGES,
  PAGE_TITLES,
  PLACEHOLDERS,
  TOOLTIP_MESSAGES,
} from '@/constants';
import type { TravelPlanResponse } from '@/types';

import TravelEditPage from './page';

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
const mockUpdateTravelPlan = vi.fn();
const mockGenerateTravelGuide = vi.fn();

vi.mock('@/lib/api', () => ({
  createApiClientFromEnv: () => ({
    getTravelPlan: mockGetTravelPlan,
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
    { id: 'spot-1', name: '金閣寺' },
    { id: 'spot-2', name: '清水寺' },
  ],
  status: 'planning',
  guideGenerationStatus: 'succeeded',
  reflectionGenerationStatus: 'not_started',
  createdAt: '2024-01-15T10:00:00Z',
  updatedAt: '2024-01-15T10:00:00Z',
  ...overrides,
});

// 入力ヘルパー関数
const typeInInput = (input: HTMLElement, value: string) => {
  fireEvent.change(input, { target: { value } });
};

describe('TravelEditPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('ローディング状態', () => {
    it('データ取得中はローディングメッセージが表示される', () => {
      // 準備: APIが解決しないPromiseを返す
      mockGetTravelPlan.mockImplementation(() => new Promise(() => {}));

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: ローディングメッセージが表示される
      expect(screen.getByText(MESSAGES.LOADING)).toBeInTheDocument();
    });
  });

  describe('初期表示', () => {
    it('ページタイトルが表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: タイトルが表示される
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: PAGE_TITLES.TRAVEL_EDIT })).toBeInTheDocument();
      });
    });

    it('フォーム項目が表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: 各フォーム項目が表示される
      await waitFor(() => {
        expect(screen.getByText(FORM_LABELS.TRAVEL_TITLE)).toBeInTheDocument();
      });
      expect(screen.getByText(FORM_LABELS.DESTINATION)).toBeInTheDocument();
      expect(screen.getByText(FORM_LABELS.SPOTS)).toBeInTheDocument();
    });

    it('既存データがフォームに読み込まれる', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: 既存のタイトルと目的地が入力欄に表示される
      await waitFor(() => {
        expect(screen.getByDisplayValue('京都歴史探訪の旅')).toBeInTheDocument();
      });
      expect(screen.getByDisplayValue('京都府')).toBeInTheDocument();
    });

    it('既存のスポットがフォームに読み込まれる', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: 既存のスポットが表示される
      await waitFor(() => {
        expect(screen.getByDisplayValue('金閣寺')).toBeInTheDocument();
      });
      expect(screen.getByDisplayValue('清水寺')).toBeInTheDocument();
    });

    it('戻るボタンと更新ボタンが表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: ボタンが表示される
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.BACK })).toBeInTheDocument();
      });
      expect(screen.getByRole('button', { name: BUTTON_LABELS.UPDATE })).toBeInTheDocument();
    });
  });

  describe('フォーム入力', () => {
    it('タイトルを変更できる', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: タイトルを変更
      await waitFor(() => {
        expect(screen.getByDisplayValue('京都歴史探訪の旅')).toBeInTheDocument();
      });

      const titleInput = screen.getByDisplayValue('京都歴史探訪の旅');
      typeInInput(titleInput, '奈良古都めぐり');

      expect(screen.getByDisplayValue('奈良古都めぐり')).toBeInTheDocument();
    });

    it('目的地を変更できる', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: 目的地を変更
      await waitFor(() => {
        expect(screen.getByDisplayValue('京都府')).toBeInTheDocument();
      });

      const destinationInput = screen.getByDisplayValue('京都府');
      typeInInput(destinationInput, '奈良県');

      expect(screen.getByDisplayValue('奈良県')).toBeInTheDocument();
    });
  });

  describe('スポット追加・削除', () => {
    it('スポットを追加できる', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: 初期状態は2つ
      await waitFor(() => {
        expect(screen.getByDisplayValue('金閣寺')).toBeInTheDocument();
      });

      // 実行: スポット追加ボタンをクリック
      const addButton = screen.getByRole('button', {
        name: BUTTON_LABELS.ADD_SPOT,
      });
      fireEvent.click(addButton);

      // 検証: スポットが追加される（空のフィールド）
      const spotInputs = screen.getAllByPlaceholderText(PLACEHOLDERS.SPOT_1);
      expect(spotInputs).toHaveLength(3);
    });

    it('スポットを削除できる', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: 初期状態は2つ
      await waitFor(() => {
        expect(screen.getByDisplayValue('金閣寺')).toBeInTheDocument();
      });

      // 実行: 削除ボタンをクリック
      const removeButtons = screen.getAllByRole('button', {
        name: ARIA_LABELS.REMOVE_SPOT,
      });
      fireEvent.click(removeButtons[0]);

      // 検証: 金閣寺が削除され、清水寺のみ残る
      expect(screen.queryByDisplayValue('金閣寺')).not.toBeInTheDocument();
      expect(screen.getByDisplayValue('清水寺')).toBeInTheDocument();
    });

    it('スポットが1つの場合は削除ボタンが無効になる', async () => {
      // 準備: スポットが1つの旅行計画
      mockGetTravelPlan.mockResolvedValue(
        createMockTravelPlan({
          spots: [{ id: 'spot-1', name: '金閣寺' }],
        })
      );

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: 削除ボタンが無効
      await waitFor(() => {
        const removeButton = screen.getByRole('button', {
          name: ARIA_LABELS.REMOVE_SPOT,
        });
        expect(removeButton).toBeDisabled();
      });
    });
  });

  describe('バリデーション', () => {
    it('タイトルが空の場合はエラーツールチップが表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: データが読み込まれるのを待つ
      await waitFor(() => {
        expect(screen.getByDisplayValue('京都歴史探訪の旅')).toBeInTheDocument();
      });

      // 実行: タイトルを空にして更新
      const titleInput = screen.getByDisplayValue('京都歴史探訪の旅');
      typeInInput(titleInput, '');

      const updateButton = screen.getByRole('button', {
        name: BUTTON_LABELS.UPDATE,
      });
      fireEvent.click(updateButton);

      // 検証: エラーが表示される
      await waitFor(() => {
        expect(screen.getByText(TOOLTIP_MESSAGES.TITLE_REQUIRED)).toBeInTheDocument();
      });
    });

    it('目的地が空の場合はエラーツールチップが表示される', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: データが読み込まれるのを待つ
      await waitFor(() => {
        expect(screen.getByDisplayValue('京都府')).toBeInTheDocument();
      });

      // 実行: 目的地を空にして更新
      const destinationInput = screen.getByDisplayValue('京都府');
      typeInInput(destinationInput, '');

      const updateButton = screen.getByRole('button', {
        name: BUTTON_LABELS.UPDATE,
      });
      fireEvent.click(updateButton);

      // 検証: エラーが表示される
      await waitFor(() => {
        expect(screen.getByText(TOOLTIP_MESSAGES.DESTINATION_REQUIRED)).toBeInTheDocument();
      });
    });
  });

  describe('フォーム送信', () => {
    it('正常に旅行計画を更新しガイドを再生成する', async () => {
      // 準備: APIモック
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());
      mockUpdateTravelPlan.mockResolvedValue({ id: 'test-plan-id' });
      mockGenerateTravelGuide.mockResolvedValue({});

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: データが読み込まれるのを待つ
      await waitFor(() => {
        expect(screen.getByDisplayValue('京都歴史探訪の旅')).toBeInTheDocument();
      });

      // 実行: タイトルを変更して更新
      const titleInput = screen.getByDisplayValue('京都歴史探訪の旅');
      typeInInput(titleInput, '奈良古都めぐり');

      const updateButton = screen.getByRole('button', {
        name: BUTTON_LABELS.UPDATE,
      });
      fireEvent.click(updateButton);

      // 検証: 更新APIが呼ばれる
      await waitFor(() => {
        expect(mockUpdateTravelPlan).toHaveBeenCalledWith({
          planId: 'test-plan-id',
          request: {
            title: '奈良古都めぐり',
            destination: '京都府',
            spots: [{ name: '金閣寺' }, { name: '清水寺' }],
          },
        });
      });

      // 検証: ガイド生成APIが呼ばれる
      expect(mockGenerateTravelGuide).toHaveBeenCalledWith({
        request: { planId: 'test-plan-id' },
      });

      // 検証: 一覧にリダイレクト
      expect(mockPush).toHaveBeenCalledWith('/travel');
    });

    it('送信中はボタンが無効になりローディング表示される', async () => {
      // 準備: APIモック（遅延させる）
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());
      mockUpdateTravelPlan.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ id: 'test-plan-id' }), 100))
      );
      mockGenerateTravelGuide.mockResolvedValue({});

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: データが読み込まれるのを待つ
      await waitFor(() => {
        expect(screen.getByDisplayValue('京都歴史探訪の旅')).toBeInTheDocument();
      });

      // 実行: 更新ボタンをクリック
      const updateButton = screen.getByRole('button', {
        name: BUTTON_LABELS.UPDATE,
      });
      fireEvent.click(updateButton);

      // 検証: ローディング状態
      expect(screen.getByRole('button', { name: MESSAGES.LOADING })).toBeDisabled();
      expect(screen.getByRole('button', { name: BUTTON_LABELS.BACK })).toBeDisabled();

      // 待機: 処理完了
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalled();
      });
    });
  });

  describe('エラー状態', () => {
    it('データ取得失敗時は戻るボタンが表示される', async () => {
      // 準備: APIがエラーをスローする
      mockGetTravelPlan.mockRejectedValue(new Error('サーバーエラー'));

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: 戻るボタンが表示される
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.BACK })).toBeInTheDocument();
      });
    });

    it('更新失敗時はエラーダイアログが表示される', async () => {
      // 準備: APIモック
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());
      mockUpdateTravelPlan.mockRejectedValue(new Error('更新失敗'));

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: データが読み込まれるのを待つ
      await waitFor(() => {
        expect(screen.getByDisplayValue('京都歴史探訪の旅')).toBeInTheDocument();
      });

      // 実行: 更新ボタンをクリック
      const updateButton = screen.getByRole('button', {
        name: BUTTON_LABELS.UPDATE,
      });
      fireEvent.click(updateButton);

      // 検証: エラーメッセージが表示される
      await waitFor(() => {
        expect(screen.getByText('更新失敗')).toBeInTheDocument();
      });
    });
  });

  describe('ナビゲーション', () => {
    it('戻るボタンをクリックすると一覧に戻る', async () => {
      // 準備: APIが旅行計画を返す
      mockGetTravelPlan.mockResolvedValue(createMockTravelPlan());

      // 実行: コンポーネントをレンダリング
      render(<TravelEditPage />);

      // 検証: データが読み込まれるのを待つ
      await waitFor(() => {
        expect(screen.getByRole('button', { name: BUTTON_LABELS.BACK })).toBeInTheDocument();
      });

      // 実行: 戻るボタンをクリック
      fireEvent.click(screen.getByRole('button', { name: BUTTON_LABELS.BACK }));

      // 検証: 一覧にリダイレクト
      expect(mockPush).toHaveBeenCalledWith('/travel');
    });
  });
});
