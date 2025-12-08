/**
 * 学習記録API接続テストページ
 */

import React, { useState, useEffect } from 'react';
import { RecordsAPI, checkHealth } from '../api/records';

const RecordsTest: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [templates, setTemplates] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const testConnection = async () => {
      try {
        setLoading(true);
        setError(null);

        // ヘルスチェック
        console.log('Testing health check...');
        const healthResponse = await checkHealth();
        setHealth(healthResponse);
        console.log('Health check response:', healthResponse);

        // テンプレート取得
        console.log('Testing templates...');
        const templatesResponse = await RecordsAPI.getTemplates();
        setTemplates(templatesResponse);
        console.log('Templates response:', templatesResponse);

      } catch (err: any) {
        console.error('Connection test failed:', err);
        setError(err.message || 'API接続に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    testConnection();
  }, []);

  const createTestRecord = async () => {
    try {
      const testData = {
        title: '接続テスト記録',
        content: 'API接続のテスト用記録です',
        duration_minutes: 30,
        difficulty: 'easy' as const,
        satisfaction: 3
      };

      console.log('Creating test record:', testData);
      const result = await RecordsAPI.createRecord(testData);
      console.log('Test record created:', result);
      alert('テスト記録が作成されました！');
    } catch (err: any) {
      console.error('Failed to create test record:', err);
      alert(`記録作成に失敗: ${err.message}`);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Records API 接続テスト</h1>
      
      {loading && (
        <div className="text-blue-600">
          API接続をテスト中...
        </div>
      )}

      {error && (
        <div className="bg-red-100 border-gray-200 border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>エラー:</strong> {error}
        </div>
      )}

      {health && (
        <div className="bg-green-100 border-gray-200 border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          <h3 className="font-bold">✅ ヘルスチェック成功</h3>
          <pre>{JSON.stringify(health, null, 2)}</pre>
        </div>
      )}

      {templates && (
        <div className="bg-blue-100 border-gray-200 border-blue-400 text-blue-700 px-4 py-3 rounded mb-4">
          <h3 className="font-bold">✅ テンプレート取得成功</h3>
          <p>テンプレート数: {templates.templates?.length}</p>
          <details className="mt-2">
            <summary>詳細を表示</summary>
            <pre className="mt-2 text-xs">{JSON.stringify(templates, null, 2)}</pre>
          </details>
        </div>
      )}

      <div className="mt-6">
        <button
          onClick={createTestRecord}
          disabled={loading || !!error}
          className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded"
        >
          テスト記録を作成
        </button>
      </div>

      <div className="mt-6 text-sm text-gray-600">
        <p><strong>API URL:</strong> http://localhost:8009</p>
        <p><strong>テストページ:</strong> このページでAPI接続を確認できます</p>
      </div>
    </div>
  );
};

export default RecordsTest;