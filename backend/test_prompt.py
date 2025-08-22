#!/usr/bin/env python3

# Testuj dokładnie ten sam prompt co w aplikacji
import ollama
import os
import uuid

def generate_ids():
    return {
        "quick_response_id": f"qr_{uuid.uuid4().hex[:6]}",
        "sq_1_id": f"sq_{uuid.uuid4().hex[:6]}",
        "sq_2_id": f"sq_{uuid.uuid4().hex[:6]}",
        "sq_3_id": f"sq_{uuid.uuid4().hex[:6]}"
    }

# System prompt z placeholderami
system_template = '''Jesteś ekspertem sprzedaży Tesla. Odpowiadaj TYLKO w JSON:

{
    "quick_response": {
        "id": "{quick_response_id}",
        "text": "Krótka odpowiedź"
    },
    "suggested_questions": [
        {
            "id": "{sq_1_id}",
            "text": "Pytanie 1?"
        },
        {
            "id": "{sq_2_id}",
            "text": "Pytanie 2?"
        }
    ],
    "sentiment_score": 8,
    "potential_score": 7
}

PAMIĘTAJ: Odpowiadaj TYLKO w JSON. Żadnego dodatkowego tekstu!'''

try:
    # Wygeneruj ID jak w aplikacji
    suggestion_ids = generate_ids()
    print(f"🔍 Generated IDs: {suggestion_ids}")
    
    # Zastąp placeholdery
    system_prompt = system_template.format(**suggestion_ids)
    print(f"🔍 Prompt fragment: {system_prompt[-200:]}")
    
    # Połącz z Ollama
    headers = {}
    api_key = os.getenv('OLLAMA_API_KEY')
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    client = ollama.Client(
        host=os.getenv('OLLAMA_API_URL'),
        headers=headers
    )
    
    print("📤 Wysyłam do Ollama...")
    response = client.chat(
        model='gpt-oss:120b',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': 'Klient pyta o cenę Tesla'}
        ]
    )
    
    message = response.get('message', {}).get('content', '')
    print("✅ OLLAMA RESPONSE OTRZYMANA!")
    print(f"📝 Raw content: {message[:200]}...")
    
    # Test parsowania JSON
    import json
    start_idx = message.find('{')
    end_idx = message.rfind('}') + 1
    if start_idx != -1 and end_idx > 0:
        json_str = message[start_idx:end_idx]
        parsed = json.loads(json_str)
        print(f"✅ JSON PARSED OK: quick_response.id = {parsed['quick_response']['id']}")
    else:
        print(f"❌ JSON NOT FOUND: start={start_idx}, end={end_idx}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
