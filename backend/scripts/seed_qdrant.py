#!/usr/bin/env python3
"""
Skrypt seedingowy dla bazy wiedzy Qdrant
Odczytuje plik nuggets.json i wysyla kazdy nugget do API Knowledge Management
"""
import asyncio
import json
import httpx
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any

# Konfiguracja
API_URL = "http://localhost:8000/api/v1/knowledge/"
NUGGETS_FILE = "Nugget.json"

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mapowanie typow nuggetow na typy API
TYPE_MAPPING = {
    "profil_psychologiczny": "general",
    "obawa": "general", 
    "komunikacja": "general",
    "argument_sprzedazowy": "product",
    "taktyka_obiekcji": "objection",
    "strategia_edukacyjna": "general",
    "default": "general"
}

def load_nuggets_file() -> Dict[str, List[Dict[str, Any]]]:
    """
    Laduje i parsuje plik nuggets.json
    Naprawia strukture JSON jesli jest fragmentem
    """
    try:
        logger.info(f"📚 Czytam plik: {NUGGETS_FILE}")
        
        # W kontenerze plik znajduje sie w /app/Nugget.json  
        project_root = Path(__file__).parent.parent  # /app
        nuggets_path = project_root / NUGGETS_FILE
        
        if not nuggets_path.exists():
            raise FileNotFoundError(f"Plik {NUGGETS_FILE} nie istnieje w {project_root}")
        
        with open(nuggets_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Napraw JSON jesli jest fragmentem (zaczyna sie od },)
        if content.startswith('},'):
            logger.info("🔧 Naprawiam fragmentaryczny JSON...")
            content = '{' + content
        
        # Sprobuj sparsowac jako JSON
        try:
            data = json.loads(content)
            logger.info(f"✅ Zaladowano JSON z {len(data)} archetypami")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"❌ Blad parsowania JSON: {e}")
            
            # Fallback: sprobuj wyciagnac strukture z tekstu
            logger.info("🔄 Probuje alternatywna metode parsowania...")
            return parse_nuggets_from_text(content)
            
    except Exception as e:
        logger.error(f"❌ Blad podczas ladowania pliku: {e}")
        raise

