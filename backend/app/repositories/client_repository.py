"""
Repozytorium dla operacji na klientach
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from app.core.db_utils import DatabaseRepository, PaginationParams, PaginatedResponse, paginate
from app.models.domain import Client, Session as SessionModel
from app.schemas.client import ClientCreate, ClientUpdate
import logging

logger = logging.getLogger(__name__)


class ClientRepository(DatabaseRepository):
    """
    Repozytorium dla modelu Client z rozszerzonymi funkcjonalnościami
    """
    
    def __init__(self):
        super().__init__(Client)
    
    async def generate_unique_alias(self, db: AsyncSession) -> str:
        """
        Generuj unikalny alias dla nowego klienta
        
        Args:
            db: Sesja bazy danych
            
        Returns:
            Unikalny alias w formacie "Klient #N"
        """
        try:
            # Policz wszystkich klientów (włącznie z usuniętymi - aby uniknąć duplikatów)
            result = await db.execute(
                select(func.count(Client.id))
            )
            count = result.scalar() or 0
            
            # Wygeneruj alias z następnym numerem
            next_number = count + 1
            alias = f"Klient #{next_number}"
            
            # Sprawdź czy alias już istnieje (na wszelki wypadek)
            while True:
                existing = await db.execute(
                    select(Client).where(Client.alias == alias)
                )
                if existing.scalar_one_or_none() is None:
                    break
                next_number += 1
                alias = f"Klient #{next_number}"
            
            logger.debug(f"Wygenerowano unikalny alias: {alias}")
            return alias
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania aliasu: {e}")
            raise

    async def create_client_with_alias(
        self, 
        db: AsyncSession, 
        client_data: ClientCreate,
        alias: str
    ) -> Client:
        """
        Utwórz nowego klienta z podanym aliasem
        
        Args:
            db: Sesja bazy danych
            client_data: Dane klienta z walidacją Pydantic
            alias: Wygenerowany alias
            
        Returns:
            Utworzony klient
        """
        try:
            # Konwersja schemy Pydantic do dict
            client_dict = client_data.model_dump()
            
            # Dodaj alias
            client_dict['alias'] = alias
            
            # Utworzenie klienta
            db_client = await self.create(db, client_dict)
            
            logger.info(f"Utworzono nowego klienta: {db_client.alias} (ID: {db_client.id})")
            return db_client
            
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia klienta: {e}")
            raise
    
    async def get_client(
        self, 
        db: AsyncSession, 
        client_id: int,
        include_sessions: bool = False
    ) -> Optional[Client]:
        """
        Pobierz klienta po ID
        
        Args:
            db: Sesja bazy danych
            client_id: ID klienta
            include_sessions: Czy dołączyć sesje
            
        Returns:
            Klient lub None
        """
        query = select(Client).where(Client.id == client_id)
        
        # Opcjonalnie dołącz sesje
        if include_sessions:
            query = query.options(selectinload(Client.sessions))
        
        result = await db.execute(query)
        client = result.scalar_one_or_none()
        
        if client:
            logger.debug(f"Pobrano klienta: {client.alias} (ID: {client_id})")
        else:
            logger.warning(f"Nie znaleziono klienta o ID: {client_id}")
            
        return client
    
    async def get_clients_paginated(
        self,
        db: AsyncSession,
        pagination: PaginationParams,
        search: Optional[str] = None,
        archetype: Optional[str] = None
    ) -> PaginatedResponse:
        """
        Pobierz klientów z paginacją i filtrowaniem (tylko dane profilujące)
        
        Args:
            db: Sesja bazy danych
            pagination: Parametry paginacji
            search: Fraza wyszukiwania (alias, notatki)
            archetype: Filtr po archetypie
            
        Returns:
            PaginatedResponse z klientami
        """
        # Podstawowe zapytanie
        query = select(Client)
        
        # Filtry
        filters = []
        
        if search:
            search_filter = or_(
                Client.alias.ilike(f"%{search}%"),
                Client.notes.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if archetype:
            filters.append(Client.archetype == archetype)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Domyślne sortowanie po dacie utworzenia (najnowsi pierwsi)
        if not pagination.order_by:
            query = query.order_by(Client.created_at.desc())
        else:
            # Obsługa sortowania po nazwie kolumny
            if hasattr(Client, pagination.order_by):
                order_column = getattr(Client, pagination.order_by)
                if pagination.order_desc:
                    query = query.order_by(order_column.desc())
                else:
                    query = query.order_by(order_column.asc())
        
        # Wykonaj z paginacją
        result = await paginate(db, query, pagination)
        
        logger.info(f"Pobrano {len(result.items)} klientów (strona {result.page}/{result.pages})")
        return result
    
    async def update_client(
        self,
        db: AsyncSession,
        client_id: int,
        update_data: ClientUpdate
    ) -> Optional[Client]:
        """
        Zaktualizuj dane klienta
        
        Args:
            db: Sesja bazy danych
            client_id: ID klienta
            update_data: Dane do aktualizacji
            
        Returns:
            Zaktualizowany klient lub None
        """
        # Pobierz klienta
        client = await self.get(db, client_id)
        
        if not client:
            logger.warning(f"Nie można zaktualizować - klient o ID {client_id} nie istnieje")
            return None
        
        # Aktualizuj tylko podane pola
        update_dict = update_data.model_dump(exclude_unset=True)
        
        if update_dict:
            updated_client = await self.update(db, client, update_dict)
            logger.info(f"Zaktualizowano klienta: {updated_client.alias} (ID: {client_id})")
            return updated_client
        else:
            logger.info(f"Brak danych do aktualizacji dla klienta ID: {client_id}")
            return client
    
    async def delete_client(
        self,
        db: AsyncSession,
        client_id: int
    ) -> bool:
        """
        Usuń klienta (kaskadowo z sesjami)
        
        Args:
            db: Sesja bazy danych
            client_id: ID klienta
            
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        success = await self.delete(db, client_id)
        
        if success:
            logger.info(f"Usunięto klienta o ID: {client_id}")
        else:
            logger.warning(f"Nie można usunąć - klient o ID {client_id} nie istnieje")
            
        return success
    
    async def get_client_by_alias(
        self,
        db: AsyncSession,
        alias: str
    ) -> Optional[Client]:
        """
        Znajdź klienta po aliasie
        
        Args:
            db: Sesja bazy danych
            alias: Alias klienta
            
        Returns:
            Klient lub None
        """
        query = select(Client).where(Client.alias == alias)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_clients_by_archetype(
        self,
        db: AsyncSession,
        archetype: str,
        limit: int = 100
    ) -> List[Client]:
        """
        Pobierz klientów według archetypu
        
        Args:
            db: Sesja bazy danych
            archetype: Nazwa archetypu
            limit: Maksymalna liczba wyników
            
        Returns:
            Lista klientów
        """
        query = select(Client).where(Client.archetype == archetype).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_client_statistics(
        self,
        db: AsyncSession,
        client_id: int
    ) -> Dict[str, Any]:
        """
        Pobierz statystyki klienta
        
        Args:
            db: Sesja bazy danych
            client_id: ID klienta
            
        Returns:
            Słownik ze statystykami
        """
        # Sprawdź czy klient istnieje
        client = await self.get(db, client_id)
        if not client:
            return {}
        
        # Policz sesje
        sessions_count = await db.execute(
            select(func.count(SessionModel.id))
            .where(SessionModel.client_id == client_id)
        )
        sessions_count = sessions_count.scalar()
        
        # Średni potencjał
        avg_potential = await db.execute(
            select(func.avg(SessionModel.potential_score))
            .where(SessionModel.client_id == client_id)
            .where(SessionModel.potential_score.isnot(None))
        )
        avg_potential = avg_potential.scalar()
        
        # Ostatnia sesja
        last_session = await db.execute(
            select(func.max(SessionModel.start_time))
            .where(SessionModel.client_id == client_id)
        )
        last_session = last_session.scalar()
        
        return {
            "client_id": client_id,
            "sessions_count": sessions_count or 0,
            "avg_potential_score": float(avg_potential) if avg_potential else None,
            "last_session_date": last_session,
            "archetype": client.archetype,
            "tags": client.tags or []
        }
    
    async def search_clients(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10
    ) -> List[Client]:
        """
        Wyszukaj klientów po nazwie, firmie lub kontakcie
        
        Args:
            db: Sesja bazy danych
            query: Fraza wyszukiwania
            limit: Maksymalna liczba wyników
            
        Returns:
            Lista klientów
        """
        search_query = select(Client).where(
            or_(
                Client.alias.ilike(f"%{query}%"),
                Client.notes.ilike(f"%{query}%")
            )
        ).limit(limit)
        
        result = await db.execute(search_query)
        clients = result.scalars().all()
        
        logger.info(f"Znaleziono {len(clients)} klientów dla frazy: '{query}'")
        return clients
