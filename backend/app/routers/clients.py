"""
Router dla endpointów zarządzania klientami - uproszczona wersja
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.client_repository import ClientRepository
from app.schemas.client import Client, ClientCreate
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


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Utwórz nowego klienta (alias generowany automatycznie)
    
    Args:
        client_data: Dane nowego klienta (bez aliasu)
        db: Sesja bazy danych
        
    Returns:
        Utworzony klient z automatycznie wygenerowanym aliasem
    """
    try:
        # Utwórz nowego klienta (alias generowany w repository)
        new_client = await client_repo.create_client(db, client_data)
        
        logger.info(f"API: Utworzono klienta {new_client.alias} (ID: {new_client.id})")
        return new_client
        
    except Exception as e:
        logger.error(f"Błąd podczas tworzenia klienta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas tworzenia klienta"
        )


@router.get("/")
async def get_clients(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Liczba klientów do pominięcia"),
    limit: int = Query(100, ge=1, le=1000, description="Maksymalna liczba klientów")
):
    """
    Pobierz listę klientów z podstawową paginacją
    
    Args:
        db: Sesja bazy danych
        skip: Liczba klientów do pominięcia
        limit: Maksymalna liczba klientów
        
    Returns:
        Lista klientów
    """
    try:
        # Pobierz klientów przez uproszczone repository
        clients = await client_repo.get_clients(db=db, skip=skip, limit=limit)
        
        logger.info(f"API: Pobrano {len(clients)} klientów")
        return clients
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania listy klientów: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania listy klientów"
        )


@router.get("/{client_id}")
async def get_client(
    client_id: int = Path(..., description="ID klienta"),
    db: AsyncSession = Depends(get_db)
):
    """
    Pobierz szczegóły klienta po ID
    
    Args:
        client_id: ID klienta
        db: Sesja bazy danych
        
    Returns:
        Szczegóły klienta
    """
    try:
        client = await client_repo.get_client(db, client_id)
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Klient o ID {client_id} nie został znaleziony"
            )
        
        logger.info(f"API: Pobrano klienta {client.alias} (ID: {client_id})")
        return client
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania klienta {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wystąpił błąd podczas pobierania szczegółów klienta"
        )