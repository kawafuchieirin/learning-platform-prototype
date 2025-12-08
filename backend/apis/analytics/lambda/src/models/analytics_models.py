from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StudySession(BaseModel):
    """学習セッション"""
    session_id: str
    user_id: str
    date: date
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: int = Field(description="学習時間（分）")
    subject: str = Field(description="学習科目")
    session_type: str = Field(description="セッション種別（timer/record）")


class DailySummary(BaseModel):
    """日別サマリー"""
    date: date
    total_duration: int = Field(description="合計学習時間（分）")
    session_count: int = Field(description="セッション数")
    subjects: List[str] = Field(description="学習した科目")
    average_session_duration: float = Field(description="平均セッション時間（分）")


class WeeklyAnalytics(BaseModel):
    """週次分析結果"""
    week_start: date
    week_end: date
    total_duration: int
    daily_summaries: List[DailySummary]
    top_subjects: List[Dict[str, Any]]
    study_consistency: float = Field(description="学習継続性スコア（0-100）")
    comparison_with_previous_week: Optional[Dict[str, Any]] = None


class MonthlyTrend(BaseModel):
    """月次トレンド"""
    month: str = Field(description="YYYY-MM形式")
    total_duration: int
    session_count: int
    average_daily_duration: float
    study_days: int
    consistency_score: float


class ProductivityMetrics(BaseModel):
    """生産性メトリクス"""
    peak_hours: List[int] = Field(description="最も生産的な時間帯")
    optimal_session_length: int = Field(description="最適なセッション長（分）")
    best_study_days: List[str] = Field(description="最も効果的な曜日")
    focus_score: float = Field(description="集中度スコア（0-100）")
    improvement_suggestions: List[str] = Field(description="改善提案")


class AnalyticsRequest(BaseModel):
    """分析リクエスト"""
    user_id: str
    analysis_type: str = Field(description="分析タイプ（weekly/monthly/custom）")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    filters: Optional[Dict[str, Any]] = None


class AnalyticsResponse(BaseModel):
    """分析レスポンス"""
    request_id: str
    user_id: str
    analysis_type: str
    generated_at: datetime
    data: Dict[str, Any]
    cache_hit: bool = False


class ChartData(BaseModel):
    """グラフデータ"""
    chart_type: str = Field(description="グラフタイプ（line/bar/pie）")
    title: str
    x_axis_label: str
    y_axis_label: str
    data_points: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class GoalTracking(BaseModel):
    """目標追跡"""
    goal_type: str = Field(description="目標タイプ（daily/weekly/monthly）")
    target_value: float
    current_value: float
    achievement_rate: float = Field(description="達成率（0-100）")
    is_achieved: bool
    remaining_to_goal: float


class AnalyticsError(BaseModel):
    """エラーレスポンス"""
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class CacheInfo(BaseModel):
    """キャッシュ情報"""
    cache_key: str
    ttl: int
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0