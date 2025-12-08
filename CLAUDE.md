# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

learning-platform-prototype - 20〜30人向けの小規模SaaS型学習管理プラットフォーム

### 主要機能
1. **学習タイマー機能** - 学習時間の記録と管理
2. **ロードマップ機能** - 学習計画の作成・管理（CSV対応）
3. **Slack連携機能** - 学習記録の自動投稿
4. **学習分析機能** - 週次レポートとデータ可視化
5. **学習記録テンプレート** - 記録作成の効率化

### 技術スタック

#### バックエンド
- **言語**: Python 3.13
- **パッケージ管理**: Poetry
- **フレームワーク**: FastAPI
- **インフラ**: AWS (Lambda + API Gateway)
- **IaC**: Terraform
- **データベース**: DynamoDB
- **認証**: AWS Cognito User Pool
- **外部連携**: Slack OAuth / Bot Token

#### フロントエンド
- **言語**: TypeScript
- **フレームワーク**: React 18
- **ビルドツール**: Vite
- **スタイリング**: Tailwind CSS
- **状態管理**: Zustand
- **ルーティング**: React Router v6
- **HTTPクライアント**: Axios
- **UI コンポーネント**: Radix UI + Tailwind
- **グラフ**: Recharts
- **フォーム管理**: React Hook Form + Zod
- **テスト**: Vitest + React Testing Library
- **E2Eテスト**: Playwright + MCP (Model Context Protocol)
- **リンター/フォーマッター**: ESLint + Prettier

### アーキテクチャ方針
- マイクロサービスアーキテクチャ（各機能を独立したLambda関数として実装）
- サーバーレス設計（ECSではなくLambda関数を使用）
- API駆動型設計（各機能はAPIとして公開）
- フロントエンドはSPAとして実装（S3 + CloudFront でホスティング）
- ローカル開発はDockerで環境構築（DynamoDB Local使用）
- AWS環境は本番環境のみ構築

### テスト・品質保証
- **ユニットテスト**: Jest (フロントエンド), pytest (バックエンド)
- **E2Eテスト**: Playwright + MCP（ブラウザ自動化、APIテスト）
- **品質管理**: pre-commit hooks, ESLint, Prettier, Black, isort

## 開発環境セットアップ

### 必要な前提条件
- Python 3.13
- Poetry 1.7以上
- Node.js 20以上
- pnpm 8以上
- Docker & Docker Compose
- Terraform 1.0以上（本番環境デプロイ用）
- AWS CLI（本番環境デプロイ用、設定済み）
- Git

### 初期セットアップ

#### バックエンド
```bash
# Poetryのインストール（未インストールの場合）
curl -sSL https://install.python-poetry.org | python3 -

# 依存関係のインストール
poetry install

# 仮想環境に入る
poetry shell

# pre-commitフックのインストール
pre-commit install
pre-commit install --hook-type commit-msg

# 初回実行（すべてのフックを実行）
pre-commit run --all-files

# Docker環境の起動
docker-compose up -d

# DynamoDB Localのテーブル初期化
poetry run python scripts/init_local_db.py
```

#### フロントエンド
```bash
# フロントエンドディレクトリへ移動
cd frontend

# pnpmのインストール（未インストールの場合）
npm install -g pnpm

# 依存関係のインストール
pnpm install

# 開発サーバーの起動
pnpm dev
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
# Docker環境の起動（バックエンド + DB）
docker-compose up -d

# Docker環境の停止
docker-compose down

# フルスタック起動（バックエンド + フロントエンド）
docker-compose up -d && cd frontend && pnpm dev

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

# 特定のフックのみ実行（Python）
pre-commit run black --all-files
pre-commit run flake8 --all-files

# 特定のフックのみ実行（フロントエンド）
pre-commit run eslint --all-files
pre-commit run prettier --all-files

# pre-commitをアップデート
pre-commit autoupdate
```

### Python開発（Poetry）
```bash
# 仮想環境に入る
poetry shell

# 依存関係の追加
poetry add package-name
poetry add --group dev package-name  # 開発依存

# 依存関係の更新
poetry update

# lockファイルの更新
poetry lock --no-update

# コードフォーマット
poetry run black .
poetry run isort .

# リント実行
poetry run flake8 .
poetry run mypy .

# セキュリティチェック
poetry run bandit -r .

# テスト実行（ローカル）
poetry run pytest
poetry run pytest --cov=. --cov-report=html

# ローカルでのAPI起動（Docker外）
poetry run uvicorn src.api.main:app --reload --port 8000
```

### フロントエンド開発
```bash
# 開発サーバーの起動
pnpm dev

# ビルド
pnpm build

# プレビュー（ビルド結果の確認）
pnpm preview

# テスト実行
pnpm test
pnpm test:watch  # ウォッチモード
pnpm test:coverage  # カバレッジレポート

# リント実行
pnpm lint
pnpm lint:fix  # 自動修正

# フォーマット
pnpm format
pnpm format:check  # チェックのみ

# 型チェック
pnpm type-check

# 依存関係の追加
pnpm add package-name
pnpm add -D package-name  # 開発依存

# Storybookの起動（UIコンポーネント開発）
pnpm storybook
pnpm build-storybook
```

