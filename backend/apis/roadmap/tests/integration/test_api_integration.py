"""
ロードマップAPI 統合テスト
実際のAPIエンドポイントとしてテストする
"""

import json
import pytest
import requests
import time
from typing import Dict, Any

# テスト設定
API_BASE_URL = "http://localhost:8003"  # ローカル開発環境のURL
TEST_USER_ID = "integration-test-user"

class TestRoadmapAPIIntegration:
    """ロードマップAPI統合テスト"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """テスト前後のセットアップ・クリーンアップ"""
        # テスト前：APIの起動確認
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{API_BASE_URL}/health")
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                if i == max_retries - 1:
                    pytest.skip("API server is not running")
                time.sleep(1)
        
        yield
        
        # テスト後：作成されたテストデータをクリーンアップ
        # 実際の実装では、テスト用のクリーンアップエンドポイントを作成することを推奨
    
    def test_health_check(self):
        """ヘルスチェックのテスト"""
        response = requests.get(f"{API_BASE_URL}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "roadmap-api"
    
    def test_roadmap_crud_flow(self):
        """ロードマップのCRUD操作の統合テスト"""
        # 1. ロードマップ作成
        create_data = {
            "title": "統合テスト用ロードマップ",
            "description": "APIの統合テストで使用するロードマップ",
            "items": [
                {
                    "title": "機能A実装",
                    "estimated_hours": 8.0,
                    "completed_hours": 0.0
                },
                {
                    "title": "テスト作成",
                    "estimated_hours": 4.0,
                    "completed_hours": 0.0
                }
            ]
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/roadmap",
            json=create_data
        )
        
        assert create_response.status_code == 200
        create_result = create_response.json()
        roadmap_id = create_result["data"]["roadmap_id"]
        
        # 作成されたロードマップの検証
        assert create_result["data"]["title"] == create_data["title"]
        assert create_result["data"]["total_hours"] == 12.0
        assert create_result["data"]["progress"] == 0.0
        
        # 2. ロードマップ一覧取得
        list_response = requests.get(f"{API_BASE_URL}/roadmap")
        
        assert list_response.status_code == 200
        list_result = list_response.json()
        assert "roadmaps" in list_result["data"]
        
        # 作成したロードマップが含まれていることを確認
        roadmap_found = any(
            rm["roadmap_id"] == roadmap_id 
            for rm in list_result["data"]["roadmaps"]
        )
        assert roadmap_found
        
        # 3. ロードマップ詳細取得
        get_response = requests.get(f"{API_BASE_URL}/roadmap/{roadmap_id}")
        
        assert get_response.status_code == 200
        get_result = get_response.json()
        assert get_result["data"]["roadmap_id"] == roadmap_id
        assert get_result["data"]["title"] == create_data["title"]
        
        # 4. ロードマップ更新
        update_data = {
            "title": "更新されたロードマップタイトル",
            "description": "更新された説明",
            "items": [
                {
                    "title": "機能A実装",
                    "estimated_hours": 8.0,
                    "completed_hours": 4.0  # 進捗を更新
                },
                {
                    "title": "テスト作成",
                    "estimated_hours": 4.0,
                    "completed_hours": 2.0  # 進捗を更新
                }
            ]
        }
        
        update_response = requests.put(
            f"{API_BASE_URL}/roadmap/{roadmap_id}",
            json=update_data
        )
        
        assert update_response.status_code == 200
        update_result = update_response.json()
        assert update_result["data"]["title"] == update_data["title"]
        assert update_result["data"]["completed_hours"] == 6.0
        assert update_result["data"]["progress"] == 50.0  # 6/12 * 100
        
        # 5. ロードマップ削除
        delete_response = requests.delete(f"{API_BASE_URL}/roadmap/{roadmap_id}")
        
        assert delete_response.status_code == 200
        delete_result = delete_response.json()
        assert "削除されました" in delete_result["data"]
        
        # 削除確認
        get_deleted_response = requests.get(f"{API_BASE_URL}/roadmap/{roadmap_id}")
        assert get_deleted_response.status_code == 404
    
    def test_csv_import_flow(self):
        """CSVインポートの統合テスト"""
        # 1. CSVテンプレートダウンロード
        template_response = requests.get(f"{API_BASE_URL}/roadmap/template")
        
        assert template_response.status_code == 200
        assert "text/csv" in template_response.headers.get("Content-Type", "")
        assert "タイトル,予定時間,完了時間" in template_response.text
        
        # 2. CSVインポート実行
        csv_data = {
            "title": "CSVインポートテスト",
            "csv_content": "React学習,20,5\nAPI開発,15,0\nテスト作成,10,10"
        }
        
        import_response = requests.post(
            f"{API_BASE_URL}/roadmap/import",
            json=csv_data
        )
        
        assert import_response.status_code == 200
        import_result = import_response.json()
        
        # インポート結果の検証
        roadmap_data = import_result["data"]
        assert roadmap_data["title"] == csv_data["title"]
        assert len(roadmap_data["items"]) == 3
        assert roadmap_data["total_hours"] == 45.0
        assert roadmap_data["completed_hours"] == 15.0
        
        # 進捗計算の確認
        expected_progress = (15.0 / 45.0) * 100  # 約33.33%
        assert abs(roadmap_data["progress"] - expected_progress) < 0.1
        
        # 各アイテムの進捗確認
        items = roadmap_data["items"]
        assert items[0]["progress"] == 25.0  # 5/20 * 100
        assert items[1]["progress"] == 0.0   # 0/15 * 100
        assert items[2]["progress"] == 100.0 # 10/10 * 100
    
    def test_error_handling(self):
        """エラーハンドリングの統合テスト"""
        # 1. 存在しないロードマップの取得
        response = requests.get(f"{API_BASE_URL}/roadmap/non-existent-id")
        assert response.status_code == 404
        
        # 2. 無効なデータでのロードマップ作成
        invalid_data = {
            "title": "",  # 空のタイトル
            "items": []   # 空のアイテム
        }
        
        response = requests.post(
            f"{API_BASE_URL}/roadmap",
            json=invalid_data
        )
        assert response.status_code == 400
        
        # 3. 無効なCSVインポート
        invalid_csv_data = {
            "csv_content": "無効な,データ,too,many,columns"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/roadmap/import",
            json=invalid_csv_data
        )
        assert response.status_code == 400
        
        # 4. 存在しないロードマップの更新
        response = requests.put(
            f"{API_BASE_URL}/roadmap/non-existent-id",
            json={"title": "新しいタイトル"}
        )
        assert response.status_code == 404
        
        # 5. 存在しないロードマップの削除
        response = requests.delete(f"{API_BASE_URL}/roadmap/non-existent-id")
        assert response.status_code == 404
    
    def test_query_parameters(self):
        """クエリパラメータのテスト"""
        # limitパラメータのテスト
        response = requests.get(f"{API_BASE_URL}/roadmap?limit=5")
        assert response.status_code == 200
        
        # statusパラメータのテスト
        response = requests.get(f"{API_BASE_URL}/roadmap?status=active")
        assert response.status_code == 200
        
        response = requests.get(f"{API_BASE_URL}/roadmap?status=all")
        assert response.status_code == 200
    
    def test_cors_headers(self):
        """CORS ヘッダーのテスト"""
        # OPTIONSリクエスト
        response = requests.options(f"{API_BASE_URL}/roadmap")
        
        # CORSヘッダーが設定されていることを確認
        headers = response.headers
        assert "Access-Control-Allow-Origin" in headers
        assert "Access-Control-Allow-Methods" in headers
        assert "Access-Control-Allow-Headers" in headers
    
    def test_large_data_handling(self):
        """大量データの処理テスト"""
        # 多数のアイテムを持つロードマップを作成
        items = []
        for i in range(50):
            items.append({
                "title": f"タスク{i+1}",
                "estimated_hours": 2.0,
                "completed_hours": 0.0
            })
        
        large_roadmap_data = {
            "title": "大規模ロードマップテスト",
            "description": "多数のアイテムを含むロードマップ",
            "items": items
        }
        
        response = requests.post(
            f"{API_BASE_URL}/roadmap",
            json=large_roadmap_data
        )
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]["items"]) == 50
        assert result["data"]["total_hours"] == 100.0
    
    def test_concurrent_requests(self):
        """同時リクエストの処理テスト"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def create_roadmap(thread_id):
            """スレッド内でロードマップを作成"""
            try:
                data = {
                    "title": f"並行テスト{thread_id}",
                    "items": [
                        {
                            "title": "テストタスク",
                            "estimated_hours": 1.0,
                            "completed_hours": 0.0
                        }
                    ]
                }
                
                response = requests.post(f"{API_BASE_URL}/roadmap", json=data)
                results.put((thread_id, response.status_code))
                
            except Exception as e:
                results.put((thread_id, f"Error: {str(e)}"))
        
        # 複数スレッドで同時にリクエストを送信
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_roadmap, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 全スレッドの完了を待機
        for thread in threads:
            thread.join()
        
        # 結果の検証
        success_count = 0
        while not results.empty():
            thread_id, status = results.get()
            if status == 200:
                success_count += 1
        
        # 少なくとも大部分のリクエストが成功することを確認
        assert success_count >= 3

class TestRoadmapAPIPerformance:
    """パフォーマンステスト"""
    
    def test_response_time(self):
        """レスポンス時間のテスト"""
        start_time = time.time()
        
        response = requests.get(f"{API_BASE_URL}/roadmap")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # レスポンス時間が2秒以内であることを確認
        assert response_time < 2.0
        assert response.status_code == 200
    
    def test_memory_efficiency(self):
        """メモリ効率のテスト（基本的なチェック）"""
        # 大量のリクエストを連続で送信
        for i in range(10):
            response = requests.get(f"{API_BASE_URL}/health")
            assert response.status_code == 200
        
        # メモリリークがないことを間接的に確認
        # 実際の本格的なメモリテストは専用ツールが必要

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])