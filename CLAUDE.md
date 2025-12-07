# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

learning-platform-prototype - 20〜30人向けの小規模SaaS型学習管理プラットフォーム

### 主要機能
1. **ログイン機能** - ユーザー認証とセッション管理
2. **学習タイマー機能** - 学習時間の記録と管理
3. **ロードマップ機能** - 学習計画の作成・管理（CSV対応）
4. **Slack連携機能** - 学習記録の自動投稿
5. **学習分析機能** - 週次レポートとデータ可視化
6. **学習記録テンプレート** - 記録作成の効率化

### 技術スタック
- **言語**: Python 3.13
- **フレームワーク**: FastAPI
- **インフラ**: AWS (Lambda + API Gateway)
- **IaC**: Terraform
- **データベース**: DynamoDB
- **外部連携**: Slack OAuth / Bot Token

### アーキテクチャ方針
- マイクロサービスアーキテクチャ（各機能を独立したLambda関数として実装）
- サーバーレス設計（ECSではなくLambda関数を使用）
- API駆動型設計（各機能はAPIとして公開）
- ローカル開発はDockerで環境構築（DynamoDB Local使用）
- AWS環境は本番環境のみ構築

## 開発環境セットアップ

### 必要な前提条件
- Python 3.13
- Docker & Docker Compose
- Terraform 1.0以上（本番環境デプロイ用）
- AWS CLI（本番環境デプロイ用、設定済み）
- Git

### 初期セットアップ
```bash
# 開発用依存関係のインストール
pip install -r requirements-dev.txt

# pre-commitフックのインストール
pre-commit install
pre-commit install --hook-type commit-msg

# 初回実行（すべてのフックを実行）
pre-commit run --all-files

# Docker環境の起動
docker-compose up -d

# DynamoDB Localのテーブル初期化
python scripts/init_local_db.py
```

### ローカル開発環境（Docker）
```yaml
# docker-compose.yml の構成
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=local
      - DYNAMODB_ENDPOINT=http://dynamodb-local:8000
    depends_on:
      - dynamodb-local

  dynamodb-local:
    image: amazon/dynamodb-local:latest
    ports:
      - "8001:8000"
    command: "-jar DynamoDBLocal.jar -sharedDb -inMemory"

  dynamodb-admin:
    image: aaronshaf/dynamodb-admin
    ports:
      - "8002:8001"
    environment:
      - DYNAMO_ENDPOINT=http://dynamodb-local:8000
```

## よく使うコマンド

### Docker関連
```bash
# Docker環境の起動
docker-compose up -d

# Docker環境の停止
docker-compose down

# ログ確認
docker-compose logs -f api

# DynamoDB Adminへアクセス（ブラウザ）
open http://localhost:8002

# コンテナ内でコマンド実行
docker-compose exec api bash

# Docker環境の再構築
docker-compose down && docker-compose up -d --build
```

### pre-commit関連
```bash
# 手動でpre-commitを実行
pre-commit run --all-files

# 特定のフックのみ実行
pre-commit run black --all-files
pre-commit run flake8 --all-files

# pre-commitをアップデート
pre-commit autoupdate
```

### Python開発
```bash
# コードフォーマット
black .
isort .

# リント実行
flake8 .
mypy .

# セキュリティチェック
bandit -r .

# テスト実行（ローカル）
docker-compose exec api pytest
docker-compose exec api pytest --cov=. --cov-report=html

# ローカルでのAPI起動（Docker外）
uvicorn src.api.main:app --reload --port 8000
```

### Terraform開発（本番環境デプロイ用）
```bash
# 本番環境ディレクトリへ移動
cd infrastructure/environments/prod

# 初期化
terraform init

# フォーマット
terraform fmt -recursive

# 検証
terraform validate

# プラン確認
terraform plan

# デプロイ実行
terraform apply

# TFLint実行
tflint

# セキュリティチェック
tfsec .
```

### 本番環境デプロイ
```bash
# デプロイスクリプト実行
./scripts/deploy.sh

# Lambda関数の個別デプロイ
cd infrastructure/environments/prod
terraform apply -target=module.lambda_auth
```

## ディレクトリ構造

