// global-teardown.js

async function globalTeardown() {
  console.log('🧹 Starting global teardown for Learning Platform E2E tests');
  
  try {
    // Clean up test data if needed
    console.log('📋 Cleaning up test data...');
    
    // In a real scenario, you might want to:
    // 1. Clear test user data from DynamoDB
    // 2. Stop any test servers
    // 3. Clean up temporary files
    
    console.log('✅ Global teardown completed successfully');
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error in teardown to avoid masking test failures
  }
}

module.exports = globalTeardown;