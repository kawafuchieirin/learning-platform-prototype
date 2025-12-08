import boto3
from datetime import date, datetime
from typing import List, Dict, Optional
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from src.core.config import settings


class DynamoDBService:
    """DynamoDB アクセス層"""
    
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
        self.users_table = self.dynamodb.Table('Users')
        self.timer_table = self.dynamodb.Table('Timer')
        self.records_table = self.dynamodb.Table('Records')
        self.roadmap_table = self.dynamodb.Table('Roadmap')
        self.slack_config_table = self.dynamodb.Table('SlackConfig')
    
    async def get_records_by_date_range(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[Dict]:
        """指定期間の学習記録を取得"""
        try:
            # DynamoDBクエリ用の開始・終了キーを作成
            start_sk = f"RECORD#{start_date.isoformat()}"
            end_sk = f"RECORD#{end_date.isoformat()}"
            
            response = self.records_table.query(
                KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') &
                                     Key('SK').between(start_sk, end_sk + 'Z')  # 日付の最後まで含める
            )
            
            records = []
            for item in response.get('Items', []):
                # DynamoDBアイテムを標準的な辞書形式に変換
                record = {
                    'id': item.get('SK', '').replace('RECORD#', ''),
                    'user_id': user_id,
                    'date': item.get('date'),
                    'content': item.get('content'),
                    'comment': item.get('comment'),
                    'duration': item.get('duration', 0),
                    'subject': item.get('subject', 'その他'),
                    'roadmap_id': item.get('roadmap_id'),
                    'created_at': item.get('created_at'),
                    'updated_at': item.get('updated_at'),
                    'type': 'record'
                }
                records.append(record)
            
            return records
            
        except ClientError as e:
            print(f"DynamoDB query error: {e}")
            return []
    
    async def get_timer_data_by_date_range(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[Dict]:
        """指定期間のタイマーデータを取得"""
        try:
            # タイマーデータは TIMER#{timestamp} 形式のSKを持つ
            response = self.timer_table.query(
                KeyConditionExpression=Key('PK').eq(f'USER#{user_id}'),
                FilterExpression=Attr('date').between(
                    start_date.isoformat(), 
                    end_date.isoformat()
                )
            )
            
            timer_data = []
            for item in response.get('Items', []):
                # 完了したセッションのみを分析対象とする
                if item.get('status') == 'completed':
                    timer_record = {
                        'id': item.get('SK', '').replace('TIMER#', ''),
                        'user_id': user_id,
                        'date': item.get('date'),
                        'start_time': item.get('start_time'),
                        'end_time': item.get('end_time'),
                        'duration': item.get('duration', 0),
                        'subject': item.get('subject', 'その他'),
                        'status': item.get('status'),
                        'created_at': item.get('created_at'),
                        'type': 'timer'
                    }
                    timer_data.append(timer_record)
            
            return timer_data
            
        except ClientError as e:
            print(f"DynamoDB query error: {e}")
            return []
    
    async def get_all_study_data(self, user_id: str) -> List[Dict]:
        """ユーザーの全学習データを取得"""
        try:
            all_data = []
            
            # 学習記録を取得
            records_response = self.records_table.query(
                KeyConditionExpression=Key('PK').eq(f'USER#{user_id}'),
                FilterExpression=Attr('SK').begins_with('RECORD#')
            )
            
            for item in records_response.get('Items', []):
                record = {
                    'id': item.get('SK', '').replace('RECORD#', ''),
                    'user_id': user_id,
                    'date': item.get('date'),
                    'duration': item.get('duration', 0),
                    'subject': item.get('subject', 'その他'),
                    'created_at': item.get('created_at'),
                    'type': 'record'
                }
                all_data.append(record)
            
            # タイマーデータを取得
            timer_response = self.timer_table.query(
                KeyConditionExpression=Key('PK').eq(f'USER#{user_id}'),
                FilterExpression=Attr('status').eq('completed')
            )
            
            for item in timer_response.get('Items', []):
                timer_record = {
                    'id': item.get('SK', '').replace('TIMER#', ''),
                    'user_id': user_id,
                    'date': item.get('date'),
                    'start_time': item.get('start_time'),
                    'duration': item.get('duration', 0),
                    'subject': item.get('subject', 'その他'),
                    'created_at': item.get('created_at'),
                    'type': 'timer'
                }
                all_data.append(timer_record)
            
            return all_data
            
        except ClientError as e:
            print(f"DynamoDB query error: {e}")
            return []
    
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
            print(f"DynamoDB get_item error: {e}")
            return None
    
    async def get_study_goals(self, user_id: str) -> Optional[Dict]:
        """ユーザーの学習目標を取得"""
        try:
            # ユーザープロファイルから目標を取得
            user_profile = await self.get_user_profile(user_id)
            if user_profile and 'study_goals' in user_profile:
                return user_profile['study_goals']
            
            # デフォルト目標を返す
            return {
                'daily_target_minutes': 60,
                'weekly_target_minutes': 420,
                'target_subjects': []
            }
            
        except Exception as e:
            print(f"Error getting study goals: {e}")
            return {
                'daily_target_minutes': 60,
                'weekly_target_minutes': 420,
                'target_subjects': []
            }
    
    async def save_analytics_cache(self, user_id: str, cache_key: str, data: Dict) -> bool:
        """分析結果をキャッシュに保存（オプション）"""
        try:
            # キャッシュテーブルがある場合の実装
            # 現在は簡略化のためスキップ
            return True
            
        except ClientError as e:
            print(f"Cache save error: {e}")
            return False
    
    async def get_analytics_cache(self, user_id: str, cache_key: str) -> Optional[Dict]:
        """分析結果のキャッシュを取得（オプション）"""
        try:
            # キャッシュテーブルがある場合の実装
            # 現在は簡略化のためスキップ
            return None
            
        except ClientError as e:
            print(f"Cache get error: {e}")
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
                    'updated_at': item.get('updated_at')
                }
                roadmaps.append(roadmap)
            
            return roadmaps
            
        except ClientError as e:
            print(f"DynamoDB query error: {e}")
            return []
    
    async def get_subject_list(self, user_id: str) -> List[str]:
        """ユーザーが使用した科目の一覧を取得"""
        try:
            # 学習記録から科目を抽出
            all_data = await self.get_all_study_data(user_id)
            subjects = set()
            
            for record in all_data:
                subject = record.get('subject')
                if subject and subject != 'その他':
                    subjects.add(subject)
            
            # ロードマップからも科目を取得
            roadmaps = await self.get_roadmap_data(user_id)
            for roadmap in roadmaps:
                for item in roadmap.get('items', []):
                    if isinstance(item, dict) and 'subject' in item:
                        subjects.add(item['subject'])
            
            return sorted(list(subjects))
            
        except Exception as e:
            print(f"Error getting subject list: {e}")
            return []
    
    # バッチ取得用のメソッド
    
    async def batch_get_study_sessions(self, user_id: str, session_ids: List[str]) -> List[Dict]:
        """複数の学習セッションを一括取得"""
        try:
            # バッチ取得を実装（実際のプロダクションではバッチAPI使用）
            sessions = []
            
            for session_id in session_ids:
                # タイマーテーブルから取得を試行
                timer_response = self.timer_table.get_item(
                    Key={'PK': f'USER#{user_id}', 'SK': f'TIMER#{session_id}'}
                )
                
                if 'Item' in timer_response:
                    sessions.append(timer_response['Item'])
                    continue
                
                # 学習記録テーブルから取得を試行
                record_response = self.records_table.get_item(
                    Key={'PK': f'USER#{user_id}', 'SK': f'RECORD#{session_id}'}
                )
                
                if 'Item' in record_response:
                    sessions.append(record_response['Item'])
            
            return sessions
            
        except ClientError as e:
            print(f"Batch get error: {e}")
            return []
    
    # 統計計算用のヘルパーメソッド
    
    def _extract_date_from_timestamp(self, timestamp: str) -> Optional[str]:
        """タイムスタンプから日付を抽出"""
        try:
            if 'T' in timestamp:
                return timestamp.split('T')[0]
            elif len(timestamp) >= 10:
                return timestamp[:10]
            return None
        except:
            return None
    
    def _calculate_duration_from_times(self, start_time: str, end_time: str) -> int:
        """開始・終了時間から学習時間を計算（分単位）"""
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration_seconds = (end_dt - start_dt).total_seconds()
            return int(duration_seconds / 60)  # 分単位で返す
        except:
            return 0