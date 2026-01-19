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
};

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
  ERROR_INVALID_FILE_TYPE: (fileName: string) => `${fileName} は許可されていないファイル形式です`,

  /** 補足情報の接頭辞 */
  ACCEPTED_FORMATS_PREFIX: '対応形式: ',
  MAX_SIZE_PREFIX: '最大サイズ: ',
};

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
  REFLECTION_PAMPHLET: '振り返りパンフレット',
} as const;

/**
 * ページ説明文
 */
export const PAGE_DESCRIPTIONS = {
  TRAVEL_LIST: '作成した旅行計画を管理できます',
  TRAVEL_NEW: '旅行先と訪問予定の観光スポットを入力してください',
  REFLECTION_LIST: '完了した旅行の振り返りを作成・確認できます',
  REFLECTION_CREATE: '旅行の写真と感想をアップロードしてください',
} as const;

/**
 * ボタン文言
 */
export const BUTTON_LABELS = {
  CREATE_NEW_TRAVEL: '新しい旅行を作成',
  VIEW_DETAILS: '詳細を見る',
  EDIT: '編集',
  DELETE: '削除',
  REMOVE: '削除',
  SAVE: '保存',
  CANCEL: 'キャンセル',
  BACK: '戻る',
  NEXT: '次へ',
  SUBMIT: '送信',
  PRINT: '印刷',
  PDF_EXPORT: 'PDF出力',
  TRAVEL_COMPLETE: '旅行完了',
  GENERATE_GUIDE: '旅行ガイドを生成',
  GENERATE_REFLECTION: '振り返りパンフレットを生成',
  ADD_SPOT: '＋ スポットを追加',
  ADD: '追加',
  START_NOW: '今すぐ始める',
  VIEW_TRAVEL_LIST: '旅行一覧を見る',
  VIEW_TRAVEL_LIST_ALT: '旅行一覧へ',
  VIEW_REFLECTION: '振り返りを見る',
  CREATE_REFLECTION: '振り返りを作成',
  COMPLETE_TRAVEL_AND_CREATE_FEEDBACK: '旅行を完了してフィードバックを作成',
} as const;

/**
 * メッセージ
 */
export const MESSAGES = {
  NO_TRAVELS: '旅行計画がありません。新しい旅行を作成してください。',
  NO_REFLECTIONS: '振り返りがありません。完了した旅行から振り返りを作成してください。',
  LOADING: '読み込み中...',
  ERROR: 'エラーが発生しました。',
  TRAVEL_NOT_FOUND: '旅行が見つかりません',
  REFLECTION_NOT_FOUND: '振り返りが見つかりません',
  REFLECTION_GENERATED: '振り返りを生成しました！',
} as const;

/**
 * ステータスラベル
 */
export const STATUS_LABELS = {
  PLANNING: '計画中',
  TRAVELING: '旅行中',
  COMPLETED: '完了',
  REFLECTION_CREATED: '作成済み',
  ADDED_SPOT: '追加スポット',
} as const;

/**
 * ステータスカラー（Tailwind CSS クラス）
 */
export const STATUS_COLORS = {
  PLANNING: 'bg-info text-white',
  TRAVELING: 'bg-warning text-white',
  COMPLETED: 'bg-success text-white',
} as const;

/**
 * フォームラベル
 */
export const FORM_LABELS = {
  TRAVEL_TITLE: '旅行タイトル',
  DESTINATION: '目的地',
  SPOTS: '観光スポット',
  SELECT_FROM_MAP: '地図から選択',
  PHOTO_UPLOAD: '📸 写真をアップロード',
  PHOTO_COMMENTS: '✍️ 写真ごとの感想',
  OVERALL_IMPRESSION: '📝 旅行全体の感想',
  OVERALL_IMPRESSION_PLAIN: '全体的な感想',
  PRE_LEARNING: '📚 事前学習で学んだこと（参考）',
  PHOTOS: '写真',
  COMMENT: '感想',
} as const;

/**
 * プレースホルダー文言
 */
export const PLACEHOLDERS = {
  TRAVEL_TITLE: '例: 京都 歴史探訪の旅',
  DESTINATION: '例: 京都府',
  SPOT_1: '例: 金閣寺',
  SPOT_2: '例: 清水寺',
  SPOT_3: '例: 伏見稲荷大社',
  PHOTO_COMMENT: 'この写真についての感想を入力してください...',
  OVERALL_COMMENT:
    '旅行全体を通しての感想を入力してください。事前学習との違いや、新たな発見などを記入すると、より充実した振り返りができます...',
  UPLOAD_INSTRUCTION: 'クリックまたはドラッグ&ドロップで写真を追加',
  SPOT_COMMENT: (spotName: string) => `${spotName}での思い出や感想を書いてみましょう...`,
  SPOT_NAME: 'スポット名を入力 (例: 原爆ドーム近くのカフェ)',
} as const;

/**
 * ヘルプテキスト
 */
export const HELP_TEXTS = {
  DESTINATION: '訪問する都道府県や地域を入力してください',
  SPOTS: '訪問予定の観光スポットを入力してください（複数可）',
  UPLOAD_FORMAT: 'JPG, PNG形式に対応（最大10MB）',
  ADDED_SPOT: '振り返りで追加したスポットです',
  ADD_SPOT_INSTRUCTION:
    '計画になかった立ち寄り場所や、特に印象に残った場所を追加して記録に残しましょう。',
} as const;

