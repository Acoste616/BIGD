"""
Router dla zarządzania bazą wiedzy (Knowledge Management)
Endpointy do obsługi wskazówek sprzedażowych w bazie wektorowej Qdrant
"""
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from ..schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeRead,
    KnowledgeSearch,
    KnowledgeSearchResult,
    KnowledgeList,
    KnowledgeStats,
    KnowledgeBulkCreate,
    KnowledgeBulkResult,
    QdrantHealthCheck,
    KnowledgeResponse,
    KnowledgeType
)
from ..services.qdrant_service import qdrant_service

logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Management"],
    responses={
        404: {"description": "Knowledge not found"},
        500: {"description": "Internal server error"}
    }
)


@router.post("/", response_model=KnowledgeResponse, status_code=201)
async def create_knowledge(knowledge_data: KnowledgeCreate):
    """
    ✨ **Dodaj nową wskazówkę do bazy wiedzy**
    
    Tworzy nową wskazówkę sprzedażową i zapisuje ją w bazie wektorowej Qdrant.
    System automatycznie generuje embedding i indeksuje treść.
    
    **Parametry:**
    - **content**: Treść wskazówki (10-5000 znaków)
    - **title**: Opcjonalny tytuł 
    - **knowledge_type**: Typ wiedzy (general, objection, closing, etc.)
    - **archetype**: Archetyp klienta którego dotyczy
    - **tags**: Lista tagów do kategoryzacji
    - **source**: Źródło wiedzy (manual, import, ai_generated)
    
    **Returns:** ID utworzonej wskazówki
    """
    try:
        logger.info(f"Tworzenie nowej wiedzy: {knowledge_data.title}")
        
        # Dodaj wiedzę do Qdrant
        point_id = qdrant_service.add_knowledge(
            content=knowledge_data.content,
            title=knowledge_data.title,
            knowledge_type=knowledge_data.knowledge_type.value,
            archetype=knowledge_data.archetype,
            tags=knowledge_data.tags,
            source=knowledge_data.source.value
        )
        
        return KnowledgeResponse(
            success=True,
            message=f"Wskazówka została dodana pomyślnie",
            data={"id": point_id, "title": knowledge_data.title}
        )
        
    except Exception as e:
        logger.error(f"Błąd podczas tworzenia wiedzy: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Nie udało się dodać wskazówki: {str(e)}"
        )


@router.get("/", response_model=KnowledgeList)
async def get_all_knowledge(
    page: int = Query(1, ge=1, description="Numer strony"),
    size: int = Query(10, ge=1, le=50, description="Rozmiar strony"),
    knowledge_type: KnowledgeType = Query(None, description="Filtr typu wiedzy"),
    archetype: str = Query(None, description="Filtr archetypu"),
    search: str = Query(None, description="Wyszukiwanie w treści")
):
    """
    📚 **Pobierz listę wszystkich wskazówek**
    
    Zwraca spaginowaną listę wskazówek z możliwością filtrowania.
    
    **Parametry:**
    - **page**: Numer strony (domyślnie 1)
    - **size**: Rozmiar strony (1-50, domyślnie 10)
    - **knowledge_type**: Filtr typu wiedzy
    - **archetype**: Filtr archetypu klienta
    - **search**: Wyszukiwanie w treści (jeśli podane, używa wyszukiwania wektorowego)
    """
    try:
        logger.info(f"Pobieranie wiedzy - strona: {page}, rozmiar: {size}")
        
        # Jeśli jest search query, użyj wyszukiwania wektorowego
        if search:
            results = qdrant_service.search_knowledge(
                query=search,
                limit=size,
                knowledge_type=knowledge_type.value if knowledge_type else None,
                archetype=archetype
            )
            
            # Konwertuj wyniki search na format listy
            items = []
            for result in results:
                item = KnowledgeRead(
                    id=result["id"],
                    content=result["content"],
                    title=result["title"],
                    knowledge_type=result["knowledge_type"],
                    archetype=result["archetype"],
                    tags=result["tags"],
                    source="manual",  # Domyślne dla wyszukiwania
                    created_at=None,
                    content_length=len(result["content"])
                )
                items.append(item)
            
            return KnowledgeList(
                items=items,
                total=len(items),
                page=1,
                size=len(items),
                pages=1
            )
        
        # Standardowe pobieranie wszystkich
        all_knowledge = qdrant_service.get_all_knowledge(limit=size * 10)  # Większy limit dla filtrowania
        
        # Filtrowanie po stronie aplikacji (w przyszłości można przenieść do Qdrant)
        filtered_knowledge = all_knowledge
        
        if knowledge_type:
            filtered_knowledge = [
                k for k in filtered_knowledge 
                if k.get("knowledge_type") == knowledge_type.value
            ]
        
        if archetype:
            filtered_knowledge = [
                k for k in filtered_knowledge 
                if k.get("archetype") == archetype
            ]
        
        # Paginacja
        total = len(filtered_knowledge)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_items = filtered_knowledge[start_idx:end_idx]
        
        # Konwertuj na schemat Pydantic
        items = []
        for item_data in paginated_items:
            item = KnowledgeRead(**item_data)
            items.append(item)
        
        pages = (total + size - 1) // size  # Ceiling division
        
        return KnowledgeList(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania wiedzy: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Nie udało się pobrać listy wskazówek: {str(e)}"
        )


