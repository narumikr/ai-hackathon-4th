/**
 * UI表示文言定数
 */

export const APP_NAME = 'Historical Travel Agent';
export const APP_DESCRIPTION = '歴史学習特化型旅行AIエージェント';

/**
 * ナビゲーション項目
 */
export const NAVIGATION_ITEMS = [
  {
    label: 'ホーム',
    href: '/',
  },
  {
    label: '旅行計画',
    href: '/travel',
  },
  {
    label: '振り返り',
    href: '/reflection',
  },
] as const;

/**
 * フッター文言
 */
export const FOOTER_LINKS = [
  {
    label: 'About',
    href: '/about',
  },
  {
    label: 'Privacy',
    href: '/privacy',
  },
  {
    label: 'Terms',
    href: '/terms',
  },
] as const;

export const COPYRIGHT_TEXT = '© 2026 Historical Travel Agent. All rights reserved.';

/**
 * ページタイトル
 */
export const PAGE_TITLES = {
  HOME: 'ホーム',
  TRAVEL_LIST: '旅行一覧',
  TRAVEL_NEW: '新規旅行作成',
  TRAVEL_GUIDE: '旅行ガイド',
  REFLECTION_LIST: '振り返り一覧',
  REFLECTION_CREATE: '振り返り作成',
} as const;

/**
 * ボタン文言
 */
export const BUTTON_LABELS = {
  CREATE_NEW_TRAVEL: '新しい旅行を作成',
  VIEW_DETAILS: '詳細を見る',
  EDIT: '編集',
  DELETE: '削除',
  SAVE: '保存',
  CANCEL: 'キャンセル',
  BACK: '戻る',
  NEXT: '次へ',
  SUBMIT: '送信',
} as const;

/**
 * メッセージ
 */
export const MESSAGES = {
  NO_TRAVELS: '旅行計画がありません。新しい旅行を作成してください。',
  NO_REFLECTIONS: '振り返りがありません。完了した旅行から振り返りを作成してください。',
  LOADING: '読み込み中...',
  ERROR: 'エラーが発生しました。',
} as const;
