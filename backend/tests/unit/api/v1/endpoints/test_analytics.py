import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app
from src.models.analytics import (
    WeeklyReportResponse,
    AnalyticsSummary,
    WeeklyStats,
    ComparisonStats,
    SubjectStats,
    ChartDataPoint
)

client = TestClient(app)


@pytest.fixture
def mock_analytics_service():
    """Analytics サービスのモック"""
    with patch('src.api.v1.endpoints.analytics.AnalyticsService') as mock_service:
        service_instance = AsyncMock()
        mock_service.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_auth():
    """認証のモック（テストユーザーを返す）"""
    with patch('src.api.v1.endpoints.analytics.get_current_user') as mock_get_user:
        mock_get_user.return_value = "test-user-1"
        yield mock_get_user


@pytest.fixture
def sample_weekly_report():
    """サンプル週次レポートデータ"""
    return WeeklyReportResponse(
        summary=AnalyticsSummary(
            total_study_time=420,  # 7時間
            total_sessions=10,
            current_streak=5,
            longest_streak=14,
            average_daily_study=60.0,
            most_productive_hour=14
        ),
        weekly_stats=WeeklyStats(
            week_start=date(2024, 1, 1),
            week_end=date(2024, 1, 7),
            total_duration=420,
            daily_sessions=[],
            average_session_duration=42.0,
            most_studied_subject="Python",
            study_days=7
        ),
        comparison=ComparisonStats(
            current_week_duration=420,
            previous_week_duration=360,
            duration_change=60,
            duration_change_percentage=16.7,
            current_week_sessions=10,
            previous_week_sessions=8,
            session_change=2
        ),
        subject_breakdown=[
            SubjectStats(subject="Python", duration=240, session_count=6, percentage=57.1),
            SubjectStats(subject="JavaScript", duration=120, session_count=3, percentage=28.6),
            SubjectStats(subject="SQL", duration=60, session_count=1, percentage=14.3)
        ],
        daily_chart_data=[
            ChartDataPoint(date="2024-01-01", value=1.0, label="60m"),
            ChartDataPoint(date="2024-01-02", value=1.5, label="90m"),
        ],
        subject_chart_data=[
            ChartDataPoint(date="Python", value=4.0, label="240m"),
            ChartDataPoint(date="JavaScript", value=2.0, label="120m"),
        ]
    )


