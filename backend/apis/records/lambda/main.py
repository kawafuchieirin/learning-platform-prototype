"""
学習記録API Lambda関数のメインハンドラー
学習記録の作成、管理、テンプレート機能を提供
"""

import json
import logging
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB設定は遅延初期化
def get_dynamodb_table():
    """DynamoDBテーブルを取得（遅延初期化）"""
    import os
    dynamodb_endpoint = os.getenv('DYNAMODB_ENDPOINT')
    region_name = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    if dynamodb_endpoint:
        # ローカル環境用の設定
        dynamodb = boto3.resource(
            'dynamodb', 
            endpoint_url=dynamodb_endpoint,
            region_name=region_name,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'local'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'local')
        )
    else:
        dynamodb = boto3.resource('dynamodb', region_name=region_name)
    
    table_name = os.getenv('DYNAMODB_TABLE_NAME', 'LearningPlatform')
    return dynamodb.Table(table_name)

def convert_floats_to_decimal(obj):
    """DynamoDB用にfloat値をDecimalに変換"""
    if isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(v) for v in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

def convert_decimals_to_float(obj):
    """JSON応答用にDecimal値をfloatに変換"""
    if isinstance(obj, dict):
        return {k: convert_decimals_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals_to_float(v) for v in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API Gateway からのリクエストを処理
    """
    try:
        http_method = event.get('httpMethod')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        body = event.get('body')
        
        # 認証情報の取得（Cognito User Pool）
        user_id = get_user_id(event)
        if not user_id:
            return error_response(401, "認証が必要です")
        
        # ルーティング
        if http_method == 'GET':
            if path.endswith('/templates'):
                return get_record_templates(user_id, query_parameters)
            elif 'recordId' in path_parameters:
                return get_record(user_id, path_parameters['recordId'])
            else:
                return list_records(user_id, query_parameters)
                
        elif http_method == 'POST':
            if path.endswith('/from-template'):
                return create_record_from_template(user_id, body)
            else:
                return create_record(user_id, body)
                
        elif http_method == 'PUT':
            record_id = path_parameters.get('recordId')
            if not record_id:
                return error_response(400, "記録IDが必要です")
            return update_record(user_id, record_id, body)
            
        elif http_method == 'DELETE':
            record_id = path_parameters.get('recordId')
            if not record_id:
                return error_response(400, "記録IDが必要です")
            return delete_record(user_id, record_id)
        
        return error_response(405, "サポートされていないHTTPメソッドです")
        
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        return error_response(500, "内部サーバーエラーが発生しました")

def get_user_id(event: Dict[str, Any]) -> Optional[str]:
    """API Gateway の認証情報からユーザーIDを取得"""
    try:
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        claims = authorizer.get('claims', {})
        return claims.get('sub')
    except Exception:
        return None

def create_record(user_id: str, body: str) -> Dict[str, Any]:
    """新しい学習記録を作成"""
    try:
        data = json.loads(body) if body else {}
        
        # バリデーション
        required_fields = ['title', 'duration_minutes']
        for field in required_fields:
            if field not in data:
                return error_response(400, f"{field}は必須項目です")
        
        # 学習時間のバリデーション
        try:
            duration_minutes = int(data['duration_minutes'])
            if duration_minutes <= 0:
                return error_response(400, "学習時間は0より大きい値である必要があります")
        except (ValueError, TypeError):
            return error_response(400, "学習時間は有効な数値である必要があります")
        
        # 記録作成
        record_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # 学習日の指定がない場合は今日の日付を使用
        study_date = data.get('study_date', datetime.utcnow().date().isoformat())
        
        record = {
            'PK': f'USER#{user_id}',
            'SK': f'RECORD#{record_id}',
            'GSI1PK': f'USER#{user_id}',
            'GSI1SK': f'RECORD#{study_date}#{timestamp}',
            'record_id': record_id,
            'title': data['title'],
            'content': data.get('content', ''),
            'duration_minutes': duration_minutes,
            'study_date': study_date,
            'roadmap_id': data.get('roadmap_id'),
            'roadmap_item_title': data.get('roadmap_item_title'),
            'tags': data.get('tags', []),
            'difficulty': data.get('difficulty', 'medium'),  # easy, medium, hard
            'satisfaction': data.get('satisfaction', 3),  # 1-5
            'notes': data.get('notes', ''),
            'created_at': timestamp,
            'updated_at': timestamp,
            'status': 'active'
        }
        
        # DynamoDB用にDecimal変換
        record = convert_floats_to_decimal(record)
        
        # DynamoDB に保存
        get_dynamodb_table().put_item(Item=record)
        
        # ロードマップの進捗を更新（該当する場合）
        if data.get('roadmap_id') and data.get('roadmap_item_title'):
            update_roadmap_progress(user_id, data['roadmap_id'], data['roadmap_item_title'], duration_minutes / 60.0)
        
        logger.info(f"学習記録を作成しました: {record_id}")
        return success_response(record)
        
    except json.JSONDecodeError:
        return error_response(400, "無効なJSONフォーマットです")
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def list_records(user_id: str, query_params: Dict[str, Any]) -> Dict[str, Any]:
    """ユーザーの学習記録一覧を取得"""
    try:
        # クエリパラメータの解析
        limit = min(int(query_params.get('limit', 50)), 100)
        date_from = query_params.get('date_from')
        date_to = query_params.get('date_to')
        roadmap_id = query_params.get('roadmap_id')
        
        # DynamoDB クエリ
        key_condition = 'GSI1PK = :pk'
        expression_values = {':pk': f'USER#{user_id}'}
        
        # 日付範囲フィルター
        if date_from or date_to:
            if date_from and date_to:
                key_condition += ' AND GSI1SK BETWEEN :sk_start AND :sk_end'
                expression_values.update({
                    ':sk_start': f'RECORD#{date_from}#',
                    ':sk_end': f'RECORD#{date_to}#~'
                })
            elif date_from:
                key_condition += ' AND GSI1SK >= :sk_start'
                expression_values[':sk_start'] = f'RECORD#{date_from}#'
            else:  # date_to のみ
                key_condition += ' AND GSI1SK <= :sk_end'
                expression_values[':sk_end'] = f'RECORD#{date_to}#~'
        else:
            key_condition += ' AND begins_with(GSI1SK, :sk)'
            expression_values[':sk'] = 'RECORD#'
        
        # フィルター式の構築
        filter_expression = None
        if roadmap_id:
            filter_expression = 'roadmap_id = :roadmap_id'
            expression_values[':roadmap_id'] = roadmap_id
        
        query_params_dict = {
            'IndexName': 'GSI1',
            'KeyConditionExpression': key_condition,
            'ExpressionAttributeValues': expression_values,
            'Limit': limit,
            'ScanIndexForward': False  # 最新順
        }
        
        if filter_expression:
            query_params_dict['FilterExpression'] = filter_expression
        
        response = get_dynamodb_table().query(**query_params_dict)
        
        records = []
        for item in response.get('Items', []):
            if item.get('status') != 'deleted':
                record_summary = {
                    'record_id': item['record_id'],
                    'title': item['title'],
                    'content': item.get('content', ''),
                    'duration_minutes': item.get('duration_minutes', 0),
                    'study_date': item.get('study_date'),
                    'roadmap_id': item.get('roadmap_id'),
                    'roadmap_item_title': item.get('roadmap_item_title'),
                    'tags': item.get('tags', []),
                    'difficulty': item.get('difficulty', 'medium'),
                    'satisfaction': item.get('satisfaction', 3),
                    'created_at': item['created_at'],
                    'updated_at': item['updated_at']
                }
                records.append(record_summary)
        
        # 統計情報の計算
        total_duration = sum(record.get('duration_minutes', 0) for record in records)
        
        return success_response({
            'records': records,
            'total_count': len(records),
            'statistics': {
                'total_duration_minutes': total_duration,
                'total_duration_hours': round(total_duration / 60.0, 1),
                'average_duration_minutes': round(total_duration / len(records), 1) if records else 0
            }
        })
        
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def get_record(user_id: str, record_id: str) -> Dict[str, Any]:
    """指定された学習記録の詳細を取得"""
    try:
        response = get_dynamodb_table().get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'RECORD#{record_id}'
            }
        )
        
        if 'Item' not in response or response['Item'].get('status') == 'deleted':
            return error_response(404, "学習記録が見つかりません")
        
        return success_response(response['Item'])
        
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def update_record(user_id: str, record_id: str, body: str) -> Dict[str, Any]:
    """学習記録を更新"""
    try:
        data = json.loads(body) if body else {}
        
        # 既存の記録を取得
        response = get_dynamodb_table().get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'RECORD#{record_id}'
            }
        )
        
        if 'Item' not in response or response['Item'].get('status') == 'deleted':
            return error_response(404, "学習記録が見つかりません")
        
        # 更新可能なフィールドをチェック
        updatable_fields = ['title', 'content', 'duration_minutes', 'study_date', 
                           'roadmap_id', 'roadmap_item_title', 'tags', 'difficulty', 
                           'satisfaction', 'notes']
        
        update_expression = ['#updated_at = :updated_at']
        expression_values = {':updated_at': datetime.utcnow().isoformat()}
        expression_names = {'#updated_at': 'updated_at'}
        
        for field in updatable_fields:
            if field in data:
                if field == 'duration_minutes':
                    # 学習時間のバリデーション
                    try:
                        duration = int(data[field])
                        if duration <= 0:
                            return error_response(400, "学習時間は0より大きい値である必要があります")
                        data[field] = duration
                    except (ValueError, TypeError):
                        return error_response(400, "学習時間は有効な数値である必要があります")
                
                update_expression.append(f'#{field} = :{field}')
                expression_values[f':{field}'] = data[field]
                expression_names[f'#{field}'] = field
        
        # DynamoDB更新
        get_dynamodb_table().update_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'RECORD#{record_id}'
            },
            UpdateExpression='SET ' + ', '.join(update_expression),
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names
        )
        
        # 更新後の記録を取得
        updated_response = get_dynamodb_table().get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'RECORD#{record_id}'
            }
        )
        
        logger.info(f"学習記録を更新しました: {record_id}")
        return success_response(updated_response['Item'])
        
    except json.JSONDecodeError:
        return error_response(400, "無効なJSONフォーマットです")
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def delete_record(user_id: str, record_id: str) -> Dict[str, Any]:
    """学習記録を削除（論理削除）"""
    try:
        # 存在チェック
        response = get_dynamodb_table().get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'RECORD#{record_id}'
            }
        )
        
        if 'Item' not in response or response['Item'].get('status') == 'deleted':
            return error_response(404, "学習記録が見つかりません")
        
        # 論理削除（statusをdeletedに変更）
        get_dynamodb_table().update_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'RECORD#{record_id}'
            },
            UpdateExpression='SET #status = :status, #updated_at = :updated_at',
            ExpressionAttributeValues={
                ':status': 'deleted',
                ':updated_at': datetime.utcnow().isoformat()
            },
            ExpressionAttributeNames={
                '#status': 'status',
                '#updated_at': 'updated_at'
            }
        )
        
        logger.info(f"学習記録を削除しました: {record_id}")
        return success_response({'message': '学習記録が削除されました'})
        
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def create_record_from_template(user_id: str, body: str) -> Dict[str, Any]:
    """テンプレートから学習記録を作成"""
    try:
        data = json.loads(body) if body else {}
        
        if 'template_type' not in data:
            return error_response(400, "template_typeが必要です")
        
        template_type = data['template_type']
        
        # テンプレートタイプに応じた初期値を設定
        if template_type == 'roadmap':
            if not data.get('roadmap_id') or not data.get('roadmap_item_title'):
                return error_response(400, "ロードマップテンプレートにはroadmap_idとroadmap_item_titleが必要です")
            
            record_data = {
                'title': f"ロードマップ学習: {data['roadmap_item_title']}",
                'content': f"{data['roadmap_item_title']}の学習記録",
                'duration_minutes': data.get('duration_minutes', 60),
                'roadmap_id': data['roadmap_id'],
                'roadmap_item_title': data['roadmap_item_title'],
                'tags': ['roadmap'],
                'difficulty': 'medium',
                'satisfaction': 3
            }
        
        elif template_type == 'reading':
            record_data = {
                'title': data.get('title', '読書記録'),
                'content': '本の内容や学んだことを記録',
                'duration_minutes': data.get('duration_minutes', 120),
                'tags': ['reading', 'book'],
                'difficulty': 'easy',
                'satisfaction': 3
            }
        
        elif template_type == 'coding':
            record_data = {
                'title': data.get('title', 'プログラミング学習'),
                'content': 'コーディングで学んだことや実装した内容',
                'duration_minutes': data.get('duration_minutes', 90),
                'tags': ['coding', 'programming'],
                'difficulty': 'medium',
                'satisfaction': 3
            }
        
        elif template_type == 'video':
            record_data = {
                'title': data.get('title', '動画学習'),
                'content': '動画で学んだ内容のまとめ',
                'duration_minutes': data.get('duration_minutes', 60),
                'tags': ['video', 'online-learning'],
                'difficulty': 'easy',
                'satisfaction': 3
            }
        
        else:
            return error_response(400, f"サポートされていないテンプレートタイプです: {template_type}")
        
        # ユーザーが指定した値で上書き
        for field in ['title', 'content', 'duration_minutes', 'tags', 'difficulty', 'satisfaction', 'notes']:
            if field in data:
                record_data[field] = data[field]
        
        # 記録作成処理を呼び出し
        return create_record(user_id, json.dumps(record_data))
        
    except json.JSONDecodeError:
        return error_response(400, "無効なJSONフォーマットです")
    except Exception as e:
        logger.error(f"テンプレート作成エラー: {str(e)}")
        return error_response(500, "テンプレートからの記録作成に失敗しました")

def get_record_templates(user_id: str, query_params: Dict[str, Any]) -> Dict[str, Any]:
    """記録作成用テンプレートの一覧を取得"""
    try:
        templates = [
            {
                'template_type': 'roadmap',
                'name': 'ロードマップ学習',
                'description': 'ロードマップに紐づく学習記録を作成',
                'default_duration_minutes': 60,
                'tags': ['roadmap'],
                'fields': ['roadmap_id', 'roadmap_item_title', 'duration_minutes', 'content', 'difficulty', 'satisfaction']
            },
            {
                'template_type': 'reading',
                'name': '読書記録',
                'description': '本や記事の読書記録を作成',
                'default_duration_minutes': 120,
                'tags': ['reading', 'book'],
                'fields': ['title', 'duration_minutes', 'content', 'satisfaction']
            },
            {
                'template_type': 'coding',
                'name': 'プログラミング学習',
                'description': 'コーディングや実装に関する学習記録',
                'default_duration_minutes': 90,
                'tags': ['coding', 'programming'],
                'fields': ['title', 'duration_minutes', 'content', 'difficulty', 'satisfaction']
            },
            {
                'template_type': 'video',
                'name': '動画学習',
                'description': '動画教材での学習記録を作成',
                'default_duration_minutes': 60,
                'tags': ['video', 'online-learning'],
                'fields': ['title', 'duration_minutes', 'content', 'satisfaction']
            }
        ]
        
        # ユーザーのロードマップがある場合、ロードマップ用テンプレートに項目を追加
        roadmap_items = get_user_roadmap_items(user_id)
        if roadmap_items:
            for template in templates:
                if template['template_type'] == 'roadmap':
                    template['roadmap_items'] = roadmap_items
        
        return success_response({
            'templates': templates,
            'total_count': len(templates)
        })
        
    except Exception as e:
        logger.error(f"テンプレート取得エラー: {str(e)}")
        return error_response(500, "テンプレート取得に失敗しました")

def get_user_roadmap_items(user_id: str) -> List[Dict[str, Any]]:
    """ユーザーのロードマップアイテム一覧を取得"""
    try:
        response = get_dynamodb_table().query(
            IndexName='GSI1',
            KeyConditionExpression='GSI1PK = :pk AND begins_with(GSI1SK, :sk)',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':sk': 'ROADMAP#'
            }
        )
        
        roadmap_items = []
        for roadmap in response.get('Items', []):
            if roadmap.get('status') == 'active':
                for item in roadmap.get('items', []):
                    roadmap_items.append({
                        'roadmap_id': roadmap['roadmap_id'],
                        'roadmap_title': roadmap['title'],
                        'item_title': item['title'],
                        'estimated_hours': item.get('estimated_hours', 0),
                        'completed_hours': item.get('completed_hours', 0),
                        'progress': item.get('progress', 0)
                    })
        
        return roadmap_items
        
    except Exception as e:
        logger.error(f"ロードマップアイテム取得エラー: {str(e)}")
        return []

def update_roadmap_progress(user_id: str, roadmap_id: str, item_title: str, hours_to_add: float):
    """ロードマップの進捗を更新"""
    try:
        # ロードマップを取得
        response = get_dynamodb_table().get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'ROADMAP#{roadmap_id}'
            }
        )
        
        if 'Item' not in response:
            return
        
        roadmap = response['Item']
        items = roadmap.get('items', [])
        total_hours = float(roadmap.get('total_hours', 0))
        
        # 該当アイテムの完了時間を更新
        updated = False
        for item in items:
            if item['title'] == item_title:
                old_completed = float(item.get('completed_hours', 0))
                new_completed = old_completed + hours_to_add
                item['completed_hours'] = new_completed
                
                # 個別アイテムの進捗計算
                estimated = float(item.get('estimated_hours', 1))
                item['progress'] = min((new_completed / estimated) * 100, 100) if estimated > 0 else 100
                updated = True
                break
        
        if not updated:
            return
        
        # 全体の完了時間と進捗を再計算
        total_completed = sum(float(item.get('completed_hours', 0)) for item in items)
        overall_progress = (total_completed / total_hours) * 100 if total_hours > 0 else 0
        
        # DynamoDB更新
        get_dynamodb_table().update_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'ROADMAP#{roadmap_id}'
            },
            UpdateExpression='SET #items = :items, #completed_hours = :completed_hours, #progress = :progress, #updated_at = :updated_at',
            ExpressionAttributeValues={
                ':items': convert_floats_to_decimal(items),
                ':completed_hours': Decimal(str(total_completed)),
                ':progress': Decimal(str(overall_progress)),
                ':updated_at': datetime.utcnow().isoformat()
            },
            ExpressionAttributeNames={
                '#items': 'items',
                '#completed_hours': 'completed_hours',
                '#progress': 'progress',
                '#updated_at': 'updated_at'
            }
        )
        
        logger.info(f"ロードマップ進捗を更新しました: {roadmap_id}, {item_title}, +{hours_to_add}h")
        
    except Exception as e:
        logger.error(f"ロードマップ進捗更新エラー: {str(e)}")
        # エラーが発生してもレコード作成は続行

def success_response(data: Any) -> Dict[str, Any]:
    """成功レスポンスを生成"""
    # DynamoDBのDecimal型をfloatに変換してJSON出力
    cleaned_data = convert_decimals_to_float(data)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
        },
        'body': json.dumps(cleaned_data, ensure_ascii=False, default=str)
    }

def error_response(status_code: int, message: str) -> Dict[str, Any]:
    """エラーレスポンスを生成"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
        },
        'body': json.dumps({
            'error': message
        }, ensure_ascii=False)
    }