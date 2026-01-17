# フロントエンド旅行計画シーケンス図

## 概要

歴史学習特化型旅行AIエージェントシステムのフロントエンド旅行計画部分のシーケンス図です。スタンダードレイアウトを採用し、Next.js 16 App Routerを使用した実装を前提としています。

## 関連ドキュメント

- [画面設計書](./screen-design.md) - 各画面の詳細設計
- [レイアウト構造設計書](./layout-structure.md) - 全体レイアウト構造
- [バックエンドAPI仕様書](../backend/README.md) - API仕様

## 1. 旅行一覧表示フロー

### シーケンス図

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Browser as ブラウザ
    participant NextJS as Next.js App
    participant TravelList as TravelList Component
    participant API as API Client
    participant Backend as FastAPI Backend
    participant DB as PostgreSQL

    User->>Browser: /travel にアクセス
    Browser->>NextJS: ページリクエスト
    NextJS->>TravelList: コンポーネント初期化
    
    Note over TravelList: useEffect でデータ取得開始
    TravelList->>API: getTravelPlans(userId)
    API->>Backend: GET /api/v1/travel-plans?user_id={userId}
    Backend->>DB: SELECT travel_plans WHERE user_id = ?
    DB-->>Backend: 旅行計画データ
    Backend-->>API: TravelPlanResponse[]
    API-->>TravelList: 旅行計画リスト
    
    TravelList->>Browser: ローディング状態解除
    Browser->>User: 旅行一覧画面表示
    
    alt 新規作成ボタンクリック
        User->>Browser: "新規旅行作成" ボタンクリック
        Browser->>NextJS: /travel/new へナビゲート
    else 既存旅行選択
        User->>Browser: 旅行項目クリック
        Browser->>NextJS: /travel/[id] へナビゲート
    end
```

### コンポーネント構成

```typescript
// app/travel/page.tsx
export default function TravelListPage() {
  return (
    <Container>
      <Header title="旅行計画" />
      <TravelList />
      <CreateTravelButton />
    </Container>
  );
}

// components/travel/TravelList.tsx
export function TravelList() {
  const [travels, setTravels] = useState<TravelPlan[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchTravelPlans();
  }, []);
  
  // API呼び出しとデータ管理
}
```

## 2. 新規旅行作成フロー

### シーケンス図

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Browser as ブラウザ
    participant NextJS as Next.js App
    participant TravelForm as TravelForm Component
    participant SpotSelector as SpotSelector Component
    participant API as API Client
    participant Backend as FastAPI Backend
    participant Gemini as Vertex AI Gemini
    participant GeminiTools as Gemini Built-in Tools
    participant DB as PostgreSQL

    User->>Browser: /travel/new にアクセス
    Browser->>NextJS: ページリクエスト
    NextJS->>TravelForm: フォームコンポーネント初期化
    TravelForm->>Browser: 入力フォーム表示
    
    User->>Browser: 旅行タイトル入力（必須）
    User->>Browser: 行先（目的地）入力（必須）
    
    alt 観光スポットを指定する場合
        User->>Browser: 観光スポット選択（任意）
        Note over SpotSelector: 複数スポット選択可能
        SpotSelector->>Browser: 選択されたスポット表示
    end
    
    User->>Browser: "旅行計画作成" ボタンクリック
    Browser->>TravelForm: フォーム送信
    
    TravelForm->>API: createTravelPlan(planData)
    Note over API: planData = {title, destination, spots?}
    API->>Backend: POST /api/v1/travel-plans
    
    Note over Backend: バリデーション実行
    Backend->>DB: INSERT travel_plan (status: "processing")
    DB-->>Backend: 作成された旅行計画ID
    
    Backend-->>API: TravelPlanResponse (status: "processing")
    API-->>TravelForm: 作成受付レスポンス
    
    TravelForm->>NextJS: /travel/[id] へリダイレクト
    NextJS->>Browser: 旅行ガイド画面へ遷移（生成中表示）
    
    Note over Backend: 非同期でAI処理開始
    Backend->>Gemini: 旅行計画生成リクエスト
    Note over Gemini: 入力情報を基に観光スポット・歴史情報を生成
    
    Gemini->>GeminiTools: Google Search（歴史情報収集）
    GeminiTools-->>Gemini: 歴史情報データ
    
    Gemini->>GeminiTools: Google Maps（地図・位置情報）
    GeminiTools-->>Gemini: 地図・位置データ
    
    Note over Gemini: 観光スポット提案 + 歴史情報 + 年表 + 地図を統合
    Gemini-->>Backend: 完成した旅行ガイドデータ
    
    Backend->>DB: UPDATE travel_plan SET guide_data, status = "completed"
    DB-->>Backend: 更新完了
```

