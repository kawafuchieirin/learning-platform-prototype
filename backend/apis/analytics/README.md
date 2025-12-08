# Analytics Service

学習プラットフォームの学習データ分析マイクロサービス

## 概要

Analytics Serviceは学習データの分析・可視化を担当するマイクロサービスです。学習時間、継続性、生産性などの様々な観点から学習活動を分析し、ユーザーにとって価値のあるインサイトを提供します。

## 主要機能

### 📊 分析機能
- **週次レポート**: 週単位の学習データ分析と前週比較
- **月次トレンド**: 長期的な学習傾向の把握
- **生産性メトリクス**: 最適な学習パターンの分析
- **目標追跡**: 学習目標の達成状況監視

### 📈 グラフ・可視化
- **日別学習時間**: 学習活動の日次推移
- **科目別分布**: 学習時間の科目別内訳
- **時間帯別分析**: 最も生産的な時間帯の特定
- **週次比較**: 複数週にわたる学習パフォーマンス比較

### 🎯 パーソナライズ
- **学習継続性スコア**: 学習習慣の定量化
- **改善提案**: AIによる学習パターンの改善提案
- **ピーク時間分析**: 個人の最適学習時間の特定

## アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  API Gateway    │    │  Lambda         │
│   Dashboard     ├────┤                 ├────┤  Analytics      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                ┌───────┴───────┐
                                                │               │
                                         ┌──────▼──────┐ ┌──────▼──────┐
                                         │  DynamoDB   │ │ CloudWatch  │
                                         │   Tables    │ │   Metrics   │
                                         └─────────────┘ └─────────────┘
```

### コンポーネント構成

- **Lambda Functions**: サーバーレス実行環境
- **DynamoDB**: 学習データの保存・クエリ
- **API Gateway**: RESTful API提供
- **CloudWatch**: ログ・メトリクス監視

## ディレクトリ構造

```
analytics/
├── README.md                    # このファイル
├── lambda/                      # Lambda関数コード
│   ├── src/
│   │   ├── handlers/           # APIエンドポイント
│   │   ├── services/           # ビジネスロジック
│   │   ├── models/             # データモデル
│   │   └── utils/              # ユーティリティ
│   ├── tests/                  # テストコード
│   ├── pyproject.toml          # Python依存関係
│   └── README.md
├── terraform/                   # インフラ定義
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── README.md
└── docker/                     # 開発環境
    ├── Dockerfile
    ├── docker-compose.yml
    ├── Makefile
    └── README.md
```

## 開発環境セットアップ

### 前提条件
- Python 3.13+
- Poetry 1.7+
- Docker & Docker Compose
- AWS CLI（本番デプロイ用）

### ローカル開発

1. **依存関係のインストール**
```bash
cd lambda
poetry install
```

2. **Docker環境の起動**
```bash
cd docker
make up
```

3. **データベース初期化**
```bash
make init-db
```

4. **サービス確認**
```bash
# Analytics API
curl http://localhost:8003/health

# API ドキュメント
open http://localhost:8003/docs
```

### 開発コマンド

```bash
# コード品質チェック
make lint

# テスト実行
make test

# コードフォーマット
make format

# 開発サイクル（フォーマット + リント + テスト）
make dev
```

## API エンドポイント

### 分析系API

| エンドポイント | メソッド | 説明 |
|----------------|----------|------|
| `/analytics/weekly` | GET | 週次レポート取得 |
| `/analytics/monthly-trends` | GET | 月次トレンド取得 |
| `/analytics/productivity` | GET | 生産性メトリクス |
| `/analytics/summary` | GET | 学習サマリー |
| `/analytics/goals` | GET | 目標追跡データ |

### グラフ系API

| エンドポイント | メソッド | 説明 |
|----------------|----------|------|
| `/analytics/charts/daily_duration` | GET | 日別学習時間グラフ |
| `/analytics/charts/subject_distribution` | GET | 科目別分布グラフ |
| `/analytics/charts/hourly_distribution` | GET | 時間帯別分布グラフ |
| `/analytics/charts/weekly_comparison` | GET | 週次比較グラフ |

### カスタム分析API

| エンドポイント | メソッド | 説明 |
|----------------|----------|------|
| `/analytics/analyze` | POST | カスタム分析実行 |

### 使用例

```bash
# 今週の学習レポート取得
curl "http://localhost:8003/analytics/weekly"

# 特定週のレポート取得
curl "http://localhost:8003/analytics/weekly?week_start=2024-01-01"

# 過去6ヶ月のトレンド取得
curl "http://localhost:8003/analytics/monthly-trends?months=6"

# 生産性分析（過去30日）
curl "http://localhost:8003/analytics/productivity?period_days=30"
```

## デプロイ

### 本番環境（AWS Lambda）

1. **Terraform によるインフラ構築**
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

2. **Lambda関数のデプロイ**
```bash
make deploy-lambda
```

### 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `ENV` | 実行環境 | `local` |
| `AWS_REGION` | AWSリージョン | `ap-northeast-1` |
| `USERS_TABLE` | ユーザーテーブル名 | `Users` |
| `TIMER_TABLE` | タイマーテーブル名 | `Timer` |
| `RECORDS_TABLE` | 学習記録テーブル名 | `Records` |
| `ROADMAP_TABLE` | ロードマップテーブル名 | `Roadmap` |
| `ENABLE_CACHE` | キャッシュ有効化 | `false` |
| `LOG_LEVEL` | ログレベル | `INFO` |

## モニタリング

### CloudWatch メトリクス
- Lambda実行時間・エラー率
- DynamoDBクエリパフォーマンス
- API Gateway レスポンス時間

### ログ
```bash
# Lambda ログの確認
aws logs tail /aws/lambda/learning-platform-analytics --follow

# ローカルログの確認
make logs
```

## テスト

### ユニットテスト
```bash
cd lambda
poetry run pytest tests/unit/
```

### 統合テスト
```bash
cd lambda
poetry run pytest tests/integration/
```

### カバレッジレポート
```bash
poetry run pytest --cov=src --cov-report=html
```

## パフォーマンス考慮事項

### キャッシュ戦略
- 週次レポート: 1時間キャッシュ
- 月次トレンド: 6時間キャッシュ
- 生産性メトリクス: 30分キャッシュ

### クエリ最適化
- DynamoDB複合インデックスの活用
- バッチクエリによる読み取り効率化
- 必要最小限のデータ取得

## セキュリティ

### 認証・認可
- JWT トークンベース認証
- ユーザーIDベースのデータ分離
- 最小権限の原則（IAMロール）

### データ保護
- 機密情報のマスキング
- ログでの個人情報除外
-暗号化転送（HTTPS/TLS）

## トラブルシューティング

### よくある問題

**Lambda タイムアウト**
```bash
# メモリサイズの増加またはクエリ最適化を検討
terraform apply -var="lambda_memory_size=512"
```

**DynamoDB スループット不足**
```bash
# プロビジョンドキャパシティの確認
aws dynamodb describe-table --table-name Timer
```

**キャッシュミス多発**
```bash
# TTL設定の確認
grep CACHE_TTL lambda/src/utils/config.py
```

## 貢献

### 開発フロー
1. feature ブランチの作成
2. コード実装とテスト追加
3. `make dev` でコード品質チェック
4. プルリクエスト作成

### コード規約
- Black によるコードフォーマット
- Type hints の必須使用
- Docstring による関数説明
- テストカバレッジ80%以上維持

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**📞 サポート**
- Issues: GitHub Issues
- Documents: `/docs`フォルダ内の技術仕様書
- API Docs: `http://localhost:8003/docs` (開発環境)