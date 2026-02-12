import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  ARIA_LABELS,
  BUTTON_LABELS,
  ERROR_DIALOG_MESSAGES,
  FORM_LABELS,
  HELP_TEXTS,
  HINTS,
  LABELS,
  MESSAGES,
  PAGE_DESCRIPTIONS,
  PAGE_TITLES,
  PLACEHOLDERS,
  TOOLTIP_MESSAGES,
} from '@/constants';

import TravelNewPage from './page';

// Next.js の useRouter をモック
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// APIクライアントのモック
const mockCreateTravelPlan = vi.fn();
const mockGenerateTravelGuide = vi.fn();

vi.mock('@/lib/api', () => ({
  createApiClientFromEnv: () => ({
    createTravelPlan: mockCreateTravelPlan,
    generateTravelGuide: mockGenerateTravelGuide,
  }),
  toApiError: (error: unknown) => ({
    message: error instanceof Error ? error.message : 'エラーが発生しました',
  }),
}));

// 入力ヘルパー関数
const typeInInput = (input: HTMLElement, value: string) => {
  fireEvent.change(input, { target: { value } });
};

describe('TravelNewPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('初期表示', () => {
    it('ページタイトルと説明が表示される', () => {
      // 実行: コンポーネントをレンダリング
      render(<TravelNewPage />);

      // 検証: タイトルと説明が表示される
      expect(screen.getByRole('heading', { name: PAGE_TITLES.TRAVEL_NEW })).toBeInTheDocument();
      expect(screen.getByText(PAGE_DESCRIPTIONS.TRAVEL_NEW)).toBeInTheDocument();
    });

    it('フォーム項目が表示される', () => {
      // 実行: コンポーネントをレンダリング
      render(<TravelNewPage />);

      // 検証: 各フォーム項目が表示される
      expect(screen.getByText(FORM_LABELS.TRAVEL_TITLE)).toBeInTheDocument();
      expect(screen.getByText(FORM_LABELS.DESTINATION)).toBeInTheDocument();
      expect(screen.getByText(FORM_LABELS.SPOTS)).toBeInTheDocument();
    });

    it('プレースホルダーが正しく表示される', () => {
      // 実行: コンポーネントをレンダリング
      render(<TravelNewPage />);

      // 検証: プレースホルダーが表示される
      expect(screen.getByPlaceholderText(PLACEHOLDERS.TRAVEL_TITLE)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(PLACEHOLDERS.DESTINATION)).toBeInTheDocument();
    });

    it('初期状態で3つのスポット入力欄が表示される', () => {
      // 実行: コンポーネントをレンダリング
      render(<TravelNewPage />);

      // 検証: 3つのスポット入力欄が表示される
      const spotInputs = screen.getAllByPlaceholderText(PLACEHOLDERS.SPOT_1);
      expect(spotInputs).toHaveLength(3);
    });

    it('ヘルプテキストが表示される', () => {
      // 実行: コンポーネントをレンダリング
      render(<TravelNewPage />);

      // 検証: ヘルプテキストが表示される
      expect(screen.getByText(HELP_TEXTS.DESTINATION)).toBeInTheDocument();
      expect(screen.getByText(HELP_TEXTS.SPOTS)).toBeInTheDocument();
    });

    it('ヒントセクションが表示される', () => {
      // 実行: コンポーネントをレンダリング
      render(<TravelNewPage />);

      // 検証: ヒントタイトルとヒント内容が表示される
      expect(screen.getByText(LABELS.HINT_TITLE)).toBeInTheDocument();
      for (const hint of HINTS.TRAVEL_NEW) {
        expect(screen.getByText(`• ${hint}`)).toBeInTheDocument();
      }
    });

    it('キャンセルボタンとガイド生成ボタンが表示される', () => {
      // 実行: コンポーネントをレンダリング
      render(<TravelNewPage />);

      // 検証: ボタンが表示される
      expect(screen.getByRole('button', { name: BUTTON_LABELS.CANCEL })).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: BUTTON_LABELS.GENERATE_GUIDE })
      ).toBeInTheDocument();
    });
  });

  describe('フォーム入力', () => {
    it('タイトルを入力できる', () => {
      // 実行: コンポーネントをレンダリングして入力
      render(<TravelNewPage />);
      const titleInput = screen.getByPlaceholderText(PLACEHOLDERS.TRAVEL_TITLE);
      typeInInput(titleInput, '京都歴史探訪の旅');

      // 検証: 入力値が反映される
      expect(titleInput).toHaveValue('京都歴史探訪の旅');
    });

    it('目的地を入力できる', () => {
      // 実行: コンポーネントをレンダリングして入力
      render(<TravelNewPage />);
      const destinationInput = screen.getByPlaceholderText(PLACEHOLDERS.DESTINATION);
      typeInInput(destinationInput, '京都府');

      // 検証: 入力値が反映される
      expect(destinationInput).toHaveValue('京都府');
    });

    it('観光スポットを入力できる', () => {
      // 実行: コンポーネントをレンダリングして入力
      render(<TravelNewPage />);
      const spotInputs = screen.getAllByPlaceholderText(PLACEHOLDERS.SPOT_1);
      typeInInput(spotInputs[0], '金閣寺');

      // 検証: 入力値が反映される
      expect(spotInputs[0]).toHaveValue('金閣寺');
    });
  });

  describe('スポット追加・削除', () => {
    it('スポットを追加できる', () => {
      // 実行: コンポーネントをレンダリング
      render(<TravelNewPage />);

      // 検証: 初期状態は3つ
      let spotInputs = screen.getAllByPlaceholderText(PLACEHOLDERS.SPOT_1);
      expect(spotInputs).toHaveLength(3);

      // 実行: スポット追加ボタンをクリック
      const addButton = screen.getByRole('button', {
        name: BUTTON_LABELS.ADD_SPOT,
      });
      fireEvent.click(addButton);

      // 検証: スポットが4つになる
      spotInputs = screen.getAllByPlaceholderText(PLACEHOLDERS.SPOT_1);
      expect(spotInputs).toHaveLength(4);
    });

    it('スポットを削除できる', () => {
      // 実行: コンポーネントをレンダリング
      render(<TravelNewPage />);

      // 検証: 初期状態は3つ
      let spotInputs = screen.getAllByPlaceholderText(PLACEHOLDERS.SPOT_1);
      expect(spotInputs).toHaveLength(3);

      // 実行: 削除ボタンをクリック
      const removeButtons = screen.getAllByRole('button', {
        name: ARIA_LABELS.REMOVE_SPOT,
      });
      fireEvent.click(removeButtons[0]);

      // 検証: スポットが2つになる
      spotInputs = screen.getAllByPlaceholderText(PLACEHOLDERS.SPOT_1);
      expect(spotInputs).toHaveLength(2);
    });

    it('スポットが1つの場合は削除ボタンが無効になる', () => {
      // 実行: コンポーネントをレンダリングし、2つのスポットを削除
      render(<TravelNewPage />);
      const removeButtons = screen.getAllByRole('button', {
        name: ARIA_LABELS.REMOVE_SPOT,
      });
      fireEvent.click(removeButtons[0]);
      fireEvent.click(screen.getAllByRole('button', { name: ARIA_LABELS.REMOVE_SPOT })[0]);

      // 検証: 残りの削除ボタンが無効
      const lastRemoveButton = screen.getByRole('button', {
        name: ARIA_LABELS.REMOVE_SPOT,
      });
      expect(lastRemoveButton).toBeDisabled();
    });
  });

  describe('バリデーション', () => {
    it('タイトルが空の場合はエラーツールチップが表示される', async () => {
      // 実行: コンポーネントをレンダリングし、目的地のみ入力して送信
      render(<TravelNewPage />);
      const destinationInput = screen.getByPlaceholderText(PLACEHOLDERS.DESTINATION);
      typeInInput(destinationInput, '京都府');

      const submitButton = screen.getByRole('button', {
        name: BUTTON_LABELS.GENERATE_GUIDE,
      });
      fireEvent.click(submitButton);

      // 検証: タイトルエラーが表示される
      await waitFor(() => {
        expect(screen.getByText(TOOLTIP_MESSAGES.TITLE_REQUIRED)).toBeInTheDocument();
      });
    });

    it('目的地が空の場合はエラーツールチップが表示される', async () => {
      // 実行: コンポーネントをレンダリングし、タイトルのみ入力して送信
      render(<TravelNewPage />);
      const titleInput = screen.getByPlaceholderText(PLACEHOLDERS.TRAVEL_TITLE);
      typeInInput(titleInput, '京都歴史探訪の旅');

      const submitButton = screen.getByRole('button', {
        name: BUTTON_LABELS.GENERATE_GUIDE,
      });
      fireEvent.click(submitButton);

      // 検証: 目的地エラーが表示される
      await waitFor(() => {
        expect(screen.getByText(TOOLTIP_MESSAGES.DESTINATION_REQUIRED)).toBeInTheDocument();
      });
    });

    it('入力後はエラーツールチップが消える', async () => {
      // 実行: コンポーネントをレンダリングして送信（エラー表示）
      render(<TravelNewPage />);
      const submitButton = screen.getByRole('button', {
        name: BUTTON_LABELS.GENERATE_GUIDE,
      });
      fireEvent.click(submitButton);

      // 検証: エラーが表示される
      await waitFor(() => {
        expect(screen.getByText(TOOLTIP_MESSAGES.TITLE_REQUIRED)).toBeInTheDocument();
      });

      // 実行: タイトルを入力
      const titleInput = screen.getByPlaceholderText(PLACEHOLDERS.TRAVEL_TITLE);
      typeInInput(titleInput, '京都');

      // 検証: タイトルエラーが消える
      await waitFor(() => {
        expect(screen.queryByText(TOOLTIP_MESSAGES.TITLE_REQUIRED)).not.toBeInTheDocument();
      });
    });
  });

  describe('フォーム送信', () => {
    it('正常に旅行計画を作成しガイドを生成する', async () => {
      // 準備: APIモック
      mockCreateTravelPlan.mockResolvedValue({ id: 'new-plan-id' });
      mockGenerateTravelGuide.mockResolvedValue({});

      // 実行: コンポーネントをレンダリングしてフォームを入力・送信
      render(<TravelNewPage />);

      const titleInput = screen.getByPlaceholderText(PLACEHOLDERS.TRAVEL_TITLE);
      const destinationInput = screen.getByPlaceholderText(PLACEHOLDERS.DESTINATION);
      const spotInputs = screen.getAllByPlaceholderText(PLACEHOLDERS.SPOT_1);

      typeInInput(titleInput, '京都歴史探訪の旅');
      typeInInput(destinationInput, '京都府');
      typeInInput(spotInputs[0], '金閣寺');
      typeInInput(spotInputs[1], '清水寺');

      const submitButton = screen.getByRole('button', {
        name: BUTTON_LABELS.GENERATE_GUIDE,
      });
      fireEvent.click(submitButton);

      // 検証: APIが呼ばれる
      await waitFor(() => {
        expect(mockCreateTravelPlan).toHaveBeenCalledWith({
          request: {
            title: '京都歴史探訪の旅',
            destination: '京都府',
            spots: [{ name: '金閣寺' }, { name: '清水寺' }],
          },
        });
      });

      // 検証: ガイド生成APIが呼ばれる
      expect(mockGenerateTravelGuide).toHaveBeenCalledWith({
        request: { planId: 'new-plan-id' },
      });

      // 検証: 旅行一覧にリダイレクト
      expect(mockPush).toHaveBeenCalledWith('/travel');
    });

    it('スポットが空の場合はspotsを送信しない', async () => {
      // 準備: APIモック
      mockCreateTravelPlan.mockResolvedValue({ id: 'new-plan-id' });
      mockGenerateTravelGuide.mockResolvedValue({});

      // 実行: スポットを入力せずに送信
      render(<TravelNewPage />);

      const titleInput = screen.getByPlaceholderText(PLACEHOLDERS.TRAVEL_TITLE);
      const destinationInput = screen.getByPlaceholderText(PLACEHOLDERS.DESTINATION);

      typeInInput(titleInput, '京都歴史探訪の旅');
      typeInInput(destinationInput, '京都府');

      const submitButton = screen.getByRole('button', {
        name: BUTTON_LABELS.GENERATE_GUIDE,
      });
      fireEvent.click(submitButton);

      // 検証: spotsがundefinedで送信される
      await waitFor(() => {
        expect(mockCreateTravelPlan).toHaveBeenCalledWith({
          request: {
            title: '京都歴史探訪の旅',
            destination: '京都府',
            spots: undefined,
          },
        });
      });
    });

    it('送信中はボタンが無効になりローディング表示される', async () => {
      // 準備: APIモック（遅延させる）
      mockCreateTravelPlan.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ id: 'id' }), 100))
      );
      mockGenerateTravelGuide.mockResolvedValue({});

      // 実行: コンポーネントをレンダリングしてフォームを送信
      render(<TravelNewPage />);

      const titleInput = screen.getByPlaceholderText(PLACEHOLDERS.TRAVEL_TITLE);
      const destinationInput = screen.getByPlaceholderText(PLACEHOLDERS.DESTINATION);

      typeInInput(titleInput, 'テスト旅行');
      typeInInput(destinationInput, 'テスト目的地');

      const submitButton = screen.getByRole('button', {
        name: BUTTON_LABELS.GENERATE_GUIDE,
      });
      fireEvent.click(submitButton);

      // 検証: ローディング状態
      expect(screen.getByRole('button', { name: MESSAGES.LOADING })).toBeDisabled();
      expect(screen.getByRole('button', { name: BUTTON_LABELS.CANCEL })).toBeDisabled();

      // 待機: 処理完了
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalled();
      });
    });
  });

  describe('エラー状態', () => {
    it('API呼び出しが失敗した場合エラーダイアログが表示される', async () => {
      // 準備: APIモック（エラー）
      mockCreateTravelPlan.mockRejectedValue(new Error('サーバーエラー'));

      // 実行: コンポーネントをレンダリングしてフォームを送信
      render(<TravelNewPage />);

      const titleInput = screen.getByPlaceholderText(PLACEHOLDERS.TRAVEL_TITLE);
      const destinationInput = screen.getByPlaceholderText(PLACEHOLDERS.DESTINATION);

      typeInInput(titleInput, 'テスト旅行');
      typeInInput(destinationInput, 'テスト目的地');

      const submitButton = screen.getByRole('button', {
        name: BUTTON_LABELS.GENERATE_GUIDE,
      });
      fireEvent.click(submitButton);

      // 検証: エラーダイアログが表示される
      await waitFor(() => {
        expect(screen.getByText(ERROR_DIALOG_MESSAGES.TRAVEL_CREATE_FAILED)).toBeInTheDocument();
      });
    });

    it('ガイド生成が失敗した場合もエラーダイアログが表示される', async () => {
      // 準備: APIモック
      mockCreateTravelPlan.mockResolvedValue({ id: 'new-plan-id' });
      mockGenerateTravelGuide.mockRejectedValue(new Error('ガイド生成失敗'));

      // 実行: コンポーネントをレンダリングしてフォームを送信
      render(<TravelNewPage />);

      const titleInput = screen.getByPlaceholderText(PLACEHOLDERS.TRAVEL_TITLE);
      const destinationInput = screen.getByPlaceholderText(PLACEHOLDERS.DESTINATION);

      typeInInput(titleInput, 'テスト旅行');
      typeInInput(destinationInput, 'テスト目的地');

      const submitButton = screen.getByRole('button', {
        name: BUTTON_LABELS.GENERATE_GUIDE,
      });
      fireEvent.click(submitButton);

      // 検証: エラーダイアログが表示される
      await waitFor(() => {
        expect(
          screen.getByText(ERROR_DIALOG_MESSAGES.TRAVEL_GUIDE_GENERATE_FAILED)
        ).toBeInTheDocument();
      });
    });
  });

  describe('キャンセル', () => {
    it('キャンセルボタンをクリックすると旅行一覧に戻る', () => {
      // 実行: コンポーネントをレンダリングしてキャンセルをクリック
      render(<TravelNewPage />);

      const cancelButton = screen.getByRole('button', {
        name: BUTTON_LABELS.CANCEL,
      });
      fireEvent.click(cancelButton);

      // 検証: 旅行一覧にリダイレクト
      expect(mockPush).toHaveBeenCalledWith('/travel');
    });
  });

  describe('エラーダイアログ操作', () => {
    it('エラーダイアログを閉じることができる', async () => {
      // 準備: APIがエラーをスローする
      mockCreateTravelPlan.mockRejectedValue(new Error('サーバーエラー'));

      // 実行: コンポーネントをレンダリングしてフォームを送信
      render(<TravelNewPage />);

      const titleInput = screen.getByPlaceholderText(PLACEHOLDERS.TRAVEL_TITLE);
      const destinationInput = screen.getByPlaceholderText(PLACEHOLDERS.DESTINATION);

      typeInInput(titleInput, 'テスト旅行');
      typeInInput(destinationInput, 'テスト目的地');

      const submitButton = screen.getByRole('button', {
        name: BUTTON_LABELS.GENERATE_GUIDE,
      });
      fireEvent.click(submitButton);

      // 検証: エラーダイアログが表示される
      await waitFor(() => {
        expect(screen.getByText(ERROR_DIALOG_MESSAGES.TRAVEL_CREATE_FAILED)).toBeInTheDocument();
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
