# APIs

機能別API実装

## 機能一覧

- `timer/` - 学習タイマー機能
- `roadmap/` - 学習ロードマップ機能
- `slack/` - Slack連携機能
- `analytics/` - 学習分析機能
- `records/` - 学習記録機能

## 共通構成

各機能ディレクトリには以下が含まれます：

- `lambda/` - Lambda関数実装
- `terraform/` - インフラ定義
- `docker/` - ローカル開発環境
- `tests/` - テスト
- `pyproject.toml` - Python依存関係
- `README.md` - 機能別ドキュメント