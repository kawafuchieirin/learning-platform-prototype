# Analytics Terraform Infrastructure

Analytics ServiceのAWSインフラストラクチャをTerraformで管理

## 概要

このTerraform設定は、Analytics ServiceをAWS上にデプロイするためのインフラリソースを定義しています。Lambda関数、IAMロール、CloudWatch監視、API Gateway統合などを含みます。

## アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│   Lambda        │───▶│   DynamoDB      │
│                 │    │   Analytics     │    │   Tables        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CloudWatch    │    │   IAM Roles     │    │   VPC (option)  │
│   Logs/Metrics  │    │   Policies      │    │   Security      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## リソース構成

### Lambda Function
- **関数名**: `{service_name}-analytics`
- **ランタイム**: Python 3.11
- **メモリ**: 256MB（設定可能）
- **タイムアウト**: 30秒（設定可能）

### IAM Roles & Policies
- **実行ロール**: Lambda基本実行権限
- **DynamoDBアクセス**: 必要テーブルへの読み取り権限
- **CloudWatchLogs**: ログ出力権限

### CloudWatch Monitoring
- **ログ保持**: 14日間（設定可能）
- **メトリクス**: エラー率・実行時間のアラーム
- **ダッシュボード**: Lambda パフォーマンス監視

## ファイル構成

```
terraform/
├── main.tf                 # メインのリソース定義
├── variables.tf            # 変数定義
├── outputs.tf             # 出力値定義
├── terraform.tfvars.example  # 変数値のサンプル
└── README.md              # このファイル
```

## セットアップ

### 前提条件

```bash
# Terraformインストール確認
terraform --version
# Terraform v1.0.0 以上が必要

# AWS CLI設定確認
aws configure list

# 必要な権限:
# - Lambda (作成・更新・削除)
# - IAM (ロール・ポリシー作成)
# - CloudWatch (ログ・メトリクス)
# - DynamoDB (テーブルアクセス)
```

### 初期化

```bash
# Terraformワークスペースの初期化
terraform init

# プロバイダーのダウンロード確認
terraform providers
```

### 変数設定

```bash
# 変数ファイルの作成
cp terraform.tfvars.example terraform.tfvars

# 必要な値を設定
vim terraform.tfvars
```

**terraform.tfvars 設定例:**
```hcl
# 基本設定
service_name = "learning-platform"
environment  = "prod"
aws_region   = "ap-northeast-1"

# DynamoDB テーブル設定（既存テーブルのARN）
users_table_arn   = "arn:aws:dynamodb:ap-northeast-1:123456789012:table/Users"
timer_table_arn   = "arn:aws:dynamodb:ap-northeast-1:123456789012:table/Timer"
records_table_arn = "arn:aws:dynamodb:ap-northeast-1:123456789012:table/Records"
roadmap_table_arn = "arn:aws:dynamodb:ap-northeast-1:123456789012:table/Roadmap"

# セキュリティ設定
jwt_secret_key = "your-production-secret-key"

# API Gateway設定
create_api_gateway = true
api_gateway_execution_arn = "arn:aws:execute-api:ap-northeast-1:123456789012:abc123/*"

# 監視設定
alarm_topic_arn = "arn:aws:sns:ap-northeast-1:123456789012:alerts"
```

## デプロイ

### 計画確認

```bash
# 実行計画の確認
terraform plan

# 特定リソースのみ計画確認
terraform plan -target=aws_lambda_function.analytics_lambda
```

### リソース作成

```bash
# 全リソースの作成
terraform apply

# 確認プロンプト時に 'yes' を入力
# または自動承認
terraform apply -auto-approve
```

### 段階的デプロイ

```bash
# IAMリソースのみ先に作成
terraform apply -target=aws_iam_role.analytics_lambda_role

# Lambda関数の作成
terraform apply -target=aws_lambda_function.analytics_lambda

# 監視設定の追加
terraform apply -target=aws_cloudwatch_metric_alarm.analytics_error_rate
```

## 設定可能変数

### 基本設定

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `service_name` | サービス名 | `learning-platform` | No |
| `environment` | 環境名 | `dev` | No |
| `aws_region` | AWSリージョン | `ap-northeast-1` | No |

### DynamoDB設定

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `users_table_arn` | ユーザーテーブルARN | - | **Yes** |
| `timer_table_arn` | タイマーテーブルARN | - | **Yes** |
| `records_table_arn` | 学習記録テーブルARN | - | **Yes** |
| `roadmap_table_arn` | ロードマップテーブルARN | - | **Yes** |

### Lambda設定

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `lambda_timeout` | タイムアウト（秒） | `30` | No |
| `lambda_memory_size` | メモリサイズ（MB） | `256` | No |
| `lambda_runtime` | ランタイム | `python3.11` | No |

### セキュリティ設定

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `jwt_secret_key` | JWT署名用秘密鍵 | - | **Yes** |

### 監視設定

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `log_retention_days` | ログ保持期間（日） | `14` | No |
| `alarm_topic_arn` | SNS通知先ARN | `""` | No |

## 出力値

デプロイ後に以下の出力値が利用可能：

```bash
# 出力値の確認
terraform output

# 特定の出力値のみ表示
terraform output lambda_function_arn
```

### 出力項目

