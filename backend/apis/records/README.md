# Records API

学習記録機能のAPI実装

## 概要

学習記録の作成・管理・テンプレート機能

## API エンドポイント

- `POST /records/` - 学習記録作成
- `GET /records/` - 学習記録一覧取得
- `GET /records/{id}` - 学習記録詳細取得
- `PUT /records/{id}` - 学習記録更新
- `DELETE /records/{id}` - 学習記録削除
- `POST /records/from-template` - テンプレートから作成

## 機能

- ロードマップからの自動生成
- カスタムテンプレートの保存
- タイマーAPIとの連携

## 開発

```bash
# 依存関係インストール
poetry install

# ローカル実行
poetry run uvicorn src.main:app --reload

# テスト実行
poetry run pytest
```