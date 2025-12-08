"""
pytest設定とフィクスチャ定義
"""

import os
import sys
import pytest
from unittest.mock import patch

# テスト対象モジュールのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lambda'))

# テスト用環境変数の設定
os.environ.setdefault('ENV', 'test')
os.environ.setdefault('DYNAMODB_TABLE_NAME', 'LearningPlatform')
os.environ.setdefault('LOG_LEVEL', 'DEBUG')

@pytest.fixture(scope="session")
def test_env():
    """テスト環境の設定"""
    return {
        'ENV': 'test',
        'DYNAMODB_TABLE_NAME': 'LearningPlatform',
        'LOG_LEVEL': 'DEBUG'
    }

@pytest.fixture(scope="function")
def mock_env(test_env):
    """環境変数のモック"""
    with patch.dict(os.environ, test_env):
        yield test_env

def pytest_configure(config):
    """pytest設定"""
    # カスタムマーカーの追加
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "aws: mark test as requiring AWS services"
    )

def pytest_collection_modifyitems(config, items):
    """テスト実行時の設定変更"""
    if config.getoption("--cov"):
        # カバレッジ測定時の設定
        pass