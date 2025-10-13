"""
BaseAIService - Podstawowa komunikacja z Ollama Turbo API
Odpowiedzialny za: konfigurację, retry logic, cache management

UPDATED: 2025-10-13 - Przepisany dla Ollama Turbo Cloud API
- Używa httpx zamiast ollama-python dla kompatybilności z Cloud API
- Implementuje OpenAI-compatible endpoint format
- Dodano proper Bearer token authentication
"""
import json
import asyncio
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAIService:
    """
    Bazowa klasa dla komunikacji z Ollama Turbo Cloud API.
    
    Funkcjonalności:
    - Konfiguracja i inicjalizacja HTTPS client dla Ollama Turbo
    - Retry logic z exponential backoff
    - Cache management dla performance optimization
    - Error handling i logging
    - OpenAI-compatible API format
    """
    
    def __init__(self):
        """Inicjalizacja bazowego serwisu AI"""
        # Validate configuration
        if not settings.OLLAMA_API_KEY or settings.OLLAMA_API_KEY == "YOUR_OLLAMA_API_KEY_HERE":
            logger.warning("⚠️ OLLAMA_API_KEY not configured! Set it in .env file")
            logger.warning("⚠️ System will operate in FALLBACK mode without AI analysis")
        
        # Konfiguracja HTTPS Client dla Ollama Turbo Cloud API
        self.api_url = settings.OLLAMA_API_URL.rstrip('/')
        self.api_key = settings.OLLAMA_API_KEY
        self.model_name = settings.OLLAMA_MODEL
        
        # HTTP Client configuration
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            timeout=60.0,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        
        self.max_retries = 3
        self.timeout_seconds = 60
        
        # Performance cache
        self._cache = {}
        self._cache_max_size = 128
        self._cache_ttl_seconds = 3600  # 1 godzina
        
        logger.info(f"✅ BaseAIService initialized - Model: {self.model_name}, API: {self.api_url}")
    
    def _generate_cache_key(self, data: Dict[str, Any], prefix: str = "") -> str:
        """
        Generuje klucz cache na podstawie danych wejściowych
        
        Args:
            data: Dane do zhashowania
            prefix: Prefix dla klucza
            
        Returns:
            str: Unique cache key
        """
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        hash_object = hashlib.sha256(json_str.encode('utf-8'))
        hash_hex = hash_object.hexdigest()[:16]  # Pierwsze 16 znaków
        
        return f"{prefix}_{hash_hex}" if prefix else hash_hex
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """
        Sprawdza czy entry w cache jest jeszcze ważny
        
        Args:
            cache_entry: Entry z cache z timestampem
            
        Returns:
            bool: True jeśli ważny, False jeśli expired
        """
        if not cache_entry or 'timestamp' not in cache_entry:
            return False
            
        cache_time = datetime.fromisoformat(cache_entry['timestamp'])
        expiry_time = cache_time + timedelta(seconds=self._cache_ttl_seconds)
        
        return datetime.now() < expiry_time
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera dane z cache jeśli są ważne
        
        Args:
            cache_key: Klucz cache
            
        Returns:
            Optional[Dict]: Dane z cache lub None jeśli nie ma lub expired
        """
        if cache_key not in self._cache:
            return None
            
        cache_entry = self._cache[cache_key]
        if self._is_cache_valid(cache_entry):
            logger.debug(f"🎯 Cache HIT: {cache_key}")
            return cache_entry['data']
        else:
            # Usuń expired entry
            del self._cache[cache_key]
            logger.debug(f"⏰ Cache EXPIRED: {cache_key}")
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Zapisuje dane do cache z timestampem
        
        Args:
            cache_key: Klucz cache
            data: Dane do zapisania
        """
        # Usuń najstarsze entries jeśli cache jest pełny
        if len(self._cache) >= self._cache_max_size:
            # Znajdź najstarszy entry
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k]['timestamp'])
            del self._cache[oldest_key]
            logger.debug(f"🗑️ Cache EVICTED: {oldest_key}")
        
        self._cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        logger.debug(f"💾 Cache SAVED: {cache_key}")
    
    async def _call_llm_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        use_cache: bool = True,
        cache_prefix: str = "llm"
    ) -> Dict[str, Any]:
        """
        Wywołuje LLM z retry logic i cache
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt  
            use_cache: Czy używać cache
            cache_prefix: Prefix dla cache key
            
        Returns:
            Dict[str, Any]: Odpowiedź z LLM
            
        Raises:
            Exception: Po wyczerpaniu retry attempts
        """
        # Sprawdź cache
        if use_cache:
            cache_key = self._generate_cache_key({
                'system': system_prompt,
                'user': user_prompt,
                'model': self.model_name
            }, cache_prefix)
            
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result
        
        # Wywołaj LLM z retry
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"🤖 LLM Call attempt {attempt}/{self.max_retries} - Model: {self.model_name}")
                
                response = await asyncio.wait_for(
                    asyncio.create_task(self._make_ollama_request(system_prompt, user_prompt)),
                    timeout=self.timeout_seconds
                )
                
                # Zapisz do cache
                if use_cache:
                    self._save_to_cache(cache_key, response)
                
                logger.info(f"✅ LLM Response received successfully (attempt {attempt})")
                return response
                
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"⏰ LLM Timeout (attempt {attempt}/{self.max_retries}): {e}")
                
            except Exception as e:
                last_exception = e
                logger.error(f"❌ LLM Error (attempt {attempt}/{self.max_retries}): {e}")
            
            # Exponential backoff
            if attempt < self.max_retries:
                wait_time = 2 ** (attempt - 1)  # 1s, 2s, 4s
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
        
        # Wyczerpano wszystkie próby
        logger.error(f"💥 LLM FAILED after {self.max_retries} attempts - Last error: {last_exception}")
        raise Exception(f"LLM call failed after {self.max_retries} attempts: {last_exception}")
    
    async def _make_ollama_request(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Wykonuje faktyczne wywołanie Ollama Turbo Cloud API
        
        Uses OpenAI-compatible endpoint: /v1/chat/completions
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            
        Returns:
            Dict[str, Any]: Parsed response from Ollama Turbo
            
        Raises:
            httpx.HTTPStatusError: For HTTP errors (401, 429, 500, etc.)
            httpx.TimeoutException: For timeout errors
        """
        # Przygotuj messages w formacie OpenAI
        messages = []
        
        if system_prompt.strip():
            messages.append({
                'role': 'system',
                'content': system_prompt.strip()
            })
        
        messages.append({
            'role': 'user', 
            'content': user_prompt.strip()
        })
        
        # Przygotuj request body (OpenAI-compatible format)
        request_body = {
            'model': self.model_name,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': settings.MAX_TOKENS_PER_REQUEST,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        }
        
        try:
            # Wywołaj Ollama Turbo API (OpenAI-compatible endpoint)
            response = await self.client.post(
                '/v1/chat/completions',
                json=request_body
            )
            
            # Sprawdź status code
            response.raise_for_status()
            
            # Parsuj odpowiedź
            response_data = response.json()
            
            # Extract content from OpenAI-compatible format
            content = ''
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0].get('message', {}).get('content', '')
            
            # Zwróć zparsowaną odpowiedź
            return {
                'content': content,
                'model': response_data.get('model', self.model_name),
                'timestamp': datetime.now().isoformat(),
                'usage': response_data.get('usage', {}),
                'raw_response': response_data
            }
            
        except httpx.HTTPStatusError as e:
            # Handle specific HTTP errors
            status_code = e.response.status_code
            
            if status_code == 401:
                logger.error("❌ Ollama API Authentication Error - Check OLLAMA_API_KEY")
                raise Exception("Invalid Ollama API key. Please check your .env configuration.")
            elif status_code == 429:
                logger.error("❌ Ollama API Rate Limit Exceeded")
                raise Exception("Ollama API rate limit exceeded. Please try again later.")
            elif status_code >= 500:
                logger.error(f"❌ Ollama API Server Error: {status_code}")
                raise Exception(f"Ollama API server error: {status_code}")
            else:
                logger.error(f"❌ Ollama API HTTP Error: {status_code} - {e.response.text}")
                raise Exception(f"Ollama API error: {status_code}")
                
        except httpx.TimeoutException as e:
            logger.error("❌ Ollama API Timeout")
            raise Exception("Ollama API request timed out")
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ollama API Invalid JSON Response: {e}")
            raise Exception("Invalid response from Ollama API")
        
        except Exception as e:
            logger.error(f"❌ Ollama API Unexpected Error: {e}")
            raise
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Zwraca statystyki cache
        
        Returns:
            Dict: Statystyki cache
        """
        valid_entries = sum(1 for entry in self._cache.values() if self._is_cache_valid(entry))
        
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self._cache) - valid_entries,
            'max_size': self._cache_max_size,
            'ttl_seconds': self._cache_ttl_seconds,
            'hit_rate_estimate': f"{(valid_entries / max(len(self._cache), 1)) * 100:.1f}%"
        }
    
    def clear_cache(self) -> None:
        """Czyści cały cache"""
        old_size = len(self._cache)
        self._cache.clear()
        logger.info(f"🧹 Cache cleared - Removed {old_size} entries")
    
    async def close(self) -> None:
        """
        Zamyka HTTP client i zwalnia zasoby
        
        WAŻNE: Wywołać przy zamykaniu aplikacji
        """
        try:
            await self.client.aclose()
            logger.info("✅ BaseAIService HTTP client closed")
        except Exception as e:
            logger.error(f"❌ Error closing HTTP client: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Sprawdza połączenie z Ollama Turbo API
        
        Returns:
            Dict: Status połączenia z API
        """
        try:
            # Prosty test call do Ollama API
            test_messages = [
                {'role': 'user', 'content': 'test'}
            ]
            
            response = await self.client.post(
                '/v1/chat/completions',
                json={
                    'model': self.model_name,
                    'messages': test_messages,
                    'max_tokens': 5
                },
                timeout=10.0
            )
            
            response.raise_for_status()
            
            return {
                'status': 'healthy',
                'api_url': self.api_url,
                'model': self.model_name,
                'authenticated': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            return {
                'status': 'unhealthy',
                'api_url': self.api_url,
                'model': self.model_name,
                'authenticated': status_code != 401,
                'error': f'HTTP {status_code}',
                'error_detail': e.response.text[:200] if hasattr(e.response, 'text') else str(e),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'api_url': self.api_url,
                'model': self.model_name,
                'authenticated': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