class TestAnalyticsAPI:
    """Analytics API のテストクラス"""

    def test_get_weekly_report_success(self, mock_analytics_service, mock_auth, sample_weekly_report):
        """週次レポート取得の正常系テスト"""
        # モックの設定
        mock_analytics_service.generate_weekly_report.return_value = sample_weekly_report
        
        # APIリクエスト
        response = client.get("/api/v1/analytics/weekly")
        
        # 検証
        assert response.status_code == 200
        data = response.json()
        
        assert data["summary"]["total_study_time"] == 420
        assert data["summary"]["total_sessions"] == 10
        assert data["weekly_stats"]["total_duration"] == 420
        assert data["comparison"]["duration_change"] == 60
        assert len(data["subject_breakdown"]) == 3
        
        # サービスメソッドが正しく呼ばれたか検証
        mock_analytics_service.generate_weekly_report.assert_called_once()

    def test_get_weekly_report_with_specific_date(self, mock_analytics_service, mock_auth, sample_weekly_report):
        """特定の週の週次レポート取得テスト"""
        mock_analytics_service.generate_weekly_report.return_value = sample_weekly_report
        
        response = client.get("/api/v1/analytics/weekly?week_start=2024-01-01")
        
        assert response.status_code == 200
        mock_analytics_service.generate_weekly_report.assert_called_once()

    def test_get_analytics_summary_success(self, mock_analytics_service, mock_auth):
        """分析サマリー取得の正常系テスト"""
        # モックデータ
        mock_summary = AnalyticsSummary(
            total_study_time=1260,  # 21時間
            total_sessions=30,
            current_streak=10,
            longest_streak=21,
            average_daily_study=42.0,
            most_productive_hour=15
        )
        mock_analytics_service.get_analytics_summary.return_value = mock_summary
        
        # APIリクエスト
        response = client.get("/api/v1/analytics/summary")
        
        # 検証
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_study_time"] == 1260
        assert data["total_sessions"] == 30
        assert data["current_streak"] == 10
        assert data["longest_streak"] == 21
        assert data["most_productive_hour"] == 15

    def test_get_analytics_summary_with_date_range(self, mock_analytics_service, mock_auth):
        """日付範囲指定のサマリー取得テスト"""
        mock_summary = AnalyticsSummary(
            total_study_time=600,
            total_sessions=12,
            current_streak=5,
            longest_streak=15,
            average_daily_study=50.0,
            most_productive_hour=13
        )
        mock_analytics_service.get_analytics_summary.return_value = mock_summary
        
        response = client.get(
            "/api/v1/analytics/summary?start_date=2024-01-01&end_date=2024-01-31"
        )
        
        assert response.status_code == 200
        mock_analytics_service.get_analytics_summary.assert_called_once()

    def test_get_comparison_data_week(self, mock_analytics_service, mock_auth):
        """週次比較データ取得テスト"""
        mock_comparison = {
            "current_week_duration": 420,
            "previous_week_duration": 360,
            "duration_change": 60,
            "duration_change_percentage": 16.7
        }
        mock_analytics_service.get_comparison_data.return_value = mock_comparison
        
        response = client.get("/api/v1/analytics/comparison?period=week")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_week_duration"] == 420
        assert data["duration_change"] == 60

    def test_get_comparison_data_month(self, mock_analytics_service, mock_auth):
        """月次比較データ取得テスト"""
        mock_comparison = {
            "current_month_duration": 1800,
            "previous_month_duration": 1500,
            "duration_change": 300,
            "duration_change_percentage": 20.0
        }
        mock_analytics_service.get_comparison_data.return_value = mock_comparison
        
        response = client.get("/api/v1/analytics/comparison?period=month")
        
        assert response.status_code == 200
        mock_analytics_service.get_comparison_data.assert_called_with("test-user-1", "month")

    def test_get_comparison_invalid_period(self, mock_analytics_service, mock_auth):
        """無効な期間指定のエラーテスト"""
        response = client.get("/api/v1/analytics/comparison?period=year")
        
        assert response.status_code == 400
        data = response.json()
        assert "week" in data["detail"] or "month" in data["detail"]

    def test_get_daily_chart_data(self, mock_analytics_service, mock_auth):
        """日別グラフデータ取得テスト"""
        mock_chart_data = [
            ChartDataPoint(date="2024-01-01", value=1.0, label="60m"),
            ChartDataPoint(date="2024-01-02", value=1.5, label="90m"),
            ChartDataPoint(date="2024-01-03", value=0.5, label="30m"),
        ]
        mock_analytics_service.get_daily_chart_data.return_value = mock_chart_data
        
        response = client.get("/api/v1/analytics/charts/daily?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 3
        assert data["data"][0]["value"] == 1.0

    def test_get_subject_chart_data(self, mock_analytics_service, mock_auth):
        """科目別グラフデータ取得テスト"""
        mock_chart_data = [
            ChartDataPoint(date="Python", value=4.0, label="240m"),
            ChartDataPoint(date="JavaScript", value=2.0, label="120m"),
        ]
        mock_analytics_service.get_subject_chart_data.return_value = mock_chart_data
        
        response = client.get("/api/v1/analytics/charts/subjects")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 2

    def test_get_hourly_distribution(self, mock_analytics_service, mock_auth):
        """時間帯別分布取得テスト"""
        mock_chart_data = [
            ChartDataPoint(date="14:00", value=2.0, label="120m"),
            ChartDataPoint(date="15:00", value=1.5, label="90m"),
        ]
        mock_analytics_service.get_hourly_distribution.return_value = mock_chart_data
        
        response = client.get("/api/v1/analytics/charts/hourly")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_get_study_streaks(self, mock_analytics_service, mock_auth):
        """学習継続データ取得テスト"""
        mock_streaks = {
            "current_streak": 7,
            "longest_streak": 21,
            "recent_study_dates": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "total_study_days": 150
        }
        mock_analytics_service.get_study_streaks.return_value = mock_streaks
        
        response = client.get("/api/v1/analytics/streaks")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_streak"] == 7
        assert data["longest_streak"] == 21
        assert len(data["recent_study_dates"]) == 3

    def test_get_productivity_insights(self, mock_analytics_service, mock_auth):
        """生産性インサイト取得テスト"""
        mock_insights = {
            "peak_hours": [14, 15, 16],
            "preferred_session_length": 45,
            "most_productive_days": ["月曜日", "火曜日"],
            "study_consistency_score": 85.5,
            "recommendations": ["継続的な学習を心がけましょう"]
        }
        mock_analytics_service.get_productivity_insights.return_value = mock_insights
        
        response = client.get("/api/v1/analytics/productivity")
        
        assert response.status_code == 200
        data = response.json()
        assert data["study_consistency_score"] == 85.5
        assert len(data["peak_hours"]) == 3

    def test_export_analytics_json(self, mock_analytics_service, mock_auth):
        """JSON形式データエクスポートテスト"""
        mock_export_data = {
            "data": [
                {"date": "2024-01-01", "duration": 60, "subject": "Python"},
                {"date": "2024-01-02", "duration": 90, "subject": "JavaScript"}
            ]
        }
        mock_analytics_service.export_analytics_data.return_value = mock_export_data
        
        response = client.get("/api/v1/analytics/export?format=json")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 2

    def test_export_analytics_csv(self, mock_analytics_service, mock_auth):
        """CSV形式データエクスポートテスト"""
        mock_csv_url = "https://example.com/exports/test-user-1/analytics_20240101_120000.csv"
        mock_analytics_service.export_analytics_data.return_value = mock_csv_url
        
        response = client.get("/api/v1/analytics/export?format=csv")
        
        assert response.status_code == 200
        data = response.json()
        assert "download_url" in data

    def test_export_invalid_format(self, mock_analytics_service, mock_auth):
        """無効なエクスポート形式のエラーテスト"""
        response = client.get("/api/v1/analytics/export?format=xml")
        
        assert response.status_code == 400

    def test_service_error_handling(self, mock_analytics_service, mock_auth):
        """サービス層エラーのハンドリングテスト"""
        # サービス層で例外が発生する場合をテスト
        mock_analytics_service.generate_weekly_report.side_effect = Exception("Database error")
        
        response = client.get("/api/v1/analytics/weekly")
        
        assert response.status_code == 500
        data = response.json()
        assert "エラー" in data["detail"]

    @patch('src.api.v1.endpoints.analytics.get_current_user')
    def test_unauthorized_access(self, mock_get_user):
        """認証エラーのテスト"""
        from fastapi import HTTPException
        mock_get_user.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        
        response = client.get("/api/v1/analytics/weekly")
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestAnalyticsAPIAsync:
    """非同期処理のテスト"""

    async def test_concurrent_requests(self):
        """並行リクエストのテスト"""
        # 実際の並行処理テストは統合テストで行う
        pass

    async def test_large_data_handling(self):
        """大量データ処理のテスト"""
        # パフォーマンステストは別途実装
        pass


if __name__ == "__main__":
    pytest.main([__file__])