# Analytics Lambda Function

学習データ分析を実行するAWS Lambda関数

## 概要

このLambda関数は学習プラットフォームの分析機能を提供します。FastAPI + Mangumを使用してサーバーレス環境でREST APIを公開し、DynamoDBから学習データを取得・分析してレスポンスを返します。

## アーキテクチャ

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ API Gateway │───▶│   Lambda    │───▶│  DynamoDB   │
│             │    │  Function   │    │   Tables    │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ CloudWatch  │
                   │    Logs     │
                   └─────────────┘
```

## ディレクトリ構造

```
lambda/
├── src/
│   ├── main.py                 # FastAPI + Mangum エントリポイント
│   ├── handlers/
│   │   └── analytics_handler.py  # API エンドポイント定義
│   ├── services/
│   │   ├── analytics_service.py   # ビジネスロジック
│   │   └── dynamodb_service.py    # データアクセス層
│   ├── models/
│   │   └── analytics_models.py    # Pydantic データモデル
│   └── utils/
│       ├── config.py              # 設定管理
│       ├── auth.py                # 認証ユーティリティ
│       └── cache.py               # キャッシュサービス
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml              # Poetry依存関係管理
├── poetry.lock                 # 依存関係ロックファイル
└── README.md                   # このファイル
```

## セットアップ

### 依存関係のインストール

```bash
# Poetry 仮想環境内でインストール
poetry install

# 開発依存関係も含めてインストール
poetry install --with dev
```

### 環境変数設定

```bash
# 開発環境用 .env ファイル作成
cp .env.example .env

# 必要な環境変数を設定
ENV=local
AWS_REGION=ap-northeast-1
DYNAMODB_ENDPOINT=http://localhost:8001
USERS_TABLE=Users
TIMER_TABLE=Timer
RECORDS_TABLE=Records
ROADMAP_TABLE=Roadmap
```

## 開発環境での実行

### ローカル FastAPI サーバー

```bash
# 開発サーバーの起動
poetry run uvicorn src.main:app --reload --port 8000

# API ドキュメントへアクセス
open http://localhost:8000/docs
```

### Lambda 関数としてのテスト

```bash
# SAM Local を使用した場合（オプション）
sam local start-api

# Docker 経由でのテスト
docker run -p 8000:8000 analytics-lambda
```

## コード構造

### main.py - エントリポイント

```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(title="Analytics Service")

# ルーター登録
app.include_router(analytics_router, prefix="/analytics")

# Lambda ハンドラー
handler = Mangum(app)
```

### ハンドラー層（handlers/）

APIエンドポイントの定義と基本的なリクエスト処理：

- リクエストパラメータの検証
- 認証・認可の確認
- サービス層の呼び出し
- レスポンス形成

### サービス層（services/）

**analytics_service.py**
- 週次レポート生成
- 月次トレンド分析
- 生産性メトリクス計算
- グラフデータ生成

**dynamodb_service.py**
- DynamoDBクエリの実行
- データ取得・変換
- エラーハンドリング

### データモデル層（models/）

Pydantic を使用したデータ構造定義：

```python
class WeeklyAnalytics(BaseModel):
    week_start: date
    week_end: date
    total_duration: int
    daily_summaries: List[DailySummary]
    study_consistency: float
```

### ユーティリティ層（utils/）

**config.py**
- 環境変数管理
- 設定値バリデーション

**auth.py**
- JWT認証
- ユーザーID抽出

**cache.py**
- メモリキャッシュ（開発用）
- 将来的にRedis/ElastiCacheに対応

## API エンドポイント

### GET /analytics/weekly
週次学習レポートを取得

**パラメータ:**
- `week_start` (optional): 週の開始日 (YYYY-MM-DD)

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "week_start": "2024-01-01",
    "week_end": "2024-01-07",
    "total_duration": 420,
    "study_consistency": 85.5,
    "comparison_with_previous_week": {
      "duration_change": 60,
      "trend": "improving"
    }
  }
}
```

### GET /analytics/productivity
生産性メトリクスを取得

**パラメータ:**
- `period_days` (optional): 分析期間日数 (デフォルト: 30)

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "peak_hours": [14, 15, 16],
    "optimal_session_length": 45,
    "focus_score": 82.3,
    "improvement_suggestions": [
      "午前中の学習時間を増やしてみましょう"
    ]
  }
}
```

### POST /analytics/analyze
カスタム分析の実行

**リクエストボディ:**
```json
{
  "user_id": "user-123",
  "analysis_type": "weekly",
  "start_date": "2024-01-01",
  "end_date": "2024-01-07",
  "filters": {
    "subject": "Python"
  }
}
```

## テスト

### ユニットテスト

```bash
# 全テスト実行
poetry run pytest

# カバレッジ付きテスト
poetry run pytest --cov=src --cov-report=html

# 特定テストファイル実行
poetry run pytest tests/unit/test_analytics_service.py
```

### 統合テスト

```bash
# DynamoDB Local が必要
docker run -p 8001:8000 amazon/dynamodb-local

# 統合テスト実行
poetry run pytest tests/integration/
```

### テスト用モックデータ

```python
# テストケースでの使用例
@pytest.fixture
def sample_study_sessions():
    return [
        StudySession(
            session_id="session1",
            user_id="test-user",
            date=date(2024, 1, 1),
            duration=60,
            subject="Python"
        )
    ]
