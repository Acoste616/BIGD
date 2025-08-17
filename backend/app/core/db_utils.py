"""
Narzędzia pomocnicze dla operacji bazodanowych
"""
from typing import Type, TypeVar, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from app.core.database import Base
import logging

logger = logging.getLogger(__name__)

# Type variable dla modeli
ModelType = TypeVar("ModelType", bound=Base)


class DatabaseRepository:
    """
    Bazowa klasa repozytorium z podstawowymi operacjami CRUD
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Args:
            model: Klasa modelu SQLAlchemy
        """
        self.model = model
    
    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """
        Pobierz pojedynczy obiekt po ID
        
        Args:
            db: Sesja bazy danych
            id: ID obiektu
            
        Returns:
            Obiekt modelu lub None
        """
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[List] = None
    ) -> List[ModelType]:
        """
        Pobierz wiele obiektów z opcjonalnym filtrowaniem
        
        Args:
            db: Sesja bazy danych
            skip: Liczba rekordów do pominięcia
            limit: Maksymalna liczba rekordów
            filters: Lista filtrów SQLAlchemy
            
        Returns:
            Lista obiektów modelu
        """
        query = select(self.model)
        
        if filters:
            query = query.where(and_(*filters))
            
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> ModelType:
        """
        Utwórz nowy obiekt
        
        Args:
            db: Sesja bazy danych
            obj_in: Dane do utworzenia obiektu
            
        Returns:
            Utworzony obiekt
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        db_obj: ModelType, 
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """
        Zaktualizuj istniejący obiekt
        
        Args:
            db: Sesja bazy danych
            db_obj: Obiekt do aktualizacji
            obj_in: Nowe dane
            
        Returns:
            Zaktualizowany obiekt
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, id: int) -> bool:
        """
        Usuń obiekt
        
        Args:
            db: Sesja bazy danych
            id: ID obiektu do usunięcia
            
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.flush()
            return True
        return False
    
    async def count(
        self, 
        db: AsyncSession, 
        filters: Optional[List] = None
    ) -> int:
        """
        Policz obiekty
        
        Args:
            db: Sesja bazy danych
            filters: Opcjonalne filtry
            
        Returns:
            Liczba obiektów
        """
        query = select(func.count()).select_from(self.model)
        
        if filters:
            query = query.where(and_(*filters))
            
        result = await db.execute(query)
        return result.scalar()
    
    async def exists(
        self, 
        db: AsyncSession, 
        filters: List
    ) -> bool:
        """
        Sprawdź czy obiekt istnieje
        
        Args:
            db: Sesja bazy danych
            filters: Filtry do sprawdzenia
            
        Returns:
            True jeśli istnieje
        """
        query = select(self.model).where(and_(*filters)).limit(1)
        result = await db.execute(query)
        return result.first() is not None


class PaginationParams:
    """
    Parametry paginacji dla zapytań
    """
    
    def __init__(
        self, 
        page: int = 1, 
        page_size: int = 20,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ):
        """
        Args:
            page: Numer strony (od 1)
            page_size: Rozmiar strony
            order_by: Pole do sortowania
            order_desc: Czy sortować malejąco
        """
        self.page = max(1, page)
        self.page_size = min(100, max(1, page_size))
        self.skip = (self.page - 1) * self.page_size
        self.limit = self.page_size
        self.order_by = order_by
        self.order_desc = order_desc


class PaginatedResponse:
    """
    Odpowiedź z paginacją
    """
    
    def __init__(
        self,
        items: List[Any],
        total: int,
        page: int,
        page_size: int
    ):
        """
        Args:
            items: Lista elementów
            total: Całkowita liczba elementów
            page: Obecna strona
            page_size: Rozmiar strony
        """
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.pages = (total + page_size - 1) // page_size
        self.has_next = page < self.pages
        self.has_prev = page > 1
        
    def dict(self) -> Dict[str, Any]:
        """
        Konwersja do słownika
        """
        return {
            "items": self.items,
            "pagination": {
                "total": self.total,
                "page": self.page,
                "page_size": self.page_size,
                "pages": self.pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev
            }
        }


async def paginate(
    db: AsyncSession,
    query,
    params: PaginationParams
) -> PaginatedResponse:
    """
    Wykonaj zapytanie z paginacją
    
    Args:
        db: Sesja bazy danych
        query: Zapytanie SQLAlchemy
        params: Parametry paginacji
        
    Returns:
        PaginatedResponse z wynikami
    """
    # Liczenie wszystkich rekordów
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.execute(count_query)
    total = total.scalar()
    
    # Sortowanie
    if params.order_by:
        if params.order_desc:
            query = query.order_by(params.order_by.desc())
        else:
            query = query.order_by(params.order_by)
    
    # Paginacja
    query = query.offset(params.skip).limit(params.limit)
    
    # Wykonanie zapytania
    result = await db.execute(query)
    items = result.scalars().all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size
    )


async def bulk_create(
    db: AsyncSession,
    model: Type[ModelType],
    objects_data: List[Dict[str, Any]]
) -> List[ModelType]:
    """
    Tworzenie wielu obiektów jednocześnie
    
    Args:
        db: Sesja bazy danych
        model: Klasa modelu
        objects_data: Lista danych obiektów
        
    Returns:
        Lista utworzonych obiektów
    """
    db_objects = [model(**data) for data in objects_data]
    db.add_all(db_objects)
    await db.commit()
    
    # Refresh wszystkich obiektów
    for obj in db_objects:
        await db.refresh(obj)
    
    return db_objects


async def transaction_wrapper(db: AsyncSession, operations):
    """
    Wrapper dla transakcji - automatyczny rollback przy błędzie
    
    Args:
        db: Sesja bazy danych
        operations: Funkcja z operacjami do wykonania
        
    Returns:
        Wynik operacji
    """
    try:
        result = await operations(db)
        await db.commit()
        return result
    except Exception as e:
        await db.rollback()
        logger.error(f"Transakcja anulowana: {e}")
        raise
