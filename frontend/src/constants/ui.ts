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
} as const;
