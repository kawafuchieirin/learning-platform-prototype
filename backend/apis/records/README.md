# 学習記録API (Records API)

学習記録の作成・管理機能を提供するAPIサービスです。ユーザーの学習活動を記録し、テンプレート機能やロードマップとの連携を通して効率的な学習管理を実現します。

## 概要

### 主要機能
1. **学習記録のCRUD操作** - 作成、取得、更新、削除
2. **テンプレート機能** - 定型的な記録作成の効率化
3. **ロードマップ連携** - 学習計画との進捗同期
4. **フィルタリング機能** - 日付、ロードマップ、タグによる絞り込み
5. **統計機能** - 学習時間の集計と分析

### 技術仕様
- **言語**: Python 3.13
- **フレームワーク**: AWS Lambda (本番) / FastAPI (ローカル開発)
- **データベース**: DynamoDB
- **認証**: AWS Cognito User Pool
- **インフラ**: Terraform

## ディレクトリ構造

```
records/
├── lambda/
│   ├── main.py                   # メインLambda関数
│   ├── app.py                    # ローカル開発用FastAPIアプリ
│   └── requirements.txt          # Python依存関係
├── terraform/
│   ├── main.tf                   # インフラ定義
│   ├── variables.tf              # 変数定義
│   └── outputs.tf                # アウトプット定義
├── docker/
│   ├── docker-compose.yml        # ローカル環境構成
│   └── Dockerfile                # コンテナ定義
├── tests/
│   ├── unit/
│   │   └── test_main.py          # ユニットテスト
│   └── integration/
│       └── test_api_integration.py # 統合テスト
└── README.md                     # このファイル
```

## API仕様

### ベースURL
- **本番環境**: `https://api.learning-platform.example.com/api/v1`
- **ローカル環境**: `http://localhost:8009`

### エンドポイント一覧

#### 学習記録管理

##### POST /records
学習記録を作成します。

```json
// リクエスト
{
  "title": "React Hooks学習",
  "content": "useStateとuseEffectについて学習しました",
  "duration_minutes": 120,
  "study_date": "2023-12-08",
  "tags": ["react", "javascript"],
  "difficulty": "medium",
  "satisfaction": 4,
  "notes": "実際にコードを書いて理解できました",
  "roadmap_id": "react-roadmap-001",
  "roadmap_item_title": "React基礎"
}

// レスポンス (200 OK)
{
  "record_id": "01HGZ8Y9X2K3M4N5P6Q7R8S9T0",
  "title": "React Hooks学習",
  "content": "useStateとuseEffectについて学習しました",
  "duration_minutes": 120,
  "study_date": "2023-12-08",
  "tags": ["react", "javascript"],
  "difficulty": "medium",
  "satisfaction": 4,
  "notes": "実際にコードを書いて理解できました",
  "roadmap_id": "react-roadmap-001",
  "roadmap_item_title": "React基礎",
  "status": "active",
  "created_at": "2023-12-08T10:30:00Z",
  "updated_at": "2023-12-08T10:30:00Z"
}
```

##### GET /records
学習記録の一覧を取得します。

**クエリパラメータ**:
- `limit` (number): 取得件数制限 (デフォルト: 50)
- `date_from` (string): 開始日 (YYYY-MM-DD)
- `date_to` (string): 終了日 (YYYY-MM-DD)
- `roadmap_id` (string): ロードマップID
- `tags` (string): タグ (カンマ区切り)

```json
// レスポンス (200 OK)
{
  "records": [
    {
      "record_id": "01HGZ8Y9X2K3M4N5P6Q7R8S9T0",
      "title": "React Hooks学習",
      "duration_minutes": 120,
      "study_date": "2023-12-08",
      "tags": ["react", "javascript"],
      "difficulty": "medium",
      "satisfaction": 4,
      "status": "active",
      "created_at": "2023-12-08T10:30:00Z"
    }
  ],
  "statistics": {
    "total_duration_minutes": 1200,
    "total_duration_hours": 20.0,
    "average_duration_minutes": 85.7,
    "total_records": 14
  },
  "pagination": {
    "limit": 50,
    "has_more": false
  }
}
```

##### GET /records/{recordId}
学習記録の詳細を取得します。

```json
// レスポンス (200 OK)
{
  "record_id": "01HGZ8Y9X2K3M4N5P6Q7R8S9T0",
  "title": "React Hooks学習",
  "content": "useStateとuseEffectについて学習しました",
  "duration_minutes": 120,
  "study_date": "2023-12-08",
  "tags": ["react", "javascript"],
  "difficulty": "medium",
  "satisfaction": 4,
  "notes": "実際にコードを書いて理解できました",
  "roadmap_id": "react-roadmap-001",
  "roadmap_item_title": "React基礎",
  "status": "active",
  "created_at": "2023-12-08T10:30:00Z",
  "updated_at": "2023-12-08T10:30:00Z"
}
```

