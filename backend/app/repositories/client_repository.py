from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.domain import Client, Session as SessionModel
from app.schemas.client import ClientCreate

class ClientRepository:
    """
    Repozytorium do zarządzania operacjami na danych klientów.
    """
    async def get(self, db: AsyncSession, client_id: int):
        """Alias dla get_client - kompatybilność z innymi routerami"""
        return await self.get_client(db, client_id)

    async def get_client(self, db: AsyncSession, client_id: int):
        query = select(Client).where(Client.id == client_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_clients(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        query = select(Client).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_client(self, db: AsyncSession, client: ClientCreate):
        """
        Tworzy nowego klienta. Jeśli alias nie jest podany, generuje go automatycznie.
        """
        client_data = client.model_dump()

        # Poprawna logika: sprawdzamy i modyfikujemy słownik, a nie model Pydantic
        if not client_data.get('alias'):
            # Policz istniejących klientów
            count_query = select(func.count(Client.id))
            count_result = await db.execute(count_query)
            count = count_result.scalar() or 0
            
            new_id = count + 1
            client_data['alias'] = f"Klient #{new_id}"

        db_client = Client(**client_data)
        db.add(db_client)
        await db.flush()
        await db.refresh(db_client)
        return db_client

    async def create_client_with_session(self, db: AsyncSession, client: ClientCreate):
        """
        Tworzy klienta i od razu powiązaną z nim nową sesję.
        """
        db_client = await self.create_client(db, client)
        db_session = SessionModel(client_id=db_client.id)
        db.add(db_session)
        await db.flush()
        await db.refresh(db_session)
        return db_client, db_session