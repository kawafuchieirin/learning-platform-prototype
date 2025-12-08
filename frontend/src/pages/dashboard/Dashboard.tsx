import { Link } from 'react-router-dom'

export function Dashboard() {
  return (
    <div className="container mx-auto p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">学習プラットフォーム</h1>
        <p className="text-gray-600 mt-2">
          学習時間を記録し、進捗を管理しましょう
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white border-gray-200 border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">学習タイマー</h2>
          <p className="text-gray-600">
            学習時間を測定し、記録を残すことができます
          </p>
          <div className="mt-4">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md">
              タイマーを開始
            </button>
          </div>
        </div>

        <div className="bg-white border-gray-200 border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">ロードマップ</h2>
          <p className="text-gray-600">
            学習計画を作成し、進捗を管理します
          </p>
          <div className="mt-4">
            <Link 
              to="/roadmap"
              className="inline-block bg-gray-100 text-gray-900 px-4 py-2 rounded-md hover:bg-gray-100/80 transition-colors"
            >
              ロードマップを見る
            </Link>
          </div>
        </div>

        <div className="bg-white border-gray-200 border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">学習記録</h2>
          <p className="text-gray-600">
            学習記録を作成・管理し、進捗を確認します
          </p>
          <div className="mt-4">
            <Link 
              to="/records"
              className="inline-block bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
            >
              学習記録を見る
            </Link>
          </div>
        </div>

        <div className="bg-white border-gray-200 border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">学習分析</h2>
          <p className="text-gray-600">
            学習データを分析し、レポートを確認します
          </p>
          <div className="mt-4">
            <Link 
              to="/analytics"
              className="inline-block bg-indigo-50 text-indigo-900 px-4 py-2 rounded-md hover:bg-indigo-50/80 transition-colors"
            >
              分析を見る
            </Link>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <h3 className="text-2xl font-semibold mb-4">最近の学習記録</h3>
        <div className="bg-white border-gray-200 border rounded-lg p-6">
          <p className="text-gray-600">
            まだ学習記録がありません。タイマーを使って学習を開始しましょう！
          </p>
        </div>
      </div>
    </div>
  )
}