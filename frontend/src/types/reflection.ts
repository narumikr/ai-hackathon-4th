/**
 * 振り返りスポットの型定義
 */
export interface ReflectionSpot {
  id: string;
  name: string;
  photos: File[];
  photoPreviews: string[];
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
