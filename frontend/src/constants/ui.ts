/**
 * UI表示文言の定数定義
 * すべてのUI表示テキストはここに定義する
 */

/**
 * リストコンポーネント関連の文言
 */
export const LIST = {
  EMPTY_MESSAGE: 'データがありません',
  LOADING_MESSAGE: '読み込み中...',
} as const;

/**
 * ローディングスピナー関連の文言
 */
export const LOADING_SPINNER = {
  ARIA_LABEL: '読み込み中',
} as const;

/**
 * UI component display strings
 * All UI text literals should be defined here for consistency and maintainability
 */

export const TABLE_LABELS = {
  // Aria labels for accessibility
  SELECT_ALL_ROWS: 'すべての行を選択',
  SELECT_ROW: (rowNumber: number) => `行${rowNumber}を選択`,

  // Default messages
  EMPTY_MESSAGE: 'データがありません',
}

/*
 * UI表示文言の定義
 * このファイルにはUIコンポーネントで使用される文言を定義します
 */

export const UI_TEXT = {
  /** モーダルの閉じるボタンのaria-label */
  MODAL_CLOSE: '閉じる',
} as const;
