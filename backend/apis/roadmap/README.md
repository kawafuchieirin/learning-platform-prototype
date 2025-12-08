# ロードマップAPI

学習計画の作成・管理・CSVインポート機能を提供するAPIサービスです。

## 概要

このAPIは学習プラットフォームのロードマップ機能を担当し、以下の機能を提供します：

- **ロードマップのCRUD操作** - 作成、読み取り、更新、削除
- **CSVインポート/エクスポート** - 学習計画のCSV形式での管理
- **進捗追跡** - 学習時間と達成率の自動計算
- **一覧表示とフィルタリング** - ステータス別の表示

## API仕様

### エンドポイント一覧

| Method | Endpoint | 説明 |
|--------|----------|------|
| `GET` | `/roadmap` | ロードマップ一覧取得 |
| `POST` | `/roadmap` | ロードマップ作成 |
| `GET` | `/roadmap/{id}` | ロードマップ詳細取得 |
| `PUT` | `/roadmap/{id}` | ロードマップ更新 |
| `DELETE` | `/roadmap/{id}` | ロードマップ削除（論理削除） |
| `POST` | `/roadmap/import` | CSVインポート |
| `GET` | `/roadmap/template` | CSVテンプレートダウンロード |

### 認証

- **認証方式**: AWS Cognito User Pools
- **必要権限**: 認証済みユーザー（CSVテンプレートダウンロードのみ認証不要）

### データ形式

#### ロードマップオブジェクト

```json
{
  "roadmap_id": "uuid",
  "title": "学習ロードマップのタイトル",
  "description": "説明（オプション）",
  "items": [
    {
      "title": "学習項目のタイトル",
      "estimated_hours": 20.0,
      "completed_hours": 5.0,
      "progress": 25.0
    }
  ],
  "total_hours": 35.0,
  "completed_hours": 10.0,
  "progress": 28.6,
  "status": "active",
  "created_at": "2023-12-01T00:00:00Z",
  "updated_at": "2023-12-01T00:00:00Z"
}
```

#### CSVフォーマット

```csv
タイトル,予定時間,完了時間
React基礎学習,20,5
API開発,15,0
テスト作成,10,0
```

## ディレクトリ構造

```
backend/apis/roadmap/
├── lambda/                    # Lambda関数コード
│   ├── main.py               # メインハンドラー
│   ├── app.py                # ローカル開発用FastAPIアプリ
│   └── requirements.txt      # Python依存関係
├── terraform/                # インフラ定義
│   ├── main.tf              # メインのTerraform設定
│   ├── variables.tf         # 変数定義
│   └── outputs.tf           # 出力値定義
├── docker/                   # ローカル開発環境
│   ├── Dockerfile           # Docker設定
│   └── docker-compose.yml   # Docker Compose設定
├── tests/                    # テストコード
│   ├── unit/                # ユニットテスト
│   ├── integration/         # 統合テスト
│   ├── conftest.py          # pytest設定
│   ├── pytest.ini          # pytest設定
│   └── requirements.txt     # テスト依存関係
└── README.md                # このファイル
```

## ローカル開発環境のセットアップ

### 前提条件

- Docker & Docker Compose
- Python 3.13
- Poetry（オプション）

### 開発環境の起動

1. **Dockerネットワークの作成（初回のみ）**
   ```bash
   docker network create learning-platform
   ```

2. **Docker環境の起動**
   ```bash
   cd backend/apis/roadmap/docker
   docker-compose up -d
   ```

3. **APIの確認**
   ```bash
   curl http://localhost:8003/health
   ```

### ローカルでのPython実行（オプション）

```bash
# 仮想環境の作成と依存関係のインストール
cd backend/apis/roadmap/lambda
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install fastapi uvicorn mangum

# 開発サーバーの起動
python app.py
```

## テストの実行

### ユニットテストの実行

```bash
cd backend/apis/roadmap/tests
pip install -r requirements.txt

# 全テストの実行
pytest

# カバレッジレポートの生成
pytest --cov=. --cov-report=html

# 特定のテストのみ実行
pytest -m unit
pytest tests/unit/test_main.py::TestCreateRoadmap::test_create_roadmap_success
```

### 統合テストの実行

```bash
# Docker環境が起動している状態で実行
pytest -m integration

# または個別に実行
pytest tests/integration/test_api_integration.py
```

## API使用例

### 1. ロードマップの作成

```bash
curl -X POST http://localhost:8003/roadmap \
  -H "Content-Type: application/json" \
  -d '{
    "title": "React学習ロードマップ",
    "description": "React基礎から応用まで",
    "items": [
      {
        "title": "React基礎",
        "estimated_hours": 20.0,
        "completed_hours": 0.0
      },
      {
        "title": "Hooks学習",
        "estimated_hours": 15.0,
        "completed_hours": 0.0
      }
    ]
  }'
```

### 2. ロードマップ一覧の取得

```bash
# 基本的な一覧取得
curl http://localhost:8003/roadmap

# クエリパラメータを使用
curl "http://localhost:8003/roadmap?limit=10&status=active"
```

### 3. ロードマップの更新

