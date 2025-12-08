// tests/api/analytics.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Analytics API E2E Tests', () => {
  const baseURL = 'http://localhost:8003';

  test.beforeAll(async () => {
    // Ensure Analytics API is running
    console.log('🔍 Verifying Analytics API availability...');
  });

  test('Health check endpoint', async ({ request }) => {
    const response = await request.get(`${baseURL}/health`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toEqual({
      status: 'healthy',
      service: 'analytics',
      version: '0.1.0'
    });
  });

  test('Root endpoint', async ({ request }) => {
    const response = await request.get(`${baseURL}/`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toMatchObject({
      service: 'analytics',
      message: 'Analytics Service for Learning Platform',
      version: '0.1.0'
    });
  });

  test('Weekly analytics endpoint', async ({ request }) => {
    const response = await request.get(`${baseURL}/analytics/weekly`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'success');
    expect(data).toHaveProperty('data');
    expect(data).toHaveProperty('generated_at');
    
    // Validate data structure
    expect(data.data).toHaveProperty('week_start');
    expect(data.data).toHaveProperty('week_end');
    expect(data.data).toHaveProperty('total_duration');
    expect(data.data).toHaveProperty('daily_summaries');
    expect(Array.isArray(data.data.daily_summaries)).toBeTruthy();
    expect(data.data.daily_summaries).toHaveLength(7);
  });

  test('Weekly analytics with custom date', async ({ request }) => {
    const testDate = '2025-12-01';
    const response = await request.get(`${baseURL}/analytics/weekly?week_start=${testDate}`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('success');
    expect(data.data.week_start).toBe(testDate);
  });

  test('Weekly analytics with invalid date format', async ({ request }) => {
    const response = await request.get(`${baseURL}/analytics/weekly?week_start=invalid-date`);
    
    expect(response.status()).toBe(400);
    
    const data = await response.json();
    expect(data.detail).toContain('無効な日付形式');
  });

  test('Monthly trends endpoint', async ({ request }) => {
    const response = await request.get(`${baseURL}/analytics/monthly-trends`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'success');
    expect(data).toHaveProperty('data');
    expect(Array.isArray(data.data)).toBeTruthy();
    expect(data.data.length).toBe(6); // Default 6 months
    
    // Validate trend data structure
    if (data.data.length > 0) {
      const trend = data.data[0];
      expect(trend).toHaveProperty('month');
      expect(trend).toHaveProperty('total_duration');
      expect(trend).toHaveProperty('session_count');
      expect(trend).toHaveProperty('average_daily_duration');
      expect(trend).toHaveProperty('study_days');
      expect(trend).toHaveProperty('consistency_score');
    }
  });

  test('Monthly trends with custom months parameter', async ({ request }) => {
    const months = 3;
    const response = await request.get(`${baseURL}/analytics/monthly-trends?months=${months}`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.data).toHaveLength(months);
  });

  test('Productivity metrics endpoint', async ({ request }) => {
    const response = await request.get(`${baseURL}/analytics/productivity`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'success');
    expect(data).toHaveProperty('data');
    
    // Validate productivity data structure
    expect(data.data).toHaveProperty('peak_hours');
    expect(data.data).toHaveProperty('optimal_session_length');
    expect(data.data).toHaveProperty('best_study_days');
    expect(data.data).toHaveProperty('focus_score');
    expect(data.data).toHaveProperty('improvement_suggestions');
    expect(Array.isArray(data.data.peak_hours)).toBeTruthy();
    expect(Array.isArray(data.data.best_study_days)).toBeTruthy();
    expect(Array.isArray(data.data.improvement_suggestions)).toBeTruthy();
  });

  test('Productivity metrics with custom period', async ({ request }) => {
    const periodDays = 7;
    const response = await request.get(`${baseURL}/analytics/productivity?period_days=${periodDays}`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('success');
  });

  test('Analytics summary endpoint', async ({ request }) => {
    const response = await request.get(`${baseURL}/analytics/summary`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'success');
    expect(data).toHaveProperty('data');
    
    // Validate summary data structure
    const summary = data.data;
    expect(summary).toHaveProperty('period');
    expect(summary).toHaveProperty('totals');
    expect(summary).toHaveProperty('averages');
    expect(summary).toHaveProperty('streaks');
    expect(summary).toHaveProperty('top_subjects');
    expect(summary).toHaveProperty('consistency_score');
    
    // Validate nested objects
    expect(summary.period).toHaveProperty('start_date');
    expect(summary.period).toHaveProperty('end_date');
    expect(summary.period).toHaveProperty('days');
    
    expect(summary.totals).toHaveProperty('study_time_minutes');
    expect(summary.totals).toHaveProperty('study_time_hours');
    expect(summary.totals).toHaveProperty('sessions');
    expect(summary.totals).toHaveProperty('study_days');
  });

  test('Chart data endpoints', async ({ request }) => {
    const chartTypes = ['daily_duration', 'subject_distribution', 'hourly_distribution', 'weekly_comparison'];
    
    for (const chartType of chartTypes) {
      const response = await request.get(`${baseURL}/analytics/charts/${chartType}`);
      
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(data).toHaveProperty('status', 'success');
      expect(data).toHaveProperty('data');
      
      // Validate chart data structure
      expect(data.data).toHaveProperty('chart_type', chartType);
      expect(data.data).toHaveProperty('data_points');
      expect(Array.isArray(data.data.data_points)).toBeTruthy();
    }
  });

  test('Chart data with invalid type', async ({ request }) => {
    const response = await request.get(`${baseURL}/analytics/charts/invalid_type`);
    
    expect(response.status()).toBe(400);
    
    const data = await response.json();
    expect(data.detail).toContain('無効なグラフタイプ');
  });

  test('Goal tracking endpoint', async ({ request }) => {
    const response = await request.get(`${baseURL}/analytics/goals`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'success');
    expect(data).toHaveProperty('data');
    expect(Array.isArray(data.data)).toBeTruthy();
  });

  test('Custom analytics endpoint', async ({ request }) => {
    const requestBody = {
      user_id: 'test-user-1',
      analysis_type: 'weekly',
      start_date: '2025-12-01',
      end_date: '2025-12-07'
    };
    
    const response = await request.post(`${baseURL}/analytics/analyze`, {
      data: requestBody
    });
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'success');
    expect(data).toHaveProperty('analytics');
    
    // Validate analytics response structure
    const analytics = data.analytics;
    expect(analytics).toHaveProperty('request_id');
    expect(analytics).toHaveProperty('user_id', requestBody.user_id);
    expect(analytics).toHaveProperty('analysis_type', requestBody.analysis_type);
    expect(analytics).toHaveProperty('generated_at');
    expect(analytics).toHaveProperty('data');
  });

  test('API response times', async ({ request }) => {
    const endpoints = [
      '/health',
      '/analytics/weekly',
      '/analytics/monthly-trends',
      '/analytics/productivity',
      '/analytics/summary'
    ];
    
    for (const endpoint of endpoints) {
      const start = Date.now();
      const response = await request.get(`${baseURL}${endpoint}`);
      const duration = Date.now() - start;
      
      expect(response.ok()).toBeTruthy();
      expect(duration).toBeLessThan(5000); // Response should be under 5 seconds
      console.log(`📊 ${endpoint}: ${duration}ms`);
    }
  });

  test('CORS headers', async ({ request }) => {
    const response = await request.get(`${baseURL}/health`);
    
    expect(response.ok()).toBeTruthy();
    
    const headers = response.headers();
    expect(headers).toHaveProperty('access-control-allow-origin');
  });
});