### フォーム構成

```typescript
// components/travel/TravelForm.tsx
export function TravelForm() {
  const [formData, setFormData] = useState<CreateTravelPlanRequest>({
    userId: '',
    title: '',           // 必須
    destination: '',     // 必須
    spots: []           // 任意（複数選択可能）
  });
  
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // spotsが空の場合は送信しない（オプショナル）
      const requestData = {
        ...formData,
        ...(formData.spots.length > 0 && { spots: formData.spots })
      };
      
      const result = await createTravelPlan(requestData);
      router.push(`/travel/${result.id}`);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <TextField 
        label="旅行タイトル"
        value={formData.title}
        onChange={(value) => setFormData({...formData, title: value})}
        required
      />
      <TextField 
        label="行先（目的地）"
        value={formData.destination}
        onChange={(value) => setFormData({...formData, destination: value})}
        required
      />
      <SpotSelector 
        label="観光スポット（任意）"
        spots={formData.spots}
        onSpotsChange={(spots) => setFormData({...formData, spots})}
        multiple
        optional
      />
      <Button type="submit" loading={loading}>
        旅行計画作成
      </Button>
    </form>
  );
}
```

## 3. 旅行ガイド表示フロー

### シーケンス図

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Browser as ブラウザ
    participant NextJS as Next.js App
    participant TravelGuide as TravelGuide Component
    participant Timeline as Timeline Component
    participant HistoricalMap as HistoricalMap Component
    participant API as API Client
    participant Backend as FastAPI Backend
    participant DB as PostgreSQL

    User->>Browser: /travel/[id] にアクセス
    Browser->>NextJS: ページリクエスト（planId付き）
    NextJS->>TravelGuide: コンポーネント初期化
    
    TravelGuide->>API: getTravelPlan(planId)
    API->>Backend: GET /api/v1/travel-plans/{planId}
    Backend->>DB: SELECT travel_plan WHERE id = ?
    DB-->>Backend: 旅行計画データ
    Backend-->>API: TravelPlanResponse
    API-->>TravelGuide: 旅行計画データ
    
    alt ガイドが生成済み（status: "completed"）
        TravelGuide->>Timeline: 年表データ渡し
        TravelGuide->>HistoricalMap: 地図データ渡し
        Timeline->>Browser: 年表コンポーネント表示
        HistoricalMap->>Browser: 地図コンポーネント表示
        TravelGuide->>Browser: 完全なガイド表示
        Note over Browser: - AI提案の観光スポット<br/>- 歴史情報・年表<br/>- 地図・位置情報<br/>- 学習価値の高い情報
    else ガイド生成中（status: "processing"）
        TravelGuide->>Browser: ローディング画面表示
        Note over TravelGuide: "AIが旅行計画を作成中です..."
        
        Note over TravelGuide: ポーリングでステータス確認（5秒間隔）
        loop ガイド生成完了まで
            TravelGuide->>API: getTravelPlan(planId)
            API->>Backend: GET /api/v1/travel-plans/{planId}
            Backend-->>API: TravelPlanResponse (status確認)
            API-->>TravelGuide: ステータス更新
            
            alt ガイド生成完了（status: "completed"）
                TravelGuide->>Timeline: 年表データ渡し
                TravelGuide->>HistoricalMap: 地図データ渡し
                Timeline->>Browser: 年表コンポーネント表示
                HistoricalMap->>Browser: 地図コンポーネント表示
                TravelGuide->>Browser: 完全なガイド表示
            else まだ生成中（status: "processing"）
                TravelGuide->>Browser: 進行状況更新
                Note over Browser: "観光スポットを選定中..."<br/>"歴史情報を収集中..."<br/>"年表を作成中..."
            end
        end
    end
    
    User->>Browser: 印刷ボタンクリック
    Browser->>TravelGuide: 印刷処理実行
    TravelGuide->>Browser: 印刷ダイアログ表示
    
    User->>Browser: 旅行完了マーク
    Browser->>TravelGuide: ステータス更新
    TravelGuide->>API: updateTravelPlan(planId, {status: 'completed'})
    API->>Backend: PUT /api/v1/travel-plans/{planId}
    Backend->>DB: UPDATE travel_plan SET status = 'completed'
    DB-->>Backend: 更新完了
    Backend-->>API: 更新成功レスポンス
    API-->>TravelGuide: ステータス更新完了
    TravelGuide->>Browser: UI状態更新