### E2Eテスト（Playwright + MCP）
```bash
# E2Eテストディレクトリへ移動
cd tests/e2e

# 依存関係のインストール
npm install

# Playwrightブラウザをインストール
npm run install-browsers

# 全てのE2Eテストを実行
npm test

# ヘッドモードでテスト実行（ブラウザを表示）
npm run test:headed

# UIモードでテスト実行（インタラクティブ）
npm run test:ui

# デバッグモードでテスト実行
npm run test:debug

# Analytics APIテストのみ実行
npm run test:analytics

# APIテストのみ実行
npm run test:api

# HTMLレポートを表示
npm run report

# Playwright Codegen（操作を記録してテストコード生成）
npm run codegen http://localhost:3000
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
# バックエンドデプロイ
./scripts/deploy-backend.sh

# フロントエンドデプロイ
./scripts/deploy-frontend.sh

# フルデプロイ
./scripts/deploy.sh

# Lambda関数の個別デプロイ
cd infrastructure/environments/prod
terraform apply -target=module.lambda_auth

# フロントエンドのみデプロイ
cd frontend && pnpm build
aws s3 sync dist/ s3://your-bucket-name --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

## ディレクトリ構造

```
learning-platform-prototype/
├── backend/                      # バックエンドコード
│   ├── apis/                     # 機能別API実装
│   │   ├── timer/                # タイマー機能
│   │   │   ├── lambda/
│   │   │   ├── terraform/
│   │   │   ├── docker/
│   │   │   ├── tests/
│   │   │   │   ├── unit/
│   │   │   │   └── integration/
│   │   │   └── README.md
│   │   ├── roadmap/              # ロードマップ機能
│   │   │   ├── lambda/
│   │   │   ├── terraform/
│   │   │   ├── docker/
│   │   │   ├── tests/
│   │   │   │   ├── unit/
│   │   │   │   └── integration/
│   │   │   └── README.md
│   │   ├── slack/                # Slack連携
│   │   │   ├── lambda/
│   │   │   ├── terraform/
│   │   │   ├── docker/
│   │   │   ├── tests/
│   │   │   │   ├── unit/
│   │   │   │   └── integration/
│   │   │   └── README.md
│   │   ├── analytics/            # 分析機能
│   │   │   ├── lambda/
│   │   │   ├── terraform/
│   │   │   ├── docker/
│   │   │   ├── tests/
│   │   │   │   ├── unit/
│   │   │   │   └── integration/
│   │   │   └── README.md
│   │   └── records/              # 学習記録
│   │       ├── lambda/
│   │       ├── terraform/
│   │       ├── docker/
│   │       ├── tests/
│   │       │   ├── unit/
│   │       │   └── integration/
│   │       └── README.md
│   ├── shared/                   # 全機能共有のコード
│   │   ├── libs/                 # 共通ライブラリ
│   │   ├── terraform/            # 共通Terraformモジュール
│   │   ├── docker/               # 共通Docker設定
│   │   └── README.md
│   └── tests/                    # プロジェクト横断のテスト（任意）
│       ├── e2e/                  # 全機能統合テスト
│       └── performance/          # 負荷テストなど
├── frontend/                     # フロントエンドコード
│   ├── public/                   # 静的ファイル
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/                  # API クライアント
│   │   │   ├── timer.ts
│   │   │   ├── roadmap.ts
│   │   │   ├── slack.ts
│   │   │   ├── analytics.ts
│   │   │   └── records.ts
│   │   ├── components/           # 共通UIコンポーネント
│   │   │   ├── common/           # 汎用コンポーネント
│   │   │   ├── layout/           # レイアウトコンポーネント
│   │   │   └── charts/           # グラフコンポーネント
│   │   ├── features/             # 機能別コンポーネント
│   │   │   ├── timer/
│   │   │   ├── roadmap/
│   │   │   ├── slack/
│   │   │   ├── analytics/
│   │   │   └── records/
│   │   ├── hooks/                # カスタムフック
│   │   ├── pages/                # ページコンポーネント
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   ├── roadmap/
│   │   │   ├── analytics/
│   │   │   └── settings/
│   │   ├── store/                # 状態管理（Zustand）
│   │   ├── styles/               # グローバルスタイル
│   │   ├── utils/                # ユーティリティ関数
│   │   ├── constants/            # 定数定義
│   │   ├── types/                # TypeScript型定義
│   │   ├── App.tsx               # メインコンポーネント
│   │   └── main.tsx              # エントリポイント
│   ├── .env.example              # 環境変数サンプル
│   ├── index.html                # HTMLテンプレート
│   ├── package.json
│   ├── pnpm-lock.yaml            # pnpm依存関係ロック
│   ├── tsconfig.json             # TypeScript設定
│   ├── vite.config.ts            # Vite設定
│   ├── tailwind.config.js        # Tailwind設定
│   ├── postcss.config.js         # PostCSS設定
│   └── README.md                 # フロントエンド開発ドキュメント
├── infrastructure/               # Terraformコード
│   ├── modules/                  # Terraformモジュール
│   │   ├── lambda/               # Lambda関数モジュール
│   │   ├── api_gateway/          # API Gatewayモジュール
│   │   ├── dynamodb/             # DynamoDBモジュール
│   │   ├── s3_cloudfront/        # S3 + CloudFront（フロントエンド用）
│   │   └── iam/                  # IAMモジュール
│   └── environments/             # 環境別設定
│       └── prod/                 # 本番環境のみ
├── scripts/                      # 各種スクリプト
│   ├── init_local_db.py          # DynamoDB Local初期化
│   └── deploy.sh                 # 本番環境デプロイスクリプト
├── docs/                         # プロジェクトドキュメント
├── docker-compose.yml            # Docker構成ファイル
├── .pre-commit-config.yaml       # pre-commit設定
└── README.md                     # プロジェクトREADME

