#!/usr/bin/env python3

import ollama
import os

try:
    print("🔍 Konfiguracja:")
    print(f"API_URL: {os.getenv('OLLAMA_API_URL')}")
    print(f"API_KEY: {'***' + os.getenv('OLLAMA_API_KEY', '')[-4:] if os.getenv('OLLAMA_API_KEY') else 'BRAK'}")
    print(f"MODEL: {os.getenv('OLLAMA_MODEL')}")
    
    headers = {}
    api_key = os.getenv('OLLAMA_API_KEY')
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    client = ollama.Client(
        host=os.getenv('OLLAMA_API_URL'),
        headers=headers
    )
    
    print("\n🧪 Testowanie połączenia...")
    
    response = client.chat(
        model='gpt-oss:120b',
        messages=[
            {'role': 'system', 'content': 'Odpowiedz krótko po polsku w formacie JSON: {"odpowiedz": "twoja odpowiedz"}'},
            {'role': 'user', 'content': 'Test połączenia'}
        ]
    )
    
    print("✅ OLLAMA TURBO DZIAŁA!")
    print(f"Raw Response: {response}")
    print(f"Message: {response.get('message', {}).get('content', 'BRAK')}")
    
except Exception as e:
    print(f"❌ OLLAMA BŁĄD: {e}")
    import traceback
    traceback.print_exc()
