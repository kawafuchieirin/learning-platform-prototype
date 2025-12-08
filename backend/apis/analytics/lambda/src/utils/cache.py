from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import json
from utils.config import settings


class CacheService:
    """シンプルなメモリキャッシュサービス
    
    注意: Lambda関数では実行間でメモリが保持されない可能性があるため、
    本格的な実装ではElastiCacheやDynamoDB TTLを使用する
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self.default_ttl = settings.CACHE_TTL_SECONDS
    
    async def get(self, key: str) -> Optional[Any]:
        """キャッシュからデータを取得"""
        
        if key not in self._cache:
            return None
        
        cache_item = self._cache[key]
        
        # TTL チェック
        if datetime.now() > cache_item['expires_at']:
            # 期限切れなので削除
            del self._cache[key]
            return None
        
        # ヒット回数を増やす
        cache_item['hit_count'] += 1
        cache_item['last_accessed'] = datetime.now()
        
        return cache_item['data']
    
    async def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """キャッシュにデータを保存"""
        
        try:
            ttl_seconds = ttl or self.default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
            self._cache[key] = {
                'data': data,
                'created_at': datetime.now(),
                'expires_at': expires_at,
                'ttl': ttl_seconds,
                'hit_count': 0,
                'last_accessed': None
            }
            
            # メモリ使用量を制限（最大100アイテム）
            if len(self._cache) > 100:
                await self._evict_oldest()
            
            return True
            
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """キャッシュからデータを削除"""
        
        try:
            if key in self._cache:
                del self._cache[key]
            return True
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """全キャッシュを削除"""
        
        try:
            self._cache.clear()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """キーが存在するかチェック"""
        
        if key not in self._cache:
            return False
        
        # TTL チェック
        cache_item = self._cache[key]
        if datetime.now() > cache_item['expires_at']:
            del self._cache[key]
            return False
        
        return True
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュ統計を取得"""
        
        total_items = len(self._cache)
        expired_items = 0
        total_hits = 0
        
        current_time = datetime.now()
        
        for cache_item in self._cache.values():
            if current_time > cache_item['expires_at']:
                expired_items += 1
            total_hits += cache_item['hit_count']
        
        return {
            'total_items': total_items,
            'expired_items': expired_items,
            'active_items': total_items - expired_items,
            'total_hits': total_hits,
            'memory_usage_estimate': self._estimate_memory_usage()
        }
    
    async def cleanup_expired(self) -> int:
        """期限切れアイテムを削除"""
        
        current_time = datetime.now()
        expired_keys = []
        
        for key, cache_item in self._cache.items():
            if current_time > cache_item['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    # プライベートメソッド
    
    async def _evict_oldest(self) -> None:
        """最も古いアイテムを削除（LRU的な動作）"""
        
        if not self._cache:
            return
        
        # 最も古いアイテムを見つける
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k]['created_at']
        )
        
        del self._cache[oldest_key]
    
    def _estimate_memory_usage(self) -> str:
        """メモリ使用量の概算"""
        
        try:
            # 簡単な推定（正確ではない）
            total_size = 0
            for cache_item in self._cache.values():
                data_str = json.dumps(cache_item['data'], default=str)
                total_size += len(data_str.encode('utf-8'))
            
            if total_size < 1024:
                return f"{total_size} bytes"
            elif total_size < 1024 * 1024:
                return f"{total_size / 1024:.1f} KB"
            else:
                return f"{total_size / (1024 * 1024):.1f} MB"
                
        except Exception:
            return "Unknown"


# グローバルキャッシュインスタンス（Lambda実行間では保持されない可能性がある）
_global_cache = None


def get_cache_service() -> CacheService:
    """キャッシュサービスのシングルトンインスタンスを取得"""
    
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheService()
    return _global_cache