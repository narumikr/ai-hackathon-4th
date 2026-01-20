# データフロー詳細解説 - Historical Travel Agent

## 概要

Historical Travel Agentシステムのデータフローについて、実際の処理順序と各サービス間の通信方法を詳しく解説します。

## 🔄 データフローの全体像

### 基本構造
```
User → Frontend → Backend API → 各サービス（並列アクセス）
                              ├─ Vertex AI (直接)
                              ├─ Cloud SQL (直接)  
                              ├─ Redis (直接)
                              └─ Cloud Storage (直接)
```

**重要**: BackendからVertex AI、Cloud SQL、Redis、Cloud Storageへは**並列で直接アクセス**します。Cloud SQLを経由してVertex AIにアクセスするわけではありません。

## 📊 詳細なデータフロー

### 1. User → Frontend (Next.js)
**通信方法**: HTTPS
**データ形式**: HTML/CSS/JavaScript、ユーザー入力

```typescript
// 旅行計画作成
const createTravelPlan = async (planData: TravelPlanData) => {
  const response = await fetch('/api/v1/travel-plans', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(planData)
  });
  return response.json();
};

// 画像アップロード
const uploadPhoto = async (file: File) => {
  const formData = new FormData();
  formData.append('photo', file);
  
  const response = await fetch('/api/v1/upload-images', {
    method: 'POST',
    body: formData
  });
  return response.json();
};
```

### 2. Frontend → Backend API (FastAPI)
**通信方法**: HTTPS REST API
**データ形式**: JSON、FormData (画像)

```python
# FastAPI エンドポイント例
@app.post("/api/v1/travel-plans")
async def create_travel_plan(plan: TravelPlanCreate):
    # 1. データベースに保存
    # 2. AI生成をトリガー
    # 3. 結果をキャッシュ
    pass

@app.post("/api/v1/upload-images")
async def upload_image(file: UploadFile):
    # 1. Cloud Storageに保存
    # 2. AI画像分析
    # 3. 結果をデータベースに保存
    pass
```

### 3. Backend → 各サービス（並列アクセス）

#### A. Backend → Vertex AI (直接アクセス)
**目的**: AI生成処理
**通信方法**: Google Cloud Client Library
**データ**: テキストプロンプト、画像データ

```python
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

class GeminiService:
    def __init__(self):
        self.model = GenerativeModel("gemini-1.5-pro")
    
    async def generate_travel_guide(self, destination: str, spots: List[str]):
        """旅行ガイド生成"""
        prompt = f"""
        {destination}の歴史的な旅行ガイドを作成してください。
        観光スポット: {', '.join(spots)}
        
        以下の形式で出力してください：
        1. 歴史年表
        2. 各スポットの詳細
        3. チェックポイント
        """
        
        # Built-in Tools (Search, Maps) を自動使用
        response = await self.model.generate_content_async(
            prompt,
            tools=["google_search", "google_maps"]
        )
        
        return response.text
    
    async def analyze_photo(self, image_data: bytes):
        """写真分析"""
        response = await self.model.generate_content_async([
            "この写真に写っている観光地や歴史的建造物を特定してください",
            {"mime_type": "image/jpeg", "data": image_data}
        ])
        
        return response.text
```

#### B. Backend → Cloud SQL (直接アクセス)
**目的**: 構造化データの永続化
**通信方法**: SQLAlchemy ORM
**データ**: 旅行計画、ガイド、振り返りデータ

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.travel_plan.entity import TravelPlan

class TravelPlanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save(self, travel_plan: TravelPlan) -> TravelPlan:
        """旅行計画を保存"""
        self.db.add(travel_plan)
        await self.db.commit()
        await self.db.refresh(travel_plan)
        return travel_plan
    
    async def find_by_id(self, plan_id: str) -> TravelPlan:
        """旅行計画を取得"""
        result = await self.db.execute(
            select(TravelPlan).where(TravelPlan.id == plan_id)
        )
        return result.scalar_one_or_none()
```

#### C. Backend → Redis (直接アクセス)
**目的**: キャッシュ、セッション管理
**通信方法**: Redis Client
**データ**: AI生成結果、セッション情報

```python
import redis.asyncio as redis
import json