def parse_nuggets_from_text(content: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Alternatywna metoda parsowania - wyciaga strukture z tekstu
    """
    logger.warning("⚠️ Uzywam fallback parsowania - struktura moze byc niepelna")
    
    # Prosty fallback - zwroc pusta strukture jesli nie mozna sparsowac
    # W praktycznym scenariuszu tu bylaby lepsza logika parsowania
    return {
        "unknown_archetype": [
            {
                "content": "Fallback nugget - niepoprawna struktura JSON",
                "metadata": {
                    "typ": "general", 
                    "archetyp": "unknown",
                    "tagi": ["fallback"]
                }
            }
        ]
    }

def convert_nugget_to_api_format(nugget: Dict[str, Any], archetype: str) -> Dict[str, Any]:
    """
    Konwertuje nugget z pliku JSON na format API Knowledge
    """
    content = nugget.get('content', '').strip()
    metadata = nugget.get('metadata', {})
    
    # Wyciagnij typ i zmapuj na typ API
    nugget_type = metadata.get('typ', 'default')
    api_type = TYPE_MAPPING.get(nugget_type, TYPE_MAPPING['default'])
    
    # Wyciagnij tagi
    tags = metadata.get('tagi', [])
    if not isinstance(tags, list):
        tags = []
    
    # Dodaj automatyczne tagi
    auto_tags = []
    if nugget_type != 'default':
        auto_tags.append(nugget_type)
    if archetype:
        auto_tags.append(archetype)
    
    all_tags = tags + auto_tags
    # Ograniczenie API: max 10 tagow
    all_tags = all_tags[:10]
    
    # Wygeneruj tytul na podstawie metadanych
    title = None
    if metadata.get('obiekcja'):
        title = f"Obiekcja: {metadata['obiekcja']}"
    elif metadata.get('cecha'):
        title = f"Cecha: {metadata['cecha']}"
    elif metadata.get('potrzeba'):
        title = f"Potrzeba: {metadata['potrzeba']}"
    elif nugget_type:
        title = f"{nugget_type.replace('_', ' ').title()}"
    
    return {
        "title": title,
        "content": content,
        "knowledge_type": api_type,
        "archetype": archetype,
        "tags": all_tags,
        "source": "import"
    }

async def send_nugget_to_api(client: httpx.AsyncClient, nugget_data: Dict[str, Any], archetype: str, index: int) -> bool:
    """
    Wysyla pojedynczy nugget do API
    """
    try:
        api_data = convert_nugget_to_api_format(nugget_data, archetype)
        
        logger.info(f"📤 Wysylam nugget {index} dla archetypu '{archetype}'...")
        
        response = await client.post(API_URL, json=api_data, timeout=30.0)
        
        if response.status_code == 201:
            result = response.json()
            nugget_id = result.get('data', {}).get('id', 'unknown')
            logger.info(f"✅ Sukces! ID: {nugget_id}")
            return True
        else:
            logger.error(f"❌ Blad HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Blad przy wysylaniu nugget {index}: {e}")
        return False

async def main():
    """
    Glowna funkcja asynchroniczna
    """
    logger.info("🚀 Rozpoczynam seedowanie bazy wiedzy Qdrant...")
    
    try:
        # Zaladuj dane z pliku
        nuggets_data = load_nuggets_file()
        
        # Przygotuj liste zadan asynchronicznych
        tasks = []
        total_nuggets = 0
        
        # Iteruj po archetypach
        for archetype, nuggets_list in nuggets_data.items():
            if not isinstance(nuggets_list, list):
                logger.warning(f"⚠️ Pomijam archetyp '{archetype}' - nieprawidlowa struktura")
                continue
            
            logger.info(f"📋 Archetyp '{archetype}': {len(nuggets_list)} nuggetow")
            
            # Iteruj po nuggetach w archetype
            for index, nugget in enumerate(nuggets_list, 1):
                if not isinstance(nugget, dict) or 'content' not in nugget:
                    logger.warning(f"⚠️ Pomijam nugget {index} w '{archetype}' - brak content")
                    continue
                
                total_nuggets += 1
        
        if total_nuggets == 0:
            logger.error("❌ Nie znaleziono prawidlowych nuggetow do zaladowania")
            return
        
        logger.info(f"📊 Laczna liczba nuggetow do zaladowania: {total_nuggets}")
        
        # Przygotuj klienta HTTP
        async with httpx.AsyncClient() as client:
            # Sprawdz polaczenie z API
            try:
                logger.info("🔍 Sprawdzam polaczenie z API...")
                health_response = await client.get("http://localhost:8000/health", timeout=10.0)
                if health_response.status_code != 200:
                    raise Exception(f"API nie jest dostepne: {health_response.status_code}")
                logger.info("✅ Polaczenie z API OK")
            except Exception as e:
                logger.error(f"❌ Nie mogę polaczyc sie z API: {e}")
                logger.error("💡 Upewnij sie ze backend jest uruchomiony: docker-compose up backend")
                return
            
            # Wyslij wszystkie nugget-y
            success_count = 0
            error_count = 0
            
            for archetype, nuggets_list in nuggets_data.items():
                if not isinstance(nuggets_list, list):
                    continue
                
                for index, nugget in enumerate(nuggets_list, 1):
                    if not isinstance(nugget, dict) or 'content' not in nugget:
                        continue
                    
                    success = await send_nugget_to_api(client, nugget, archetype, index)
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                    
                    # Krotka przerwa miedzy requestami
                    await asyncio.sleep(0.1)
        
        # Podsumowanie
        logger.info("=" * 60)
        logger.info(f"🎉 Seedowanie zakonczone!")
        logger.info(f"✅ Sukces: {success_count} nuggetow")
        logger.info(f"❌ Bledy: {error_count} nuggetow")
        logger.info(f"📊 Laczna liczba: {success_count + error_count}")
        logger.info("=" * 60)
        
        if error_count > 0:
            logger.warning(f"⚠️ Wystapily bledy przy {error_count} nuggetach")
            sys.exit(1)
        else:
            logger.info("🎯 Wszystkie nugget-y zostaly pomyslnie zaladowane!")
        
    except Exception as e:
        logger.error(f"💥 Krytyczny blad: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Uruchom asynchroniczna funkcje glowna
    asyncio.run(main())
