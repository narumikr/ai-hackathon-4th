# 共通UIコンポーネント設計書

## 概要

歴史学習特化型旅行AIエージェントシステムのフロントエンド共通UIコンポーネント一覧。Next.js 16 + TypeScriptで実装し、再利用可能で一貫性のあるユーザーインターフェースを提供する。

## 基本方針

- **再利用性**: 複数の画面で使用可能な汎用的な設計
- **一貫性**: 統一されたデザインシステム
- **アクセシビリティ**: WCAG 2.1 AA準拠
- **TypeScript**: 型安全性の確保
- **レスポンシブ**: モバイルファースト対応

## コンポーネント一覧

### 1. 基本フォームコンポーネント

#### Button
- **ファイル**: `components/ui/Button.tsx`
- **用途**: 各種アクション実行
- **バリエーション**:
  - Primary（メインアクション）
  - Secondary（サブアクション）
  - Danger（削除など危険な操作）
  - Ghost（軽微なアクション）
- **Props**:
  - `variant`: 'primary' | 'secondary' | 'danger' | 'ghost'
  - `size`: 'sm' | 'md' | 'lg'
  - `disabled`: boolean
  - `loading`: boolean
  - `onClick`: () => void

#### TextField
- **ファイル**: `components/ui/TextField.tsx`
- **用途**: 単一行テキスト入力
- **機能**:
  - バリデーションエラー表示
  - プレースホルダー対応
  - 必須項目マーク
- **Props**:
  - `label`: string
  - `placeholder`: string
  - `required`: boolean
  - `error`: string
  - `value`: string
  - `onChange`: (value: string) => void

#### TextArea
- **ファイル**: `components/ui/TextArea.tsx`
- **用途**: 複数行テキスト入力（感想・メモ）
- **機能**:
  - 自動リサイズ
  - 文字数カウント
  - バリデーションエラー表示
- **Props**:
  - `label`: string
  - `placeholder`: string
  - `required`: boolean
  - `error`: string
  - `maxLength`: number
  - `rows`: number
  - `value`: string
  - `onChange`: (value: string) => void

#### Checkbox
- **ファイル**: `components/ui/Checkbox.tsx`
- **用途**: チェックポイント確認、複数選択
- **機能**:
  - 中間状態（indeterminate）対応
  - ラベルクリックでの切り替え
- **Props**:
  - `label`: string
  - `checked`: boolean
  - `indeterminate`: boolean
  - `disabled`: boolean
  - `onChange`: (checked: boolean) => void

#### RadioButton
- **ファイル**: `components/ui/RadioButton.tsx`
- **用途**: 単一選択（旅行状態選択など）
- **機能**:
  - グループ管理
  - ラベルクリックでの選択
- **Props**:
  - `name`: string
  - `value`: string
  - `label`: string
  - `checked`: boolean
  - `disabled`: boolean
  - `onChange`: (value: string) => void

#### FormField
- **ファイル**: `components/ui/FormField.tsx`
- **用途**: ラベル+入力+エラーメッセージのセット
- **機能**:
  - 統一されたフォームレイアウト
  - エラー状態の視覚的表示
  - 必須項目マーク
- **Props**:
  - `label`: string
  - `required`: boolean
  - `error`: string
  - `helpText`: string
  - `children`: ReactNode

### 2. ファイル・メディア関連コンポーネント

#### FileUploader
- **ファイル**: `components/ui/FileUploader.tsx`
- **用途**: 画像ファイルのアップロード
- **機能**:
  - ドラッグ&ドロップ対応
  - 複数ファイル選択
  - ファイル形式制限
  - プログレス表示
- **Props**:
  - `accept`: string
  - `multiple`: boolean
  - `maxSize`: number
  - `onUpload`: (files: File[]) => void
  - `onError`: (error: string) => void

#### Card
- **ファイル**: `components/ui/Card.tsx`
- **用途**: 汎用カードコンポーネント（画像、テキスト、アクションなど多様なコンテンツ表示）
- **機能**:
  - 画像表示（オプション）
  - タイトル・説明文表示
  - アクションボタン配置
  - クリック可能なカード
  - 複数のバリエーション対応
- **Props**:
  - `variant`: 'default' | 'outlined' | 'elevated'
  - `image`: { src: string; alt: string } | undefined
  - `title`: string | undefined
  - `description`: string | undefined
  - `actions`: ReactNode | undefined
  - `clickable`: boolean | undefined - カードをクリック可能にするかどうか（デフォルト: false。`onClick` が提供されている場合は自動的に true になる）
  - `onClick`: (e: React.MouseEvent<HTMLDivElement>) => void | undefined
  - `children`: ReactNode

### 3. データ表示コンポーネント

#### Table
- **ファイル**: `components/ui/Table.tsx`
- **用途**: 旅行一覧、振り返り一覧の表示
- **機能**:
  - ソート機能
  - ページネーション
  - 行選択
  - レスポンシブ対応
- **Props**:
  - `columns`: ColumnDef[]
  - `data`: T[]
  - `sortable`: boolean
  - `selectable`: boolean
  - `onRowClick`: (row: T) => void

#### List
- **ファイル**: `components/ui/List.tsx`
- **用途**: 汎用リスト表示
- **機能**:
  - カスタムアイテムレンダリング
  - 空状態表示
  - ローディング状態
- **Props**:
  - `items`: T[]
  - `renderItem`: (item: T) => ReactNode
  - `loading`: boolean
  - `emptyMessage`: string

