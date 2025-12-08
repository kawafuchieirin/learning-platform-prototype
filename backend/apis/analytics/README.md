# Analytics API

学習分析機能のAPI実装

## 概要

週次レポートとデータ可視化機能

## API エンドポイント

- `GET /analytics/weekly` - 週次レポート取得
- `GET /analytics/summary` - サマリー取得
- `GET /analytics/comparison` - 前週比較データ取得

## 機能

- 週単位の集計（月曜始まり）
- グラフデータのJSON形式での提供
- 前週比の自動計算

## データ処理

- pandas による集計処理
- numpy による統計計算
- DynamoDB からのデータ取得・分析

## 開発

```bash
# 依存関係インストール
poetry install

# ローカル実行
poetry run uvicorn src.main:app --reload

# テスト実行
poetry run pytest
```