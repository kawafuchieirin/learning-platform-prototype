"""
学習記録API Lambda関数のユニットテスト
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
    create_record,
    list_records,
    get_record,
    update_record,
    delete_record,
    create_record_from_template,
    get_record_templates
)

# テスト用のダミーデータ
DUMMY_USER_ID = "test-user-id"

@pytest.fixture
def api_gateway_event():
    """API Gateway イベントのベース"""
    return {
        "httpMethod": "GET",
        "path": "/records",
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
    context.function_name = "records-api"
    context.function_version = "1"
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:records-api"
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

class TestCreateRecord:
    """学習記録作成のテスト"""
    
    def test_create_record_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常な学習記録作成のテスト"""
        record_data = {
            "title": "React学習",
            "content": "React Hooksについて学習しました",
            "duration_minutes": 120,
            "study_date": "2023-12-01",
            "tags": ["react", "javascript"],
            "difficulty": "medium",
            "satisfaction": 4,
            "notes": "とても勉強になりました"
        }
        
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["body"] = json.dumps(record_data)
        
        with patch('main.get_dynamodb_table', return_value=dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert response_body["title"] == record_data["title"]
        assert response_body["duration_minutes"] == record_data["duration_minutes"]
        assert response_body["status"] == "active"
    
    def test_create_record_missing_title(self, api_gateway_event, lambda_context):
        """タイトルが欠けている場合のテスト"""
        record_data = {
            "content": "学習内容",
            "duration_minutes": 60
        }
        
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["body"] = json.dumps(record_data)
        
        response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 400
        assert "title" in response["body"]
    
    def test_create_record_invalid_duration(self, api_gateway_event, lambda_context):
        """無効な学習時間の場合のテスト"""
        record_data = {
            "title": "テスト学習",
            "duration_minutes": -30
        }
        
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["body"] = json.dumps(record_data)
        
        response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 400
        assert "0より大きい値" in response["body"]

class TestListRecords:
    """学習記録一覧取得のテスト"""
    
    def test_list_records_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常な学習記録一覧取得のテスト"""
        # テストデータを事前に挿入
        test_record = {
            'PK': f'USER#{DUMMY_USER_ID}',
            'SK': 'RECORD#test-record-1',
            'GSI1PK': f'USER#{DUMMY_USER_ID}',
            'GSI1SK': 'RECORD#2023-12-01#2023-12-01T10:00:00',
            'record_id': 'test-record-1',
            'title': 'テスト学習記録',
            'content': 'テスト用の学習記録です',
            'duration_minutes': 60,
            'study_date': '2023-12-01',
            'tags': ['test'],
            'difficulty': 'medium',
            'satisfaction': 3,
            'status': 'active',
            'created_at': '2023-12-01T10:00:00',
            'updated_at': '2023-12-01T10:00:00'
        }
        dynamodb_table.put_item(Item=test_record)
        
        api_gateway_event["httpMethod"] = "GET"
        api_gateway_event["path"] = "/records"
        
        with patch('main.get_dynamodb_table', return_value=dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert "records" in response_body
        assert len(response_body["records"]) == 1
        assert response_body["records"][0]["title"] == "テスト学習記録"
        assert "statistics" in response_body

class TestGetRecord:
    """学習記録詳細取得のテスト"""
    
    def test_get_record_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常な学習記録詳細取得のテスト"""
        record_id = "test-record-1"
        
        test_record = {
            'PK': f'USER#{DUMMY_USER_ID}',
            'SK': f'RECORD#{record_id}',
            'record_id': record_id,
            'title': 'テスト学習記録',
            'content': 'テスト用の学習記録です',
            'duration_minutes': 60,
            'status': 'active',
            'created_at': '2023-12-01T10:00:00',
            'updated_at': '2023-12-01T10:00:00'
        }
        dynamodb_table.put_item(Item=test_record)
        
        api_gateway_event["httpMethod"] = "GET"
        api_gateway_event["path"] = f"/records/{record_id}"
        api_gateway_event["pathParameters"] = {"recordId": record_id}
        
        with patch('main.get_dynamodb_table', return_value=dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert response_body["record_id"] == record_id
        assert response_body["title"] == "テスト学習記録"
    
    def test_get_record_not_found(self, api_gateway_event, lambda_context, dynamodb_table):
        """存在しない学習記録のテスト"""
        record_id = "non-existent-record"
        
        api_gateway_event["httpMethod"] = "GET"
        api_gateway_event["path"] = f"/records/{record_id}"
        api_gateway_event["pathParameters"] = {"recordId": record_id}
        
        with patch('main.get_dynamodb_table', return_value=dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 404
        assert "見つかりません" in response["body"]

class TestUpdateRecord:
    """学習記録更新のテスト"""
    
    def test_update_record_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常な学習記録更新のテスト"""
        record_id = "test-record-1"
        
        existing_record = {
            'PK': f'USER#{DUMMY_USER_ID}',
            'SK': f'RECORD#{record_id}',
            'record_id': record_id,
            'title': '元のタイトル',
            'content': '元の内容',
            'duration_minutes': 60,
            'status': 'active',
            'created_at': '2023-12-01T10:00:00',
            'updated_at': '2023-12-01T10:00:00'
        }
        dynamodb_table.put_item(Item=existing_record)
        
        update_data = {
            "title": "更新されたタイトル",
            "content": "更新された内容",
            "duration_minutes": 90
        }
        
        api_gateway_event["httpMethod"] = "PUT"
        api_gateway_event["path"] = f"/records/{record_id}"
        api_gateway_event["pathParameters"] = {"recordId": record_id}
        api_gateway_event["body"] = json.dumps(update_data)
        
        with patch('main.get_dynamodb_table', return_value=dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert response_body["title"] == "更新されたタイトル"
        assert response_body["duration_minutes"] == 90

class TestDeleteRecord:
    """学習記録削除のテスト"""
    
    def test_delete_record_success(self, api_gateway_event, lambda_context, dynamodb_table):
        """正常な学習記録削除のテスト"""
        record_id = "test-record-1"
        
        existing_record = {
            'PK': f'USER#{DUMMY_USER_ID}',
            'SK': f'RECORD#{record_id}',
            'record_id': record_id,
            'title': 'テスト学習記録',
            'status': 'active',
            'created_at': '2023-12-01T10:00:00',
            'updated_at': '2023-12-01T10:00:00'
        }
        dynamodb_table.put_item(Item=existing_record)
        
        api_gateway_event["httpMethod"] = "DELETE"
        api_gateway_event["path"] = f"/records/{record_id}"
        api_gateway_event["pathParameters"] = {"recordId": record_id}
        
        with patch('main.get_dynamodb_table', return_value=dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        assert "削除されました" in response["body"]

class TestTemplateFeatures:
    """テンプレート機能のテスト"""
    
    def test_get_record_templates(self, api_gateway_event, lambda_context):
        """記録テンプレート取得のテスト"""
        api_gateway_event["httpMethod"] = "GET"
        api_gateway_event["path"] = "/records/templates"
        
        with patch('main.get_user_roadmap_items') as mock_roadmap:
            mock_roadmap.return_value = [
                {
                    'roadmap_id': 'test-roadmap',
                    'roadmap_title': 'テストロードマップ',
                    'item_title': 'React基礎',
                    'estimated_hours': 20,
                    'completed_hours': 5,
                    'progress': 25
                }
            ]
            
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert "templates" in response_body
        assert len(response_body["templates"]) >= 4  # 基本4種類のテンプレート
        
        # ロードマップテンプレートの確認
        roadmap_template = next(
            (t for t in response_body["templates"] if t["template_type"] == "roadmap"), 
            None
        )
        assert roadmap_template is not None
        assert "roadmap_items" in roadmap_template
    
    def test_create_record_from_template(self, api_gateway_event, lambda_context, dynamodb_table):
        """テンプレートからの記録作成テスト"""
        template_data = {
            "template_type": "reading",
            "title": "JavaScript本の読書",
            "duration_minutes": 90,
            "satisfaction": 5
        }
        
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["path"] = "/records/from-template"
        api_gateway_event["body"] = json.dumps(template_data)
        
        with patch('main.get_dynamodb_table', return_value=dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert response_body["title"] == "JavaScript本の読書"
        assert response_body["duration_minutes"] == 90
        assert response_body["satisfaction"] == 5
        assert "reading" in response_body["tags"]

class TestRoadmapIntegration:
    """ロードマップ連携のテスト"""
    
    @patch('main.update_roadmap_progress')
    def test_create_record_with_roadmap(self, mock_update_progress, api_gateway_event, lambda_context, dynamodb_table):
        """ロードマップに紐づく記録作成のテスト"""
        record_data = {
            "title": "ロードマップ学習",
            "content": "React基礎の学習",
            "duration_minutes": 120,
            "roadmap_id": "test-roadmap-id",
            "roadmap_item_title": "React基礎"
        }
        
        api_gateway_event["httpMethod"] = "POST"
        api_gateway_event["body"] = json.dumps(record_data)
        
        with patch('main.get_dynamodb_table', return_value=dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        assert response_body["roadmap_id"] == "test-roadmap-id"
        assert response_body["roadmap_item_title"] == "React基礎"
        
        # ロードマップ進捗更新が呼び出されたことを確認
        mock_update_progress.assert_called_once_with(
            DUMMY_USER_ID, "test-roadmap-id", "React基礎", 2.0
        )

class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def test_unauthorized_request(self, api_gateway_event, lambda_context):
        """認証情報がない場合のテスト"""
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

class TestQueryFilters:
    """クエリフィルターのテスト"""
    
    def test_list_records_with_date_filter(self, api_gateway_event, lambda_context, dynamodb_table):
        """日付フィルターでの記録一覧取得テスト"""
        # 複数の日付の記録を作成
        records = [
            {
                'PK': f'USER#{DUMMY_USER_ID}',
                'SK': 'RECORD#record1',
                'GSI1PK': f'USER#{DUMMY_USER_ID}',
                'GSI1SK': 'RECORD#2023-12-01#2023-12-01T10:00:00',
                'record_id': 'record1',
                'title': '12月1日の記録',
                'duration_minutes': 60,
                'study_date': '2023-12-01',
                'status': 'active',
                'created_at': '2023-12-01T10:00:00',
                'updated_at': '2023-12-01T10:00:00'
            },
            {
                'PK': f'USER#{DUMMY_USER_ID}',
                'SK': 'RECORD#record2',
                'GSI1PK': f'USER#{DUMMY_USER_ID}',
                'GSI1SK': 'RECORD#2023-12-05#2023-12-05T10:00:00',
                'record_id': 'record2',
                'title': '12月5日の記録',
                'duration_minutes': 90,
                'study_date': '2023-12-05',
                'status': 'active',
                'created_at': '2023-12-05T10:00:00',
                'updated_at': '2023-12-05T10:00:00'
            }
        ]
        
        for record in records:
            dynamodb_table.put_item(Item=record)
        
        api_gateway_event["httpMethod"] = "GET"
        api_gateway_event["path"] = "/records"
        api_gateway_event["queryStringParameters"] = {
            "date_from": "2023-12-01",
            "date_to": "2023-12-03"
        }
        
        with patch('main.get_dynamodb_table', return_value=dynamodb_table):
            response = lambda_handler(api_gateway_event, lambda_context)
        
        assert response["statusCode"] == 200
        
        response_body = json.loads(response["body"])
        # 日付範囲内の記録のみ取得される
        assert len(response_body["records"]) == 1
        assert response_body["records"][0]["title"] == "12月1日の記録"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])