/**
 * エラーメッセージ
 */
export const ERROR_MESSAGES = {
  MAX_IMAGES_EXCEEDED: (maxImages: number) => `写真は最大${maxImages}枚までアップロードできます`,
  INVALID_FILE_TYPE: '画像ファイルのみアップロードできます',
  FILE_SIZE_EXCEEDED: (fileName: string, maxSize: number) =>
    `${fileName} はファイルサイズ上限（${maxSize}MB）を超えています`,
} as const;

/**
 * セクション見出し
 */
export const SECTION_TITLES = {
  MAIN_FEATURES: '主な機能',
  HOW_TO_USE: '使い方',
  CTA: 'さあ、歴史を学ぶ旅を始めましょう',
  TIMELINE: '📅 歴史年表',
  MAP: '🗺️ 観光マップ',
  SPOT_DETAILS: '📍 観光スポット詳細',
  HISTORICAL_CONTEXT: '🏛️ 歴史的背景',
  CHECKPOINTS: '✅ チェックポイント',
  SPOT_REFLECTIONS: '観光スポットの振り返り',
  SPOT_MEMORIES: '観光スポットの思い出',
  ADD_SPOT: 'スポットを追加する',
  MEMORY_SCENE: (index: number) => `思い出の場面 #${index}`,
} as const;

/**
 * ホームページコンテンツ
 */
export const HOME_CONTENT = {
  HERO_SUBTITLE:
    '旅行前に歴史的背景を学び、旅行後に写真と共に振り返る。\nAIが生成する歴史学習特化型の旅行ガイドで、より深い旅の体験を。',
  CTA_SUBTITLE: '次の旅行をより深い学びの体験に変えてみませんか？',
  SECTION_TITLES: {
    MAIN_FEATURES: '主な機能',
    HOW_TO_USE: '使い方',
    CTA: 'さあ、歴史を学ぶ旅を始めましょう',
  },
  FEATURES: [
    {
      emoji: '📚',
      title: '事前学習ガイド生成',
      description:
        '訪問予定の観光スポットの歴史的背景や見どころを、AIが分かりやすくまとめた旅行ガイドを自動生成。',
    },
    {
      emoji: '🗺️',
      title: '歴史年表と地図',
      description:
        '時系列で整理された歴史年表と、歴史的コンテキスト付きの地図で、訪問地の理解を深めます。',
    },
    {
      emoji: '📸',
      title: '旅行後の振り返り',
      description:
        '旅行写真と感想をアップロードすると、AIが事前学習との比較を含めた振り返りパンフレットを生成。',
    },
  ],
  STEPS: [
    {
      title: '旅行計画を作成',
      description:
        '訪問予定の目的地と計画のタイトルを入力、任意で観光スポットを追加して旅行計画を作成します。',
    },
    {
      title: '旅行ガイドを確認',
      description:
        'AIが生成した歴史的背景や見どころ、観光スポットを含む旅行ガイドを確認・編集ができます。',
    },
    {
      title: '旅行を楽しむ',
      description: '生成されたガイドを参考に、歴史的な背景を理解しながら旅行を楽しみます。',
    },
    {
      title: '振り返りを作成',
      description:
        '旅行後、写真と感想をアップロードすると、AIが学習体験を振り返るパンフレットを生成します。',
    },
  ],
} as const;

/**
 * ヒント・注意事項
 */
export const HINTS = {
  TRAVEL_NEW: [
    '観光スポットは具体的な名称を入力してください',
    '歴史的な建造物や史跡がおすすめです',
    'ガイド生成には1-2分程度かかる場合があります',
  ],
  REFLECTION: [
    '旅行の写真をアップロードして感想を入力してください',
    'AIが事前学習との比較を含めた振り返りパンフレットを生成します',
    '生成されたパンフレットは保存・印刷できます',
  ],
  REFLECTION_CREATE: [
    '写真は訪問した場所が分かるものがおすすめです',
    '事前学習との違いや新たな発見を記入すると効果的です',
    'パンフレット生成には1-2分程度かかる場合があります',
  ],
} as const;

/**
 * プレースホルダーメッセージ
 */
export const PLACEHOLDER_MESSAGES = {
  MAP_COMING_SOON: '地図機能は今後実装予定',
  MAP_DESCRIPTION: '各スポットの位置と歴史的コンテキストを表示',
} as const;

/**
 * その他の表示文言
 */
export const LABELS = {
  SPOTS_COUNT: 'スポット',
  PHOTOS_COUNT: '枚',
  PHOTO_NUMBER: '写真',
  YEAR_SUFFIX: '年',
  COMPLETED_DATE: '完了:',
  HINT_TITLE: '💡 ヒント',
  ABOUT_REFLECTION: '💡 振り返りについて',
  REMOVE_IMAGE: '削除',
} as const;

/**
 * 絵文字のアクセシビリティラベル
 */
export const EMOJI_LABELS = {
  HISTORIC_BUILDING: '歴史的建造物',
  USER: 'ユーザー',
  BOOK: '本',
  MAP: '地図',
  CAMERA: 'カメラ',
  PENCIL: '鉛筆',
  NOTEBOOK: 'ノート',
  CALENDAR: 'カレンダー',
  PIN: 'ピン',
  CHECKMARK: 'チェックマーク',
  LIGHTBULB: '電球',
  PICTURE: '写真',
} as const;
