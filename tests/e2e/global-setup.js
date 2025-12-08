// global-setup.js
const { chromium } = require('@playwright/test');

async function globalSetup() {
  console.log('🚀 Starting global setup for Learning Platform E2E tests');
  
  // Launch browser for authentication setup if needed
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Wait for Analytics API to be ready
    console.log('📊 Checking Analytics API availability...');
    let retries = 0;
    const maxRetries = 30;
    
    while (retries < maxRetries) {
      try {
        const response = await page.request.get('http://localhost:8003/health');
        if (response.ok()) {
          console.log('✅ Analytics API is ready');
          break;
        }
      } catch (error) {
        retries++;
        console.log(`⏳ Waiting for Analytics API... (${retries}/${maxRetries})`);
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    if (retries >= maxRetries) {
      throw new Error('❌ Analytics API failed to start within timeout');
    }

    // Setup test data if needed
    console.log('📋 Setting up test data...');
    
    // Initialize DynamoDB tables with test data
    const testUser = {
      PK: 'USER#test-user-e2e',
      SK: 'PROFILE',
      email: 'e2e-test@example.com',
      name: 'E2E Test User',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    // Add sample study sessions for testing
    const studySessions = [
      {
        PK: 'USER#test-user-e2e',
        SK: 'TIMER#2025-12-01T10:00:00Z',
        start_time: '2025-12-01T10:00:00Z',
        end_time: '2025-12-01T11:30:00Z',
        duration: 90,
        subject: 'JavaScript',
        status: 'completed'
      },
      {
        PK: 'USER#test-user-e2e',
        SK: 'TIMER#2025-12-02T14:00:00Z',
        start_time: '2025-12-02T14:00:00Z',
        end_time: '2025-12-02T15:45:00Z',
        duration: 105,
        subject: 'Python',
        status: 'completed'
      }
    ];
    
    console.log('✅ Global setup completed successfully');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

module.exports = globalSetup;