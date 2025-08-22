from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import Optional
from app.models.domain import Session as SessionModel, Client, Interaction
from app.schemas.session import SessionCreate, SessionCreateNested

class SessionRepository:
    """
    Repozytorium do zarządzania operacjami na danych sesji.
    """
    async def get_session(self, db: AsyncSession, session_id: int):
        query = select(SessionModel).where(SessionModel.id == session_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_sessions(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        query = select(SessionModel).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_client_sessions(self, db: AsyncSession, client_id: int, skip: int = 0, limit: int = 100):
        query = select(SessionModel).where(SessionModel.client_id == client_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_session(self, db: AsyncSession, client_id: int, session_data: Optional[SessionCreateNested] = None):
        """
        Tworzy nową sesję dla klienta.
        """
        # Sprawdź czy klient istnieje
        client_query = select(Client).where(Client.id == client_id)
        client_result = await db.execute(client_query)
        client = client_result.scalar_one_or_none()
        
        if not client:
            raise ValueError(f"Klient o ID {client_id} nie istnieje")

        # Przygotuj dane sesji
        session_dict = {
            "client_id": client_id,
            "status": "active"
        }
        
        if session_data:
            session_dict.update(session_data.model_dump(exclude_unset=True))

        db_session = SessionModel(**session_dict)
        db.add(db_session)
        await db.flush()
        await db.refresh(db_session)
        return db_session

    async def end_session(self, db: AsyncSession, session_id: int):
        """
        Kończy sesję ustawiając end_timestamp.
        """
        query = select(SessionModel).where(SessionModel.id == session_id)
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            return None
        
        session.end_timestamp = datetime.utcnow()
        session.status = "completed"
        await db.flush()
        await db.refresh(session)
        return session

    async def get_active_session_for_client(self, db: AsyncSession, client_id: int):
        """
        Pobiera aktywną sesję dla klienta.
        """
        query = select(SessionModel).where(
            SessionModel.client_id == client_id,
            SessionModel.end_timestamp == None
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_session(self, db: AsyncSession, session_id: int, update_data: dict):
        """
        Aktualizuje dane sesji.
        """
        query = select(SessionModel).where(SessionModel.id == session_id)
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            return None
        
        for field, value in update_data.items():
            if hasattr(session, field):
                setattr(session, field, value)
        
        await db.flush()
        await db.refresh(session)
        return session

    async def delete_session(self, db: AsyncSession, session_id: int):
        """
        Usuwa sesję.
        """
        query = select(SessionModel).where(SessionModel.id == session_id)
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        await db.delete(session)
        await db.flush()
        return True

    async def get_session_statistics(self, db: AsyncSession, session_id: int):
        """
        Pobiera statystyki sesji.
        """
        session = await self.get_session(db, session_id)
        if not session:
            return {}
        
        # Policz interakcje
        interactions_query = select(func.count(Interaction.id)).where(Interaction.session_id == session_id)
        interactions_result = await db.execute(interactions_query)
        interactions_count = interactions_result.scalar() or 0
        
        return {
            "session_id": session_id,
            "interactions_count": interactions_count,
            "status": session.status,
            "start_timestamp": session.start_timestamp.isoformat() if session.start_timestamp else None,
            "end_timestamp": session.end_timestamp.isoformat() if session.end_timestamp else None
        }

    async def get_recent_sessions(self, db: AsyncSession, limit: int = 10):
        """
        Pobiera ostatnie sesje.
        """
        query = select(SessionModel).order_by(SessionModel.start_timestamp.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def calculate_client_engagement(self, db: AsyncSession, client_id: int):
        """
        Oblicza zaangażowanie klienta.
        """
        # Policz sesje
        sessions_query = select(func.count(SessionModel.id)).where(SessionModel.client_id == client_id)
        sessions_result = await db.execute(sessions_query)
        sessions_count = sessions_result.scalar() or 0
        
        # Znajdź ostatnią sesję
        last_session_query = select(SessionModel).where(
            SessionModel.client_id == client_id
        ).order_by(SessionModel.start_timestamp.desc()).limit(1)
        last_session_result = await db.execute(last_session_query)
        last_session = last_session_result.scalar_one_or_none()
        
        engagement_level = "low"
        if sessions_count >= 5:
            engagement_level = "high"
        elif sessions_count >= 2:
            engagement_level = "medium"
        
        return {
            "client_id": client_id,
            "sessions_count": sessions_count,
            "engagement_level": engagement_level,
            "last_session_date": last_session.start_timestamp.isoformat() if last_session else None
        }