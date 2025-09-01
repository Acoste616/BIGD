#!/usr/bin/env python3
import sys
sys.path.append('/app')
import asyncio
import httpx

async def test_analytics():
    async with httpx.AsyncClient(base_url='http://localhost:8000') as client:
        try:
            response = await client.get('/api/v1/sessions/2/analytics')
            print(f'Status: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                print('Dane analytics:')
                print(f'Psychology confidence: {data.get("psychology_confidence", "N/A")}')
                cumulative = data.get('cumulative_psychology', {})
                print(f'Big Five traits: {len(cumulative.get("big_five", {}))}')
                print(f'DISC traits: {len(cumulative.get("disc", {}))}')
                print(f'Schwartz values: {len(cumulative.get("schwartz_values", []))}')
                print(f'Customer archetype: {data.get("customer_archetype", {}).get("archetype_key", "N/A")}')
                print(f'Sales indicators: {len(data.get("sales_indicators", {}))}')

                # Szczegółowy dump danych
                print('\n=== SZCZEGÓŁOWY DUMP ===')
                import json
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + '...')
            else:
                print(f'Błąd: {response.text}')
        except Exception as e:
            print(f'Błąd połączenia: {e}')

if __name__ == "__main__":
    asyncio.run(test_analytics())