| 出力名 | 説明 | 使用用途 |
|--------|------|----------|
| `lambda_function_name` | Lambda関数名 | CLI操作・モニタリング |
| `lambda_function_arn` | Lambda関数ARN | 他サービスとの連携 |
| `lambda_invoke_arn` | Lambda呼び出しARN | API Gateway設定 |
| `lambda_function_url` | 関数URL（dev環境のみ） | 開発テスト |
| `cloudwatch_log_group_name` | ログ群名 | ログ確認 |

## 環境管理

### 複数環境での運用

```bash
# 開発環境用ワークスペース
terraform workspace new dev
terraform workspace select dev

# 本番環境用ワークスペース
terraform workspace new prod
terraform workspace select prod

# 現在のワークスペース確認
terraform workspace show
```

### 環境固有の変数ファイル

```bash
# 環境別変数ファイル
terraform.tfvars.dev
terraform.tfvars.prod

# 環境指定でのデプロイ
terraform apply -var-file="terraform.tfvars.dev"
terraform apply -var-file="terraform.tfvars.prod"
```

## モニタリングと運用

### CloudWatch ダッシュボード

```bash
# ダッシュボード用の JSON設定出力
terraform output lambda_function_name | \
aws cloudwatch put-dashboard \
  --dashboard-name "analytics-dashboard" \
  --dashboard-body file://dashboard.json
```

### アラート設定

デフォルトで以下のアラートが設定されます：

1. **エラー率アラート**
   - 閾値: 5エラー/5分
   - 評価期間: 2回連続

2. **実行時間アラート**
   - 閾値: 25秒平均
   - 評価期間: 2回連続

### ログ確認

```bash
# CloudWatch ログの確認
aws logs tail $(terraform output -raw cloudwatch_log_group_name) --follow

# エラーログの抽出
aws logs filter-events \
  --log-group-name $(terraform output -raw cloudwatch_log_group_name) \
  --filter-pattern "ERROR"
```

## セキュリティ

### IAM 最小権限の原則

```hcl
# 必要最小限のDynamoDB権限
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:Query",
    "dynamodb:GetItem",
    "dynamodb:BatchGetItem"
  ],
  "Resource": [
    "arn:aws:dynamodb:region:account:table/Timer",
    "arn:aws:dynamodb:region:account:table/Timer/index/*"
  ]
}
```

### 機密情報管理

```bash
# AWS Systems Manager Parameter Store使用例
aws ssm put-parameter \
  --name "/learning-platform/analytics/jwt-secret" \
  --value "your-secret-key" \
  --type "SecureString"

# Terraformでの参照
data "aws_ssm_parameter" "jwt_secret" {
  name = "/learning-platform/analytics/jwt-secret"
}
```

## トラブルシューティング

### よくある問題

**1. DynamoDB アクセス拒否**
```bash
# IAMポリシーの確認
aws iam get-role-policy \
  --role-name $(terraform output -raw lambda_role_name) \
  --policy-name dynamodb-policy

# テーブルARNの確認
aws dynamodb describe-table --table-name Timer
```

**2. Lambda デプロイエラー**
```bash
# ZIPファイルサイズ確認
ls -lh analytics_lambda.zip

# Lambda関数の詳細確認
aws lambda get-function \
  --function-name $(terraform output -raw lambda_function_name)
```

**3. CloudWatch ログが出力されない**
```bash
# ログ群の存在確認
aws logs describe-log-groups \
  --log-group-name-prefix "/aws/lambda/"

# Lambda実行ロールの権限確認
aws iam simulate-principal-policy \
  --policy-source-arn $(terraform output -raw lambda_role_arn) \
  --action-names logs:CreateLogStream
```

### 状態ファイルの問題

```bash
# 状態ファイルの修復
terraform refresh

# リソースのインポート（既存リソースを管理対象に）
terraform import aws_lambda_function.analytics_lambda function-name

# 状態ファイルのバックアップ
cp terraform.tfstate terraform.tfstate.backup
```

## バックアップと復旧

### 状態管理

```bash
# リモートバックエンドの設定（推奨）
terraform {
  backend "s3" {
    bucket = "learning-platform-terraform-state"
    key    = "analytics/terraform.tfstate"
    region = "ap-northeast-1"
  }
}
```

### 災害復旧

```bash
# 設定ファイルから環境の復元
terraform apply

# 特定リソースの再作成
terraform taint aws_lambda_function.analytics_lambda
terraform apply
```

## アップデート

### Lambda 関数コードの更新

```bash
# コード変更後の再デプロイ
terraform apply

# 強制的な再作成
terraform taint aws_lambda_function.analytics_lambda
terraform apply
```

### Terraform 設定の更新

```bash
# 設定変更の計画確認
terraform plan

# 段階的な適用
terraform apply -target=specific_resource
```

## Clean Up

```bash
# 全リソースの削除
terraform destroy

# 特定リソースのみ削除
terraform destroy -target=aws_lambda_function.analytics_lambda

# 確認プロンプトをスキップ
terraform destroy -auto-approve
```

## ベストプラクティス

### 設定管理
1. 変数ファイルでの設定値管理
2. 環境別設定の分離
3. 機密情報のParameter Store使用

### バージョン管理
1. Terraformバージョンの固定
2. プロバイダーバージョンの固定
3. 状態ファイルのリモート保存

### セキュリティ
1. 最小権限の原則
2. タグによるリソース管理
3. コスト監視の設定

---

このTerraform設定により、Analytics ServiceのAWSインフラを自動化・標準化し、継続的で信頼性の高いデプロイを実現します。