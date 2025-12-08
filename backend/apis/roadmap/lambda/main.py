"""
ロードマップAPI Lambda関数のメインハンドラー
学習計画の作成、管理、CSVインポート機能を提供
"""

import json
import logging
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import io
import csv
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
    """
    DynamoDB用にfloat値をDecimalに変換
    """
    if isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(v) for v in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

def convert_decimals_to_float(obj):
    """
    JSON応答用にDecimal値をfloatに変換
    """
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
            if path.endswith('/template'):
                return download_csv_template()
            elif 'roadmapId' in path_parameters:
                return get_roadmap(user_id, path_parameters['roadmapId'])
            else:
                return list_roadmaps(user_id, query_parameters)
                
        elif http_method == 'POST':
            if path.endswith('/import'):
                return import_csv_roadmap(user_id, body)
            else:
                return create_roadmap(user_id, body)
                
        elif http_method == 'PUT':
            roadmap_id = path_parameters.get('roadmapId')
            if not roadmap_id:
                return error_response(400, "ロードマップIDが必要です")
            return update_roadmap(user_id, roadmap_id, body)
            
        elif http_method == 'DELETE':
            roadmap_id = path_parameters.get('roadmapId')
            if not roadmap_id:
                return error_response(400, "ロードマップIDが必要です")
            return delete_roadmap(user_id, roadmap_id)
        
        return error_response(405, "サポートされていないHTTPメソッドです")
        
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        return error_response(500, "内部サーバーエラーが発生しました")

def get_user_id(event: Dict[str, Any]) -> Optional[str]:
    """
    API Gateway の認証情報からユーザーIDを取得
    """
    try:
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        claims = authorizer.get('claims', {})
        return claims.get('sub')
    except Exception:
        return None

