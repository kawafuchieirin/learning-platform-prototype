import { useState, useEffect } from 'react'
import axios from 'axios'

interface WeeklyAnalytics {
  week_start: string
  week_end: string
  total_duration: number
  daily_summaries: Array<{
    date: string
    total_duration: number
    session_count: number
    subjects: string[]
    average_session_duration: number
  }>
  top_subjects: Array<{
    subject: string
    duration: number
    percentage: number
  }>
  study_consistency: number
  comparison_with_previous_week: {
    duration_change: number
    duration_change_percentage: number
    session_change: number
    trend: string
  }
}

interface AnalyticsResponse {
  status: string
  data: WeeklyAnalytics
  generated_at: string
}

export function Analytics() {
  const [weeklyData, setWeeklyData] = useState<WeeklyAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchWeeklyAnalytics = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Analytics APIからデータを取得
        const response = await axios.get<AnalyticsResponse>(
          'http://localhost:8003/analytics/weekly'
        )
        
        setWeeklyData(response.data.data)
      } catch (err) {
        console.error('Analytics APIエラー:', err)
        setError('分析データの取得に失敗しました')
      } finally {
        setLoading(false)
      }
    }

    fetchWeeklyAnalytics()
  }, [])

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex justify-center items-center min-h-64">
          <div className="text-lg">データを読み込み中...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-50 border-gray-200 border-red-200 rounded-lg p-6 text-center">
          <div className="text-red-600 font-medium mb-2">エラー</div>
          <div className="text-red-500">{error}</div>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 bg-red-100 hover:bg-red-200 text-red-700 px-4 py-2 rounded-md"
          >
            再読み込み
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">学習分析</h1>
        <p className="text-gray-600 mt-2">
          週次の学習データと進捗を確認できます
        </p>
      </header>

      {weeklyData && (
        <>
          {/* サマリーカード */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white border rounded-lg p-6">
              <h3 className="text-sm font-medium text-gray-600 mb-2">
                総学習時間
              </h3>
              <div className="text-3xl font-bold text-gray-900">
                {Math.floor(weeklyData.total_duration / 60)}h {weeklyData.total_duration % 60}m
              </div>
            </div>

            <div className="bg-white border rounded-lg p-6">
              <h3 className="text-sm font-medium text-gray-600 mb-2">
                学習日数
              </h3>
              <div className="text-3xl font-bold text-gray-900">
                {weeklyData.daily_summaries.filter(day => day.total_duration > 0).length}日
              </div>
            </div>

            <div className="bg-white border rounded-lg p-6">
              <h3 className="text-sm font-medium text-gray-600 mb-2">
                継続率
              </h3>
              <div className="text-3xl font-bold text-gray-900">
                {weeklyData.study_consistency.toFixed(1)}%
              </div>
            </div>

            <div className="bg-white border rounded-lg p-6">
              <h3 className="text-sm font-medium text-gray-600 mb-2">
                前週比
              </h3>
              <div className={`text-3xl font-bold ${
                weeklyData.comparison_with_previous_week.duration_change >= 0 
                  ? 'text-green-600' 
                  : 'text-red-600'
              }`}>
                {weeklyData.comparison_with_previous_week.duration_change >= 0 ? '+' : ''}
                {weeklyData.comparison_with_previous_week.duration_change}分
              </div>
            </div>
          </div>

          {/* 日別学習時間 */}
          <div className="bg-white border rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">日別学習時間</h2>
            <div className="space-y-3">
              {weeklyData.daily_summaries.map((day) => (
                <div key={day.date} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-20 text-sm text-gray-600">
                      {new Date(day.date).toLocaleDateString('ja-JP', { 
                        month: 'short', 
                        day: 'numeric',
                        weekday: 'short'
                      })}
                    </div>
                    <div className="flex-1">
                      <div 
                        className="h-6 bg-primary rounded"
                        style={{
                          width: `${day.total_duration > 0 ? Math.max(day.total_duration / Math.max(...weeklyData.daily_summaries.map(d => d.total_duration)) * 100, 10) : 0}%`
                        }}
                      />
                    </div>
                  </div>
                  <div className="text-sm font-medium w-16 text-right">
                    {day.total_duration > 0 ? `${day.total_duration}分` : '-'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 期間情報 */}
          <div className="bg-gray-100 rounded-lg p-4">
            <div className="text-sm text-gray-600">
              分析期間: {weeklyData.week_start} 〜 {weeklyData.week_end}
            </div>
          </div>
        </>
      )}
    </div>
  )
}