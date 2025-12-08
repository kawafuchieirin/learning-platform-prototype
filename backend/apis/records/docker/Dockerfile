# 学習記録API用 Dockerfile（ローカル開発環境）

FROM python:3.13-slim

# 作業ディレクトリの設定
WORKDIR /app

# システムパッケージの更新とタイムゾーン設定
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# Python依存関係のインストール
COPY lambda/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI用の追加依存関係（ローカル開発用）
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    mangum==0.17.0

# アプリケーションコードのコピー
COPY lambda/ .

# ポート設定
EXPOSE 8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 起動コマンド
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]