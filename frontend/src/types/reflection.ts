/**
 * 写真データの型定義
 * 新規アップロード時と既存データ読み込み時の両方に対応
 */
export interface PhotoData {
  /** プレビュー/表示用のURL（blob:...またはhttp:...） */
  url: string;
  /** 新規アップロード時のFileオブジェクト（既存データの場合はundefined） */
  file?: File;
  /** サーバーから取得した既存写真のID（既存データの場合のみ） */
  id?: string;
}

/**
 * 振り返りスポットの型定義
 */
export interface ReflectionSpot {
  id: string;
  name: string;
  photos: PhotoData[];
  comment: string;
  isAdded: boolean; // ユーザーが追加したスポットかどうか
}

/**
 * 振り返りデータの型定義
 */
export interface ReflectionFormData {
  spots: ReflectionSpot[];
  overallComment: string;
}

export interface ImageAnalysisResponse {
  detectedSpots: string[];
  historicalElements: string[];
  landmarks: string[];
  confidence: number;
}

export interface ReflectionPhotoResponse {
  id: string;
  spotId: string;
  url: string;
  analysis: ImageAnalysisResponse;
  userDescription?: string | null;
}

export interface ReflectionResponse {
  id: string;
  planId: string;
  userId: string;
  photos: ReflectionPhotoResponse[];
  spotNotes: Record<string, string | null>;
  userNotes?: string | null;
  createdAt: string;
}

export interface CreateReflectionRequest {
  planId: string;
  userId: string;
  userNotes?: string | null;
}