##### PUT /records/{recordId}
学習記録を更新します。

```json
// リクエスト
{
  "title": "React Hooks詳細学習",
  "content": "useStateとuseEffect、さらにuseContextについても学習しました",
  "duration_minutes": 180,
  "satisfaction": 5
}

// レスポンス (200 OK)
// 更新された記録の全データ
```

##### DELETE /records/{recordId}
学習記録を削除します。

```json
// レスポンス (200 OK)
{
  "message": "学習記録が正常に削除されました",
  "record_id": "01HGZ8Y9X2K3M4N5P6Q7R8S9T0"
}
```

#### テンプレート機能

##### GET /records/templates
利用可能な記録テンプレート一覧を取得します。

```json
// レスポンス (200 OK)
{
  "templates": [
    {
      "template_type": "reading",
      "title": "読書記録テンプレート",
      "description": "書籍や記事の読書記録用",
      "default_difficulty": "easy",
      "default_tags": ["reading"],
      "sample_content": "書籍名: \n著者: \n感想: \n学んだこと: "
    },
    {
      "template_type": "coding",
      "title": "コーディング記録テンプレート",
      "description": "プログラミング学習記録用",
      "default_difficulty": "medium",
      "default_tags": ["coding"],
      "sample_content": "言語/技術: \n作成したもの: \n学んだこと: \n課題: "
    },
    {
      "template_type": "video",
      "title": "動画学習記録テンプレート",
      "description": "動画教材の学習記録用",
      "default_difficulty": "easy",
      "default_tags": ["video"],
      "sample_content": "動画タイトル: \n概要: \n重要なポイント: \nメモ: "
    },
    {
      "template_type": "roadmap",
      "title": "ロードマップ記録テンプレート",
      "description": "ロードマップに基づく学習記録用",
      "roadmap_items": [
        {
          "roadmap_id": "react-roadmap-001",
          "roadmap_title": "React学習ロードマップ",
          "item_title": "React基礎",
          "estimated_hours": 20,
          "completed_hours": 5,
          "progress": 25
        }
      ]
    }
  ]
}
```

##### POST /records/from-template
テンプレートから学習記録を作成します。

```json
// リクエスト
{
  "template_type": "reading",
  "title": "JavaScript入門書の読書",
  "duration_minutes": 90,
  "satisfaction": 5,
  "notes": "基礎がよく理解できました"
}

// レスポンス (200 OK)
// テンプレートが適用された記録データ
{
  "record_id": "01HGZ9A1B2C3D4E5F6G7H8I9J0",
  "title": "JavaScript入門書の読書",
  "content": "書籍名: \n著者: \n感想: \n学んだこと: ",
  "duration_minutes": 90,
  "tags": ["reading"],
  "difficulty": "easy",
  "satisfaction": 5,
  "notes": "基礎がよく理解できました",
  "status": "active",
  "created_at": "2023-12-08T11:00:00Z",
  "updated_at": "2023-12-08T11:00:00Z"
}
```

## ローカル開発環境

### 前提条件
- Docker & Docker Compose
- Python 3.13
- Poetry (オプション、Python直接実行時)

### 環境構築手順

1. **Dockerネットワークの作成**
```bash
docker network create learning-platform
```

2. **環境変数の設定**
```bash
# .env.example をコピーして .env を作成
cp .env.example .env

# 必要に応じて設定を調整
vim .env
```

3. **Docker環境の起動**
```bash
# records API ディレクトリへ移動
cd backend/apis/records

# Docker Compose でサービス起動
docker-compose up -d

# ログの確認
docker-compose logs -f records-api
```

4. **動作確認**
```bash
# ヘルスチェック
curl http://localhost:8009/health

# テンプレート一覧取得
curl http://localhost:8009/records/templates
```

### 開発用コマンド

```bash
# コンテナ内でのコマンド実行
docker-compose exec records-api bash

# ログの監視
docker-compose logs -f records-api

# 環境の停止
docker-compose down

# 環境の再構築
docker-compose down && docker-compose up -d --build
```

## テスト

### ユニットテスト
```bash
# コンテナ内でテスト実行
docker-compose exec records-api python -m pytest tests/unit/ -v

# カバレッジレポート付き
docker-compose exec records-api python -m pytest tests/unit/ --cov=. --cov-report=html
```