```
learning-platform-prototype/
├── src/                          # ソースコード
│   ├── api/                      # FastAPI アプリケーション
│   │   ├── auth/                 # 認証機能
│   │   ├── timer/                # タイマー機能
│   │   ├── roadmap/              # ロードマップ機能
│   │   ├── slack/                # Slack連携
│   │   ├── analytics/            # 分析機能
│   │   └── records/              # 学習記録
│   ├── lambda/                   # Lambda関数
│   │   ├── auth/                 # 認証Lambda
│   │   ├── timer/                # タイマーLambda
│   │   ├── roadmap/              # ロードマップLambda
│   │   ├── slack/                # Slack連携Lambda
│   │   ├── analytics/            # 分析Lambda
│   │   └── records/              # 学習記録Lambda
│   ├── models/                   # データモデル定義
│   ├── services/                 # ビジネスロジック
│   ├── repositories/             # DynamoDBアクセス層
│   └── shared/                   # 共通ユーティリティ
├── infrastructure/               # Terraformコード
│   ├── modules/                  # Terraformモジュール
│   │   ├── lambda/              # Lambda関数モジュール
│   │   ├── api_gateway/         # API Gatewayモジュール
│   │   ├── dynamodb/            # DynamoDBモジュール
│   │   └── iam/                 # IAMモジュール
│   └── environments/            # 環境別設定
│       └── prod/                # 本番環境のみ（ローカルはDocker使用）
├── tests/                       # テストコード
│   ├── unit/                    # ユニットテスト
│   ├── integration/             # 統合テスト
│   └── e2e/                     # E2Eテスト
├── scripts/                     # 各種スクリプト
│   ├── init_local_db.py        # DynamoDB Local初期化
│   └── deploy.sh               # 本番環境デプロイスクリプト
├── docs/                        # ドキュメント
├── templates/                   # テンプレートファイル
│   └── csv/                     # CSVテンプレート
├── docker-compose.yml           # Docker構成ファイル
├── Dockerfile                   # APIコンテナ定義
└── .env.example                 # 環境変数サンプル

## API設計

### 認証API (`/api/v1/auth`)
- `POST /login` - ユーザーログイン
- `POST /logout` - ユーザーログアウト
- `POST /refresh` - トークンリフレッシュ
- `GET /me` - 現在のユーザー情報取得

### タイマーAPI (`/api/v1/timer`)
- `POST /start` - タイマー開始
- `POST /stop` - タイマー停止
- `GET /current` - 現在のタイマー状態取得
- `GET /history` - タイマー履歴取得

### ロードマップAPI (`/api/v1/roadmap`)
- `POST /` - ロードマップ作成
- `GET /` - ロードマップ一覧取得
- `GET /{id}` - ロードマップ詳細取得
- `PUT /{id}` - ロードマップ更新
- `DELETE /{id}` - ロードマップ削除
- `POST /import` - CSVインポート
- `GET /template` - CSVテンプレートダウンロード

### Slack API (`/api/v1/slack`)
- `POST /connect` - Slack連携設定
- `DELETE /disconnect` - Slack連携解除
- `POST /test` - テスト投稿
- `GET /status` - 連携状態確認

### 分析API (`/api/v1/analytics`)
- `GET /weekly` - 週次レポート取得
- `GET /summary` - サマリー取得
- `GET /comparison` - 前週比較データ取得

### 学習記録API (`/api/v1/records`)
- `POST /` - 学習記録作成
- `GET /` - 学習記録一覧取得
- `GET /{id}` - 学習記録詳細取得
- `PUT /{id}` - 学習記録更新
- `DELETE /{id}` - 学習記録削除
- `POST /from-template` - テンプレートから作成

## DynamoDBテーブル設計

### Users Table
- PK: `USER#{user_id}`
- SK: `PROFILE`
- Attributes: email, name, created_at, updated_at

### Timer Table
- PK: `USER#{user_id}`
- SK: `TIMER#{timestamp}`
- Attributes: start_time, end_time, duration, status

### Roadmap Table
- PK: `USER#{user_id}`
- SK: `ROADMAP#{roadmap_id}`
- Attributes: title, items, total_hours, progress, created_at

### Records Table
- PK: `USER#{user_id}`
- SK: `RECORD#{timestamp}`
- Attributes: content, comment, duration, roadmap_id, created_at

