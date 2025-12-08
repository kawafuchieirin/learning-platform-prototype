# Analytics Docker Environment

Analytics Serviceのローカル開発環境をDockerで構築

## 概要

このDockerセットアップにより、Analytics ServiceをLambda環境に近い形でローカル実行できます。DynamoDB Local、API、管理ツールがセットで起動し、完全な開発環境を提供します。

## アーキテクチャ

```
┌─────────────────────┐    ┌─────────────────────┐
│   Frontend          │    │   Analytics API     │
│   (port: 5173)      │───▶│   (port: 8003)      │
└─────────────────────┘    └─────────────────────┘
                                       │
                              ┌────────┴────────┐
                              ▼                 ▼
                   ┌─────────────────┐ ┌─────────────────┐
                   │ DynamoDB Local  │ │ DynamoDB Admin  │
                   │ (port: 8004)    │ │ (port: 8005)    │
                   └─────────────────┘ └─────────────────┘
```

## サービス構成

### analytics-api
- **ポート**: 8003
- **説明**: FastAPI + Analytics Lambda Function
- **ヘルスチェック**: `http://localhost:8003/health`
- **API ドキュメント**: `http://localhost:8003/docs`

### dynamodb-local
- **ポート**: 8004
- **説明**: DynamoDB Local インスタンス
- **データ**: インメモリ（再起動で消失）

### dynamodb-admin
- **ポート**: 8005
- **説明**: DynamoDB管理UI
- **アクセス**: `http://localhost:8005`

## ファイル構成

```
docker/
├── Dockerfile              # Analytics API用Dockerイメージ
├── docker-compose.yml      # マルチサービス構成
├── Makefile               # 開発用コマンド集
├── .dockerignore          # Docker除外ファイル
└── README.md              # このファイル
```

## クイックスタート

### 1. 環境確認

```bash
# Docker & Docker Composeの確認
docker --version
docker-compose --version

# 必要なポートの空き確認
lsof -i :8003,8004,8005
```

### 2. サービス起動

```bash
# 全サービス起動
make up

# または直接実行
docker-compose up -d
```

### 3. サービス確認

```bash
# Analytics API
curl http://localhost:8003/health

# DynamoDB Local
aws dynamodb list-tables --endpoint-url http://localhost:8004

# DynamoDB Admin UI
open http://localhost:8005
```

### 4. データベース初期化

```bash
# テーブル作成（プロジェクトルートから実行）
make init-db

# または手動実行
cd ../../../scripts
poetry run python init_local_db.py
```

## 開発コマンド（Makefile）

### 基本操作
```bash
# サービス起動
make up

# サービス停止
make down

# 再起動
make restart

# ログ確認
make logs
make logs-all
```

### 開発ツール
```bash
# コード品質チェック
make lint

# テスト実行
make test

# コードフォーマット
make format

# 開発環境セットアップ
make dev-setup
```

### データベース操作
```bash
# DynamoDB初期化
make init-db

# ヘルスチェック
make health

# サービス状態確認
make status
```

### クリーンアップ
```bash
# コンテナ・ボリューム削除
make clean

# 全イメージ削除
make clean-all
```

## 環境変数

docker-compose.ymlで設定される環境変数：

| 変数名 | 値 | 説明 |
|--------|----|----- |
| `ENV` | `local` | 実行環境 |
| `DEBUG` | `true` | デバッグモード |
| `AWS_REGION` | `ap-northeast-1` | AWSリージョン |
| `DYNAMODB_ENDPOINT` | `http://dynamodb-local:8000` | DynamoDB接続先 |
| `AWS_ACCESS_KEY_ID` | `dummy` | 開発用アクセスキー |
| `AWS_SECRET_ACCESS_KEY` | `dummy` | 開発用シークレットキー |
| `USERS_TABLE` | `Users` | ユーザーテーブル名 |
| `TIMER_TABLE` | `Timer` | タイマーテーブル名 |
| `RECORDS_TABLE` | `Records` | 学習記録テーブル名 |
| `ROADMAP_TABLE` | `Roadmap` | ロードマップテーブル名 |

## API エンドポイントテスト

### ヘルスチェック
```bash
curl -X GET http://localhost:8003/health
```

### 週次レポート取得
```bash
# 今週のレポート
curl -X GET http://localhost:8003/analytics/weekly

# 特定週のレポート
curl -X GET "http://localhost:8003/analytics/weekly?week_start=2024-01-01"
```

### 生産性メトリクス
```bash
curl -X GET "http://localhost:8003/analytics/productivity?period_days=30"
```

### 月次トレンド
```bash
curl -X GET "http://localhost:8003/analytics/monthly-trends?months=6"
```

### グラフデータ
```bash
# 日別学習時間
curl -X GET "http://localhost:8003/analytics/charts/daily_duration?period_days=30"

# 科目別分布
curl -X GET "http://localhost:8003/analytics/charts/subject_distribution"

# 時間帯別分布
curl -X GET "http://localhost:8003/analytics/charts/hourly_distribution"
```

## データベース操作

### DynamoDB Local CLI操作

