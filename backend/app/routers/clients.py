"""
Router dla endpointów zarządzania klientami
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.db_utils import PaginationParams
from app.repositories.client_repository import ClientRepository
from app.schemas.client import (
    Client,
    ClientCreate,
    ClientUpdate,
    ClientWithSessions,
    ClientSummary
)
import logging

logger = logging.getLogger(__name__)

# Inicjalizacja routera
router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    responses={
        404: {"description": "Klient nie znaleziony"},
        400: {"description": "Nieprawidłowe dane wejściowe"}
    }
)

# Inicjalizacja repozytorium
client_repo = ClientRepository()


@router.post("/", response_model=Client, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db)
) -> Client:
    """
    Utwórz nowego klienta (alias generowany automatycznie)
    
    Args:
        client_data: Dane nowego klienta (bez aliasu)
        db: Sesja bazy danych
        
    Returns:
        Utworzony klient z automatycznie wygenerowanym aliasem
    """
    try:
        # Wygeneruj unikalny alias
        alias = await client_repo.generate_unique_alias(db)
        
        # Utwórz nowego klienta z aliasem
        new_client = await client_repo.create_client_with_alias(db, client_data, alias)
        
        logger.info(f"API: Utworzono klienta {new_client.alias} (ID: {new_client.id})")
        return new_client
        
    except Exception as e:
        logger.error(f"Błąd podczas tworzenia klienta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas tworzenia klienta"
        )


@router.get("/", response_model=Dict[str, Any])
async def get_clients(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Numer strony"),
    page_size: int = Query(20, ge=1, le=100, description="Liczba wyników na stronę"),
    search: Optional[str] = Query(None, description="Fraza wyszukiwania"),
    archetype: Optional[str] = Query(None, description="Filtr po archetypie"),
    order_by: Optional[str] = Query(None, description="Pole do sortowania"),
    order_desc: bool = Query(False, description="Sortowanie malejące")
) -> Dict[str, Any]:
    """
    Pobierz listę klientów z paginacją i filtrowaniem (tylko dane profilujące)
    
    Args:
        db: Sesja bazy danych
        page: Numer strony
        page_size: Rozmiar strony
        search: Wyszukiwanie po aliasie lub notatkach
        archetype: Filtruj po archetypie
        order_by: Pole sortowania (alias, created_at, archetype)
        order_desc: Czy sortować malejąco
        
    Returns:
        Lista klientów z metadanymi paginacji (tylko dane profilujące)
    """
    try:
        # Przygotuj parametry paginacji
        pagination = PaginationParams(
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_desc=order_desc
        )
        
        # Pobierz klientów
        result = await client_repo.get_clients_paginated(
            db=db,
            pagination=pagination,
            search=search,
            archetype=archetype
        )
        
        # Konwertuj do odpowiedzi
        response = result.dict()
        
        # Konwertuj obiekty Client do schematów Pydantic
        response["items"] = [
            Client.model_validate(client) 
            for client in result.items
        ]
        
        logger.info(f"API: Pobrano {len(result.items)} klientów (strona {page})")
        return response
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania listy klientów: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania listy klientów"
        )


@router.get("/{client_id}", response_model=Client)
async def get_client(
    client_id: int = Path(..., description="ID klienta"),
    include_sessions: bool = Query(False, description="Czy dołączyć sesje"),
    db: AsyncSession = Depends(get_db)
) -> Client:
    """
    Pobierz szczegóły klienta po ID
    
    Args:
        client_id: ID klienta
        include_sessions: Czy dołączyć listę sesji
        db: Sesja bazy danych
        
    Returns:
        Dane klienta
        
    Raises:
        HTTPException: Gdy klient nie istnieje
    """
    try:
        client = await client_repo.get_client(
            db=db,
            client_id=client_id,
            include_sessions=include_sessions
        )
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Klient o ID {client_id} nie został znaleziony"
            )
        
        logger.info(f"API: Pobrano dane klienta ID: {client_id}")
        
        # Jeśli include_sessions, zwróć ClientWithSessions
        if include_sessions and client.sessions:
            return ClientWithSessions.model_validate(client)
        
        return Client.model_validate(client)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania klienta {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania danych klienta"
        )


@router.put("/{client_id}", response_model=Client)
async def update_client(
    client_id: int = Path(..., description="ID klienta"),
    update_data: ClientUpdate = ...,
    db: AsyncSession = Depends(get_db)
) -> Client:
    """
    Zaktualizuj dane klienta
    
    Args:
        client_id: ID klienta do aktualizacji
        update_data: Nowe dane klienta
        db: Sesja bazy danych
        
    Returns:
        Zaktualizowany klient
        
    Raises:
        HTTPException: Gdy klient nie istnieje
    """
    try:
        # Sprawdź czy nazwa nie jest zajęta przez innego klienta
        if update_data.name:
            existing = await client_repo.get_client_by_name(db, update_data.name)
            if existing and existing.id != client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Klient o nazwie '{update_data.name}' już istnieje"
                )
        
        # Aktualizuj klienta
        updated_client = await client_repo.update_client(
            db=db,
            client_id=client_id,
            update_data=update_data
        )
        
        if not updated_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Klient o ID {client_id} nie został znaleziony"
            )
        
        logger.info(f"API: Zaktualizowano klienta ID: {client_id}")
        return Client.model_validate(updated_client)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas aktualizacji klienta {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas aktualizacji danych klienta"
        )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int = Path(..., description="ID klienta"),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Usuń klienta (wraz z wszystkimi sesjami - kaskadowo)
    
    Args:
        client_id: ID klienta do usunięcia
        db: Sesja bazy danych
        
    Raises:
        HTTPException: Gdy klient nie istnieje
    """
    try:
        success = await client_repo.delete_client(db, client_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Klient o ID {client_id} nie został znaleziony"
            )
        
        logger.info(f"API: Usunięto klienta ID: {client_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas usuwania klienta {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas usuwania klienta"
        )


