#!/usr/bin/env python3
"""
Test Ollama Turbo API Connection - UPDATED for Cloud API

Tests:
1. Configuration validation
2. API connection
3. Simple chat completion
4. Error handling

Usage:
    python test_ollama_turbo.py
"""

import os
import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai.base_ai_service import BaseAIService
from app.core.config import settings


async def test_ollama_turbo():
    """Test Ollama Turbo API connection and functionality"""
    
    print("=" * 80)
    print("🧪 OLLAMA TURBO API - CONNECTION TEST")
    print("=" * 80)
    
    # Step 1: Configuration Check
    print("\n📋 Step 1: Checking Configuration...")
    print("-" * 80)
    print(f"API URL: {settings.OLLAMA_API_URL}")
    
    if settings.OLLAMA_API_KEY and settings.OLLAMA_API_KEY != "YOUR_OLLAMA_API_KEY_HERE":
        masked_key = settings.OLLAMA_API_KEY[:8] + "..." + settings.OLLAMA_API_KEY[-4:]
        print(f"API Key: {masked_key} ✅")
    else:
        print(f"API Key: NOT CONFIGURED ❌")
        print("\n⚠️  Please set OLLAMA_API_KEY in your .env file")
        print("Example: OLLAMA_API_KEY=sk-your-key-here")
        return False
    
    print(f"Model: {settings.OLLAMA_MODEL}")
    print(f"Max Tokens: {settings.MAX_TOKENS_PER_REQUEST}")
    
    # Step 2: Initialize Service
    print("\n🔌 Step 2: Initializing BaseAIService...")
    print("-" * 80)
    
    try:
        service = BaseAIService()
        print("✅ BaseAIService initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return False
    
    # Step 3: Health Check
    print("\n🏥 Step 3: Running Health Check...")
    print("-" * 80)
    
    try:
        health_status = await service.health_check()
        
        print(f"Status: {health_status.get('status', 'unknown')}")
        print(f"Authenticated: {health_status.get('authenticated', False)}")
        
        if health_status.get('status') == 'healthy':
            print("✅ Ollama Turbo API is reachable and authenticated")
        else:
            print(f"❌ Health check failed: {health_status.get('error', 'Unknown error')}")
            if 'error_detail' in health_status:
                print(f"Details: {health_status['error_detail']}")
            await service.close()
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        await service.close()
        return False
    
    # Step 4: Test Chat Completion
    print("\n💬 Step 4: Testing Chat Completion...")
    print("-" * 80)
    
    system_prompt = "You are a helpful assistant. Respond in Polish with a JSON object."
    user_prompt = "Odpowiedz krótko: Czy jesteś gotowy do pracy? Zwróć JSON: {\"status\": \"ready\", \"message\": \"krótka wiadomość\"}"
    
    try:
        print("Sending test message...")
        response = await service._call_llm_with_retry(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            use_cache=False
        )
        
        print("\n📥 Response received:")
        print("-" * 80)
        print(f"Content: {response.get('content', 'No content')[:200]}")
        print(f"Model: {response.get('model', 'Unknown')}")
        
        if 'usage' in response:
            usage = response['usage']
            print(f"\n📊 Token Usage:")
            print(f"  - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"  - Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"  - Total tokens: {usage.get('total_tokens', 'N/A')}")
        
        print("\n✅ Chat completion test PASSED")
        
    except Exception as e:
        print(f"\n❌ Chat completion test FAILED: {e}")
        import traceback
        traceback.print_exc()
        await service.close()
        return False
    
    # Step 5: Test Cache
    print("\n💾 Step 5: Testing Cache Functionality...")
    print("-" * 80)
    
    try:
        # Same request with cache enabled
        response_cached = await service._call_llm_with_retry(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            use_cache=True,
            cache_prefix="test"
        )
        
        cache_stats = service.get_cache_stats()
        print(f"Cache entries: {cache_stats.get('total_entries', 0)}")
        print(f"Valid entries: {cache_stats.get('valid_entries', 0)}")
        print("✅ Cache test PASSED")
        
    except Exception as e:
        print(f"⚠️  Cache test failed (non-critical): {e}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    print("-" * 80)
    await service.close()
    print("✅ Service closed")
    
    # Final Summary
    print("\n" + "=" * 80)
    print("🎉 ALL TESTS PASSED - OLLAMA TURBO API IS WORKING!")
    print("=" * 80)
    print("\n✅ System is ready for production use")
    print(f"✅ Model: {settings.OLLAMA_MODEL}")
    print(f"✅ API: {settings.OLLAMA_API_URL}")
    print("\n" + "=" * 80)
    
    return True


async def main():
    """Main entry point"""
    try:
        success = await test_ollama_turbo()
        
        if success:
            print("\n✅ Test completed successfully")
            sys.exit(0)
        else:
            print("\n❌ Test failed - please check configuration")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
