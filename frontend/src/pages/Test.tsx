import React from 'react';

const Test: React.FC = () => {
  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold text-blue-600 mb-4">
        テストページ
      </h1>
      <p className="text-gray-600 mb-6">
        フロントエンドアプリケーションが正常に動作しています。
      </p>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-3">ロードマップ機能</h2>
        <p className="text-gray-700">
          ロードマップページへの遷移をテストします。
        </p>
        <a 
          href="/roadmap" 
          className="inline-block mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          ロードマップページへ
        </a>
      </div>
    </div>
  );
};

export default Test;