// tests/ui/analytics-dashboard.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Analytics Dashboard UI Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to analytics dashboard (フロントエンドが実装された場合)
    await page.goto('/analytics');
  });

  test('Analytics dashboard loads correctly', async ({ page }) => {
    // タイトル確認
    await expect(page).toHaveTitle(/Analytics.*Learning Platform/);
    
    // メインコンテンツの存在確認
    await expect(page.locator('h1')).toContainText('Analytics Dashboard');
  });

  test('Weekly analytics chart displays', async ({ page }) => {
    // 週次分析チャートの存在確認
    const weeklyChart = page.locator('[data-testid="weekly-chart"]');
    await expect(weeklyChart).toBeVisible();
    
    // チャートデータの読み込み確認
    await expect(weeklyChart).not.toBeEmpty();
  });

  test('Monthly trends chart displays', async ({ page }) => {
    // 月次トレンドチャートの存在確認
    const monthlyChart = page.locator('[data-testid="monthly-trends-chart"]');
    await expect(monthlyChart).toBeVisible();
  });

  test('Productivity metrics section displays', async ({ page }) => {
    // 生産性メトリクスセクションの確認
    const productivitySection = page.locator('[data-testid="productivity-metrics"]');
    await expect(productivitySection).toBeVisible();
    
    // フォーカススコアの表示確認
    const focusScore = page.locator('[data-testid="focus-score"]');
    await expect(focusScore).toBeVisible();
  });

  test('Study summary statistics display', async ({ page }) => {
    // 学習統計の表示確認
    const summaryStats = page.locator('[data-testid="summary-stats"]');
    await expect(summaryStats).toBeVisible();
    
    // 各統計項目の確認
    await expect(page.locator('[data-testid="total-study-time"]')).toBeVisible();
    await expect(page.locator('[data-testid="session-count"]')).toBeVisible();
    await expect(page.locator('[data-testid="study-days"]')).toBeVisible();
  });

  test('Date range picker functionality', async ({ page }) => {
    // 日付範囲選択機能のテスト
    const datePicker = page.locator('[data-testid="date-range-picker"]');
    await expect(datePicker).toBeVisible();
    
    // 日付範囲を変更
    await datePicker.click();
    await page.locator('[data-testid="last-7-days"]').click();
    
    // チャートが更新されることを確認
    await expect(page.locator('[data-testid="weekly-chart"]')).toBeVisible();
  });

  test('Export functionality', async ({ page }) => {
    // エクスポート機能のテスト
    const exportButton = page.locator('[data-testid="export-data"]');
    await expect(exportButton).toBeVisible();
    
    // ダウンロード開始を監視
    const downloadPromise = page.waitForEvent('download');
    await exportButton.click();
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('analytics');
  });

  test('Responsive design on mobile', async ({ page, browserName }) => {
    test.skip(browserName !== 'Mobile Chrome', 'Mobile-specific test');
    
    // モバイルでのレスポンシブデザイン確認
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/analytics');
    
    // モバイル用ナビゲーション確認
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
    
    // チャートが適切にリサイズされることを確認
    const chart = page.locator('[data-testid="weekly-chart"]');
    await expect(chart).toBeVisible();
    
    const chartBox = await chart.boundingBox();
    expect(chartBox.width).toBeLessThanOrEqual(375);
  });

  test('Loading states', async ({ page }) => {
    // ローディング状態のテスト
    
    // ページ読み込み時のローディングスピナー確認
    await page.goto('/analytics', { waitUntil: 'domcontentloaded' });
    
    // ローディングスピナーが表示されることを確認
    const loadingSpinner = page.locator('[data-testid="loading-spinner"]');
    await expect(loadingSpinner).toBeVisible();
    
    // データ読み込み完了後、スピナーが非表示になることを確認
    await expect(loadingSpinner).not.toBeVisible({ timeout: 10000 });
  });

  test('Error handling', async ({ page }) => {
    // エラーハンドリングのテスト
    
    // Analytics APIが利用できない場合のエラー表示をテスト
    // (ネットワークリクエストをブロックしてテスト)
    await page.route('**/analytics/**', route => route.abort());
    
    await page.goto('/analytics');
    
    // エラーメッセージの表示確認
    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText('データの読み込みに失敗しました');
  });

  test('Real-time updates', async ({ page }) => {
    // リアルタイム更新機能のテスト
    
    await page.goto('/analytics');
    
    // 自動更新ボタンの確認
    const autoRefreshToggle = page.locator('[data-testid="auto-refresh-toggle"]');
    await expect(autoRefreshToggle).toBeVisible();
    
    // 自動更新を有効化
    await autoRefreshToggle.check();
    
    // 一定時間後にデータが更新されることを確認
    const initialTimestamp = await page.locator('[data-testid="last-updated"]').textContent();
    
    // 少し待機して更新を確認
    await page.waitForTimeout(5000);
    
    const updatedTimestamp = await page.locator('[data-testid="last-updated"]').textContent();
    expect(updatedTimestamp).not.toBe(initialTimestamp);
  });

  test('Accessibility features', async ({ page }) => {
    // アクセシビリティ機能のテスト
    
    await page.goto('/analytics');
    
    // キーボードナビゲーション確認
    await page.keyboard.press('Tab');
    const focusedElement = await page.evaluate(() => document.activeElement.tagName);
    expect(['BUTTON', 'A', 'INPUT']).toContain(focusedElement);
    
    // ARIA ラベルの確認
    const charts = page.locator('[role="img"]');
    await expect(charts.first()).toHaveAttribute('aria-label');
    
    // カラーコントラスト確認（基本的なチェック）
    const backgroundColor = await page.locator('body').evaluate(el => 
      getComputedStyle(el).backgroundColor
    );
    const textColor = await page.locator('h1').evaluate(el => 
      getComputedStyle(el).color
    );
    
    // 背景色とテキスト色が異なることを確認
    expect(backgroundColor).not.toBe(textColor);
  });
});