def create_roadmap(user_id: str, body: str) -> Dict[str, Any]:
    """
    新しいロードマップを作成
    """
    try:
        data = json.loads(body) if body else {}
        
        # バリデーション
        required_fields = ['title', 'items']
        for field in required_fields:
            if field not in data:
                return error_response(400, f"{field}は必須項目です")
        
        # ロードマップアイテムのバリデーション
        items = data.get('items', [])
        if not isinstance(items, list) or len(items) == 0:
            return error_response(400, "アイテムは少なくとも1つ必要です")
        
        total_hours = 0
        for item in items:
            if not isinstance(item, dict) or 'title' not in item or 'estimated_hours' not in item:
                return error_response(400, "各アイテムにはタイトルと予定時間が必要です")
            
            try:
                estimated_hours = float(item['estimated_hours'])
                if estimated_hours <= 0:
                    return error_response(400, "予定時間は0より大きい値である必要があります")
                total_hours += estimated_hours
                item['estimated_hours'] = estimated_hours
                item['completed_hours'] = item.get('completed_hours', 0.0)
                item['progress'] = 0.0  # 初期進捗は0%
            except (ValueError, TypeError):
                return error_response(400, "予定時間は有効な数値である必要があります")
        
        # ロードマップ作成
        roadmap_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        roadmap = {
            'PK': f'USER#{user_id}',
            'SK': f'ROADMAP#{roadmap_id}',
            'GSI1PK': f'USER#{user_id}',
            'GSI1SK': f'ROADMAP#{timestamp}',
            'roadmap_id': roadmap_id,
            'title': data['title'],
            'description': data.get('description', ''),
            'items': items,
            'total_hours': total_hours,
            'completed_hours': 0.0,
            'progress': 0.0,
            'created_at': timestamp,
            'updated_at': timestamp,
            'status': 'active'
        }
        
        # DynamoDB用にDecimal変換
        roadmap = convert_floats_to_decimal(roadmap)
        
        # DynamoDB に保存
        get_dynamodb_table().put_item(Item=roadmap)
        
        logger.info(f"ロードマップを作成しました: {roadmap_id}")
        return success_response(roadmap)
        
    except json.JSONDecodeError:
        return error_response(400, "無効なJSONフォーマットです")
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def list_roadmaps(user_id: str, query_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    ユーザーのロードマップ一覧を取得
    """
    try:
        # クエリパラメータの解析
        limit = min(int(query_params.get('limit', 20)), 100)
        status_filter = query_params.get('status', 'active')
        
        # DynamoDB クエリ
        response = get_dynamodb_table().query(
            IndexName='GSI1',
            KeyConditionExpression='GSI1PK = :pk AND begins_with(GSI1SK, :sk)',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':sk': 'ROADMAP#'
            },
            Limit=limit,
            ScanIndexForward=False  # 最新順
        )
        
        roadmaps = []
        for item in response.get('Items', []):
            if status_filter == 'all' or item.get('status') == status_filter:
                # 必要な情報のみを返す（サマリー）
                roadmap_summary = {
                    'roadmap_id': item['roadmap_id'],
                    'title': item['title'],
                    'description': item.get('description', ''),
                    'total_hours': item.get('total_hours', 0),
                    'completed_hours': item.get('completed_hours', 0),
                    'progress': item.get('progress', 0),
                    'items_count': len(item.get('items', [])),
                    'status': item.get('status', 'active'),
                    'created_at': item['created_at'],
                    'updated_at': item['updated_at']
                }
                roadmaps.append(roadmap_summary)
        
        return success_response({
            'roadmaps': roadmaps,
            'total_count': len(roadmaps)
        })
        
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def get_roadmap(user_id: str, roadmap_id: str) -> Dict[str, Any]:
    """
    指定されたロードマップの詳細を取得
    """
    try:
        response = get_dynamodb_table().get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'ROADMAP#{roadmap_id}'
            }
        )
        
        if 'Item' not in response:
            return error_response(404, "ロードマップが見つかりません")
        
        return success_response(response['Item'])
        
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def update_roadmap(user_id: str, roadmap_id: str, body: str) -> Dict[str, Any]:
    """
    ロードマップを更新
    """
    try:
        data = json.loads(body) if body else {}
        
        # 既存のロードマップを取得
        response = get_dynamodb_table().get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'ROADMAP#{roadmap_id}'
            }
        )
        
        if 'Item' not in response:
            return error_response(404, "ロードマップが見つかりません")
        
        roadmap = response['Item']
        
        # 更新可能なフィールドをチェック
        updatable_fields = ['title', 'description', 'items']
        update_expression = ['#updated_at = :updated_at']
        expression_values = {':updated_at': datetime.utcnow().isoformat()}
        expression_names = {'#updated_at': 'updated_at'}
        
        for field in updatable_fields:
            if field in data:
                if field == 'items':
                    # アイテム更新時は進捗も再計算
                    items = data[field]
                    if not isinstance(items, list):
                        return error_response(400, "アイテムは配列である必要があります")
                    
                    total_hours = 0
                    completed_hours = 0
                    
                    for item in items:
                        if not isinstance(item, dict) or 'title' not in item or 'estimated_hours' not in item:
                            return error_response(400, "各アイテムにはタイトルと予定時間が必要です")
                        
                        try:
                            estimated_hours = float(item['estimated_hours'])
                            completed_hours_item = float(item.get('completed_hours', 0))
                            
                            if estimated_hours <= 0:
                                return error_response(400, "予定時間は0より大きい値である必要があります")
                            
                            total_hours += estimated_hours
                            completed_hours += completed_hours_item
                            
                            # 進捗計算
                            item['progress'] = min((completed_hours_item / estimated_hours) * 100, 100) if estimated_hours > 0 else 0
                            
                        except (ValueError, TypeError):
                            return error_response(400, "時間は有効な数値である必要があります")
                    
                    # 全体の進捗計算
                    overall_progress = (completed_hours / total_hours) * 100 if total_hours > 0 else 0
                    
                    update_expression.extend([
                        '#items = :items',
                        '#total_hours = :total_hours',
                        '#completed_hours = :completed_hours',
                        '#progress = :progress'
                    ])
                    expression_values.update({
                        ':items': items,
                        ':total_hours': total_hours,
                        ':completed_hours': completed_hours,
                        ':progress': overall_progress
                    })
                    expression_names.update({
                        '#items': 'items',
                        '#total_hours': 'total_hours',
                        '#completed_hours': 'completed_hours',
                        '#progress': 'progress'
                    })
                else:
                    update_expression.append(f'#{field} = :{field}')
                    expression_values[f':{field}'] = data[field]
                    expression_names[f'#{field}'] = field
        
        # DynamoDB更新
        get_dynamodb_table().update_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'ROADMAP#{roadmap_id}'
            },
            UpdateExpression='SET ' + ', '.join(update_expression),
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names
        )
        
        # 更新後のロードマップを取得
        updated_response = get_dynamodb_table().get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'ROADMAP#{roadmap_id}'
            }
        )
        
        logger.info(f"ロードマップを更新しました: {roadmap_id}")
        return success_response(updated_response['Item'])
        
    except json.JSONDecodeError:
        return error_response(400, "無効なJSONフォーマットです")
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def delete_roadmap(user_id: str, roadmap_id: str) -> Dict[str, Any]:
    """
    ロードマップを削除（論理削除）
    """
    try:
        # 存在チェック
        response = get_dynamodb_table().get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'ROADMAP#{roadmap_id}'
            }
        )
        
        if 'Item' not in response:
            return error_response(404, "ロードマップが見つかりません")
        
        # 論理削除（statusをdeletedに変更）
        get_dynamodb_table().update_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'ROADMAP#{roadmap_id}'
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
        
        logger.info(f"ロードマップを削除しました: {roadmap_id}")
        return success_response({'message': 'ロードマップが削除されました'})
        
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def import_csv_roadmap(user_id: str, body: str) -> Dict[str, Any]:
    """
    CSVファイルからロードマップをインポート
    フォーマット: タイトル,予定時間,進捗率
    """
    try:
        data = json.loads(body) if body else {}
        
        if 'csv_content' not in data:
            return error_response(400, "CSVコンテンツが必要です")
        
        csv_content = data['csv_content']
        roadmap_title = data.get('title', f'インポートされたロードマップ {datetime.utcnow().strftime("%Y-%m-%d %H:%M")}')
        
        # CSV解析
        csv_reader = csv.reader(io.StringIO(csv_content))
        items = []
        total_hours = 0
        
        for row_num, row in enumerate(csv_reader, 1):
            if len(row) < 2:
                continue  # 空行やヘッダーをスキップ
            
            try:
                title = row[0].strip()
                estimated_hours = float(row[1])
                completed_hours = float(row[2]) if len(row) > 2 and row[2].strip() else 0.0
                
                if not title:
                    return error_response(400, f"{row_num}行目: タイトルが空です")
                
                if estimated_hours <= 0:
                    return error_response(400, f"{row_num}行目: 予定時間は0より大きい値である必要があります")
                
                progress = (completed_hours / estimated_hours) * 100 if estimated_hours > 0 else 0
                
                items.append({
                    'title': title,
                    'estimated_hours': estimated_hours,
                    'completed_hours': completed_hours,
                    'progress': min(progress, 100)
                })
                
                total_hours += estimated_hours
                
            except (ValueError, IndexError) as e:
                return error_response(400, f"{row_num}行目: データ形式が正しくありません")
        
        if not items:
            return error_response(400, "有効なアイテムが見つかりませんでした")
        
        # ロードマップ作成
        roadmap_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        roadmap = {
            'PK': f'USER#{user_id}',
            'SK': f'ROADMAP#{roadmap_id}',
            'GSI1PK': f'USER#{user_id}',
            'GSI1SK': f'ROADMAP#{timestamp}',
            'roadmap_id': roadmap_id,
            'title': roadmap_title,
            'description': 'CSVファイルからインポートされたロードマップ',
            'items': items,
            'total_hours': total_hours,
            'completed_hours': sum(item['completed_hours'] for item in items),
            'progress': sum(item['completed_hours'] for item in items) / total_hours * 100 if total_hours > 0 else 0,
            'created_at': timestamp,
            'updated_at': timestamp,
            'status': 'active'
        }
        
        # DynamoDB用にDecimal変換
        roadmap = convert_floats_to_decimal(roadmap)
        
        # DynamoDB に保存
        get_dynamodb_table().put_item(Item=roadmap)
        
        logger.info(f"CSVからロードマップをインポートしました: {roadmap_id}")
        return success_response(roadmap)
        
    except json.JSONDecodeError:
        return error_response(400, "無効なJSONフォーマットです")
    except ClientError as e:
        logger.error(f"DynamoDB エラー: {str(e)}")
        return error_response(500, "データベースエラーが発生しました")

def download_csv_template() -> Dict[str, Any]:
    """
    CSVテンプレートファイルを返す
    """
    template_content = "タイトル,予定時間,完了時間\n" \
                      "React基礎学習,20,5\n" \
                      "API開発,15,0\n" \
                      "テスト作成,10,0\n"
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/csv; charset=utf-8',
            'Content-Disposition': 'attachment; filename="roadmap_template.csv"',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
        },
        'body': template_content
    }

def success_response(data: Any) -> Dict[str, Any]:
    """
    成功レスポンスを生成
    """
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
    """
    エラーレスポンスを生成
    """
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