```

### ガイド表示コンポーネント

```typescript
// components/display/TravelGuide.tsx
export function TravelGuide({ planId }: { planId: string }) {
  const [travelPlan, setTravelPlan] = useState<TravelPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [generationStatus, setGenerationStatus] = useState<string>('');
  
  useEffect(() => {
    fetchTravelPlan();
    
    // ガイド生成中の場合はポーリング（5秒間隔）
    if (travelPlan?.status === 'processing') {
      const interval = setInterval(fetchTravelPlan, 5000);
      return () => clearInterval(interval);
    }
  }, [planId, travelPlan?.status]);
  
  const fetchTravelPlan = async () => {
    try {
      const plan = await getTravelPlan(planId);
      setTravelPlan(plan);
      
      // 生成状況に応じたメッセージ更新
      if (plan.status === 'processing') {
        updateGenerationStatus(plan);
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  const updateGenerationStatus = (plan: TravelPlan) => {
    // AI生成の進行状況を表示
    if (!plan.guide) {
      setGenerationStatus('観光スポットを選定中...');
    } else if (!plan.guide.timeline) {
      setGenerationStatus('歴史情報を収集中...');
    } else if (!plan.guide.mapData) {
      setGenerationStatus('年表を作成中...');
    } else {
      setGenerationStatus('最終調整中...');
    }
  };
  
  if (loading) return <LoadingSpinner />;
  if (!travelPlan) return <ErrorMessage />;
  
  return (
    <div className="travel-guide">
      <TravelOverview plan={travelPlan} />
      
      {travelPlan.status === 'completed' && travelPlan.guide ? (
        <>
          <AIGeneratedSpots spots={travelPlan.guide.aiSuggestedSpots} />
          <Timeline events={travelPlan.guide.timeline} />
          <HistoricalMap 
            spots={travelPlan.spots} 
            mapData={travelPlan.guide.mapData} 
          />
          <SpotDetails details={travelPlan.guide.spotDetails} />
          <CheckpointList checkpoints={travelPlan.guide.checkpoints} />
          <EducationalContent content={travelPlan.guide.educationalValue} />
        </>
      ) : (
        <GuideGenerationProgress 
          planId={planId} 
          status={generationStatus}
          message="AIが旅行計画を作成中です..."
        />
      )}
    </div>
  );
}
```

## 4. エラーハンドリングフロー

### シーケンス図

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Browser as ブラウザ
    participant Component as React Component
    participant API as API Client
    participant Backend as FastAPI Backend

    User->>Browser: アクション実行
    Browser->>Component: イベント発火
    Component->>API: API呼び出し
    API->>Backend: HTTPリクエスト
    
    alt 正常レスポンス
        Backend-->>API: 200 OK + データ
        API-->>Component: 成功レスポンス
        Component->>Browser: UI更新
    else バリデーションエラー
        Backend-->>API: 422 Validation Error
        API-->>Component: バリデーションエラー
        Component->>Browser: エラーメッセージ表示
    else サーバーエラー
        Backend-->>API: 500 Internal Server Error
        API-->>Component: サーバーエラー
        Component->>Browser: エラー画面表示
    else ネットワークエラー
        API-->>Component: ネットワークエラー
        Component->>Browser: 再試行ボタン表示
    end
    
    alt エラー発生時
        User->>Browser: 再試行ボタンクリック
        Browser->>Component: 再試行処理
        Component->>API: API再呼び出し
    end
```

## 5. 状態管理フロー

### React状態管理

```typescript
// hooks/useTravel.ts
export function useTravel() {
  const [travels, setTravels] = useState<TravelPlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const fetchTravels = useCallback(async (userId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getTravelPlans(userId);
      setTravels(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '取得に失敗しました');
    } finally {
      setLoading(false);
    }
  }, []);
  
  const createTravel = useCallback(async (planData: CreateTravelPlanRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const newPlan = await createTravelPlan(planData);
      setTravels(prev => [...prev, newPlan]);
      return newPlan;
    } catch (err) {
      setError(err instanceof Error ? err.message : '作成に失敗しました');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);
  
  return {
    travels,
    loading,
    error,
    fetchTravels,
    createTravel
  };
}
```

## 6. API通信フロー

### API Client実装

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8000' 
  : 'https://your-backend-url.com';

class ApiClient {
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API呼び出しに失敗しました');
    }
    
    return response.json();
  }
  
  async getTravelPlans(userId: string): Promise<TravelPlan[]> {
    return this.request(`/api/v1/travel-plans?user_id=${userId}`);
  }
  
  async getTravelPlan(planId: string): Promise<TravelPlan> {
    return this.request(`/api/v1/travel-plans/${planId}`);
  }
  
  async createTravelPlan(data: CreateTravelPlanRequest): Promise<TravelPlan> {
    return this.request('/api/v1/travel-plans', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  
  async updateTravelPlan(
    planId: string, 
    data: UpdateTravelPlanRequest
  ): Promise<TravelPlan> {
    return this.request(`/api/v1/travel-plans/${planId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }
}

export const apiClient = new ApiClient();
```

## 7. レスポンシブ対応フロー

### モバイル・タブレット対応

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Mobile as モバイルブラウザ
    participant NextJS as Next.js App
    participant Component as React Component

    User->>Mobile: 画面サイズ変更
    Mobile->>NextJS: リサイズイベント
    NextJS->>Component: useEffect (resize listener)
    
    Component->>Component: 画面サイズ判定
    
    alt モバイル (< 768px)
        Component->>Mobile: モバイルレイアウト適用
        Note over Component: - ハンバーガーメニュー<br/>- 単一カラム<br/>- タッチ最適化
    else タブレット (768px - 1023px)
        Component->>Mobile: タブレットレイアウト適用
        Note over Component: - 簡略ナビゲーション<br/>- 2カラム可能
    else デスクトップ (>= 1024px)
        Component->>Mobile: デスクトップレイアウト適用
        Note over Component: - フルナビゲーション<br/>- 3カラム可能
    end
```

## 実装優先度

### Phase 1（MVP必須）
1. 旅行一覧表示フロー
2. 新規旅行作成フロー（基本版）
   - 必須項目（タイトル・行先）の入力
   - 任意項目（観光スポット）の選択
   - 非同期処理での受付レスポンス
3. 旅行ガイド表示フロー（基本版）
   - ポーリングによるリアルタイム更新
   - AI生成進行状況の表示
4. エラーハンドリング（基本版）

### Phase 2（機能充実）
1. AI生成コンテンツの詳細表示
   - 観光スポット提案の詳細
   - 歴史情報・年表の充実
   - 教育価値の高い情報表示
2. 印刷・PDF出力機能
3. 旅行完了マーク機能
4. レスポンシブ対応の強化

### Phase 3（UX向上）
1. アニメーション効果
2. オフライン対応
3. プッシュ通知
4. パフォーマンス最適化

## 次のステップ

1. **コンポーネント実装**: 各シーケンス図に基づいたReactコンポーネントの実装
2. **API統合**: バックエンドAPIとの連携実装
3. **状態管理**: React hooksを使用した状態管理の実装
4. **テスト**: 各フローのUnit/Integration/E2Eテスト
5. **レスポンシブ対応**: モバイル・タブレット対応の実装

## 調整されたシーケンス図の主な変更点

### 1. **入力フィールドの調整**
- **必須項目**: 旅行タイトル、行先（目的地）
- **任意項目**: 観光スポット（複数選択可能）
- オプショナルな観光スポットは提案材料として活用

### 2. **AI処理フローの詳細化**
- **Vertex AI Gemini Built-in Tools**を使用
- **Google Search Tool**: 歴史情報収集
- **Google Maps Tool**: 地図・位置情報取得
- AIが観光スポット提案 + 歴史情報 + 年表 + 地図を統合生成

### 3. **非同期処理の実装**
- 旅行計画作成後、即座に受付レスポンス（status: "processing"）
- バックグラウンドでAI生成処理
- フロントエンドでポーリング（5秒間隔）によるリアルタイム更新

### 4. **生成進行状況の表示**
- "観光スポットを選定中..."
- "歴史情報を収集中..."
- "年表を作成中..."
- "最終調整中..."

### 5. **AIが提供する価値**
- **観光スポット提案**: ユーザー入力を基にした最適な観光地選定
- **歴史情報**: 各スポットの歴史的背景と意義
- **年表**: 時系列での歴史的コンテキスト
- **地図**: 歴史的価値を含む位置情報
- **教育価値**: 学習に役立つ情報の提供
- **旅行価値**: 実際の旅行として価値の高い案内

この調整により、ユーザーは最小限の入力（タイトル + 行先）で、AIが包括的で教育価値の高い旅行計画を自動生成する流れが明確になりました。