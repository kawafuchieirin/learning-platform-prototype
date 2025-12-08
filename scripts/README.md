# Scripts

開発・デプロイ用スクリプト

## 概要

プロジェクトの各種作業を自動化するスクリプト群

## スクリプト一覧

- `init_local_db.py` - DynamoDB Local初期化
- `deploy.sh` - 本番環境デプロイスクリプト
- `deploy-backend.sh` - バックエンドのみデプロイ  
- `deploy-frontend.sh` - フロントエンドのみデプロイ

## 使用方法

```bash
# DynamoDB Local初期化
python scripts/init_local_db.py

# 本番環境フルデプロイ
./scripts/deploy.sh

# バックエンドのみデプロイ
./scripts/deploy-backend.sh

# フロントエンドのみデプロイ  
./scripts/deploy-frontend.sh
```

## 前提条件

- AWS CLI設定済み
- Terraform インストール済み
- Poetry インストール済み
- pnpm インストール済み