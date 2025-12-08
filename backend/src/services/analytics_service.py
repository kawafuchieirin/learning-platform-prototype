from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import csv
from collections import defaultdict, Counter

from src.models.analytics import (
    WeeklyReportResponse,
    DetailedAnalyticsResponse,
    AnalyticsSummary,
    WeeklyStats,
    ComparisonStats,
    SubjectStats,
    ChartDataPoint,
    StudySessionSummary,
    MonthlyTrend,
    GoalProgress,
    ProductivityInsight,
    AnalyticsQueryParams
)
from src.services.dynamodb_service import DynamoDBService


class AnalyticsService:
    """Analytics サービス - 学習データ分析のビジネスロジック"""
    
    def __init__(self):
        self.db_service = DynamoDBService()
    
    async def generate_weekly_report(self, user_id: str, week_start: date) -> WeeklyReportResponse:
        """週次レポートを生成"""
        week_end = week_start + timedelta(days=6)
        
        # 今週のデータを取得
        current_week_data = await self._get_study_data_for_period(user_id, week_start, week_end)
        
        # 先週のデータを取得（比較用）
        prev_week_start = week_start - timedelta(days=7)
        prev_week_end = week_start - timedelta(days=1)
        previous_week_data = await self._get_study_data_for_period(user_id, prev_week_start, prev_week_end)
        
        # 累計サマリーを生成
        summary = await self.get_analytics_summary(user_id, week_start, week_end)
        
        # 週次統計を生成
        weekly_stats = self._calculate_weekly_stats(current_week_data, week_start, week_end)
        
        # 比較データを生成
        comparison = self._calculate_comparison_stats(current_week_data, previous_week_data)
        
        # 科目別統計を生成
        subject_breakdown = self._calculate_subject_breakdown(current_week_data)
        
        # グラフ用データを生成
        daily_chart_data = self._generate_daily_chart_data(current_week_data, week_start, week_end)
        subject_chart_data = self._generate_subject_chart_data(subject_breakdown)
        
        return WeeklyReportResponse(
            summary=summary,
            weekly_stats=weekly_stats,
            comparison=comparison,
            subject_breakdown=subject_breakdown,
            daily_chart_data=daily_chart_data,
            subject_chart_data=subject_chart_data
        )
    
    async def get_analytics_summary(
        self, user_id: str, start_date: date, end_date: date
    ) -> AnalyticsSummary:
        """分析サマリーを取得"""
        # 指定期間のデータを取得
        study_data = await self._get_study_data_for_period(user_id, start_date, end_date)
        
        # 全期間のデータを取得（連続日数計算用）
        all_data = await self._get_all_study_data(user_id)
        
        # 基本統計計算
        total_study_time = sum(session.get('duration', 0) for session in study_data)
        total_sessions = len(study_data)
        
        # 連続学習日数を計算
        current_streak, longest_streak = self._calculate_streaks(all_data)
        
        # 平均日次学習時間を計算
        period_days = (end_date - start_date).days + 1
        average_daily_study = total_study_time / period_days if period_days > 0 else 0
        
        # 最も生産性の高い時間帯を計算
        most_productive_hour = self._find_most_productive_hour(study_data)
        
        return AnalyticsSummary(
            total_study_time=total_study_time,
            total_sessions=total_sessions,
            current_streak=current_streak,
            longest_streak=longest_streak,
            average_daily_study=round(average_daily_study, 1),
            most_productive_hour=most_productive_hour
        )
    
    async def get_comparison_data(self, user_id: str, period: str) -> dict:
        """前期間比較データを取得"""
        if period == "week":
            return await self._get_weekly_comparison(user_id)
        elif period == "month":
            return await self._get_monthly_comparison(user_id)
        else:
            raise ValueError("期間は 'week' または 'month' を指定してください")
    
    async def get_detailed_analytics(self, params: AnalyticsQueryParams) -> DetailedAnalyticsResponse:
        """詳細分析データを取得"""
        # 期間サマリー
        period_summary = await self.get_analytics_summary(
            params.user_id, params.start_date, params.end_date
        )
        
        # 学習データを取得
        study_data = await self._get_study_data_for_period(
            params.user_id, params.start_date, params.end_date
        )
        
        # 科目フィルターを適用
        if params.subject:
            study_data = [s for s in study_data if s.get('subject') == params.subject]
        
        # 生産性インサイト
        productivity_insights = self._calculate_productivity_insights(study_data)
        
        # 月次トレンド
        monthly_trends = await self._calculate_monthly_trends(
            params.user_id, params.start_date, params.end_date
        )
        
        # 時間帯別分布
        hourly_distribution = self._calculate_hourly_distribution(study_data)
        
        # 週別継続性
        weekly_consistency = self._calculate_weekly_consistency(
            study_data, params.start_date, params.end_date
        )
        
        return DetailedAnalyticsResponse(
            period_summary=period_summary,
            productivity_insights=productivity_insights,
            monthly_trends=monthly_trends,
            hourly_distribution=hourly_distribution,
            weekly_consistency=weekly_consistency
        )
    
    async def get_daily_chart_data(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[ChartDataPoint]:
        """日別学習時間のグラフデータを取得"""
        study_data = await self._get_study_data_for_period(user_id, start_date, end_date)
        return self._generate_daily_chart_data(study_data, start_date, end_date)
    
    async def get_subject_chart_data(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[ChartDataPoint]:
        """科目別学習時間のグラフデータを取得"""
        study_data = await self._get_study_data_for_period(user_id, start_date, end_date)
        subject_breakdown = self._calculate_subject_breakdown(study_data)
        return self._generate_subject_chart_data(subject_breakdown)
    
    async def get_hourly_distribution(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[ChartDataPoint]:
        """時間帯別学習分布を取得"""
        study_data = await self._get_study_data_for_period(user_id, start_date, end_date)
        return self._calculate_hourly_distribution(study_data)
    
    async def get_study_streaks(self, user_id: str) -> dict:
        """学習継続データを取得"""
        all_data = await self._get_all_study_data(user_id)
        current_streak, longest_streak = self._calculate_streaks(all_data)
        
        # 最近の学習日を取得
        recent_study_dates = self._get_recent_study_dates(all_data, 30)
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "recent_study_dates": recent_study_dates,
            "total_study_days": len(set(s.get('date') for s in all_data if s.get('date')))
        }
    
    async def get_productivity_insights(
        self, user_id: str, start_date: date, end_date: date
    ) -> ProductivityInsight:
        """生産性インサイトを取得"""
        study_data = await self._get_study_data_for_period(user_id, start_date, end_date)
        return self._calculate_productivity_insights(study_data)
    
    async def export_analytics_data(
        self, user_id: str, start_date: date, end_date: date, format: str
    ) -> dict:
        """分析データをエクスポート"""
        study_data = await self._get_study_data_for_period(user_id, start_date, end_date)
        
        if format == "json":
            return {"data": study_data}
        elif format == "csv":
            # CSVファイルを生成してS3にアップロード（実装簡略化のため、ここではURLを返す）
            csv_url = await self._generate_csv_export(study_data, user_id)
            return csv_url
        else:
            raise ValueError("サポートされていない形式です")
    
    # プライベートメソッド
    
    async def _get_study_data_for_period(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[dict]:
        """指定期間の学習データを取得"""
        # DynamoDBから学習記録とタイマーデータを取得
        records = await self.db_service.get_records_by_date_range(user_id, start_date, end_date)
        timer_data = await self.db_service.get_timer_data_by_date_range(user_id, start_date, end_date)
        
        # データを統合して返す
        combined_data = []
        combined_data.extend(records)
        combined_data.extend(timer_data)
        
        return combined_data
    
    async def _get_all_study_data(self, user_id: str) -> List[dict]:
        """全ての学習データを取得"""
        return await self.db_service.get_all_study_data(user_id)
    
    def _calculate_weekly_stats(
        self, study_data: List[dict], week_start: date, week_end: date
    ) -> WeeklyStats:
        """週次統計を計算"""
        # 日別にグループ化
        daily_data = defaultdict(list)
        for session in study_data:
            session_date = session.get('date')
            if session_date:
                daily_data[session_date].append(session)
        
        # 日別サマリーを作成
        daily_sessions = []
        total_duration = 0
        all_subjects = set()
        
        current_date = week_start
        while current_date <= week_end:
            date_str = current_date.isoformat()
            day_sessions = daily_data.get(date_str, [])
            day_duration = sum(s.get('duration', 0) for s in day_sessions)
            day_subjects = list(set(s.get('subject', 'その他') for s in day_sessions))
            
            daily_sessions.append(StudySessionSummary(
                date=current_date,
                total_duration=day_duration,
                session_count=len(day_sessions),
                subjects=day_subjects
            ))
            
            total_duration += day_duration
            all_subjects.update(day_subjects)
            current_date += timedelta(days=1)
        
        # 統計計算
        total_sessions = len(study_data)
        average_session_duration = total_duration / total_sessions if total_sessions > 0 else 0
        
        # 最も学習した科目
        subject_durations = defaultdict(int)
        for session in study_data:
            subject = session.get('subject', 'その他')
            subject_durations[subject] += session.get('duration', 0)
        
        most_studied_subject = max(subject_durations, key=subject_durations.get) if subject_durations else None
        
        # 学習した日数
        study_days = len([d for d in daily_sessions if d.total_duration > 0])
        
        return WeeklyStats(
            week_start=week_start,
            week_end=week_end,
            total_duration=total_duration,
            daily_sessions=daily_sessions,
            average_session_duration=round(average_session_duration, 1),
            most_studied_subject=most_studied_subject,
            study_days=study_days
        )
    
    def _calculate_comparison_stats(
        self, current_data: List[dict], previous_data: List[dict]
    ) -> ComparisonStats:
        """比較統計を計算"""
        current_duration = sum(s.get('duration', 0) for s in current_data)
        previous_duration = sum(s.get('duration', 0) for s in previous_data)
        
        duration_change = current_duration - previous_duration
        duration_change_percentage = (
            (duration_change / previous_duration * 100) if previous_duration > 0 else 0
        )
        
        current_sessions = len(current_data)
        previous_sessions = len(previous_data)
        session_change = current_sessions - previous_sessions
        
        return ComparisonStats(
            current_week_duration=current_duration,
            previous_week_duration=previous_duration,
            duration_change=duration_change,
            duration_change_percentage=round(duration_change_percentage, 1),
            current_week_sessions=current_sessions,
            previous_week_sessions=previous_sessions,
            session_change=session_change
        )
    
    def _calculate_subject_breakdown(self, study_data: List[dict]) -> List[SubjectStats]:
        """科目別統計を計算"""
        subject_data = defaultdict(lambda: {'duration': 0, 'sessions': 0})
        total_duration = 0
        
        for session in study_data:
            subject = session.get('subject', 'その他')
            duration = session.get('duration', 0)
            
            subject_data[subject]['duration'] += duration
            subject_data[subject]['sessions'] += 1
            total_duration += duration
        
        breakdown = []
        for subject, data in subject_data.items():
            percentage = (data['duration'] / total_duration * 100) if total_duration > 0 else 0
            breakdown.append(SubjectStats(
                subject=subject,
                duration=data['duration'],
                session_count=data['sessions'],
                percentage=round(percentage, 1)
            ))
        
        # 学習時間でソート
        return sorted(breakdown, key=lambda x: x.duration, reverse=True)
    
    def _generate_daily_chart_data(
        self, study_data: List[dict], start_date: date, end_date: date
    ) -> List[ChartDataPoint]:
        """日別グラフデータを生成"""
        daily_durations = defaultdict(int)
        
        for session in study_data:
            session_date = session.get('date')
            if session_date:
                daily_durations[session_date] += session.get('duration', 0)
        
        chart_data = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            duration = daily_durations.get(date_str, 0)
            
            chart_data.append(ChartDataPoint(
                date=date_str,
                value=duration / 60.0,  # 時間単位に変換
                label=f"{duration // 60}h {duration % 60}m" if duration > 0 else "0m"
            ))
            current_date += timedelta(days=1)
        
        return chart_data
    
    def _generate_subject_chart_data(self, subject_breakdown: List[SubjectStats]) -> List[ChartDataPoint]:
        """科目別グラフデータを生成"""
        return [
            ChartDataPoint(
                date=stat.subject,
                value=stat.duration / 60.0,  # 時間単位に変換
                label=f"{stat.duration // 60}h {stat.duration % 60}m"
            )
            for stat in subject_breakdown
        ]
    
    def _calculate_streaks(self, study_data: List[dict]) -> Tuple[int, int]:
        """連続学習日数を計算"""
        if not study_data:
            return 0, 0
        
        # 学習した日付を取得してソート
        study_dates = sorted(set(
            datetime.strptime(s.get('date'), '%Y-%m-%d').date()
            for s in study_data
            if s.get('date')
        ))
        
        if not study_dates:
            return 0, 0
        
        current_streak = 0
        longest_streak = 0
        temp_streak = 1
        
        # 今日から逆算して現在の連続日数を計算
        today = date.today()
        if today in study_dates or (today - timedelta(days=1)) in study_dates:
            current_streak = 1
            check_date = today - timedelta(days=1)
            while check_date in study_dates:
                current_streak += 1
                check_date -= timedelta(days=1)
        
        # 最長連続日数を計算
        for i in range(1, len(study_dates)):
            if study_dates[i] - study_dates[i-1] == timedelta(days=1):
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
        
        longest_streak = max(longest_streak, temp_streak)
        
        return current_streak, longest_streak
    
    def _find_most_productive_hour(self, study_data: List[dict]) -> Optional[int]:
        """最も生産性の高い時間帯を見つける"""
        hourly_durations = defaultdict(int)
        
        for session in study_data:
            start_time = session.get('start_time')
            duration = session.get('duration', 0)
            
            if start_time and duration > 0:
                try:
                    # ISO形式の時刻から時間を抽出
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    hour = dt.hour
                    hourly_durations[hour] += duration
                except:
                    continue
        
        if not hourly_durations:
            return None
        
        return max(hourly_durations, key=hourly_durations.get)
    
    def _calculate_productivity_insights(self, study_data: List[dict]) -> ProductivityInsight:
        """生産性インサイトを計算"""
        # ピーク時間帯（上位3時間）
        hourly_durations = defaultdict(int)
        session_lengths = []
        daily_durations = defaultdict(int)
        
        for session in study_data:
            duration = session.get('duration', 0)
            start_time = session.get('start_time')
            date = session.get('date')
            
            session_lengths.append(duration)
            
            if date:
                daily_durations[date] += duration
            
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    hourly_durations[dt.hour] += duration
                except:
                    continue
        
        # ピーク時間帯
        peak_hours = sorted(hourly_durations, key=hourly_durations.get, reverse=True)[:3]
        
        # 好ましいセッション長（中央値）
        preferred_session_length = int(sorted(session_lengths)[len(session_lengths)//2]) if session_lengths else 0
        
        # 最も生産的な曜日（仮実装）
        most_productive_days = ["月曜日", "火曜日", "水曜日"]  # 実際は曜日別分析が必要
        
        # 継続性スコア（簡単な計算）
        total_days = len(set(s.get('date') for s in study_data if s.get('date')))
        consistency_score = min(100, total_days * 5)  # 仮の計算
        
        # 改善提案
        recommendations = []
        if len(study_data) > 0:
            avg_duration = sum(s.get('duration', 0) for s in study_data) / len(study_data)
            if avg_duration < 30:
                recommendations.append("セッション時間を長めに設定することをお勧めします")
            if total_days < 5:
                recommendations.append("継続的な学習習慣を身につけましょう")
        
        return ProductivityInsight(
            peak_hours=peak_hours,
            preferred_session_length=preferred_session_length,
            most_productive_days=most_productive_days,
            study_consistency_score=float(consistency_score),
            recommendations=recommendations
        )
    
    async def _calculate_monthly_trends(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[MonthlyTrend]:
        """月次トレンドを計算"""
        # 簡単な実装（実際はより詳細な月別分析が必要）
        trends = []
        current_month = start_date.replace(day=1)
        
        while current_month <= end_date:
            next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
            month_end = next_month - timedelta(days=1)
            
            month_data = await self._get_study_data_for_period(user_id, current_month, month_end)
            total_duration = sum(s.get('duration', 0) for s in month_data)
            session_count = len(month_data)
            
            days_in_month = (month_end - current_month).days + 1
            average_daily = total_duration / days_in_month
            
            trends.append(MonthlyTrend(
                month=current_month.strftime("%Y-%m"),
                total_duration=total_duration,
                session_count=session_count,
                average_daily=round(average_daily, 1)
            ))
            
            current_month = next_month
        
        return trends
    
    def _calculate_hourly_distribution(self, study_data: List[dict]) -> List[ChartDataPoint]:
        """時間帯別分布を計算"""
        hourly_durations = defaultdict(int)
        
        for session in study_data:
            start_time = session.get('start_time')
            duration = session.get('duration', 0)
            
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    hourly_durations[dt.hour] += duration
                except:
                    continue
        
        chart_data = []
        for hour in range(24):
            duration = hourly_durations.get(hour, 0)
            chart_data.append(ChartDataPoint(
                date=f"{hour:02d}:00",
                value=duration / 60.0,  # 時間単位に変換
                label=f"{duration // 60}h {duration % 60}m" if duration > 0 else "0m"
            ))
        
        return chart_data
    
    def _calculate_weekly_consistency(
        self, study_data: List[dict], start_date: date, end_date: date
    ) -> List[ChartDataPoint]:
        """週別継続性を計算"""
        # 週別にデータを集計
        weekly_data = defaultdict(int)
        
        for session in study_data:
            session_date_str = session.get('date')
            if session_date_str:
                try:
                    session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
                    # その週の月曜日を取得
                    week_start = session_date - timedelta(days=session_date.weekday())
                    weekly_data[week_start] += session.get('duration', 0)
                except:
                    continue
        
        chart_data = []
        current_week = start_date - timedelta(days=start_date.weekday())
        end_week = end_date - timedelta(days=end_date.weekday())
        
        while current_week <= end_week:
            duration = weekly_data.get(current_week, 0)
            chart_data.append(ChartDataPoint(
                date=current_week.isoformat(),
                value=duration / 60.0,  # 時間単位に変換
                label=f"Week of {current_week.strftime('%m/%d')}"
            ))
            current_week += timedelta(days=7)
        
        return chart_data
    
    async def _get_weekly_comparison(self, user_id: str) -> dict:
        """週次比較データを取得"""
        today = date.today()
        this_week_start = today - timedelta(days=today.weekday())
        this_week_end = this_week_start + timedelta(days=6)
        
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(days=1)
        
        this_week_data = await self._get_study_data_for_period(user_id, this_week_start, this_week_end)
        last_week_data = await self._get_study_data_for_period(user_id, last_week_start, last_week_end)
        
        return self._calculate_comparison_stats(this_week_data, last_week_data).dict()
    
    async def _get_monthly_comparison(self, user_id: str) -> dict:
        """月次比較データを取得"""
        today = date.today()
        this_month_start = today.replace(day=1)
        
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        this_month_data = await self._get_study_data_for_period(user_id, this_month_start, today)
        last_month_data = await self._get_study_data_for_period(user_id, last_month_start, last_month_end)
        
        return self._calculate_comparison_stats(this_month_data, last_month_data).dict()
    
    def _get_recent_study_dates(self, study_data: List[dict], days: int) -> List[str]:
        """最近の学習日を取得"""
        cutoff_date = date.today() - timedelta(days=days)
        
        recent_dates = set()
        for session in study_data:
            session_date_str = session.get('date')
            if session_date_str:
                try:
                    session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
                    if session_date >= cutoff_date:
                        recent_dates.add(session_date_str)
                except:
                    continue
        
        return sorted(list(recent_dates))
    
    async def _generate_csv_export(self, study_data: List[dict], user_id: str) -> str:
        """CSV エクスポートファイルを生成"""
        # 実際の実装ではS3にアップロードして署名付きURLを返す
        # ここでは簡略化してダミーURLを返す
        return f"https://example.com/exports/{user_id}/analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"