"""
学習記録API 統合テスト
実際のAPIエンドポイントとしてテストする
"""

import json
import pytest
import requests
import time
from typing import Dict, Any

# テスト設定
API_BASE_URL = "http://localhost:8009"  # ローカル開発環境のURL
TEST_USER_ID = "integration-test-user"

class TestRecordsAPIIntegration:
    """学習記録API統合テスト"""
    
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
        assert data["service"] == "records-api"
    
    def test_record_crud_flow(self):
        """学習記録のCRUD操作の統合テスト"""
        # 1. 学習記録作成
        create_data = {
            "title": "統合テスト用学習記録",
            "content": "APIの統合テストで使用する学習記録です",
            "duration_minutes": 120,
            "study_date": "2023-12-08",
            "tags": ["integration-test", "api"],
            "difficulty": "medium",
            "satisfaction": 4,
            "notes": "テスト用の記録です"
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/records",
            json=create_data
        )
        
        assert create_response.status_code == 200
        create_result = create_response.json()
        record_id = create_result["record_id"]
        
        # 作成された記録の検証
        assert create_result["title"] == create_data["title"]
        assert create_result["duration_minutes"] == create_data["duration_minutes"]
        assert create_result["status"] == "active"
        
        # 2. 学習記録一覧取得
        list_response = requests.get(f"{API_BASE_URL}/records")
        
        assert list_response.status_code == 200
        list_result = list_response.json()
        assert "records" in list_result
        assert "statistics" in list_result
        
        # 作成した記録が含まれていることを確認
        record_found = any(
            record["record_id"] == record_id 
            for record in list_result["records"]
        )
        assert record_found
        
        # 3. 学習記録詳細取得
        get_response = requests.get(f"{API_BASE_URL}/records/{record_id}")
        
        assert get_response.status_code == 200
        get_result = get_response.json()
        assert get_result["record_id"] == record_id
        assert get_result["title"] == create_data["title"]
        
        # 4. 学習記録更新
        update_data = {
            "title": "更新された学習記録タイトル",
            "content": "更新された内容です",
            "duration_minutes": 150,
            "satisfaction": 5
        }
        
        update_response = requests.put(
            f"{API_BASE_URL}/records/{record_id}",
            json=update_data
        )
        
        assert update_response.status_code == 200
        update_result = update_response.json()
        assert update_result["title"] == update_data["title"]
        assert update_result["duration_minutes"] == update_data["duration_minutes"]
        assert update_result["satisfaction"] == update_data["satisfaction"]
        
        # 5. 学習記録削除
        delete_response = requests.delete(f"{API_BASE_URL}/records/{record_id}")
        
        assert delete_response.status_code == 200
        delete_result = delete_response.json()
        assert "削除されました" in delete_result["message"]
        
        # 削除確認
        get_deleted_response = requests.get(f"{API_BASE_URL}/records/{record_id}")
        assert get_deleted_response.status_code == 404
    
    def test_template_functionality(self):
        """テンプレート機能の統合テスト"""
        # 1. テンプレート一覧取得
        templates_response = requests.get(f"{API_BASE_URL}/records/templates")
        
        assert templates_response.status_code == 200
        templates_result = templates_response.json()
        assert "templates" in templates_result
        
        templates = templates_result["templates"]
        assert len(templates) >= 4  # 基本4種類のテンプレート
        
        # 各テンプレートタイプの存在確認
        template_types = {t["template_type"] for t in templates}
        expected_types = {"roadmap", "reading", "coding", "video"}
        assert expected_types.issubset(template_types)
        
        # 2. 読書テンプレートから記録作成
        reading_template_data = {
            "template_type": "reading",
            "title": "JavaScript入門書の読書",
            "duration_minutes": 180,
            "satisfaction": 5,
            "notes": "とても良い本でした"
        }
        
        template_response = requests.post(
            f"{API_BASE_URL}/records/from-template",
            json=reading_template_data
        )
        
        assert template_response.status_code == 200
        template_result = template_response.json()
        
        # テンプレートから作成された記録の検証
        assert template_result["title"] == reading_template_data["title"]
        assert template_result["duration_minutes"] == reading_template_data["duration_minutes"]
        assert "reading" in template_result["tags"]
        assert template_result["difficulty"] == "easy"  # 読書テンプレートのデフォルト
        
        # 3. コーディングテンプレートから記録作成
        coding_template_data = {
            "template_type": "coding",
            "title": "React Hooksの実装練習",
            "duration_minutes": 240,
            "difficulty": "hard",
            "satisfaction": 4
        }
        
        coding_response = requests.post(
            f"{API_BASE_URL}/records/from-template",
            json=coding_template_data
        )
        
        assert coding_response.status_code == 200
        coding_result = coding_response.json()
        
        assert coding_result["title"] == coding_template_data["title"]
        assert "coding" in coding_result["tags"]
        assert coding_result["difficulty"] == "hard"
    
    def test_query_filters(self):
        """クエリフィルターの統合テスト"""
        # テスト用の記録を複数作成
        test_records = [
            {
                "title": "2023年12月1日の学習",
                "content": "JavaScript基礎",
                "duration_minutes": 60,
                "study_date": "2023-12-01"
            },
            {
                "title": "2023年12月3日の学習", 
                "content": "React学習",
                "duration_minutes": 90,
                "study_date": "2023-12-03"
            },
            {
                "title": "2023年12月5日の学習",
                "content": "Node.js学習",
                "duration_minutes": 120,
                "study_date": "2023-12-05"
            }
        ]
        
        created_records = []
        for record_data in test_records:
            response = requests.post(f"{API_BASE_URL}/records", json=record_data)
            assert response.status_code == 200
            created_records.append(response.json())
        
        # 1. 日付範囲フィルターのテスト
        date_filter_response = requests.get(
            f"{API_BASE_URL}/records",
            params={
                "date_from": "2023-12-01",
                "date_to": "2023-12-03"
            }
        )
        
        assert date_filter_response.status_code == 200
        filtered_result = date_filter_response.json()
        
        # 日付範囲内の記録のみ取得されることを確認
        filtered_records = filtered_result["records"]
        assert len(filtered_records) == 2
        
        filtered_titles = {record["title"] for record in filtered_records}
        expected_titles = {"2023年12月1日の学習", "2023年12月3日の学習"}
        assert filtered_titles == expected_titles
        
        # 2. 制限数のテスト
        limit_response = requests.get(
            f"{API_BASE_URL}/records",
            params={"limit": 2}
        )
        
        assert limit_response.status_code == 200
        limit_result = limit_response.json()
        assert len(limit_result["records"]) <= 2
        
        # 3. 統計情報の確認
        all_records_response = requests.get(f"{API_BASE_URL}/records")
        assert all_records_response.status_code == 200
        all_result = all_records_response.json()
        
        statistics = all_result["statistics"]
        assert "total_duration_minutes" in statistics
        assert "total_duration_hours" in statistics
        assert "average_duration_minutes" in statistics
        assert statistics["total_duration_minutes"] > 0
    
    def test_roadmap_integration(self):
        """ロードマップ連携の統合テスト"""
        # ロードマップに紐づく記録を作成
        roadmap_record_data = {
            "title": "ロードマップ学習記録",
            "content": "React基礎をロードマップに沿って学習",
            "duration_minutes": 180,
            "roadmap_id": "test-roadmap-123",
            "roadmap_item_title": "React基礎学習",
            "tags": ["roadmap", "react"]
        }
        
        response = requests.post(
            f"{API_BASE_URL}/records",
            json=roadmap_record_data
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # ロードマップ情報が正しく記録されているかを確認
        assert result["roadmap_id"] == roadmap_record_data["roadmap_id"]
        assert result["roadmap_item_title"] == roadmap_record_data["roadmap_item_title"]
        
        # ロードマップフィルターでの取得テスト
        roadmap_filter_response = requests.get(
            f"{API_BASE_URL}/records",
            params={"roadmap_id": "test-roadmap-123"}
        )
        
        assert roadmap_filter_response.status_code == 200
        filtered_result = roadmap_filter_response.json()
        
        # 該当するロードマップの記録のみ取得されることを確認
        roadmap_records = [
            r for r in filtered_result["records"] 
            if r.get("roadmap_id") == "test-roadmap-123"
        ]
        assert len(roadmap_records) >= 1
    
    def test_error_handling(self):
        """エラーハンドリングの統合テスト"""
        # 1. 存在しない記録の取得
        response = requests.get(f"{API_BASE_URL}/records/non-existent-id")
        assert response.status_code == 404
        
        # 2. 無効なデータでの記録作成
        invalid_data = {
            "title": "",  # 空のタイトル
            "duration_minutes": -30  # 無効な時間
        }
        
        response = requests.post(f"{API_BASE_URL}/records", json=invalid_data)
        assert response.status_code == 400
        
        # 3. 無効なテンプレートタイプ
        invalid_template_data = {
            "template_type": "invalid_type"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/records/from-template",
            json=invalid_template_data
        )
        assert response.status_code == 400
        
        # 4. 存在しない記録の更新
        response = requests.put(
            f"{API_BASE_URL}/records/non-existent-id",
            json={"title": "新しいタイトル"}
        )
        assert response.status_code == 404
        
        # 5. 存在しない記録の削除
        response = requests.delete(f"{API_BASE_URL}/records/non-existent-id")
        assert response.status_code == 404
    
    def test_data_validation(self):
        """データバリデーションの統合テスト"""
        # 1. 必須フィールドが欠けている場合
        incomplete_data = {
            "content": "内容だけ"
            # title と duration_minutes が欠けている
        }
        
        response = requests.post(f"{API_BASE_URL}/records", json=incomplete_data)
        assert response.status_code == 400
        
        # 2. 無効な学習時間
        invalid_duration_data = {
            "title": "テスト記録",
            "duration_minutes": "invalid"  # 文字列は無効
        }
        
        response = requests.post(f"{API_BASE_URL}/records", json=invalid_duration_data)
        assert response.status_code == 400
        
        # 3. 負の学習時間
        negative_duration_data = {
            "title": "テスト記録",
            "duration_minutes": -60
        }
        
        response = requests.post(f"{API_BASE_URL}/records", json=negative_duration_data)
        assert response.status_code == 400
        assert "0より大きい値" in response.text
    
    def test_cors_headers(self):
        """CORS ヘッダーのテスト"""
        # OPTIONSリクエスト
        response = requests.options(f"{API_BASE_URL}/records")
        
        # CORSヘッダーが設定されていることを確認
        headers = response.headers
        assert "Access-Control-Allow-Origin" in headers
        assert "Access-Control-Allow-Methods" in headers
        assert "Access-Control-Allow-Headers" in headers
    
    def test_large_content_handling(self):
        """大きなコンテンツの処理テスト"""
        # 大きなコンテンツを含む記録を作成
        large_content = "あ" * 5000  # 5000文字のコンテンツ
        
        large_record_data = {
            "title": "大きなコンテンツのテスト",
            "content": large_content,
            "duration_minutes": 60
        }
        
        response = requests.post(f"{API_BASE_URL}/records", json=large_record_data)
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["content"]) == 5000
    
    def test_concurrent_requests(self):
        """同時リクエストの処理テスト"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def create_record(thread_id):
            """スレッド内で記録を作成"""
            try:
                data = {
                    "title": f"並行テスト{thread_id}",
                    "content": f"スレッド{thread_id}で作成された記録",
                    "duration_minutes": 60
                }
                
                response = requests.post(f"{API_BASE_URL}/records", json=data)
                results.put((thread_id, response.status_code))
                
            except Exception as e:
                results.put((thread_id, f"Error: {str(e)}"))
        
        # 複数スレッドで同時にリクエストを送信
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_record, args=(i,))
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

class TestRecordsAPIPerformance:
    """パフォーマンステスト"""
    
    def test_response_time(self):
        """レスポンス時間のテスト"""
        start_time = time.time()
        
        response = requests.get(f"{API_BASE_URL}/records")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # レスポンス時間が2秒以内であることを確認
        assert response_time < 2.0
        assert response.status_code == 200
    
    def test_bulk_operations(self):
        """一括操作のテスト"""
        # 複数の記録を連続で作成
        start_time = time.time()
        
        for i in range(10):
            data = {
                "title": f"バルクテスト記録{i}",
                "content": f"記録{i}の内容",
                "duration_minutes": 30 + i * 10
            }
            response = requests.post(f"{API_BASE_URL}/records", json=data)
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 10件の作成が10秒以内で完了することを確認
        assert total_time < 10.0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])