```

## パフォーマンス最適化

### Lambda 最適化

**コールドスタート対策:**
```python
# モジュールレベルでの初期化
analytics_service = AnalyticsService()

def handler(event, context):
    # 毎回の初期化を避ける
    return analytics_service.process(event)
```

**メモリ使用量最適化:**
```python
# 大量データ処理時のジェネレータ使用
def process_sessions(sessions):
    for session in sessions:
        yield analyze_session(session)
```

### DynamoDB 最適化

**効率的なクエリパターン:**
```python
# 複合キーを活用した範囲クエリ
response = table.query(
    KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') &
                          Key('SK').between(start_key, end_key)
)
```

**バッチ取得:**
```python
# 複数テーブルの並列取得
import asyncio

async def get_all_user_data(user_id):
    tasks = [
        get_timer_data(user_id),
        get_records_data(user_id),
        get_roadmap_data(user_id)
    ]
    return await asyncio.gather(*tasks)
```

## エラーハンドリング

### 一般的なエラーパターン

```python
try:
    result = await analytics_service.generate_weekly_analytics(user_id)
    return {"status": "success", "data": result.dict()}
except AuthError as e:
    raise HTTPException(status_code=401, detail=str(e))
except ValueError as e:
    raise HTTPException(status_code=400, detail=f"無効なパラメータ: {str(e)}")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise HTTPException(status_code=500, detail="内部エラーが発生しました")
```

### ログ出力

```python
import logging

logger = logging.getLogger(__name__)

# 構造化ログ
logger.info("Analytics request", extra={
    "user_id": user_id,
    "analysis_type": "weekly",
    "execution_time": elapsed_time
})
```

## デバッグ

### ローカルデバッグ

```bash
# デバッグモードでの起動
ENV=local DEBUG=true poetry run uvicorn src.main:app --reload

# DynamoDB Local データ確認
aws dynamodb scan --table-name Timer --endpoint-url http://localhost:8001
```

### Lambda デバッグ

```bash
# CloudWatch Logs確認
aws logs tail /aws/lambda/analytics --follow

# Lambda関数の直接実行
aws lambda invoke --function-name analytics response.json
```

## デプロイ

### パッケージング

```bash
# 依存関係のエクスポート
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Lambda レイヤー作成用
mkdir python
pip install -r requirements.txt -t python/
zip -r dependencies.zip python/
```

### 手動デプロイ

```bash
# ソースコードのZIP作成
zip -r analytics.zip src/

# Lambda関数の更新
aws lambda update-function-code \
    --function-name analytics \
    --zip-file fileb://analytics.zip
```

## 監視・運用

### メトリクス

- **実行時間**: 平均・最大応答時間
- **エラー率**: 4xx・5xx エラーの発生率
- **スループット**: 毎分リクエスト数
- **メモリ使用量**: ピーク使用量

### アラート

```bash
# CloudWatch アラーム確認
aws cloudwatch describe-alarms --alarm-names "analytics-error-rate"
```

### ログレベル設定

```python
# 本番環境: INFO, 開発環境: DEBUG
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
```

## セキュリティ考慮事項

### 入力検証

```python
from pydantic import BaseModel, validator

class AnalyticsRequest(BaseModel):
    period_days: int
    
    @validator('period_days')
    def validate_period(cls, v):
        if not 1 <= v <= 365:
            raise ValueError('期間は1-365日の間で指定してください')
        return v
```

### 機密情報の保護

```python
# ログでの機密情報マスキング
def mask_sensitive_data(data):
    masked = data.copy()
    if 'user_id' in masked:
        masked['user_id'] = f"***{masked['user_id'][-4:]}"
    return masked
```

## トラブルシューティング

### よくある問題

**1. Lambda タイムアウト**
```python
# 長時間処理の分割
async def analyze_large_dataset(data):
    batch_size = 1000
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        await process_batch(batch)
```

**2. メモリ不足**
```python
# メモリ効率的なデータ処理
def efficient_aggregation(sessions):
    return reduce(
        lambda acc, session: update_aggregation(acc, session),
        sessions,
        create_empty_aggregation()
    )
```

**3. DynamoDB スループット制限**
```python
# 指数バックオフでのリトライ
import time
import random

def exponential_backoff_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except ClientError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

## 貢献ガイドライン

### コーディング規約

1. **Type Hints必須**
```python
def calculate_metrics(sessions: List[StudySession]) -> ProductivityMetrics:
    pass
```

2. **Docstring記述**
```python
def generate_weekly_analytics(user_id: str) -> WeeklyAnalytics:
    """
    週次分析レポートを生成する
    
    Args:
        user_id: 分析対象のユーザーID
        
    Returns:
        WeeklyAnalytics: 週次分析結果
        
    Raises:
        AuthError: 認証エラー
        ValueError: 無効なパラメータ
    """
```

3. **Error Handling**
```python
# 具体的なエラー情報を含める
except ClientError as e:
    error_code = e.response.get('Error', {}).get('Code', 'Unknown')
    logger.error(f"DynamoDB error: {error_code}")
    raise
```

### プルリクエスト

1. 機能ブランチでの開発
2. テストの追加・更新
3. ドキュメントの更新
4. コードレビューの実施

---

このLambda関数は学習プラットフォームの核となる分析機能を提供します。継続的な改善と最適化により、ユーザーにとって価値のある学習インサイトを提供し続けます。