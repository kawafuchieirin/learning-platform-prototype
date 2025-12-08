# Shared

全機能で共有するコードとリソース

## 構成

- `libs/` - 共通ライブラリ
- `terraform/` - 共通Terraformモジュール  
- `docker/` - 共通Docker設定

## 共通ライブラリ

- DynamoDB接続・操作
- 認証・認可
- エラーハンドリング
- バリデーション
- ユーティリティ関数

## Terraform モジュール

- DynamoDB テーブル定義
- IAM ロール・ポリシー
- VPC・セキュリティグループ
- CloudWatch ログ設定

## Docker設定

- 開発環境用の共通設定
- DynamoDB Local
- 環境変数管理