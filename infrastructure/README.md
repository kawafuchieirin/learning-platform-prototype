# Infrastructure

Terraformによるインフラストラクチャ定義

## 概要

AWS上でのサーバーレスアーキテクチャ構築

## 構成

- `modules/` - Terraformモジュール
- `environments/prod/` - 本番環境設定

## Terraformモジュール

- `lambda/` - Lambda関数
- `api_gateway/` - API Gateway
- `dynamodb/` - DynamoDB テーブル
- `s3_cloudfront/` - S3 + CloudFront (フロントエンド用)
- `iam/` - IAM ロール・ポリシー

## 環境

- **prod** - 本番環境のみ（開発環境はローカルDocker）

## デプロイ

```bash
# 本番環境へのデプロイ
cd infrastructure/environments/prod
terraform init
terraform plan
terraform apply
```

## 必要な権限

- Lambda作成・更新
- API Gateway設定
- DynamoDB操作
- S3バケット作成・管理
- CloudFront配信設定
- IAM ロール・ポリシー管理