### 統合テスト
```bash
# API サーバーが起動していることを確認
docker-compose ps

# 統合テスト実行
cd tests/integration
python -m pytest test_api_integration.py -v -s

# 特定のテストクラスのみ実行
python -m pytest test_api_integration.py::TestRecordsAPIIntegration::test_record_crud_flow -v -s
```

### テストデータのクリーンアップ
```bash
# DynamoDB Local のデータをクリア（再起動）
docker-compose restart dynamodb-local
```

## デプロイ

### Terraform による本番環境デプロイ

1. **AWS 認証情報の設定**
```bash
aws configure
# または
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

2. **Terraform の初期化と実行**
```bash
cd terraform/

# 初期化
terraform init

# プランの確認
terraform plan

# デプロイ実行
terraform apply
```

3. **Lambda 関数の更新**
```bash
# Lambda 関数のコードを更新
zip -r records-api.zip lambda/

# AWS CLI で関数を更新
aws lambda update-function-code \
  --function-name learning-platform-records-api \
  --zip-file fileb://records-api.zip
```

### CI/CD パイプライン
GitHub Actions を使用した自動デプロイの設定例は、プロジェクトルートの `.github/workflows/` を参照してください。

## ロードマップ連携

学習記録作成時に `roadmap_id` と `roadmap_item_title` を指定すると、対応するロードマップアイテムの進捗が自動更新されます。

### 進捗更新ロジック
1. 学習記録の `duration_minutes` を時間単位に変換
2. ロードマップAPIを呼び出して進捗を更新
3. 学習記録にロードマップ情報を紐づけて保存

### 連携エラー処理
- ロードマップAPIが利用できない場合も記録作成は正常に完了
- エラーログを出力して後で手動同期可能

## パフォーマンス考慮事項

### DynamoDB 最適化
- 適切なキー設計による効率的なクエリ
- GSI（Global Secondary Index）を活用した日付範囲検索
- 一括操作時のスループット制限への配慮

### Lambda 関数最適化
- コールドスタート対策
- 接続プールの活用
- 適切なメモリ設定（推奨: 256MB）

## モニタリング

### CloudWatch メトリクス
- Lambda 実行時間
- エラー率
- DynamoDB read/write 使用量
- API Gateway リクエスト数

### ログ出力
- 構造化ログ（JSON形式）
- 適切なログレベル設定
- 機密情報の除外

## トラブルシューティング

### よくある問題

#### 1. DynamoDB 接続エラー
```
Error: Unable to locate credentials
```

**解決策**:
```bash
# AWS 認証情報を確認
aws sts get-caller-identity

# 環境変数を設定
export AWS_DEFAULT_REGION=us-east-1
```

#### 2. ロードマップAPI連携エラー
```
Error: Failed to update roadmap progress
```

**解決策**:
- ロードマップAPIの動作確認
- ネットワーク接続の確認
- IAM権限の確認

#### 3. テンプレート作成エラー
```
Error: Invalid template type
```

**解決策**:
- 有効なテンプレートタイプ: `roadmap`, `reading`, `coding`, `video`
- リクエストボディの形式を確認

### デバッグ方法

#### 1. ローカル環境でのデバッグ
```bash
# デバッグモードでAPI起動
docker-compose exec records-api python app.py

# ログレベルをDEBUGに設定
export LOG_LEVEL=DEBUG
```

#### 2. CloudWatch Logs での確認
```bash
# AWS CLI でログを確認
aws logs tail /aws/lambda/learning-platform-records-api --follow
```

## セキュリティ考慮事項

### 認証・認可
- AWS Cognito による認証
- リクエスト毎のユーザー検証
- 適切な CORS 設定

### データ保護
- 入力値のサニタイゼーション
- SQLインジェクション対策
- 機密情報のログ出力防止

### IAM 権限
最小権限の原則に基づく権限設定:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/LearningPlatform*"
    }
  ]
}
```

## 今後の拡張予定

### 機能拡張
- [ ] 学習記録の画像添付機能
- [ ] AI による学習内容の自動分析
- [ ] 学習記録の公開・共有機能
- [ ] 学習記録のエクスポート機能

### 技術的改善
- [ ] GraphQL API の導入
- [ ] リアルタイム通知機能
- [ ] オフライン対応
- [ ] パフォーマンス最適化

## 参考資料

- [AWS Lambda Python ドキュメント](https://docs.aws.amazon.com/lambda/latest/dg/python-programming-model.html)
- [DynamoDB ベストプラクティス](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)
- [プロジェクト全体の README](../../README.md)

## 問い合わせ・サポート

技術的な質問や問題については、プロジェクトの GitHub Issues までお問い合わせください。