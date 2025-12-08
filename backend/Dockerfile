FROM python:3.13-slim

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Poetryのインストール
RUN pip install poetry

# ワーキングディレクトリを設定
WORKDIR /app

# Poetryの設定（仮想環境をプロジェクト内に作成しない）
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# 依存関係ファイルをコピー
COPY pyproject.toml poetry.lock* ./

# 依存関係をインストール
RUN poetry install --no-dev

# アプリケーションコードをコピー
COPY . .

# ポートを公開
EXPOSE 8000

# アプリケーション起動
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]