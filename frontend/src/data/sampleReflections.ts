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
