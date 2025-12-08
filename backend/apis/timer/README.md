# Timer API

学習タイマー機能のAPI実装

## 概要

ユーザーの学習時間を測定・記録するための機能

## API エンドポイント

- `POST /timer/start` - タイマー開始
- `POST /timer/stop` - タイマー停止
- `GET /timer/current` - 現在のタイマー状態取得
- `GET /timer/history` - タイマー履歴取得

## 機能

- ユーザーごとの同時実行制限（1つのタイマーのみ）
- 自動保存機能（5分ごと）
- 異常終了時の復旧機能

## 開発

```bash
# 依存関係インストール
poetry install

# ローカル実行
poetry run uvicorn src.main:app --reload

# テスト実行
poetry run pytest
```