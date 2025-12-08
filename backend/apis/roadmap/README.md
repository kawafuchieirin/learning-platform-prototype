# Roadmap API

学習ロードマップ機能のAPI実装

## 概要

学習計画の作成・管理・CSV対応機能

## API エンドポイント

- `POST /roadmap/` - ロードマップ作成
- `GET /roadmap/` - ロードマップ一覧取得
- `GET /roadmap/{id}` - ロードマップ詳細取得
- `PUT /roadmap/{id}` - ロードマップ更新
- `DELETE /roadmap/{id}` - ロードマップ削除
- `POST /roadmap/import` - CSVインポート
- `GET /roadmap/template` - CSVテンプレートダウンロード

## 機能

- CSV形式対応（タイトル, 予定時間, 進捗率）
- インポート時のバリデーション
- 進捗率の自動計算（学習記録から）

## 開発

```bash
# 依存関係インストール
poetry install

# ローカル実行
poetry run uvicorn src.main:app --reload

# テスト実行
poetry run pytest
```