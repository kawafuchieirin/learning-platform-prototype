from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path
import json

from models.analytics_models import (
    WeeklyAnalytics,
    MonthlyTrend,
    ProductivityMetrics,
    AnalyticsRequest,
    AnalyticsResponse,
    ChartData,
    GoalTracking,
    AnalyticsError
)
from services.analytics_service import AnalyticsService
from utils.auth import extract_user_id_from_event, AuthError, validate_user_access

router = APIRouter()
analytics_service = AnalyticsService()


@router.get("/weekly")
async def get_weekly_analytics(
    week_start: Optional[str] = Query(None, description="週の開始日 (YYYY-MM-DD)")
):
    """週次分析データを取得"""
    
    try:
        # 開発環境用の簡単なユーザーID取得
        user_id = "test-user-1"  # 実際はAuthorizationヘッダーから取得
        
        # 日付パラメータの処理
        if week_start:
            try:
                week_start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="無効な日付形式です (YYYY-MM-DD)")
        else:
            week_start_date = None
        
        # 週次分析を実行
        result = await analytics_service.generate_weekly_analytics(user_id, week_start_date)
        
        return {
            "status": "success",
            "data": result.dict(),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"週次分析エラー: {str(e)}")


@router.get("/monthly-trends")
async def get_monthly_trends(
    months: int = Query(6, description="取得する月数", ge=1, le=12)
):
    """月次トレンドデータを取得"""
    
    try:
        user_id = "test-user-1"
        
        trends = await analytics_service.generate_monthly_trends(user_id, months)
        
        return {
            "status": "success",
            "data": [trend.dict() for trend in trends],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"月次トレンド取得エラー: {str(e)}")


@router.get("/productivity")
async def get_productivity_metrics(
    period_days: int = Query(30, description="分析期間（日数）", ge=7, le=365)
):
    """生産性メトリクスを取得"""
    
    try:
        user_id = "test-user-1"
        
        metrics = await analytics_service.generate_productivity_metrics(user_id, period_days)
        
        return {
            "status": "success",
            "data": metrics.dict(),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生産性メトリクス取得エラー: {str(e)}")


@router.get("/charts/{chart_type}")
async def get_chart_data(
    chart_type: str = Path(..., description="グラフタイプ"),
    period_days: int = Query(30, description="期間（日数）", ge=1, le=365)
):
    """グラフデータを取得"""
    
    try:
        user_id = "test-user-1"
        
        valid_chart_types = [
            "daily_duration", "subject_distribution", 
            "hourly_distribution", "weekly_comparison"
        ]
        
        if chart_type not in valid_chart_types:
            raise HTTPException(
                status_code=400, 
                detail=f"無効なグラフタイプです。利用可能: {valid_chart_types}"
            )
        
        chart_data = await analytics_service.generate_chart_data(user_id, chart_type, period_days)
        
        return {
            "status": "success",
            "data": chart_data.dict(),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"グラフデータ取得エラー: {str(e)}")


@router.get("/goals")
async def get_goal_tracking():
    """目標追跡データを取得"""
    
    try:
        user_id = "test-user-1"
        
        goals = await analytics_service.track_goals(user_id)
        
        return {
            "status": "success",
            "data": [goal.dict() for goal in goals],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"目標追跡取得エラー: {str(e)}")


@router.post("/analyze")
async def analyze_custom(request: AnalyticsRequest):
    """カスタム分析を実行"""
    
    try:
        user_id = request.user_id
        
        # ユーザー権限チェック
        if not validate_user_access(user_id):
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        # 分析タイプに応じて処理を分岐
        if request.analysis_type == "weekly":
            result = await analytics_service.generate_weekly_analytics(
                user_id, request.start_date
            )
            data = result.dict()
            
        elif request.analysis_type == "monthly":
            if request.start_date and request.end_date:
                # カスタム期間の月次分析
                months_diff = (request.end_date.year - request.start_date.year) * 12 + \
                             (request.end_date.month - request.start_date.month)
                months_diff = max(1, min(12, months_diff + 1))
            else:
                months_diff = 6
                
            trends = await analytics_service.generate_monthly_trends(user_id, months_diff)
            data = [trend.dict() for trend in trends]
            
        elif request.analysis_type == "productivity":
            if request.start_date and request.end_date:
                period_days = (request.end_date - request.start_date).days + 1
            else:
                period_days = 30
                
            metrics = await analytics_service.generate_productivity_metrics(user_id, period_days)
            data = metrics.dict()
            
        else:
            raise HTTPException(status_code=400, detail="無効な分析タイプです")
        
        response = AnalyticsResponse(
            request_id=f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            user_id=user_id,
            analysis_type=request.analysis_type,
            generated_at=datetime.utcnow(),
            data=data
        )
        
        return {
            "status": "success",
            "analytics": response.dict()
        }
        
    except HTTPException:
        raise
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"カスタム分析エラー: {str(e)}")


