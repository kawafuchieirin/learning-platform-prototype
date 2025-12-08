from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any
import json
from collections import defaultdict, Counter

from models.analytics_models import (
    StudySession,
    DailySummary,
    WeeklyAnalytics,
    MonthlyTrend,
    ProductivityMetrics,
    AnalyticsRequest,
    AnalyticsResponse,
    ChartData,
    GoalTracking
)
from services.dynamodb_service import DynamoDBService
from utils.cache import CacheService
from utils.config import settings


class AnalyticsService:
    """Analytics ビジネスロジック"""
    
    def __init__(self):
        self.db_service = DynamoDBService()
        self.cache_service = CacheService() if settings.ENABLE_CACHE else None
    
    async def generate_weekly_analytics(
        self, user_id: str, week_start: Optional[date] = None
    ) -> WeeklyAnalytics:
        """週次分析を生成"""
        
        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=6)
        
        # キャッシュチェック
        cache_key = f"weekly_analytics:{user_id}:{week_start.isoformat()}"
        if self.cache_service:
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                return WeeklyAnalytics(**cached_result)
        
        # 学習データを取得
        study_sessions = await self.db_service.get_study_sessions_by_date_range(
            user_id, week_start, week_end
        )
        
        # 日別サマリーを計算
        daily_summaries = self._calculate_daily_summaries(study_sessions, week_start, week_end)
        
        # 週次統計を計算
        total_duration = sum(session.duration for session in study_sessions)
        top_subjects = self._calculate_top_subjects(study_sessions)
        consistency = self._calculate_study_consistency(daily_summaries)
        
        # 前週比較データを取得
        previous_week_start = week_start - timedelta(days=7)
        previous_week_end = week_start - timedelta(days=1)
        previous_week_data = await self.db_service.get_study_sessions_by_date_range(
            user_id, previous_week_start, previous_week_end
        )
        
        comparison = self._calculate_week_comparison(study_sessions, previous_week_data)
        
        result = WeeklyAnalytics(
            week_start=week_start,
            week_end=week_end,
            total_duration=total_duration,
            daily_summaries=daily_summaries,
            top_subjects=top_subjects,
            study_consistency=consistency,
            comparison_with_previous_week=comparison
        )
        
        # キャッシュに保存
        if self.cache_service:
            await self.cache_service.set(cache_key, result.dict(), ttl=3600)
        
        return result
    
    async def generate_monthly_trends(
        self, user_id: str, months_back: int = 6
    ) -> List[MonthlyTrend]:
        """月次トレンドを生成"""
        
        end_date = date.today().replace(day=1)
        trends = []
        
        for i in range(months_back):
            month_start = end_date - timedelta(days=32 * i)
            month_start = month_start.replace(day=1)
            
            # 次月の1日を取得
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            
            month_end = next_month - timedelta(days=1)
            
            # その月のデータを取得
            study_sessions = await self.db_service.get_study_sessions_by_date_range(
                user_id, month_start, month_end
            )
            
            total_duration = sum(session.duration for session in study_sessions)
            session_count = len(study_sessions)
            
            # 学習した日数を計算
            study_dates = set(session.date for session in study_sessions)
            study_days = len(study_dates)
            
            # 平均日次学習時間
            days_in_month = (month_end - month_start).days + 1
            average_daily_duration = total_duration / days_in_month if days_in_month > 0 else 0
            
            # 継続性スコア（学習日数 / 月の日数 * 100）
            consistency_score = (study_days / days_in_month * 100) if days_in_month > 0 else 0
            
            trend = MonthlyTrend(
                month=month_start.strftime("%Y-%m"),
                total_duration=total_duration,
                session_count=session_count,
                average_daily_duration=round(average_daily_duration, 1),
                study_days=study_days,
                consistency_score=round(consistency_score, 1)
            )
            
            trends.append(trend)
        
        return sorted(trends, key=lambda x: x.month)
    
    async def generate_productivity_metrics(
        self, user_id: str, analysis_period_days: int = 30
    ) -> ProductivityMetrics:
        """生産性メトリクスを生成"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=analysis_period_days)
        
        study_sessions = await self.db_service.get_study_sessions_by_date_range(
            user_id, start_date, end_date
        )
        
        # 時間帯別の分析
        hourly_productivity = defaultdict(int)
        session_durations = []
        daily_productivity = defaultdict(int)
        
        for session in study_sessions:
            # 時間帯別
            if session.start_time:
                hour = session.start_time.hour
                hourly_productivity[hour] += session.duration
            
            # セッション長
            session_durations.append(session.duration)
            
            # 曜日別
            day_of_week = session.date.strftime('%A')
            daily_productivity[day_of_week] += session.duration
        
        # ピーク時間帯（上位3時間）
        peak_hours = sorted(hourly_productivity, key=hourly_productivity.get, reverse=True)[:3]
        
        # 最適セッション長（中央値）
        if session_durations:
            session_durations.sort()
            optimal_session_length = session_durations[len(session_durations) // 2]
        else:
            optimal_session_length = 0
        
        # 最も効果的な曜日（上位3日）
        best_days = sorted(daily_productivity, key=daily_productivity.get, reverse=True)[:3]
        
        # 集中度スコア（平均セッション長から計算）
        if session_durations:
            avg_session_duration = sum(session_durations) / len(session_durations)
            # 45分を100点として正規化
            focus_score = min(100, (avg_session_duration / 45) * 100)
        else:
            focus_score = 0
        
        # 改善提案を生成
        suggestions = self._generate_improvement_suggestions(
            peak_hours, optimal_session_length, len(study_sessions), analysis_period_days
        )
        
        return ProductivityMetrics(
            peak_hours=peak_hours,
            optimal_session_length=optimal_session_length,
            best_study_days=best_days,
            focus_score=round(focus_score, 1),
            improvement_suggestions=suggestions
        )
    
    async def generate_chart_data(
        self, user_id: str, chart_type: str, period_days: int = 30
    ) -> ChartData:
        """グラフデータを生成"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        
        study_sessions = await self.db_service.get_study_sessions_by_date_range(
            user_id, start_date, end_date
        )
        
        if chart_type == "daily_duration":
            return self._generate_daily_duration_chart(study_sessions, start_date, end_date)
        elif chart_type == "subject_distribution":
            return self._generate_subject_distribution_chart(study_sessions)
        elif chart_type == "hourly_distribution":
            return self._generate_hourly_distribution_chart(study_sessions)
        elif chart_type == "weekly_comparison":
            return await self._generate_weekly_comparison_chart(user_id, study_sessions)
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
    
    async def track_goals(self, user_id: str) -> List[GoalTracking]:
        """目標追跡を実行"""
        
        # ユーザーの目標設定を取得
        user_goals = await self.db_service.get_user_goals(user_id)
        if not user_goals:
            return []
        
        today = date.today()
        goal_tracking = []
        
        # 日次目標
        if "daily_target_minutes" in user_goals:
            daily_sessions = await self.db_service.get_study_sessions_by_date_range(
                user_id, today, today
            )
            daily_duration = sum(session.duration for session in daily_sessions)
            
            daily_goal = GoalTracking(
                goal_type="daily",
                target_value=user_goals["daily_target_minutes"],
                current_value=daily_duration,
                achievement_rate=min(100, (daily_duration / user_goals["daily_target_minutes"]) * 100),
                is_achieved=daily_duration >= user_goals["daily_target_minutes"],
                remaining_to_goal=max(0, user_goals["daily_target_minutes"] - daily_duration)
            )
            goal_tracking.append(daily_goal)
        
        # 週次目標
        if "weekly_target_minutes" in user_goals:
            week_start = today - timedelta(days=today.weekday())
            weekly_sessions = await self.db_service.get_study_sessions_by_date_range(
                user_id, week_start, today
            )
            weekly_duration = sum(session.duration for session in weekly_sessions)
            
            weekly_goal = GoalTracking(
                goal_type="weekly",
                target_value=user_goals["weekly_target_minutes"],
                current_value=weekly_duration,
                achievement_rate=min(100, (weekly_duration / user_goals["weekly_target_minutes"]) * 100),
                is_achieved=weekly_duration >= user_goals["weekly_target_minutes"],
                remaining_to_goal=max(0, user_goals["weekly_target_minutes"] - weekly_duration)
            )
            goal_tracking.append(weekly_goal)
        
        return goal_tracking
    
    # プライベートメソッド
    
    def _calculate_daily_summaries(
        self, study_sessions: List[StudySession], week_start: date, week_end: date
    ) -> List[DailySummary]:
        """日別サマリーを計算"""
        
        daily_data = defaultdict(list)
        for session in study_sessions:
            daily_data[session.date].append(session)
        
        summaries = []
        current_date = week_start
        
        while current_date <= week_end:
            day_sessions = daily_data[current_date]
            total_duration = sum(session.duration for session in day_sessions)
            session_count = len(day_sessions)
            subjects = list(set(session.subject for session in day_sessions))
            
            avg_duration = total_duration / session_count if session_count > 0 else 0
            
            summary = DailySummary(
                date=current_date,
                total_duration=total_duration,
                session_count=session_count,
                subjects=subjects,
                average_session_duration=round(avg_duration, 1)
            )
            summaries.append(summary)
            current_date += timedelta(days=1)
        
        return summaries
    
    def _calculate_top_subjects(self, study_sessions: List[StudySession]) -> List[Dict[str, Any]]:
        """トップ科目を計算"""
        
        subject_data = defaultdict(lambda: {"duration": 0, "sessions": 0})
        
        for session in study_sessions:
            subject_data[session.subject]["duration"] += session.duration
            subject_data[session.subject]["sessions"] += 1
        
        total_duration = sum(data["duration"] for data in subject_data.values())
        
        top_subjects = []
        for subject, data in subject_data.items():
            percentage = (data["duration"] / total_duration * 100) if total_duration > 0 else 0
            top_subjects.append({
                "subject": subject,
                "duration": data["duration"],
                "sessions": data["sessions"],
                "percentage": round(percentage, 1)
            })
        
        return sorted(top_subjects, key=lambda x: x["duration"], reverse=True)[:5]
    
    def _calculate_study_consistency(self, daily_summaries: List[DailySummary]) -> float:
        """学習継続性スコアを計算"""
        
        study_days = sum(1 for summary in daily_summaries if summary.total_duration > 0)
        total_days = len(daily_summaries)
        
        if total_days == 0:
            return 0.0
        
        # 基本継続性（学習日数の割合）
        base_consistency = (study_days / total_days) * 100
        
        # 学習時間の均等性も考慮
        durations = [summary.total_duration for summary in daily_summaries if summary.total_duration > 0]
        if len(durations) > 1:
            avg_duration = sum(durations) / len(durations)
            variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
            cv = (variance ** 0.5) / avg_duration if avg_duration > 0 else 0
            # 変動係数が低いほど安定（0.5以下で高評価）
            stability_bonus = max(0, (0.5 - cv) * 20) if cv < 0.5 else 0
        else:
            stability_bonus = 0
        
        return min(100, base_consistency + stability_bonus)
    
    def _calculate_week_comparison(
        self, current_sessions: List[StudySession], previous_sessions: List[StudySession]
    ) -> Dict[str, Any]:
        """週比較データを計算"""
        
        current_duration = sum(session.duration for session in current_sessions)
        previous_duration = sum(session.duration for session in previous_sessions)
        
        current_session_count = len(current_sessions)
        previous_session_count = len(previous_sessions)
        
        duration_change = current_duration - previous_duration
        session_change = current_session_count - previous_session_count
        
        duration_change_pct = (
            (duration_change / previous_duration * 100) 
            if previous_duration > 0 else 0
        )
        
        return {
            "duration_change": duration_change,
            "duration_change_percentage": round(duration_change_pct, 1),
            "session_change": session_change,
            "trend": "improving" if duration_change > 0 else "declining" if duration_change < 0 else "stable"
        }
    
    def _generate_improvement_suggestions(
        self, peak_hours: List[int], optimal_session_length: int, 
        total_sessions: int, period_days: int
    ) -> List[str]:
        """改善提案を生成"""
        
        suggestions = []
        
        # セッション長に関する提案
        if optimal_session_length < 25:
            suggestions.append("セッション時間を25-45分に延ばすことで、より深い集中状態を得られます")
        elif optimal_session_length > 60:
            suggestions.append("セッション時間を45-60分に調整し、適度な休憩を挟むことをお勧めします")
        
        # 学習頻度に関する提案
        avg_sessions_per_day = total_sessions / period_days
        if avg_sessions_per_day < 0.5:
            suggestions.append("学習頻度を上げて、継続的な学習習慣を身につけましょう")
        
        # 時間帯に関する提案
        if peak_hours and min(peak_hours) >= 20:
            suggestions.append("午前中や午後の早い時間帯での学習も試してみてください")
        
        if not suggestions:
            suggestions.append("現在の学習パターンを維持し、継続的な改善を心がけましょう")
        
        return suggestions
    
    def _generate_daily_duration_chart(
        self, study_sessions: List[StudySession], start_date: date, end_date: date
    ) -> ChartData:
        """日別学習時間グラフを生成"""
        
        daily_durations = defaultdict(int)
        for session in study_sessions:
            daily_durations[session.date] += session.duration
        
        data_points = []
        current_date = start_date
        
        while current_date <= end_date:
            duration_hours = daily_durations[current_date] / 60.0
            data_points.append({
                "x": current_date.isoformat(),
                "y": duration_hours,
                "label": f"{daily_durations[current_date]}分"
            })
            current_date += timedelta(days=1)
        
        return ChartData(
            chart_type="line",
            title="日別学習時間",
            x_axis_label="日付",
            y_axis_label="学習時間（時間）",
            data_points=data_points
        )
    
    def _generate_subject_distribution_chart(self, study_sessions: List[StudySession]) -> ChartData:
        """科目別分布グラフを生成"""
        
        subject_durations = defaultdict(int)
        for session in study_sessions:
            subject_durations[session.subject] += session.duration
        
        total_duration = sum(subject_durations.values())
        data_points = []
        
        for subject, duration in subject_durations.items():
            percentage = (duration / total_duration * 100) if total_duration > 0 else 0
            data_points.append({
                "x": subject,
                "y": percentage,
                "value": duration,
                "label": f"{duration}分 ({percentage:.1f}%)"
            })
        
        return ChartData(
            chart_type="pie",
            title="科目別学習時間分布",
            x_axis_label="科目",
            y_axis_label="割合（%）",
            data_points=sorted(data_points, key=lambda x: x["value"], reverse=True)
        )
    
    def _generate_hourly_distribution_chart(self, study_sessions: List[StudySession]) -> ChartData:
        """時間帯別分布グラフを生成"""
        
        hourly_durations = defaultdict(int)
        for session in study_sessions:
            if session.start_time:
                hour = session.start_time.hour
                hourly_durations[hour] += session.duration
        
        data_points = []
        for hour in range(24):
            duration = hourly_durations[hour]
            data_points.append({
                "x": f"{hour:02d}:00",
                "y": duration,
                "label": f"{duration}分"
            })
        
        return ChartData(
            chart_type="bar",
            title="時間帯別学習分布",
            x_axis_label="時間",
            y_axis_label="学習時間（分）",
            data_points=data_points
        )
    
    async def _generate_weekly_comparison_chart(
        self, user_id: str, current_sessions: List[StudySession]
    ) -> ChartData:
        """週次比較グラフを生成"""
        
        # 過去4週間のデータを取得
        weeks_data = []
        today = date.today()
        
        for i in range(4):
            week_start = today - timedelta(days=today.weekday() + (7 * i))
            week_end = week_start + timedelta(days=6)
            
            if i == 0:
                sessions = current_sessions
            else:
                sessions = await self.db_service.get_study_sessions_by_date_range(
                    user_id, week_start, week_end
                )
            
            total_duration = sum(session.duration for session in sessions)
            weeks_data.append({
                "week_label": f"{week_start.strftime('%m/%d')}週",
                "duration": total_duration
            })
        
        weeks_data.reverse()  # 古い週から新しい週の順に
        
        data_points = []
        for week_data in weeks_data:
            data_points.append({
                "x": week_data["week_label"],
                "y": week_data["duration"] / 60.0,  # 時間単位
                "label": f"{week_data['duration']}分"
            })
        
        return ChartData(
            chart_type="bar",
            title="週次学習時間比較",
            x_axis_label="週",
            y_axis_label="学習時間（時間）",
            data_points=data_points
        )