### SlackConfig Table
- PK: `USER#{user_id}`
- SK: `SLACK_CONFIG`
- Attributes: workspace_id, channel_id, bot_token, enabled

## 開発時の注意事項

### 一般的な開発方針
- プロジェクトの段階に応じた適切な品質レベルを維持
- プロトタイプ段階では、素早い実装と検証を優先
- 将来の拡張性を考慮した設計を心がける
- コミット前にpre-commitが自動実行されるため、エラーがある場合は修正してから再度コミット
- Pythonコードは Black でフォーマットされ、isort でインポートが整理される
- Terraformコードは terraform fmt で自動整形される

### Lambda関数開発
- 各Lambda関数は単一責任の原則に従う
- コールドスタート対策として軽量な実装を心がける
- 環境変数で設定値を管理
- Lambda Layerで共通ライブラリを共有

### API開発
- FastAPIの自動ドキュメント生成機能を活用
- Pydanticでリクエスト/レスポンスの型定義
- 適切なHTTPステータスコードの使用
- エラーハンドリングの統一

### DynamoDB設計
- Single Table Designパターンを採用
- 複合キー（PK/SK）で効率的なクエリを実現
- GSI（Global Secondary Index）は必要最小限に
- TTLで古いデータの自動削除を設定

### セキュリティ
- 環境変数に機密情報を格納（AWS Systems Manager Parameter Store推奨）
- IAMロールは最小権限の原則に従う
- API GatewayでのCORS設定に注意
- Slack Bot Tokenの安全な管理

### 環境の切り分け
- **ローカル環境**: Docker + DynamoDB Local
  - FastAPIは通常のWebサーバーとして起動
  - DynamoDB LocalをDynamoDBの代替として使用
  - 環境変数 `ENV=local` で識別

- **本番環境**: AWS Lambda + DynamoDB
  - FastAPIをMangumでラップしてLambdaで実行
  - API Gateway経由でアクセス
  - 環境変数 `ENV=production` で識別
  - Terraformで全リソースを管理

### README.md運用
- 各意味のあるディレクトリにREADME.mdを配置
- コード作成時に必ずREADME.mdを読み込む
- 変更があれば必ずREADME.mdも更新
- APIエンドポイントの仕様を明記

## 各機能の詳細

### ログイン機能
- JWT（JSON Web Token）を使用した認証
- アクセストークンとリフレッシュトークンの管理
- セッションの有効期限設定（デフォルト: 24時間）

### 学習タイマー機能
- ユーザーごとの同時実行制限（1つのタイマーのみ）
- 自動保存機能（5分ごと）
- 異常終了時の復旧機能

### ロードマップ機能
- CSV形式: タイトル, 予定時間, 進捗率
- インポート時のバリデーション
- 進捗率の自動計算（学習記録から）

### Slack連携機能
- OAuth 2.0による認証フロー
- 学習記録の自動投稿フォーマット
- 投稿タイミングの設定（即時/日次まとめ）

### 学習分析機能
- 週単位の集計（月曜始まり）
- グラフデータのJSON形式での提供
- 前週比の自動計算

### 学習記録テンプレート
- ロードマップからの自動生成
- カスタムテンプレートの保存
- タイマーAPIとの連携

## pre-commitフック

このプロジェクトでは以下のpre-commitフックが設定されています：

### 汎用フック
- trailing-whitespace: 行末の空白を削除
- end-of-file-fixer: ファイル末尾に改行を追加
- check-yaml: YAMLファイルの構文チェック
- check-json: JSONファイルの構文チェック
- check-added-large-files: 大きなファイルの追加を防止
- check-merge-conflict: マージコンフリクトマーカーの検出
- mixed-line-ending: 改行コードをLFに統一

### Python用フック
- black: コードフォーマッター（最大行長88文字）
- isort: インポート文の整理
- flake8: Pythonリンター
- mypy: 静的型チェック
- bandit: セキュリティ脆弱性チェック

### Terraform用フック
- terraform_fmt: Terraformコードのフォーマット
- terraform_validate: Terraform構文検証
- terraform_tflint: TFLintによる詳細チェック
- terraform_docs: ドキュメント自動生成
- terraform_checkov: インフラのセキュリティチェック
- terraform_tfsec: Terraformセキュリティスキャナー

### セキュリティ
- detect-secrets: 秘密情報の検出