class CacheService:
    def __init__(self):
        self.redis = redis.Redis(host="memorystore-redis-host")
    
    async def cache_ai_result(self, key: str, result: dict, ttl: int = 3600):
        """AI生成結果をキャッシュ"""
        await self.redis.setex(
            key, 
            ttl, 
            json.dumps(result, ensure_ascii=False)
        )
    
    async def get_cached_result(self, key: str) -> dict:
        """キャッシュされた結果を取得"""
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_user_session(self, session_id: str, user_data: dict):
        """ユーザーセッションをキャッシュ"""
        await self.redis.setex(
            f"session:{session_id}",
            1800,  # 30分
            json.dumps(user_data)
        )
```

#### D. Backend → Cloud Storage (直接アクセス)
**目的**: ファイル保存・取得
**通信方法**: Google Cloud Storage Client
**データ**: 画像ファイル、生成されたPDF

```python
from google.cloud import storage
import aiofiles

class StorageService:
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket("historical-travel-photos")
    
    async def upload_photo(self, user_id: str, photo_id: str, file_data: bytes) -> str:
        """写真をアップロード"""
        blob_name = f"photos/{user_id}/{photo_id}.jpg"
        blob = self.bucket.blob(blob_name)
        
        # 非同期アップロード
        blob.upload_from_string(file_data, content_type="image/jpeg")
        
        # 公開URLを返す
        return f"https://storage.googleapis.com/{self.bucket.name}/{blob_name}"
    
    async def get_photo_url(self, user_id: str, photo_id: str) -> str:
        """写真のURLを取得"""
        blob_name = f"photos/{user_id}/{photo_id}.jpg"
        blob = self.bucket.blob(blob_name)
        
        # 署名付きURLを生成（1時間有効）
        return blob.generate_signed_url(expiration=3600)
```

## 🔄 実際の処理フロー例

### 例1: 旅行ガイド生成
```python
async def generate_travel_guide_use_case(plan_id: str):
    # 1. データベースから旅行計画を取得
    travel_plan = await travel_plan_repo.find_by_id(plan_id)
    
    # 2. キャッシュをチェック
    cache_key = f"guide:{plan_id}"
    cached_guide = await cache_service.get_cached_result(cache_key)
    if cached_guide:
        return cached_guide
    
    # 3. AI生成（Vertex AI）
    guide_content = await gemini_service.generate_travel_guide(
        travel_plan.destination,
        [spot.name for spot in travel_plan.spots]
    )
    
    # 4. 結果をデータベースに保存
    travel_guide = TravelGuide(
        plan_id=plan_id,
        content=guide_content
    )
    await travel_guide_repo.save(travel_guide)
    
    # 5. 結果をキャッシュ
    await cache_service.cache_ai_result(cache_key, guide_content)
    
    return guide_content
```

### 例2: 写真アップロード・分析
```python
async def upload_and_analyze_photo_use_case(user_id: str, file_data: bytes):
    photo_id = generate_uuid()
    
    # 1. Cloud Storageに保存（並列）
    upload_task = storage_service.upload_photo(user_id, photo_id, file_data)
    
    # 2. AI分析（並列）
    analysis_task = gemini_service.analyze_photo(file_data)
    
    # 並列実行
    photo_url, analysis_result = await asyncio.gather(
        upload_task,
        analysis_task
    )
    
    # 3. 結果をデータベースに保存
    photo = Photo(
        id=photo_id,
        user_id=user_id,
        url=photo_url,
        analysis=analysis_result
    )
    await photo_repo.save(photo)
    
    return photo
```

## 🎯 重要なポイント

### 1. **並列処理**
- Backend から各サービスへは**並列でアクセス**
- Cloud SQL を経由して他のサービスにアクセスすることはない
- 各サービスは独立して動作

### 2. **データの流れ**
- **構造化データ** → Cloud SQL
- **キャッシュデータ** → Redis  
- **ファイルデータ** → Cloud Storage
- **AI処理** → Vertex AI

### 3. **パフォーマンス最適化**
- AI生成結果のキャッシュ（Redis）
- 画像の署名付きURL（Cloud Storage）
- 非同期処理（asyncio）

### 4. **エラーハンドリング**
- 各サービスへのアクセスは独立してエラーハンドリング
- 一つのサービスが失敗しても他に影響しない設計

この設計により、高いパフォーマンスと可用性を実現しています。