#### Accordion
- **ファイル**: `components/ui/Accordion.tsx`
- **用途**: 折りたたみ可能なセクション表示
- **機能**:
  - 単一・複数展開対応
  - アニメーション
  - アイコン表示
- **Props**:
  - `items`: AccordionItem[]
  - `multiple`: boolean
  - `defaultOpen`: string[]

### 4. フィードバック・状態表示コンポーネント

#### Modal
- **ファイル**: `components/ui/Modal.tsx`
- **用途**: 確認ダイアログ、詳細表示
- **機能**:
  - オーバーレイ
  - ESCキーで閉じる
  - フォーカストラップ
- **Props**:
  - `isOpen`: boolean
  - `onClose`: () => void
  - `title`: string
  - `size`: 'sm' | 'md' | 'lg' | 'xl'
  - `children`: ReactNode

#### Dialog
- **ファイル**: `components/ui/Dialog.tsx`
- **用途**: 確認・警告メッセージ
- **機能**:
  - 確認/キャンセルボタン
  - アイコン表示
  - 危険な操作の警告
- **Props**:
  - `isOpen`: boolean
  - `onClose`: () => void
  - `onConfirm`: () => void
  - `title`: string
  - `message`: string
  - `type`: 'info' | 'warning' | 'danger'

#### LoadingSpinner
- **ファイル**: `components/ui/LoadingSpinner.tsx`
- **用途**: AI生成処理中の表示
- **機能**:
  - 回転アニメーション
  - サイズ調整
  - メッセージ表示
- **Props**:
  - `size`: 'sm' | 'md' | 'lg'
  - `message`: string
  - `overlay`: boolean

#### Tooltip
- **ファイル**: `components/ui/Tooltip.tsx`
- **用途**: ヘルプ・説明表示
- **機能**:
  - ホバー・フォーカスで表示
  - 位置調整
  - 遅延表示
- **Props**:
  - `content`: string
  - `position`: 'top' | 'bottom' | 'left' | 'right'
  - `delay`: number
  - `children`: ReactNode

### 5. レイアウトコンポーネント

#### Header
- **ファイル**: `components/layout/Header.tsx`
- **用途**: サイト共通ヘッダー
- **機能**:
  - ロゴ表示
  - ナビゲーションメニュー
  - ユーザー情報表示
  - レスポンシブメニュー
- **Props**:
  - `user`: User | null
  - `onMenuClick`: () => void

#### Breadcrumb
- **ファイル**: `components/layout/Breadcrumb.tsx`
- **用途**: パンくずナビゲーション
- **機能**:
  - 階層表示
  - リンク機能
  - 現在ページの強調
- **Props**:
  - `items`: BreadcrumbItem[]
  - `separator`: string

## ファイル構成

```
frontend/src/components/
├── ui/                          # 基本UIコンポーネント
│   ├── Button.tsx
│   ├── TextField.tsx
│   ├── TextArea.tsx
│   ├── Checkbox.tsx
│   ├── RadioButton.tsx
│   ├── FormField.tsx
│   ├── FileUploader.tsx
│   ├── Card.tsx
│   ├── Table.tsx
│   ├── List.tsx
│   ├── Accordion.tsx
│   ├── Modal.tsx
│   ├── Dialog.tsx
│   ├── LoadingSpinner.tsx
│   ├── Tooltip.tsx
│   └── index.ts                 # エクスポート用
└── layout/                      # レイアウトコンポーネント
    ├── Header.tsx
    ├── Breadcrumb.tsx
    └── index.ts                 # エクスポート用
```

## 型定義

```typescript
// types/ui.ts
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: ReactNode;
  onClick?: () => void;
}

export interface TextFieldProps {
  label: string;
  placeholder?: string;
  required?: boolean;
  error?: string;
  value: string;
  onChange: (value: string) => void;
}

export interface CardProps {
  variant?: 'default' | 'outlined' | 'elevated';
  image?: { src: string; alt: string };
  title?: string;
  description?: string;
  actions?: ReactNode;
  clickable?: boolean;
  onClick?: () => void;
  children?: ReactNode;
}

export interface ColumnDef {
  key: string;
  title: string;
  sortable?: boolean;
  render?: (value: T, row: T) => ReactNode;
}

export interface AccordionItem {
  id: string;
  title: string;
  content: ReactNode;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
}
```

## スタイリング方針

- **CSS Modules** または **Tailwind CSS** を使用
- **CSS Variables** でテーマカラー管理
- **レスポンシブブレークポイント**:
  - Mobile: ~768px
  - Tablet: 768px~1024px
  - Desktop: 1024px~

## 実装優先度

### Phase 1（MVP必須）
Button, TextField, TextArea, Modal, LoadingSpinner, Header

### Phase 2（機能充実）
Table, List, FormField, FileUploader, Card, Dialog

### Phase 3（UX向上）
Checkbox, RadioButton, Accordion, Tooltip, Breadcrumb

## 使用例

```tsx
// 基本的な使用例
import { Button, TextField, Modal } from '@/components/ui';

function TravelForm() {
  return (
    <form>
      <TextField
        label="旅行先"
        placeholder="例: 京都"
        required
        value={destination}
        onChange={setDestination}
      />
      <Button variant="primary" onClick={handleSubmit}>
        旅行ガイドを生成
      </Button>
    </form>
  );
}
```

この設計書に基づいて、段階的にコンポーネントを実装していくことで、一貫性のあるUIシステムを構築できます。