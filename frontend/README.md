# Frontend

学習プラットフォームのフロントエンド実装

## 概要

React 18 + TypeScript による SPA

## 技術スタック

- React 18
- TypeScript
- Vite (ビルドツール)
- Tailwind CSS (スタイリング)
- Zustand (状態管理)
- React Router v6 (ルーティング)
- Axios (HTTPクライアント)
- Radix UI (UIコンポーネント)
- Recharts (グラフ)
- React Hook Form + Zod (フォーム管理)

## 開発コマンド

```bash
# 依存関係インストール
pnpm install

# 開発サーバー起動
pnpm dev

# ビルド
pnpm build

# テスト実行
pnpm test

# リント・フォーマット
pnpm lint
pnpm format
```

## ディレクトリ構成

- `src/api/` - API通信ロジック
- `src/components/` - 共通UIコンポーネント
- `src/features/` - 機能別コンポーネント
- `src/hooks/` - カスタムフック
- `src/pages/` - ページコンポーネント
- `src/store/` - 状態管理
- `src/utils/` - ユーティリティ関数