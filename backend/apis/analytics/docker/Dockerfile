FROM python:3.13-slim

# メタデータ
LABEL maintainer="Learning Platform Team"
LABEL service="analytics"
LABEL version="0.1.0"

# 環境変数
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Poetryのインストール
RUN pip install poetry

# ワーキングディレクトリを設定
WORKDIR /app

# Poetryの設定（仮想環境をプロジェクト内に作成）
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# 依存関係ファイルをコピー
COPY lambda/pyproject.toml ./

# 依存関係をインストール（lockファイル無しで、プロジェクト本体はスキップ）
RUN poetry install --only=main --no-root

# アプリケーションコードをコピー
COPY lambda/src ./src

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ポートを公開
EXPOSE 8000

# アプリケーション起動
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]