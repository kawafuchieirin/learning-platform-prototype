#!/usr/bin/env python3
"""
DynamoDB Localの初期化スクリプト
必要なテーブルを作成します
"""

import boto3
import json
from botocore.exceptions import ClientError

# DynamoDB Local設定（Analytics用）
DYNAMODB_LOCAL_ENDPOINT = "http://localhost:8004"
REGION = "ap-northeast-1"

def create_dynamodb_client():
    """DynamoDB Localクライアントを作成"""
    return boto3.resource(
        'dynamodb',
        endpoint_url=DYNAMODB_LOCAL_ENDPOINT,
        region_name=REGION,
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy'
    )

def create_users_table(dynamodb):
    """Usersテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='Users',
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
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {table.name}")
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"✓ Table already exists: Users")
            return dynamodb.Table('Users')
        else:
            raise

def create_timer_table(dynamodb):
    """Timerテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='Timer',
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
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {table.name}")
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"✓ Table already exists: Timer")
            return dynamodb.Table('Timer')
        else:
            raise

def create_roadmap_table(dynamodb):
    """Roadmapテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='Roadmap',
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
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {table.name}")
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"✓ Table already exists: Roadmap")
            return dynamodb.Table('Roadmap')
        else:
            raise

def create_records_table(dynamodb):
    """Recordsテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='Records',
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
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {table.name}")
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"✓ Table already exists: Records")
            return dynamodb.Table('Records')
        else:
            raise

def create_slack_config_table(dynamodb):
    """SlackConfigテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='SlackConfig',
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
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {table.name}")
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"✓ Table already exists: SlackConfig")
            return dynamodb.Table('SlackConfig')
        else:
            raise

def insert_sample_data(dynamodb):
    """サンプルデータを挿入"""
    users_table = dynamodb.Table('Users')
    
    # サンプルユーザー
    sample_user = {
        'PK': 'USER#test-user-1',
        'SK': 'PROFILE',
        'email': 'test@example.com',
        'name': 'テストユーザー',
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z'
    }
    
    try:
        users_table.put_item(Item=sample_user)
        print("✓ Inserted sample user data")
    except Exception as e:
        print(f"✓ Sample user data already exists or error: {e}")

def main():
    """メイン処理"""
    print("🚀 Initializing DynamoDB Local...")
    print(f"Endpoint: {DYNAMODB_LOCAL_ENDPOINT}")
    
    try:
        dynamodb = create_dynamodb_client()
        
        # テーブル作成
        print("\n📋 Creating tables...")
        create_users_table(dynamodb)
        create_timer_table(dynamodb)
        create_roadmap_table(dynamodb)
        create_records_table(dynamodb)
        create_slack_config_table(dynamodb)
        
        # サンプルデータ挿入
        print("\n💾 Inserting sample data...")
        insert_sample_data(dynamodb)
        
        print("\n🎉 DynamoDB Local initialization completed!")
        print("\n📊 You can view the tables at: http://localhost:8002")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please make sure DynamoDB Local is running:")
        print("docker-compose up -d dynamodb-local")

if __name__ == "__main__":
    main()