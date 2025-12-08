# Slack API

Slack連携機能のAPI実装

## 概要

学習記録のSlack自動投稿機能

## API エンドポイント

- `POST /slack/connect` - Slack連携設定
- `DELETE /slack/disconnect` - Slack連携解除
- `POST /slack/test` - テスト投稿
- `GET /slack/status` - 連携状態確認

## 機能

- OAuth 2.0による認証フロー
- 学習記録の自動投稿フォーマット
- 投稿タイミングの設定（即時/日次まとめ）

## 環境変数

```bash
SLACK_CLIENT_ID=your_client_id
SLACK_CLIENT_SECRET=your_client_secret
SLACK_SIGNING_SECRET=your_signing_secret
```

## 開発

```bash
# 依存関係インストール
poetry install

# ローカル実行
poetry run uvicorn src.main:app --reload

# テスト実行
poetry run pytest
```