/**
 * 旅行ステータスの型定義
 */
export type TravelStatus = 'planning' | 'traveling' | 'completed';

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
    status: 'traveling',
    spotsCount: 4,
    createdAt: '2026-01-08',
  },
  {
    id: '3',
    title: '広島 平和学習の旅',
    destination: '広島県',
    status: 'completed',
    spotsCount: 3,
    createdAt: '2025-12-21',
  },
];
