# Tests

E2Eテストとテスト関連リソース

## 概要

Playwright + MCPによるE2Eテスト実装

## 構成

- `e2e/` - E2Eテストスイート

## テスト対象

- フロントエンド画面操作
- API動作確認
- 機能間連携テスト
- ユーザーシナリオテスト

## 実行方法

```bash
# Playwright環境セットアップ
cd tests/e2e
npm install
npm run install-browsers

# テスト実行
npm test                # 全テスト実行
npm run test:headed     # ブラウザ表示
npm run test:ui         # UIモード
npm run test:debug      # デバッグモード

# レポート表示
npm run report
```

## テスト環境

- Chromium, Firefox, Safari対応
- ローカル環境・本番環境両対応
- 自動スクリーンショット・動画記録