@router.get("/{client_id}/statistics", response_model=Dict[str, Any])
async def get_client_statistics(
    client_id: int = Path(..., description="ID klienta"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Pobierz statystyki klienta
    
    Args:
        client_id: ID klienta
        db: Sesja bazy danych
        
    Returns:
        Statystyki klienta (liczba sesji, średni potencjał, itp.)
        
    Raises:
        HTTPException: Gdy klient nie istnieje
    """
    try:
        stats = await client_repo.get_client_statistics(db, client_id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Klient o ID {client_id} nie został znaleziony"
            )
        
        logger.info(f"API: Pobrano statystyki klienta ID: {client_id}")
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania statystyk klienta {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania statystyk"
        )


@router.get("/search/quick", response_model=List[ClientSummary])
async def search_clients(
    q: str = Query(..., min_length=2, description="Fraza wyszukiwania"),
    limit: int = Query(10, ge=1, le=50, description="Maksymalna liczba wyników"),
    db: AsyncSession = Depends(get_db)
) -> List[ClientSummary]:
    """
    Szybkie wyszukiwanie klientów
    
    Args:
        q: Fraza wyszukiwania (minimum 2 znaki)
        limit: Maksymalna liczba wyników
        db: Sesja bazy danych
        
    Returns:
        Lista klientów pasujących do frazy
    """
    try:
        clients = await client_repo.search_clients(
            db=db,
            query=q,
            limit=limit
        )
        
        # Konwertuj do ClientSummary
        summaries = []
        for client in clients:
            # Pobierz statystyki
            stats = await client_repo.get_client_statistics(db, client.id)
            
            summary = ClientSummary(
                id=client.id,
                alias=client.alias,
                archetype=client.archetype,
                tags=client.tags or [],
                sessions_count=stats.get("sessions_count", 0),
                last_contact=stats.get("last_session_date"),
                potential_score=stats.get("avg_potential_score")
            )
            summaries.append(summary)
        
        logger.info(f"API: Wyszukano {len(summaries)} klientów dla frazy '{q}'")
        return summaries
        
    except Exception as e:
        logger.error(f"Błąd podczas wyszukiwania klientów: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas wyszukiwania"
        )
