from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StudySessionSummary(BaseModel):
    """学習セッションサマリー"""
    date: date
    total_duration: int = Field(description="合計学習時間（分）")
    session_count: int = Field(description="セッション数")
    subjects: List[str] = Field(description="学習した科目")


class WeeklyStats(BaseModel):
    """週次統計"""
    week_start: date = Field(description="週の開始日（月曜日）")
    week_end: date = Field(description="週の終了日（日曜日）") 
    total_duration: int = Field(description="合計学習時間（分）")
    daily_sessions: List[StudySessionSummary] = Field(description="日別学習記録")
    average_session_duration: float = Field(description="平均セッション時間（分）")
    most_studied_subject: Optional[str] = Field(description="最も学習した科目")
    study_days: int = Field(description="学習した日数")


class ComparisonStats(BaseModel):
    """比較統計"""
    current_week_duration: int = Field(description="今週の学習時間（分）")
    previous_week_duration: int = Field(description="先週の学習時間（分）")
    duration_change: int = Field(description="学習時間の変化（分）")
    duration_change_percentage: float = Field(description="学習時間変化率（%）")
    current_week_sessions: int = Field(description="今週のセッション数")
    previous_week_sessions: int = Field(description="先週のセッション数")
    session_change: int = Field(description="セッション数の変化")


class SubjectStats(BaseModel):
    """科目別統計"""
    subject: str = Field(description="科目名")
    duration: int = Field(description="学習時間（分）")
    session_count: int = Field(description="セッション数")
    percentage: float = Field(description="全学習時間に占める割合（%）")


class ChartDataPoint(BaseModel):
    """グラフデータポイント"""
    date: str = Field(description="日付（YYYY-MM-DD）")
    value: float = Field(description="値")
    label: Optional[str] = Field(description="ラベル", default=None)


class AnalyticsSummary(BaseModel):
    """分析サマリー"""
    total_study_time: int = Field(description="累計学習時間（分）")
    total_sessions: int = Field(description="累計セッション数")
    current_streak: int = Field(description="現在の連続学習日数")
    longest_streak: int = Field(description="最長連続学習日数")
    average_daily_study: float = Field(description="1日平均学習時間（分）")
    most_productive_hour: Optional[int] = Field(description="最も生産性の高い時間帯")


class WeeklyReportResponse(BaseModel):
    """週次レポートレスポンス"""
    summary: AnalyticsSummary
    weekly_stats: WeeklyStats
    comparison: ComparisonStats
    subject_breakdown: List[SubjectStats]
    daily_chart_data: List[ChartDataPoint] = Field(description="日別学習時間グラフ用データ")
    subject_chart_data: List[ChartDataPoint] = Field(description="科目別グラフ用データ")


class MonthlyTrend(BaseModel):
    """月次トレンド"""
    month: str = Field(description="月（YYYY-MM）")
    total_duration: int = Field(description="月間学習時間（分）")
    session_count: int = Field(description="月間セッション数")
    average_daily: float = Field(description="1日平均学習時間（分）")


class AnalyticsQueryParams(BaseModel):
    """分析クエリパラメータ"""
    start_date: Optional[date] = Field(description="開始日", default=None)
    end_date: Optional[date] = Field(description="終了日", default=None)
    subject: Optional[str] = Field(description="科目フィルター", default=None)
    user_id: str = Field(description="ユーザーID")


class StudyGoal(BaseModel):
    """学習目標"""
    daily_target_minutes: int = Field(description="日次目標時間（分）")
    weekly_target_minutes: int = Field(description="週次目標時間（分）")
    target_subjects: List[str] = Field(description="目標科目", default=[])


class GoalProgress(BaseModel):
    """目標進捗"""
    daily_progress: float = Field(description="日次目標達成率（%）")
    weekly_progress: float = Field(description="週次目標達成率（%）")
    daily_remaining: int = Field(description="日次目標残り時間（分）")
    weekly_remaining: int = Field(description="週次目標残り時間（分）")
    is_daily_achieved: bool = Field(description="日次目標達成済み")
    is_weekly_achieved: bool = Field(description="週次目標達成済み")


class ProductivityInsight(BaseModel):
    """生産性インサイト"""
    peak_hours: List[int] = Field(description="ピーク時間帯")
    preferred_session_length: int = Field(description="好ましいセッション長（分）")
    most_productive_days: List[str] = Field(description="最も生産的な曜日")
    study_consistency_score: float = Field(description="学習継続スコア（0-100）")
    recommendations: List[str] = Field(description="改善提案")


class DetailedAnalyticsResponse(BaseModel):
    """詳細分析レスポンス"""
    period_summary: AnalyticsSummary
    goal_progress: Optional[GoalProgress] = None
    productivity_insights: ProductivityInsight
    monthly_trends: List[MonthlyTrend]
    hourly_distribution: List[ChartDataPoint] = Field(description="時間帯別分布")
    weekly_consistency: List[ChartDataPoint] = Field(description="週別継続性")


class AnalyticsError(BaseModel):
    """エラーレスポンス"""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None