@router.get("/{point_id}", response_model=KnowledgeRead)
async def get_knowledge_by_id(point_id: str):
    """
    📄 **Pobierz szczegóły pojedynczej wskazówki**
    
    **Parametry:**
    - **point_id**: Unikatowy identyfikator wskazówki
    """
    try:
        # Pobierz wszystkie i znajdź konkretną (można zoptymalizować)
        all_knowledge = qdrant_service.get_all_knowledge()
        
        knowledge_item = next(
            (item for item in all_knowledge if item["id"] == point_id),
            None
        )
        
        if not knowledge_item:
            raise HTTPException(
                status_code=404,
                detail=f"Wskazówka o ID {point_id} nie została znaleziona"
            )
        
        return KnowledgeRead(**knowledge_item)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania wiedzy {point_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Nie udało się pobrać wskazówki: {str(e)}"
        )


@router.delete("/{point_id}", response_model=KnowledgeResponse)
async def delete_knowledge(point_id: str):
    """
    🗑️ **Usuń wskazówkę z bazy wiedzy**
    
    Usuwa wskazówkę z bazy wektorowej Qdrant.
    
    **Parametry:**
    - **point_id**: Unikatowy identyfikator wskazówki do usunięcia
    """
    try:
        logger.info(f"Usuwanie wiedzy: {point_id}")
        
        # Sprawdź czy wskazówka istnieje
        all_knowledge = qdrant_service.get_all_knowledge()
        knowledge_exists = any(item["id"] == point_id for item in all_knowledge)
        
        if not knowledge_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Wskazówka o ID {point_id} nie została znaleziona"
            )
        
        # Usuń z Qdrant
        success = qdrant_service.delete_knowledge(point_id)
        
        if success:
            return KnowledgeResponse(
                success=True,
                message=f"Wskazówka została usunięta pomyślnie",
                data={"deleted_id": point_id}
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Nie udało się usunąć wskazówki"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas usuwania wiedzy {point_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Nie udało się usunąć wskazówki: {str(e)}"
        )


@router.post("/search", response_model=List[KnowledgeSearchResult])
async def search_knowledge(search_data: KnowledgeSearch):
    """
    🔍 **Wyszukaj podobne wskazówki**
    
    Używa wyszukiwania wektorowego do znalezienia wskazówek podobnych do zapytania.
    
    **Parametry:**
    - **query**: Zapytanie wyszukiwania (3-500 znaków)
    - **limit**: Maksymalna liczba wyników (1-20)
    - **knowledge_type**: Opcjonalny filtr typu wiedzy
    - **archetype**: Opcjonalny filtr archetypu
    """
    try:
        logger.info(f"Wyszukiwanie wiedzy: '{search_data.query}'")
        
        results = qdrant_service.search_knowledge(
            query=search_data.query,
            limit=search_data.limit,
            knowledge_type=search_data.knowledge_type.value if search_data.knowledge_type else None,
            archetype=search_data.archetype
        )
        
        # Konwertuj na schemat wyników wyszukiwania
        search_results = []
        for result in results:
            search_result = KnowledgeSearchResult(
                id=result["id"],
                score=result["score"],
                content=result["content"],
                title=result["title"],
                knowledge_type=result["knowledge_type"],
                archetype=result["archetype"],
                tags=result["tags"],
                source="manual",  # Domyślne
                created_at=None,
                content_length=len(result["content"])
            )
            search_results.append(search_result)
        
        return search_results
        
    except Exception as e:
        logger.error(f"Błąd podczas wyszukiwania wiedzy: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Nie udało się wyszukać wskazówek: {str(e)}"
        )


@router.get("/stats/summary", response_model=KnowledgeStats)
async def get_knowledge_stats():
    """
    📊 **Pobierz statystyki bazy wiedzy**
    
    Zwraca szczegółowe statystyki całej bazy wiedzy.
    """
    try:
        logger.info("Pobieranie statystyk bazy wiedzy")
        
        # Pobierz wszystkie wskazówki
        all_knowledge = qdrant_service.get_all_knowledge()
        
        # Podstawowe statystyki
        total_items = len(all_knowledge)
        
        # Statystyki według typu
        by_type = {}
        for item in all_knowledge:
            knowledge_type = item.get("knowledge_type", "unknown")
            by_type[knowledge_type] = by_type.get(knowledge_type, 0) + 1
        
        # Statystyki według archetypu
        by_archetype = {}
        for item in all_knowledge:
            archetype = item.get("archetype") or "brak"
            by_archetype[archetype] = by_archetype.get(archetype, 0) + 1
        
        # Statystyki według źródła
        by_source = {}
        for item in all_knowledge:
            source = item.get("source", "unknown")
            by_source[source] = by_source.get(source, 0) + 1
        
        # Top tagi
        tag_counts = {}
        for item in all_knowledge:
            tags = item.get("tags", [])
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sortuj tagi według popularności
        top_tags = [
            {"tag": tag, "count": count}
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Informacje o kolekcji Qdrant
        collection_info = qdrant_service.get_collection_info()
        
        return KnowledgeStats(
            total_items=total_items,
            by_type=by_type,
            by_archetype=by_archetype,
            by_source=by_source,
            top_tags=top_tags,
            collection_info=collection_info
        )
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania statystyk: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Nie udało się pobrać statystyk: {str(e)}"
        )


