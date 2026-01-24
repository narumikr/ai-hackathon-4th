/**
 * 旅行ステータスの型定義
 */
export type TravelStatus = 'planning' | 'completed';

/**
 * 旅行データの型定義
 */
export interface SampleTravel {
  id: string;
  title: string;
  destination: string;
  status: TravelStatus;
  spotsCount: number;
  createdAt: string;
  // 以下、完了時の情報（オプショナル）
  completedAt?: string;
  hasReflection?: boolean;
  photosCount?: number;
}

/**
 * サンプル旅行データ
 */
export const sampleTravels: SampleTravel[] = [
  {
    id: '1',
    title: '京都 歴史探訪の旅',
    destination: '京都府',
    status: 'planning',
    spotsCount: 5,
    createdAt: '2026-01-10',
  },
  {
    id: '2',
    title: '奈良 古代史の旅',
    destination: '奈良県',
    status: 'planning',
    spotsCount: 4,
    createdAt: '2026-01-08',
  },
  {
    id: '3',
    title: '広島 平和学習の旅',
    destination: '広島県',
    status: 'completed',
    spotsCount: 3,
    createdAt: '2025-12-20',
    completedAt: '2025-12-25',
    hasReflection: true,
    photosCount: 8,
  },
  {
    id: '4',
    title: '鎌倉 武家文化の旅',
    destination: '神奈川県',
    status: 'completed',
    spotsCount: 6,
    createdAt: '2025-11-10',
    completedAt: '2025-11-15',
    hasReflection: false,
    photosCount: 0,
  },
  {
    id: '5',
    title: '金沢 伝統工芸の旅',
    destination: '石川県',
    status: 'completed',
    spotsCount: 4,
    createdAt: '2025-10-05',
    completedAt: '2025-10-12',
    hasReflection: true,
    photosCount: 12,
  },
];
