"""
Schematy Pydantic dla modułu Knowledge Management
Definicje struktur danych dla zarządzania bazą wiedzy
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class KnowledgeType(str, Enum):
    """Typy wiedzy w systemie"""
    GENERAL = "general"
    OBJECTION = "objection"
    CLOSING = "closing"
    PRODUCT = "product"
    PRICING = "pricing"
    COMPETITION = "competition"
    DEMO = "demo"
    FOLLOW_UP = "follow_up"
    TECHNICAL = "technical"


# class SourceType(str, Enum):
#     """Źródła wiedzy"""
#     MANUAL = "manual"
#     IMPORT = "import"
#     AI_GENERATED = "ai_generated"
#     FEEDBACK = "feedback"


class KnowledgeBase(BaseModel):
    """Bazowy schemat dla Knowledge"""
    title: Optional[str] = Field(
        None, 
        description="Tytuł wskazówki",
        example="Jak odpowiadać na zastrzeżenia cenowe"
    )
    content: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Treść wskazówki lub wiedzy",
        example="Gdy klient mówi że cena jest za wysoka, warto zapytać o budżet..."
    )
    knowledge_type: KnowledgeType = Field(
        KnowledgeType.GENERAL,
        description="Typ wiedzy"
    )
    archetype: Optional[str] = Field(
        None,
        description="Archetyp klienta którego dotyczy wskazówka",
        example="Analityk"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Lista tagów do kategoryzacji",
        example=["cena", "zastrzeżenia", "negocjacje"]
    )
    source: Optional[str] = Field(
        None,
        max_length=255,
        description="Źródło wiedzy"
    )

    @validator('tags')
    def validate_tags(cls, v):
        """Walidacja tagów"""
        if len(v) > 10:
            raise ValueError('Maksymalnie 10 tagów')
        
        # Normalizacja tagów (lowercase, bez białych znaków)
        return [tag.strip().lower() for tag in v if tag.strip()]

    @validator('content')
    def validate_content(cls, v):
        """Walidacja treści"""
        if not v.strip():
            raise ValueError('Treść nie może być pusta')
        return v.strip()


class KnowledgeCreate(KnowledgeBase):
    """Schemat tworzenia nowej wiedzy"""
    pass


class KnowledgeUpdate(BaseModel):
    """Schemat aktualizacji wiedzy"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    knowledge_type: Optional[KnowledgeType] = None
    archetype: Optional[str] = None
    tags: Optional[List[str]] = None

    @validator('tags')
    def validate_tags(cls, v):
        """Walidacja tagów przy aktualizacji"""
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError('Maksymalnie 10 tagów')
        return [tag.strip().lower() for tag in v if tag.strip()]


class KnowledgeRead(KnowledgeBase):
    """Schemat odczytu wiedzy z bazy"""
    id: str = Field(..., description="Unikatowy identyfikator")
    created_at: Optional[str] = Field(None, description="Data utworzenia")
    content_length: Optional[int] = Field(None, description="Długość treści")

    class Config:
        from_attributes = True


class KnowledgeSearch(BaseModel):
    """Schemat wyszukiwania wiedzy"""
    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Zapytanie wyszukiwania",
        example="jak odpowiedzieć na zastrzeżenia cenowe"
    )
    limit: int = Field(
        5,
        ge=1,
        le=20,
        description="Maksymalna liczba wyników"
    )
    knowledge_type: Optional[KnowledgeType] = Field(
        None,
        description="Filtr typu wiedzy"
    )
    archetype: Optional[str] = Field(
        None,
        description="Filtr archetypu klienta"
    )


class KnowledgeSearchResult(KnowledgeRead):
    """Wynik wyszukiwania wiedzy"""
    score: float = Field(
        ...,
        description="Ocena podobieństwa (0.0 - 1.0)",
        example=0.85
    )


class KnowledgeList(BaseModel):
    """Lista wiedzy z paginacją"""
    items: List[KnowledgeRead] = Field(default_factory=list)
    total: int = Field(0, description="Całkowita liczba elementów")
    page: int = Field(1, description="Aktualna strona")
    size: int = Field(10, description="Rozmiar strony")
    pages: int = Field(0, description="Liczba stron")


class KnowledgeStats(BaseModel):
    """Statystyki bazy wiedzy"""
    total_items: int = Field(0, description="Całkowita liczba wskazówek")
    by_type: Dict[str, int] = Field(
        default_factory=dict,
        description="Liczba wskazówek według typu"
    )
    by_archetype: Dict[str, int] = Field(
        default_factory=dict,
        description="Liczba wskazówek według archetypu"
    )
    by_source: Dict[str, int] = Field(
        default_factory=dict,
        description="Liczba wskazówek według źródła"
    )
    top_tags: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Najpopularniejsze tagi"
    )
    collection_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Informacje o kolekcji Qdrant"
    )


class KnowledgeBulkCreate(BaseModel):
    """Schemat masowego dodawania wiedzy"""
    items: List[KnowledgeCreate] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="Lista wskazówek do dodania"
    )
    
    @validator('items')
    def validate_unique_titles(cls, v):
        """Sprawdź czy tytuły są unikatowe"""
        titles = [item.title for item in v if item.title]
        if len(titles) != len(set(titles)):
            raise ValueError('Tytuły muszą być unikatowe w ramach jednego batcha')
        return v


class KnowledgeBulkResult(BaseModel):
    """Wynik masowego dodawania"""
    success_count: int = Field(0, description="Liczba pomyślnie dodanych")
    error_count: int = Field(0, description="Liczba błędów")
    created_ids: List[str] = Field(default_factory=list, description="ID utworzonych elementów")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Lista błędów")


class QdrantHealthCheck(BaseModel):
    """Status połączenia z Qdrant"""
    status: str = Field(..., description="Status połączenia")
    qdrant_version: Optional[str] = Field(None, description="Wersja Qdrant")
    collection_exists: bool = Field(False, description="Czy kolekcja istnieje")
    collection_name: str = Field(..., description="Nazwa kolekcji")
    collections_count: Optional[int] = Field(None, description="Liczba kolekcji")
    error: Optional[str] = Field(None, description="Błąd połączenia")


# Pomocnicze typy dla response
class KnowledgeResponse(BaseModel):
    """Standardowa odpowiedź API"""
    success: bool = Field(True, description="Status operacji")
    message: str = Field("", description="Wiadomość")
    data: Optional[Any] = Field(None, description="Dane odpowiedzi")


class KnowledgeErrorResponse(BaseModel):
    """Odpowiedź błędu"""
    success: bool = Field(False, description="Status operacji")
    error: str = Field(..., description="Opis błędu")
    details: Optional[Dict[str, Any]] = Field(None, description="Szczegóły błędu")


# Export schemas for easier imports
__all__ = [
    "KnowledgeType",
    "KnowledgeBase",
    "KnowledgeCreate",
    "KnowledgeUpdate",
    "KnowledgeRead",
    "KnowledgeSearch",
    "KnowledgeSearchResult",
    "KnowledgeList",
    "KnowledgeStats",
    "KnowledgeBulkCreate",
    "KnowledgeBulkResult",
    "QdrantHealthCheck",
    "KnowledgeResponse",
    "KnowledgeErrorResponse"
]
