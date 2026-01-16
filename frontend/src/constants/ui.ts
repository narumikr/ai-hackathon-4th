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
