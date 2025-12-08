"""
ロードマップAPI Lambda関数のユニットテスト
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from moto import mock_dynamodb
import boto3
from decimal import Decimal

# テスト対象のモジュールをインポート
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lambda'))

from main import (
    lambda_handler,
    create_roadmap,
    list_roadmaps,
    get_roadmap,
    update_roadmap,
    delete_roadmap,
    import_csv_roadmap,
    download_csv_template
)

# テスト用のダミーデータ
DUMMY_USER_ID = "test-user-id"

@pytest.fixture
def api_gateway_event():
    """API Gateway イベントのベース"""
    return {
        "httpMethod": "GET",
        "path": "/roadmap",
        "pathParameters": None,
        "queryStringParameters": None,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": None,
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": DUMMY_USER_ID
                }
            }
        }
    }

@pytest.fixture
def lambda_context():
    """Lambda コンテキストのモック"""
    context = Mock()
    context.function_name = "roadmap-api"
    context.function_version = "1"
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:roadmap-api"
    context.memory_limit_in_mb = 256
    context.remaining_time_in_millis = lambda: 30000
    return context

@pytest.fixture
def dynamodb_table():
    """DynamoDB テーブルのモック"""
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # テーブル作成
        table = dynamodb.create_table(
            TableName='LearningPlatform',
            KeySchema=[
                {
                    'AttributeName': 'PK',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'SK',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'SK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'GSI1PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'GSI1SK',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'GSI1',
                    'KeySchema': [
                        {
                            'AttributeName': 'GSI1PK',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'GSI1SK',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # テーブルが作成されるまで待機
        table.wait_until_exists()
        yield table

class TestCreateRoadmap:
    """ロードマップ作成のテスト"""
    
    def test_create_roadmap_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常なロードマップ作成のテスト"""
        # テストデータ
        roadmap_data = {
            "title": "React学習ロードマップ",
            "description": "React基礎から応用まで",
            "items": [
                {
                    "title": "React基礎",
                    "estimated_hours": 20.0,
                    "completed_hours": 0.0
                },
                {
                    "title": "Hooks学習",
                    "estimated_hours": 15.0,
                    "completed_hours": 0.0
                }
            ]
        }
        
        # イベント設定
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["body"] = json.dumps(roadmap_data)
        
        # DynamoDBのモックパッチ
        with patch('main.table', dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        # レスポンス検証
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert response_body["title"] == roadmap_data["title"]
        assert response_body["total_hours"] == 35.0
        assert response_body["progress"] == 0.0
        assert len(response_body["items"]) == 2
    
    def test_create_roadmap_missing_title(self, api_gateway_event, lambda_context):
        """タイトルが欠けている場合のテスト"""
        roadmap_data = {
            "items": [
                {
                    "title": "React基礎",
                    "estimated_hours": 20.0
                }
            ]
        }
        
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["body"] = json.dumps(roadmap_data)
        
        response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 400
        assert "title" in response["body"]
    
    def test_create_roadmap_invalid_hours(self, api_gateway_event, lambda_context):
        """無効な時間データの場合のテスト"""
        roadmap_data = {
            "title": "テストロードマップ",
            "items": [
                {
                    "title": "React基礎",
                    "estimated_hours": -5.0  # 無効な値
                }
            ]
        }
        
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["body"] = json.dumps(roadmap_data)
        
        response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 400
        assert "0より大きい値" in response["body"]

class TestListRoadmaps:
    """ロードマップ一覧取得のテスト"""
    
    def test_list_roadmaps_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常なロードマップ一覧取得のテスト"""
        # テストデータを事前に挿入
        test_roadmap = {
            'PK': f'USER#{DUMMY_USER_ID}',
            'SK': 'ROADMAP#test-roadmap-1',
            'GSI1PK': f'USER#{DUMMY_USER_ID}',
            'GSI1SK': 'ROADMAP#2023-12-01T00:00:00',
            'roadmap_id': 'test-roadmap-1',
            'title': 'テストロードマップ',
            'description': 'テスト用',
            'items': [
                {
                    'title': 'アイテム1',
                    'estimated_hours': Decimal('10'),
                    'completed_hours': Decimal('5'),
                    'progress': Decimal('50')
                }
            ],
            'total_hours': Decimal('10'),
            'completed_hours': Decimal('5'),
            'progress': Decimal('50'),
            'status': 'active',
            'created_at': '2023-12-01T00:00:00',
            'updated_at': '2023-12-01T00:00:00'
        }
        dynamodb_table.put_item(Item=test_roadmap)
        
        # イベント設定
        api_gateway_event["httpMethod"] = "GET"
        api_gateway_event["path"] = "/roadmap"
        
        with patch('main.table', dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert "roadmaps" in response_body
        assert len(response_body["roadmaps"]) == 1
        assert response_body["roadmaps"][0]["title"] == "テストロードマップ"

class TestGetRoadmap:
    """ロードマップ詳細取得のテスト"""
    
    def test_get_roadmap_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常なロードマップ詳細取得のテスト"""
        roadmap_id = "test-roadmap-1"
        
        # テストデータを事前に挿入
        test_roadmap = {
            'PK': f'USER#{DUMMY_USER_ID}',
            'SK': f'ROADMAP#{roadmap_id}',
            'roadmap_id': roadmap_id,
            'title': 'テストロードマップ',
            'description': 'テスト用',
            'items': [],
            'total_hours': Decimal('10'),
            'status': 'active',
            'created_at': '2023-12-01T00:00:00',
            'updated_at': '2023-12-01T00:00:00'
        }
        dynamodb_table.put_item(Item=test_roadmap)
        
        # イベント設定
        api_gateway_event["httpMethod"] = "GET"
        api_gateway_event["path"] = f"/roadmap/{roadmap_id}"
        api_gateway_event["pathParameters"] = {"roadmapId": roadmap_id}
        
        with patch('main.table', dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert response_body["roadmap_id"] == roadmap_id
        assert response_body["title"] == "テストロードマップ"
    
    def test_get_roadmap_not_found(self, api_gateway_event, lambda_context, dynamodb_table):
        """存在しないロードマップのテスト"""
        roadmap_id = "non-existent-roadmap"
        
        api_gateway_event["httpMethod"] = "GET"
        api_gateway_event["path"] = f"/roadmap/{roadmap_id}"
        api_gateway_event["pathParameters"] = {"roadmapId": roadmap_id}
        
        with patch('main.table', dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 404
        assert "見つかりません" in response["body"]

class TestUpdateRoadmap:
    """ロードマップ更新のテスト"""
    
    def test_update_roadmap_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常なロードマップ更新のテスト"""
        roadmap_id = "test-roadmap-1"
        
        # 既存のロードマップを作成
        existing_roadmap = {
            'PK': f'USER#{DUMMY_USER_ID}',
            'SK': f'ROADMAP#{roadmap_id}',
            'roadmap_id': roadmap_id,
            'title': '元のタイトル',
            'description': '元の説明',
            'items': [
                {
                    'title': 'アイテム1',
                    'estimated_hours': Decimal('10'),
                    'completed_hours': Decimal('0'),
                    'progress': Decimal('0')
                }
            ],
            'total_hours': Decimal('10'),
            'completed_hours': Decimal('0'),
            'progress': Decimal('0'),
            'status': 'active',
            'created_at': '2023-12-01T00:00:00',
            'updated_at': '2023-12-01T00:00:00'
        }
        dynamodb_table.put_item(Item=existing_roadmap)
        
        # 更新データ
        update_data = {
            "title": "更新されたタイトル",
            "description": "更新された説明"
        }
        
        # イベント設定
        api_gateway_event["httpMethod"] = "PUT"
        api_gateway_event["path"] = f"/roadmap/{roadmap_id}"
        api_gateway_event["pathParameters"] = {"roadmapId": roadmap_id}
        api_gateway_event["body"] = json.dumps(update_data)
        
        with patch('main.table', dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert response_body["title"] == "更新されたタイトル"
        assert response_body["description"] == "更新された説明"

class TestDeleteRoadmap:
    """ロードマップ削除のテスト"""
    
    def test_delete_roadmap_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常なロードマップ削除のテスト"""
        roadmap_id = "test-roadmap-1"
        
        # 既存のロードマップを作成
        existing_roadmap = {
            'PK': f'USER#{DUMMY_USER_ID}',
            'SK': f'ROADMAP#{roadmap_id}',
            'roadmap_id': roadmap_id,
            'title': 'テストロードマップ',
            'status': 'active',
            'created_at': '2023-12-01T00:00:00',
            'updated_at': '2023-12-01T00:00:00'
        }
        dynamodb_table.put_item(Item=existing_roadmap)
        
        # イベント設定
        api_gateway_event["httpMethod"] = "DELETE"
        api_gateway_event["path"] = f"/roadmap/{roadmap_id}"
        api_gateway_event["pathParameters"] = {"roadmapId": roadmap_id}
        
        with patch('main.table', dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        assert "削除されました" in response["body"]

class TestCSVImport:
    """CSVインポートのテスト"""
    
    def test_import_csv_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常なCSVインポートのテスト"""
        csv_data = {
            "title": "インポートテスト",
            "csv_content": "React基礎,20,5\nHooks学習,15,0\nState管理,10,10"
        }
        
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["path"] = "/roadmap/import"
        api_gateway_event["body"] = json.dumps(csv_data)
        
        with patch('main.table', dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert response_body["title"] == "インポートテスト"
        assert len(response_body["items"]) == 3
        assert response_body["total_hours"] == 45.0
    
    def test_import_csv_invalid_format(self, api_gateway_event, lambda_context):
        """無効なCSVフォーマットのテスト"""
        csv_data = {
            "csv_content": "無効な,データ,形式,extra"
        }
        
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["path"] = "/roadmap/import"
        api_gateway_event["body"] = json.dumps(csv_data)
        
        response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 400

class TestCSVTemplate:
    """CSVテンプレートのテスト"""
    
    def test_download_csv_template(self, api_gateway_event, lambda_context):
        """CSVテンプレートダウンロードのテスト"""
        api_gateway_event["httpMethod"] = "GET"
        api_gateway_event["path"] = "/roadmap/template"
        
        response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        assert response["headers"]["Content-Type"] == "text/csv; charset=utf-8"
        assert "タイトル,予定時間,完了時間" in response["body"]

class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def test_unauthorized_request(self, api_gateway_event, lambda_context):
        """認証情報がない場合のテスト"""
        # 認証情報を削除
        api_gateway_event["requestContext"] = {}
        
        response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 401
        assert "認証が必要" in response["body"]
    
    def test_unsupported_method(self, api_gateway_event, lambda_context):
        """サポートされていないHTTPメソッドのテスト"""
        api_gateway_event["httpMethod"] = "PATCH"
        
        response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 405
        assert "サポートされていない" in response["body"]
    
    def test_invalid_json_body(self, api_gateway_event, lambda_context):
        """無効なJSONボディのテスト"""
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["body"] = "invalid json"
        
        response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 400
        assert "無効なJSONフォーマット" in response["body"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])