```bash
curl -X PUT http://localhost:8003/roadmap/{roadmap_id} \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新されたタイトル",
    "items": [
      {
        "title": "React基礎",
        "estimated_hours": 20.0,
        "completed_hours": 10.0
      }
    ]
  }'
```

### 4. CSVインポート

```bash
curl -X POST http://localhost:8003/roadmap/import \
  -H "Content-Type: application/json" \
  -d '{
    "title": "CSVからインポート",
    "csv_content": "React基礎,20,5\nAPI開発,15,0"
  }'
```

### 5. CSVテンプレートのダウンロード

```bash
curl http://localhost:8003/roadmap/template -o template.csv
```

## データベース設計

### DynamoDBテーブル構造

**プライマリキー構成:**
- `PK`: `USER#{user_id}`
- `SK`: `ROADMAP#{roadmap_id}`

**GSI1（時系列ソート用）:**
- `GSI1PK`: `USER#{user_id}`
- `GSI1SK`: `ROADMAP#{timestamp}`

**主要な属性:**
- `roadmap_id`: ロードマップの一意ID
- `title`: ロードマップのタイトル
- `description`: 説明
- `items`: 学習項目の配列
- `total_hours`: 総予定時間
- `completed_hours`: 総完了時間
- `progress`: 全体の進捗率
- `status`: ステータス（active/deleted）
- `created_at`: 作成日時
- `updated_at`: 更新日時

## エラーハンドリング

### HTTPステータスコード

- `200 OK`: 正常処理
- `400 Bad Request`: リクエストデータが不正
- `401 Unauthorized`: 認証が必要
- `404 Not Found`: リソースが見つからない
- `405 Method Not Allowed`: サポートされていないHTTPメソッド
- `500 Internal Server Error`: サーバー内部エラー

### エラーレスポンス形式

```json
{
  "error": "エラーメッセージ"
}
```

## パフォーマンス考慮事項

### Lambda関数の最適化

- **コールドスタート対策**: 最小限の依存関係
- **メモリ使用量**: 256MB設定
- **タイムアウト**: 30秒設定
- **同時実行制御**: デフォルト設定を使用

### DynamoDBクエリの最適化

- **効率的なクエリパターン**: PKとSKによる直接アクセス
- **GSI活用**: 時系列ソートでの一覧取得
- **バッチ処理**: 複数アイテムの一括処理は避け、個別処理を推奨

## セキュリティ

### 認証・認可

- **Cognito User Pools**: JWT トークンベースの認証
- **ユーザー分離**: ユーザーIDによるデータ分離
- **CORS設定**: フロントエンドからのアクセス制御

### データ保護

- **機密情報**: 学習データは個人情報として適切に管理
- **アクセスログ**: CloudWatch Logsによる監査ログ
- **暗号化**: DynamoDB暗号化（保存時・転送時）

## 運用・監視

### CloudWatch Logs

- **Lambda関数ログ**: `/aws/lambda/roadmap-api`
- **API Gatewayログ**: `/aws/apigateway/roadmap-api`
- **ログ保持期間**: 14日

### メトリクス監視

- **Lambda実行時間**: 平均・最大実行時間
- **エラー率**: 4xx/5xxエラーの発生率
- **DynamoDB使用率**: 読み取り・書き込み容量の使用状況

## デプロイメント

### Terraform によるインフラ管理

```bash
cd backend/apis/roadmap/terraform
terraform init
terraform plan
terraform apply
```

### Lambda関数のデプロイ

```bash
# ZIPファイルの作成
cd backend/apis/roadmap/lambda
zip -r roadmap-lambda.zip . -x "*.pyc" "__pycache__/*" "tests/*"

# AWS CLIによる更新
aws lambda update-function-code \
  --function-name roadmap-api \
  --zip-file fileb://roadmap-lambda.zip
```

## トラブルシューティング

### よくある問題

1. **DynamoDB接続エラー**
   - 環境変数 `DYNAMODB_ENDPOINT` の確認
   - IAM権限の確認

2. **認証エラー**
   - JWT トークンの有効期限確認
   - Cognito User Pool設定の確認

3. **CORS エラー**
   - API Gatewayの CORS設定確認
   - フロントエンドのオリジン設定確認

### ログ確認方法

```bash
# Docker環境のログ
docker-compose logs -f roadmap-api

# AWS環境のログ
aws logs tail /aws/lambda/roadmap-api --follow
```

## 今後の拡張予定

- **バージョン管理**: ロードマップの変更履歴管理
- **テンプレート機能**: 再利用可能なロードマップテンプレート
- **共有機能**: ロードマップの他ユーザーとの共有
- **統計機能**: 学習パターンの分析・レポート

## 開発ガイドライン

### コーディング規約

- **PEP 8**: Python標準のコーディング規約に準拠
- **型ヒント**: すべての関数に型ヒントを追加
- **ドキュメント**: 関数・クラスにはdocstringを記述

### コミット規約

- **コンベンショナルコミット**: `feat:`, `fix:`, `docs:` などのプレフィックスを使用
- **日本語**: コミットメッセージは日本語で記述
- **単一責任**: 1つのコミットは1つの機能・修正に限定

### テスト規約

- **カバレッジ**: 80%以上のテストカバレッジを維持
- **テスト分離**: テスト間の依存関係を排除
- **モック使用**: 外部サービスは適切にモック化