```bash
# テーブル一覧
aws dynamodb list-tables --endpoint-url http://localhost:8004

# テーブルスキャン
aws dynamodb scan \
  --table-name Timer \
  --endpoint-url http://localhost:8004

# アイテム作成
aws dynamodb put-item \
  --table-name Timer \
  --item '{"PK": {"S": "USER#test-user"}, "SK": {"S": "TIMER#123"}}' \
  --endpoint-url http://localhost:8004
```

### DynamoDB Admin UI

ブラウザで `http://localhost:8005` にアクセス：

- テーブル一覧表示
- データの作成・更新・削除
- クエリ・スキャン実行
- JSON形式でのデータ表示

## ログとデバッグ

### ログ確認

```bash
# Analytics APIのログ
docker-compose logs -f analytics-api

# 全サービスのログ
docker-compose logs -f

# 特定時間以降のログ
docker-compose logs --since="2024-01-01T00:00:00" analytics-api
```

### デバッグモード

```bash
# デバッグレベルでログ出力
docker-compose exec analytics-api poetry run python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# your debug code here
"
```

### コンテナ内での作業

```bash
# Analytics APIコンテナに入る
docker-compose exec analytics-api bash

# Python インタラクティブシェル
docker-compose exec analytics-api poetry run python

# 依存関係の確認
docker-compose exec analytics-api poetry show
```

## 開発ワークフロー

### 1. 機能開発

```bash
# サービス起動
make up

# コード変更（ホットリロード対応）
# lambda/src/ 配下のファイルを編集

# テスト実行
make test

# API確認
curl http://localhost:8003/analytics/weekly
```

### 2. コード品質チェック

```bash
# フォーマット
make format

# リント
make lint

# 全チェック
make dev
```

### 3. データベース操作

```bash
# 新しいテーブル追加後
make init-db

# データ確認
open http://localhost:8005
```

## パフォーマンステスト

### 負荷テスト

```bash
# Apache Benchを使用
ab -n 100 -c 10 http://localhost:8003/analytics/weekly

# curlを使用した連続リクエスト
for i in {1..10}; do
  time curl -s http://localhost:8003/analytics/productivity > /dev/null
done
```

### メモリ使用量確認

```bash
# コンテナリソース確認
docker stats analytics-api

# 詳細統計
docker-compose exec analytics-api ps aux
```

## トラブルシューティング

### よくある問題

**1. ポート競合**
```bash
# 使用中ポートの確認
lsof -i :8003

# 該当プロセスの終了
kill -9 <PID>
```

**2. DynamoDB接続エラー**
```bash
# DynamoDB Localの状態確認
docker-compose logs dynamodb-local

# 接続テスト
aws dynamodb list-tables --endpoint-url http://localhost:8004
```

**3. Analytics API起動失敗**
```bash
# 詳細ログ確認
docker-compose logs analytics-api

# コンテナ再ビルド
docker-compose build analytics-api
```

**4. 依存関係の問題**
```bash
# Poetry環境の再構築
docker-compose exec analytics-api poetry install --no-cache

# コンテナ再作成
docker-compose down
docker-compose up --build
```

### デバッグ手順

1. **ログ確認**
```bash
make logs
```

2. **ヘルスチェック**
```bash
make health
```

3. **サービス状態確認**
```bash
make status
```

4. **完全リセット**
```bash
make clean
make up
make init-db
```

## カスタマイズ

### ポート変更

docker-compose.ymlを編集：

```yaml
services:
  analytics-api:
    ports:
      - "8080:8000"  # 8003 → 8080 に変更
```

### 環境変数追加

```yaml
services:
  analytics-api:
    environment:
      - CUSTOM_SETTING=value
      - LOG_LEVEL=DEBUG
```

### ボリュームマウント

```yaml
services:
  analytics-api:
    volumes:
      - ../lambda/src:/app/src
      - ./custom-config:/app/config
```

## CI/CD統合

### GitHub Actions例

```yaml
name: Analytics API Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Start services
      run: |
        cd backend/apis/analytics/docker
        make up
        
    - name: Run tests
      run: |
        cd backend/apis/analytics/docker
        make test
        
    - name: Cleanup
      run: |
        cd backend/apis/analytics/docker
        make clean
```

## セキュリティ考慮事項

### 開発環境限定
- ダミーAWSクレデンシャル使用
- 認証機能の簡略化
- 本番データの使用禁止

### ネットワークセキュリティ
- ローカルホストからのアクセスのみ
- デフォルトポートの変更推奨
- ファイアウォール設定の確認

## 本番環境との差異

| 項目 | 開発環境 | 本番環境 |
|------|----------|----------|
| 実行環境 | Docker Container | AWS Lambda |
| データベース | DynamoDB Local | DynamoDB |
| 認証 | 簡略化 | JWT + Cognito |
| ログ | stdout | CloudWatch Logs |
| 監視 | 手動確認 | CloudWatch Metrics |
| スケーリング | 固定 | オートスケーリング |

---

このDocker環境により、本番に近い環境でAnalytics Serviceの開発・テストを効率的に行えます。問題が発生した場合は、ログ確認とサービス再起動により解決できることがほとんどです。