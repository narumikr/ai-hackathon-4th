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

/**
 * FileUploaderコンポーネント関連の文言
 */
export const FILE_UPLOADER = {
  /** デフォルトのラベル */
  DEFAULT_LABEL: 'ファイルをドラッグ&ドロップ',
  
  /** ヒントテキスト */
  HINT_TEXT: 'またはクリックしてファイルを選択',
  
  /** エラーメッセージテンプレート */
  ERROR_FILE_SIZE_EXCEEDED: (fileName: string, maxSize: string) => 
    `${fileName} はファイルサイズ上限（${maxSize}）を超えています`,
  ERROR_INVALID_FILE_TYPE: (fileName: string) => 
    `${fileName} は許可されていないファイル形式です`,
  
  /** 補足情報の接頭辞 */
  ACCEPTED_FORMATS_PREFIX: '対応形式: ',
  MAX_SIZE_PREFIX: '最大サイズ: ',
} as const;