@router.post("/bulk", response_model=KnowledgeBulkResult)
async def bulk_create_knowledge(bulk_data: KnowledgeBulkCreate):
    """
    📦 **Masowe dodawanie wskazówek**
    
    Dodaje wiele wskazówek jednocześnie (maksymalnie 50).
    
    **Parametry:**
    - **items**: Lista wskazówek do dodania (1-50 elementów)
    """
    try:
        logger.info(f"Masowe dodawanie {len(bulk_data.items)} wskazówek")
        
        created_ids = []
        errors = []
        
        for idx, knowledge_item in enumerate(bulk_data.items):
            try:
                point_id = qdrant_service.add_knowledge(
                    content=knowledge_item.content,
                    title=knowledge_item.title,
                    knowledge_type=knowledge_item.knowledge_type.value,
                    archetype=knowledge_item.archetype,
                    tags=knowledge_item.tags,
                    source=knowledge_item.source.value
                )
                created_ids.append(point_id)
                
            except Exception as item_error:
                errors.append({
                    "index": idx,
                    "title": knowledge_item.title,
                    "error": str(item_error)
                })
        
        return KnowledgeBulkResult(
            success_count=len(created_ids),
            error_count=len(errors),
            created_ids=created_ids,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Błąd podczas masowego dodawania: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Nie udało się wykonać masowego dodawania: {str(e)}"
        )


@router.get("/health/qdrant", response_model=QdrantHealthCheck)
async def qdrant_health_check():
    """
    🏥 **Sprawdź połączenie z Qdrant**
    
    Weryfikuje stan połączenia z bazą wektorową Qdrant.
    """
    try:
        health_status = qdrant_service.health_check()
        return QdrantHealthCheck(**health_status)
        
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        return QdrantHealthCheck(
            status="error",
            collection_exists=False,
            collection_name=qdrant_service.collection_name,
            error=str(e)
        )


# Pomocnicze endpointy dla administracji

@router.get("/types/available", response_model=List[Dict[str, str]])
async def get_available_knowledge_types():
    """
    📋 **Pobierz dostępne typy wiedzy**
    
    Zwraca listę wszystkich dostępnych typów wiedzy w systemie.
    """
    types = [
        {"value": "general", "label": "Ogólne", "description": "Podstawowe wskazówki sprzedażowe"},
        {"value": "objection", "label": "Zastrzeżenia", "description": "Odpowiedzi na zastrzeżenia klientów"},
        {"value": "closing", "label": "Zamknięcie", "description": "Techniki finalizowania sprzedaży"},
        {"value": "product", "label": "Produkt", "description": "Informacje o produktach"},
        {"value": "pricing", "label": "Cennik", "description": "Strategie cenowe"},
        {"value": "competition", "label": "Konkurencja", "description": "Analiza konkurencji"},
        {"value": "demo", "label": "Demonstracja", "description": "Prowadzenie prezentacji"},
        {"value": "follow_up", "label": "Kontakt", "description": "Działania następcze"},
        {"value": "technical", "label": "Techniczne", "description": "Aspekty techniczne produktów"}
    ]
    return types


@router.delete("/all", response_model=KnowledgeResponse)
async def delete_all_knowledge():
    """
    ⚠️ **UWAGA: Usuń całą bazę wiedzy**
    
    Usuwa wszystkie wskazówki z bazy wiedzy. Ta operacja jest nieodwracalna!
    Użyj tylko w celach deweloperskich.
    """
    try:
        logger.warning("USUWANIE CAŁEJ BAZY WIEDZY - operacja nieodwracalna!")
        
        # Pobierz wszystkie ID
        all_knowledge = qdrant_service.get_all_knowledge()
        deleted_count = 0
        
        for item in all_knowledge:
            try:
                qdrant_service.delete_knowledge(item["id"])
                deleted_count += 1
            except Exception as e:
                logger.error(f"Błąd podczas usuwania {item['id']}: {e}")
        
        return KnowledgeResponse(
            success=True,
            message=f"Usunięto {deleted_count} wskazówek z bazy wiedzy",
            data={"deleted_count": deleted_count}
        )
        
    except Exception as e:
        logger.error(f"Błąd podczas czyszczenia bazy wiedzy: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Nie udało się wyczyścić bazy wiedzy: {str(e)}"
        )