## API設計

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

### フロントエンド開発
- コンポーネント駆動開発（React）
- TypeScriptで型安全性を確保
- フィーチャーベースのディレクトリ構成
- Tailwind CSSでユーティリティファーストなスタイリング
- Zustandによるシンプルな状態管理
- React Hook Form + Zodで型安全なフォームバリデーション

### セキュリティ
- 環境変数に機密情報を格納（AWS Systems Manager Parameter Store推奨）
- IAMロールは最小権限の原則に従う
- API GatewayでのCORS設定に注意
- Slack Bot Tokenの安全な管理

### 環境の切り分け

#### バックエンド
- **ローカル環境**: Docker + DynamoDB Local
  - FastAPIは通常のWebサーバーとして起動
  - DynamoDB LocalをDynamoDBの代替として使用
  - 環境変数 `ENV=local` で識別

- **本番環境**: AWS Lambda + DynamoDB
  - FastAPIをMangumでラップしてLambdaで実行
  - API Gateway経由でアクセス
  - 環境変数 `ENV=production` で識別
  - Terraformで全リソースを管理

#### フロントエンド
- **ローカル環境**: Vite開発サーバー
  - HMR（Hot Module Replacement）で高速リロード
  - ローカルAPIへプロキシ設定
  - 環境変数 `VITE_ENV=local` で識別

- **本番環境**: S3 + CloudFront
  - ビルド済みSPAをS3にデプロイ
  - CloudFrontでグローバル配信
  - 環境変数 `VITE_ENV=production` で識別

### README.md運用
- 各意味のあるディレクトリにREADME.mdを配置
- コード作成時に必ずREADME.mdを読み込む
- 変更があれば必ずREADME.mdも更新
- APIエンドポイントの仕様を明記
- フロントエンドのコンポーネント使用方法を記載

## 各機能の詳細

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

### フロントエンド用フック
- prettier: コードフォーマッター（HTML/CSS/JS/TS/JSON/MD）
- eslint: JavaScript/TypeScriptリンター
- stylelint: CSS/SCSSリンター

### Terraform用フック
- terraform_fmt: Terraformコードのフォーマット
- terraform_validate: Terraform構文検証
- terraform_tflint: TFLintによる詳細チェック
- terraform_docs: ドキュメント自動生成
- terraform_checkov: インフラのセキュリティチェック
- terraform_tfsec: Terraformセキュリティスキャナー

### セキュリティ
- detect-secrets: 秘密情報の検出

## フロントエンド向け設定

### package.jsonスクリプト
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:watch": "vitest watch",
    "test:coverage": "vitest --coverage",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "type-check": "tsc --noEmit",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  }
}
```

### フロントエンドのフォルダ構成ガイドライン

#### api/
- APIとの通信ロジックを集約
- Axiosインスタンスの設定とエラーハンドリング
- エンドポイント別にファイルを分割

#### components/
- 再利用可能なUIコンポーネント
- ビジネスロジックを含まない純粋なUI要素
- Storybookでドキュメント化

#### features/
- 機能単位でコンポーネントとロジックをまとめる
- 各機能ごとにhooks, components, utilsなどを含む
- 機能横断的な共通コンポーネントはcomponents/へ

#### hooks/
- カスタムフックを集約
- ビジネスロジックと状態管理を抽象化
- テスト可能な単位で分割

#### pages/
- ルーティングに対応するページコンポーネント
- ページ固有のレイアウトとロジック
- features/のコンポーネントを組み合わせて構成

#### store/
- Zustandでのグローバル状態管理
- 機能別にストアを分割
- 永続化が必要な場合はpersistミドルウェアを使用

### フロントエンドのベストプラクティス
- コンポーネントは関数コンポーネントで作成
- カスタムフックでロジックを分離
- ErrorBoundaryでエラーハンドリング
- Suspenseでローディング状態を管理
- コードスプリッティングでバンドルサイズ最適化
- アクセシビリティを考慮したUI実装