@router.get("/summary")
async def get_analytics_summary(
    period_days: int = Query(30, description="集計期間（日数）", ge=1, le=365)
):
    """分析サマリーを取得"""
    
    try:
        user_id = "test-user-1"
        
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        
        # 基本統計を計算
        from services.dynamodb_service import DynamoDBService
        db_service = DynamoDBService()
        
        study_sessions = await db_service.get_study_sessions_by_date_range(
            user_id, start_date, end_date
        )
        
        total_duration = sum(session.duration for session in study_sessions)
        total_sessions = len(study_sessions)
        
        # 学習日数
        study_dates = set(session.date for session in study_sessions)
        study_days = len(study_dates)
        
        # 平均学習時間
        avg_daily_minutes = total_duration / period_days if period_days > 0 else 0
        avg_session_minutes = total_duration / total_sessions if total_sessions > 0 else 0
        
        # 連続学習日数
        streak_data = await db_service.get_study_streak_data(user_id)
        
        # 科目別統計
        subject_stats = {}
        for session in study_sessions:
            subject = session.subject
            if subject not in subject_stats:
                subject_stats[subject] = {"duration": 0, "sessions": 0}
            subject_stats[subject]["duration"] += session.duration
            subject_stats[subject]["sessions"] += 1
        
        # トップ科目
        top_subjects = sorted(
            subject_stats.items(), 
            key=lambda x: x[1]["duration"], 
            reverse=True
        )[:3]
        
        summary = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": period_days
            },
            "totals": {
                "study_time_minutes": total_duration,
                "study_time_hours": round(total_duration / 60, 1),
                "sessions": total_sessions,
                "study_days": study_days
            },
            "averages": {
                "daily_minutes": round(avg_daily_minutes, 1),
                "session_minutes": round(avg_session_minutes, 1)
            },
            "streaks": {
                "current": streak_data.get("current_streak", 0),
                "longest": streak_data.get("longest_streak", 0)
            },
            "top_subjects": [
                {
                    "subject": subject,
                    "duration": stats["duration"],
                    "sessions": stats["sessions"],
                    "percentage": round((stats["duration"] / total_duration) * 100, 1) if total_duration > 0 else 0
                }
                for subject, stats in top_subjects
            ],
            "consistency_score": round((study_days / period_days) * 100, 1) if period_days > 0 else 0
        }
        
        return {
            "status": "success",
            "data": summary,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サマリー取得エラー: {str(e)}")


# Lambda 関数用のダイレクトハンドラー

async def lambda_handler(event: dict, context: dict) -> dict:
    """Lambda 直接実行用のハンドラー"""
    
    try:
        # イベントからパスとHTTPメソッドを取得
        http_method = event.get("httpMethod", "GET")
        path = event.get("path", "")
        query_params = event.get("queryStringParameters") or {}
        
        # ユーザー認証
        try:
            user_id = extract_user_id_from_event(event)
        except AuthError as e:
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)})
            }
        
        # パスルーティング
        if path.endswith("/weekly") and http_method == "GET":
            week_start = query_params.get("week_start")
            result = await analytics_service.generate_weekly_analytics(
                user_id, 
                datetime.strptime(week_start, "%Y-%m-%d").date() if week_start else None
            )
            
        elif path.endswith("/summary") and http_method == "GET":
            period_days = int(query_params.get("period_days", 30))
            # サマリー生成ロジック（上記のget_analytics_summaryと同様）
            result = {"message": "Summary endpoint"}  # 簡略化
            
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "エンドポイントが見つかりません"})
            }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": "success",
                "data": result.dict() if hasattr(result, 'dict') else result
            }, default=str)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"内部エラー: {str(e)}"})
        }