"""RedisCacheService - Serwis do obsługi cache'owania w Redis

Odpowiedzialny za:
- Przechowywanie wyników kosztownych operacji AI
- Zarządzanie czasem życia (TTL) danych w cache
- Inwalidację cache'a przy aktualizacji danych
- Optymalizację wydajności serwisów AI
"""
import redis.asyncio as redis
import json
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import hashlib

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisCacheService:
    """
    Serwis do obsługi cache'owania w Redis dla optymalizacji wydajności.
    
    Funkcjonalności:
    - Cache'owanie wyników serwisów AI
    - Zarządzanie TTL (Time To Live)
    - Inwalidacja cache'a
    - Generowanie kluczy cache'a
    - Statystyki cache'a
    """
    
    def __init__(self):
        """Inicjalizacja połączenia z Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            logger.info(f"✅ RedisCacheService initialized with URL: {settings.REDIS_URL}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis connection: {e}")
            raise
    
    async def get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera dane z cache'a Redis.
        
        Args:
            key: Klucz cache'a
            
        Returns:
            Dict z danymi lub None jeśli brak w cache
        """
        try:
            cached_data = await self.redis_client.get(key)
            if cached_data:
                logger.debug(f"🎯 Cache HIT dla klucza: {key}")
                return json.loads(cached_data)
            else:
                logger.debug(f"❌ Cache MISS dla klucza: {key}")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error dla klucza {key}: {e}")
            # Usuń uszkodzone dane
            await self.invalidate_cache(key)
            return None
        except Exception as e:
            logger.error(f"❌ Redis get error dla klucza {key}: {e}")
            return None
    
    async def set_cache(
        self, 
        key: str, 
        data: Dict[str, Any], 
        ttl: int = 1800
    ) -> bool:
        """
        Ustawia dane w cache'u Redis z określonym czasem życia (TTL w sekundach).
        
        Args:
            key: Klucz cache'a
            data: Dane do zapisania
            ttl: Czas życia w sekundach (domyślnie 30 minut)
            
        Returns:
            bool: True jeśli zapisano pomyślnie
        """
        try:
            # Dodaj metadane do cache'a
            cache_data = {
                "data": data,
                "cached_at": datetime.now().isoformat(),
                "ttl": ttl,
                "version": "1.0"
            }
            
            json_data = json.dumps(cache_data, ensure_ascii=False)
            await self.redis_client.setex(key, ttl, json_data)
            
            logger.debug(f"💾 Cache SET dla klucza: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis set error dla klucza {key}: {e}")
            return False
    
    async def invalidate_cache(self, key: str) -> bool:
        """
        Usuwa klucz z cache'a.
        
        Args:
            key: Klucz do usunięcia
            
        Returns:
            bool: True jeśli usunięto pomyślnie
        """
        try:
            result = await self.redis_client.delete(key)
            if result > 0:
                logger.debug(f"🗑️ Cache INVALIDATED dla klucza: {key}")
                return True
            else:
                logger.debug(f"ℹ️ Cache key nie istniał: {key}")
                return False
        except Exception as e:
            logger.error(f"❌ Redis delete error dla klucza {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Usuwa wszystkie klucze pasujące do wzorca.
        
        Args:
            pattern: Wzorzec klucza (np. "session:123:*")
            
        Returns:
            int: Liczba usuniętych kluczy
        """
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"🗑️ Cache PATTERN INVALIDATED: {pattern} ({deleted} kluczy)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"❌ Redis pattern delete error dla wzorca {pattern}: {e}")
            return 0
    
    def generate_cache_key(
        self, 
        service_name: str, 
        session_id: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generuje unikalny klucz cache'a na podstawie parametrów.
        
        Args:
            service_name: Nazwa serwisu (np. "holistic_synthesis")
            session_id: ID sesji (opcjonalne)
            **kwargs: Dodatkowe parametry do klucza
            
        Returns:
            str: Wygenerowany klucz cache'a
        """
        key_parts = [service_name]
        
        if session_id:
            key_parts.append(f"session:{session_id}")
        
        # Dodaj dodatkowe parametry
        for k, v in sorted(kwargs.items()):
            if v is not None:
                # Dla złożonych obiektów stwórz hash
                if isinstance(v, (dict, list)):
                    v_str = json.dumps(v, sort_keys=True, ensure_ascii=False)
                    v_hash = hashlib.md5(v_str.encode()).hexdigest()[:8]
                    key_parts.append(f"{k}:{v_hash}")
                else:
                    key_parts.append(f"{k}:{v}")
        
        return ":".join(key_parts)
    
    async def get_cache_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera informacje o kluczu cache'a (TTL, rozmiar, etc.).
        
        Args:
            key: Klucz cache'a
            
        Returns:
            Dict z informacjami o cache lub None
        """
        try:
            ttl = await self.redis_client.ttl(key)
            if ttl == -2:  # Klucz nie istnieje
                return None
            
            size = await self.redis_client.memory_usage(key)
            
            return {
                "key": key,
                "ttl_seconds": ttl,
                "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat() if ttl > 0 else None,
                "size_bytes": size,
                "exists": True
            }
        except Exception as e:
            logger.error(f"❌ Cache info error dla klucza {key}: {e}")
            return None
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Pobiera statystyki cache'a Redis.
        
        Returns:
            Dict ze statystykami
        """
        try:
            info = await self.redis_client.info()
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "redis_version": info.get("redis_version", "unknown")
            }
        except Exception as e:
            logger.error(f"❌ Cache stats error: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> bool:
        """
        Sprawdza czy połączenie z Redis działa.
        
        Returns:
            bool: True jeśli Redis jest dostępny
        """
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"❌ Redis health check failed: {e}")
            return False
    
    async def close(self):
        """
        Zamyka połączenie z Redis.
        """
        try:
            await self.redis_client.close()
            logger.info("✅ Redis connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Redis connection: {e}")


# Singleton instance dla łatwego użycia
_redis_cache_instance: Optional[RedisCacheService] = None


def get_redis_cache() -> RedisCacheService:
    """
    Zwraca singleton instancję RedisCacheService.
    
    Returns:
        RedisCacheService: Instancja serwisu cache
    """
    global _redis_cache_instance
    
    if _redis_cache_instance is None:
        _redis_cache_instance = RedisCacheService()
    
    return _redis_cache_instance


async def check_redis_health() -> Dict[str, Any]:
    """
    Sprawdza status Redis i zwraca informacje diagnostyczne.
    
    Returns:
        Dict ze statusem Redis
    """
    try:
        cache_service = get_redis_cache()
        is_healthy = await cache_service.health_check()
        
        if is_healthy:
            stats = await cache_service.get_cache_stats()
            return {
                "status": "healthy",
                "redis_url": settings.REDIS_URL,
                "stats": stats
            }
        else:
            return {
                "status": "unhealthy",
                "redis_url": settings.REDIS_URL,
                "error": "Connection failed"
            }
    except Exception as e:
        return {
            "status": "error",
            "redis_url": settings.REDIS_URL,
            "error": str(e)
        }