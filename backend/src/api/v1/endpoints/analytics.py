from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from src.models.analytics import (
    WeeklyReportResponse,
    DetailedAnalyticsResponse,
    AnalyticsSummary,
    AnalyticsError,
    AnalyticsQueryParams
)
from src.services.analytics_service import AnalyticsService
from src.core.auth import get_current_user

router = APIRouter()


def get_analytics_service() -> AnalyticsService:
    """Analytics サービスの依存性注入"""
    return AnalyticsService()


@router.get("/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    week_start: Optional[date] = Query(None, description="週の開始日（月曜日）。未指定の場合は今週"),
    user_id: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    週次レポートを取得
    
    - 指定された週の学習データを分析
    - 前週との比較データを含む
    - グラフ表示用のデータも提供
    """
    try:
        if week_start is None:
            # 今週の月曜日を取得
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        report = await analytics_service.generate_weekly_report(user_id, week_start)
        return report
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"週次レポート生成エラー: {str(e)}")


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    start_date: Optional[date] = Query(None, description="集計開始日"),
    end_date: Optional[date] = Query(None, description="集計終了日"),
    user_id: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    学習サマリーを取得
    
    - 累計学習時間
    - セッション数
    - 連続学習日数
    - 平均学習時間
    """
    try:
        if start_date is None:
            # デフォルトは30日前から
            start_date = date.today() - timedelta(days=30)
        if end_date is None:
            end_date = date.today()
            
        summary = await analytics_service.get_analytics_summary(
            user_id, start_date, end_date
        )
        return summary
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サマリー取得エラー: {str(e)}")


@router.get("/comparison", response_model=dict)
async def get_comparison_data(
    period: str = Query("week", description="比較期間 (week, month)"),
    user_id: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    前期間比較データを取得
    
    - 週次比較: 今週 vs 先週
    - 月次比較: 今月 vs 先月
    """
    try:
        if period not in ["week", "month"]:
            raise HTTPException(status_code=400, detail="期間は 'week' または 'month' を指定してください")
            
        comparison = await analytics_service.get_comparison_data(user_id, period)
        return comparison
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"比較データ取得エラー: {str(e)}")


@router.get("/detailed", response_model=DetailedAnalyticsResponse)
async def get_detailed_analytics(
    start_date: Optional[date] = Query(None, description="集計開始日"),
    end_date: Optional[date] = Query(None, description="集計終了日"),
    subject: Optional[str] = Query(None, description="科目フィルター"),
    user_id: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    詳細分析データを取得
    
    - 期間サマリー
    - 目標進捗
    - 生産性インサイト
    - 月次トレンド
    - 時間帯別分布
    """
    try:
        if start_date is None:
            # デフォルトは90日前から
            start_date = date.today() - timedelta(days=90)
        if end_date is None:
            end_date = date.today()
            
        query_params = AnalyticsQueryParams(
            start_date=start_date,
            end_date=end_date,
            subject=subject,
            user_id=user_id
        )
        
        detailed_analytics = await analytics_service.get_detailed_analytics(query_params)
        return detailed_analytics
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"詳細分析取得エラー: {str(e)}")


@router.get("/charts/daily")
async def get_daily_chart_data(
    days: int = Query(30, description="取得する日数", ge=1, le=365),
    user_id: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """日別学習時間のグラフデータを取得"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        chart_data = await analytics_service.get_daily_chart_data(
            user_id, start_date, end_date
        )
        return {"data": chart_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"グラフデータ取得エラー: {str(e)}")


@router.get("/charts/subjects")
async def get_subject_chart_data(
    days: int = Query(30, description="取得する日数", ge=1, le=365),
    user_id: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """科目別学習時間のグラフデータを取得"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        chart_data = await analytics_service.get_subject_chart_data(
            user_id, start_date, end_date
        )
        return {"data": chart_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"科目別グラフデータ取得エラー: {str(e)}")


@router.get("/charts/hourly")
async def get_hourly_distribution(
    days: int = Query(30, description="取得する日数", ge=1, le=365),
    user_id: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """時間帯別学習分布のグラフデータを取得"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        chart_data = await analytics_service.get_hourly_distribution(
            user_id, start_date, end_date
        )
        return {"data": chart_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"時間帯別データ取得エラー: {str(e)}")


@router.get("/streaks")
async def get_study_streaks(
    user_id: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """学習継続データを取得"""
    try:
        streaks = await analytics_service.get_study_streaks(user_id)
        return streaks
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"継続データ取得エラー: {str(e)}")


@router.get("/productivity")
async def get_productivity_insights(
    days: int = Query(60, description="分析期間（日数）", ge=7, le=365),
    user_id: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """生産性インサイトを取得"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        insights = await analytics_service.get_productivity_insights(
            user_id, start_date, end_date
        )
        return insights
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生産性インサイト取得エラー: {str(e)}")


@router.get("/export")
async def export_analytics_data(
    format: str = Query("json", description="エクスポート形式 (json, csv)"),
    start_date: Optional[date] = Query(None, description="開始日"),
    end_date: Optional[date] = Query(None, description="終了日"),
    user_id: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """分析データをエクスポート"""
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="形式は 'json' または 'csv' を指定してください")
            
        if start_date is None:
            start_date = date.today() - timedelta(days=90)
        if end_date is None:
            end_date = date.today()
            
        export_data = await analytics_service.export_analytics_data(
            user_id, start_date, end_date, format
        )
        
        if format == "csv":
            return JSONResponse(
                content={"download_url": export_data},
                headers={"Content-Type": "application/json"}
            )
        else:
            return export_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データエクスポートエラー: {str(e)}")


# エラーハンドリング
@router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content=AnalyticsError(
            error_code="INVALID_PARAMETER",
            message=str(exc)
        ).dict()
    )


@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=AnalyticsError(
            error_code="INTERNAL_ERROR",
            message="内部エラーが発生しました",
            details={"error": str(exc)}
        ).dict()
    )