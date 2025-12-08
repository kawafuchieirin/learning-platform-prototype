import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // コンソールエラーを監視
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  // ページエラーを監視
  const pageErrors = [];
  page.on('pageerror', err => {
    pageErrors.push(err.toString());
  });

  try {
    console.log('Checking http://localhost:5173 for CSS errors...');
    
    // タイムアウトを設定
    const response = await page.goto('http://localhost:5173', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    if (!response) {
      console.error('Failed to load page');
      process.exit(1);
    }

    console.log(`Page loaded with status: ${response.status()}`);

    // CSSが正しく適用されているか確認
    const backgroundColor = await page.evaluate(() => {
      const body = document.querySelector('body');
      return window.getComputedStyle(body).backgroundColor;
    });
    console.log(`Body background color: ${backgroundColor}`);

    // ページコンテンツの確認
    const title = await page.textContent('h1');
    console.log(`Page title: ${title}`);

    // エラーの確認
    await page.waitForTimeout(2000); // 2秒待機してエラーをキャッチ

    if (consoleErrors.length > 0) {
      console.error('\n❌ Console Errors Found:');
      consoleErrors.forEach(err => console.error('  - ' + err));
    }

    if (pageErrors.length > 0) {
      console.error('\n❌ Page Errors Found:');
      pageErrors.forEach(err => console.error('  - ' + err));
    }

    if (consoleErrors.length === 0 && pageErrors.length === 0) {
      console.log('\n✅ No CSS errors detected!');
      console.log('✅ Page loaded successfully without errors');
    }

    // 各ページもチェック
    const pages = ['/dashboard', '/records', '/roadmap', '/analytics'];
    for (const pagePath of pages) {
      console.log(`\nChecking ${pagePath}...`);
      await page.goto(`http://localhost:5173${pagePath}`, {
        waitUntil: 'networkidle'
      });
      await page.waitForTimeout(1000);
      console.log(`✅ ${pagePath} loaded successfully`);
    }

  } catch (error) {
    console.error('Test failed:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
    
    if (consoleErrors.length === 0 && pageErrors.length === 0) {
      console.log('\n🎉 All CSS errors have been fixed!');
      process.exit(0);
    } else {
      process.exit(1);
    }
  }
})();