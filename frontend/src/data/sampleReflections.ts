/**
 * 振り返り詳細コンテンツの型定義
 */
export interface ReflectionContent {
  travelId: string;
  overallComment: string;
  photos: {
    id: number;
    comment: string;
  }[];
}

/**
 * サンプル振り返りコンテンツデータ
 */
export const sampleReflectionContents: ReflectionContent[] = [
  {
    travelId: '3',
    overallComment:
      '広島での平和学習を通じて、戦争の悲惨さと平和の尊さを改めて実感しました。原爆ドームや資料館を見学し、当時の人々の苦しみに思いを馳せることができました。この経験を忘れず、日々の生活でも平和について考えていきたいと思います。',
    photos: [
      { id: 1, comment: '原爆ドーム前で撮影。建物の痛々しい姿に言葉を失いました。' },
      { id: 2, comment: '平和記念資料館の展示。一つ一つの遺品が語りかけてくるようでした。' },
      { id: 3, comment: '平和の灯。消えることのない火に祈りを捧げました。' },
      { id: 4, comment: '折り鶴タワーからの眺め。復興した街並みが美しかったです。' },
    ],
  },
  {
    travelId: '5',
    overallComment:
      '金沢の伝統工芸に触れる素晴らしい旅でした。加賀友禅や金箔貼りの体験を通じて、職人さんの技術の凄さに感動しました。兼六園の美しさも心に残っています。また違う季節に訪れてみたいです。',
    photos: [
      { id: 1, comment: '兼六園の琴柱灯籠。定番スポットですが、やはり風情があります。' },
      { id: 2, comment: '金箔貼り体験で作った小箱。難しかったけど良い思い出になりました。' },
      { id: 3, comment: 'ひがし茶屋街の町並み。着物を着て歩いている人も多く素敵でした。' },
    ],
  },
];

/**
 * 完了済み旅行の型定義
 */
export interface CompletedTravel {
  id: string;
  title: string;
  destination: string;
  completedAt: string;
  hasReflection: boolean;
  photosCount: number;
}

/**
 * 事前学習情報の型定義
 */
export interface PreLearningInfo {
  spotName: string;
  description: string;
}

/**
 * サンプル完了済み旅行データ
 * @deprecated sampleTravels を使用してください
 */
export const completedTravels: CompletedTravel[] = [
  {
    id: '3',
    title: '広島 平和学習の旅',
    destination: '広島県',
    completedAt: '2025-12-25',
    hasReflection: true,
    photosCount: 8,
  },
  {
    id: '4',
    title: '鎌倉 武家文化の旅',
    destination: '神奈川県',
    completedAt: '2025-11-15',
    hasReflection: false,
    photosCount: 0,
  },
];

/**
 * サンプル事前学習情報（振り返り作成ページ用）
 */
export const samplePreLearningInfo: PreLearningInfo[] = [
  {
    spotName: '原爆ドーム',
    description:
      '1945年8月6日の原子爆弾投下により被爆した建物。広島平和記念碑として世界遺産に登録。',
  },
  {
    spotName: '平和記念資料館',
    description: '原爆の惨禍を伝える資料館。被爆の実相を後世に伝える重要な施設。',
  },
];
