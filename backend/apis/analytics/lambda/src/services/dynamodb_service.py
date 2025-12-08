import boto3
from datetime import date, datetime
from typing import List, Dict, Optional
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from models.analytics_models import StudySession
from utils.config import settings


class DynamoDBService:
    """DynamoDB データアクセス層"""
    
    def __init__(self):
        # DynamoDBクライアントの初期化
        if settings.ENV == "local":
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=settings.DYNAMODB_ENDPOINT,
                region_name=settings.AWS_REGION,
                aws_access_key_id='dummy',
                aws_secret_access_key='dummy'
            )
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        
        # テーブル参照を取得
        self.users_table = self.dynamodb.Table(settings.USERS_TABLE)
        self.timer_table = self.dynamodb.Table(settings.TIMER_TABLE)
        self.records_table = self.dynamodb.Table(settings.RECORDS_TABLE)
        self.roadmap_table = self.dynamodb.Table(settings.ROADMAP_TABLE)
    
    async def get_study_sessions_by_date_range(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[StudySession]:
        """指定期間の学習セッションを取得"""
        
        study_sessions = []
        
        try:
            # タイマーデータを取得
            timer_sessions = await self._get_timer_sessions(user_id, start_date, end_date)
            study_sessions.extend(timer_sessions)
            
            # 学習記録データを取得
            record_sessions = await self._get_record_sessions(user_id, start_date, end_date)
            study_sessions.extend(record_sessions)
            
            # 日付でソート
            study_sessions.sort(key=lambda x: (x.date, x.start_time or datetime.min))
            
            return study_sessions
            
        except ClientError as e:
            print(f"DynamoDB error in get_study_sessions_by_date_range: {e}")
            return []
    
    async def _get_timer_sessions(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[StudySession]:
        """タイマーセッションを取得"""
        
        try:
            response = self.timer_table.query(
                KeyConditionExpression=Key('PK').eq(f'USER#{user_id}'),
                FilterExpression=(
                    Attr('date').between(start_date.isoformat(), end_date.isoformat()) &
                    Attr('status').eq('completed')  # 完了したセッションのみ
                )
            )
            
            sessions = []
            for item in response.get('Items', []):
                try:
                    # DynamoDBアイテムをStudySessionに変換
                    session = StudySession(
                        session_id=item.get('SK', '').replace('TIMER#', ''),
                        user_id=user_id,
                        date=datetime.strptime(item.get('date'), '%Y-%m-%d').date(),
                        start_time=datetime.fromisoformat(
                            item.get('start_time', '').replace('Z', '+00:00')
                        ) if item.get('start_time') else None,
                        end_time=datetime.fromisoformat(
                            item.get('end_time', '').replace('Z', '+00:00')
                        ) if item.get('end_time') else None,
                        duration=item.get('duration', 0),
                        subject=item.get('subject', 'その他'),
                        session_type='timer'
                    )
                    sessions.append(session)
                except (ValueError, TypeError) as e:
                    print(f"Error parsing timer session {item.get('SK', 'unknown')}: {e}")
                    continue
            
            return sessions
            
        except ClientError as e:
            print(f"DynamoDB error in _get_timer_sessions: {e}")
            return []
    
    async def _get_record_sessions(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[StudySession]:
        """学習記録セッションを取得"""
        
        try:
            start_sk = f"RECORD#{start_date.isoformat()}"
            end_sk = f"RECORD#{end_date.isoformat()}Z"
            
            response = self.records_table.query(
                KeyConditionExpression=(
                    Key('PK').eq(f'USER#{user_id}') &
                    Key('SK').between(start_sk, end_sk)
                )
            )
            
            sessions = []
            for item in response.get('Items', []):
                try:
                    # 学習記録の場合、start_timeがない場合があるので作成日時を使用
                    created_at = item.get('created_at')
                    if created_at:
                        start_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        # フォールバック：日付の開始時刻を使用
                        session_date = datetime.strptime(item.get('date'), '%Y-%m-%d').date()
                        start_time = datetime.combine(session_date, datetime.min.time())
                    
                    session = StudySession(
                        session_id=item.get('SK', '').replace('RECORD#', ''),
                        user_id=user_id,
                        date=datetime.strptime(item.get('date'), '%Y-%m-%d').date(),
                        start_time=start_time,
                        end_time=None,  # 学習記録には終了時刻がない
                        duration=item.get('duration', 0),
                        subject=item.get('subject', 'その他'),
                        session_type='record'
                    )
                    sessions.append(session)
                except (ValueError, TypeError) as e:
                    print(f"Error parsing record session {item.get('SK', 'unknown')}: {e}")
                    continue
            
            return sessions
            
        except ClientError as e:
            print(f"DynamoDB error in _get_record_sessions: {e}")
            return []
    
    async def get_user_goals(self, user_id: str) -> Optional[Dict]:
        """ユーザーの学習目標を取得"""
        
        try:
            response = self.users_table.get_item(
                Key={
                    'PK': f'USER#{user_id}',
                    'SK': 'PROFILE'
                }
            )
            
            item = response.get('Item')
            if item and 'study_goals' in item:
                return item['study_goals']
            
            # デフォルト目標を返す
            return {
                'daily_target_minutes': 60,
                'weekly_target_minutes': 420,  # 7時間
                'monthly_target_minutes': 1800,  # 30時間
                'target_subjects': []
            }
            
        except ClientError as e:
            print(f"DynamoDB error in get_user_goals: {e}")
            return {
                'daily_target_minutes': 60,
                'weekly_target_minutes': 420,
                'monthly_target_minutes': 1800,
                'target_subjects': []
            }
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """ユーザープロファイルを取得"""
        
        try:
            response = self.users_table.get_item(
                Key={
                    'PK': f'USER#{user_id}',
                    'SK': 'PROFILE'
                }
            )
            
            item = response.get('Item')
            if item:
                return {
                    'user_id': user_id,
                    'email': item.get('email'),
                    'name': item.get('name'),
                    'created_at': item.get('created_at'),
                    'updated_at': item.get('updated_at'),
                    'timezone': item.get('timezone', 'Asia/Tokyo'),
                    'study_goals': item.get('study_goals', {})
                }
            return None
            
        except ClientError as e:
            print(f"DynamoDB error in get_user_profile: {e}")
            return None
    
    async def get_roadmap_data(self, user_id: str) -> List[Dict]:
        """ユーザーのロードマップデータを取得"""
        
        try:
            response = self.roadmap_table.query(
                KeyConditionExpression=Key('PK').eq(f'USER#{user_id}'),
                FilterExpression=Attr('SK').begins_with('ROADMAP#')
            )
            
            roadmaps = []
            for item in response.get('Items', []):
                roadmap = {
                    'roadmap_id': item.get('SK', '').replace('ROADMAP#', ''),
                    'title': item.get('title'),
                    'items': item.get('items', []),
                    'total_hours': item.get('total_hours', 0),
                    'progress': item.get('progress', 0),
                    'created_at': item.get('created_at'),
                    'updated_at': item.get('updated_at'),
                    'subjects': self._extract_subjects_from_roadmap(item.get('items', []))
                }
                roadmaps.append(roadmap)
            
            return roadmaps
            
        except ClientError as e:
            print(f"DynamoDB error in get_roadmap_data: {e}")
            return []
    
    async def get_subject_list(self, user_id: str) -> List[str]:
        """ユーザーが使用した科目リストを取得"""
        
        try:
            subjects = set()
            
            # 学習セッションから科目を抽出
            # 過去30日のデータから科目リストを作成
            from datetime import timedelta
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            study_sessions = await self.get_study_sessions_by_date_range(user_id, start_date, end_date)
            
            for session in study_sessions:
                if session.subject and session.subject != 'その他':
                    subjects.add(session.subject)
            
            # ロードマップからも科目を取得
            roadmaps = await self.get_roadmap_data(user_id)
            for roadmap in roadmaps:
                subjects.update(roadmap.get('subjects', []))
            
            return sorted(list(subjects))
            
        except Exception as e:
            print(f"Error in get_subject_list: {e}")
            return []
    
    async def get_study_streak_data(self, user_id: str) -> Dict:
        """学習継続データを取得"""
        
        try:
            # 過去90日のデータを取得して継続日数を計算
            from datetime import timedelta
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
            
            study_sessions = await self.get_study_sessions_by_date_range(user_id, start_date, end_date)
            
            # 学習した日付のセットを作成
            study_dates = set(session.date for session in study_sessions)
            
            # 現在の連続日数を計算
            current_streak = 0
            check_date = end_date
            
            while check_date in study_dates:
                current_streak += 1
                check_date -= timedelta(days=1)
            
            # 最長連続日数を計算
            longest_streak = 0
            temp_streak = 0
            
            for i in range(90):
                check_date = end_date - timedelta(days=i)
                if check_date in study_dates:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 0
            
            return {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'total_study_days': len(study_dates),
                'study_dates': sorted([d.isoformat() for d in study_dates])
            }
            
        except Exception as e:
            print(f"Error in get_study_streak_data: {e}")
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'total_study_days': 0,
                'study_dates': []
            }
    
    # ヘルパーメソッド
    
    def _extract_subjects_from_roadmap(self, roadmap_items: List[Dict]) -> List[str]:
        """ロードマップアイテムから科目を抽出"""
        
        subjects = set()
        for item in roadmap_items:
            if isinstance(item, dict):
                subject = item.get('subject') or item.get('category')
                if subject:
                    subjects.add(subject)
        
        return list(subjects)
    
    async def save_analytics_cache(self, cache_key: str, data: Dict, ttl_seconds: int = 3600) -> bool:
        """分析結果をキャッシュに保存（将来の拡張用）"""
        
        # 現在は実装なし（ElastiCacheやDynamoDB TTLで実装予定）
        return True
    
    async def get_analytics_cache(self, cache_key: str) -> Optional[Dict]:
        """分析結果のキャッシュを取得（将来の拡張用）"""
        
        # 現在は実装なし
        return None