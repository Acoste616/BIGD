"""
Repozytorium dla operacji na sesjach rozmów z klientami
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload

from app.core.db_utils import DatabaseRepository, PaginationParams, PaginatedResponse, paginate
from app.models.domain import Session as SessionModel, Client, Interaction
from app.schemas.session import SessionCreate, SessionCreateNested, SessionUpdate, SessionEnd
import logging

logger = logging.getLogger(__name__)


class SessionRepository(DatabaseRepository):
    """
    Repozytorium dla modelu Session z rozszerzonymi funkcjonalnościami
    """
    
    def __init__(self):
        super().__init__(SessionModel)
    
    async def create_session(
        self,
        db: AsyncSession,
        client_id: int,
        session_data: Optional[SessionCreateNested] = None
    ) -> SessionModel:
        """
        Rozpocznij nową sesję dla klienta
        
        Args:
            db: Sesja bazy danych
            client_id: ID klienta
            session_data: Opcjonalne dane początkowe sesji
            
        Returns:
            Utworzona sesja
            
        Raises:
            ValueError: Gdy klient nie istnieje
        """
        try:
            # Sprawdź czy klient istnieje
            client_exists = await db.execute(
                select(Client).where(Client.id == client_id)
            )
            if not client_exists.scalar_one_or_none():
                raise ValueError(f"Klient o ID {client_id} nie istnieje")
            
            # Sprawdź czy klient nie ma już aktywnej sesji
            active_session = await self.get_active_session_for_client(db, client_id)
            if active_session:
                logger.warning(f"Klient {client_id} ma już aktywną sesję (ID: {active_session.id})")
                # Możemy albo zwrócić istniejącą, albo zakończyć starą
                # Tutaj zakończmy starą automatycznie
                await self.end_session(db, active_session.id, auto_summary="Sesja zakończona automatycznie - rozpoczęto nową")
            
            # Przygotuj dane sesji
            session_dict = {
                "client_id": client_id,
                "start_time": datetime.utcnow()
            }
            
            # Dodaj opcjonalne dane
            if session_data:
                data = session_data.model_dump(exclude_unset=True)
                session_dict.update(data)
            
            # Utwórz sesję
            db_session = await self.create(db, session_dict)
            
            logger.info(f"Utworzono nową sesję ID: {db_session.id} dla klienta ID: {client_id}")
            return db_session
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia sesji: {e}")
            raise
    
    async def get_session(
        self,
        db: AsyncSession,
        session_id: int,
        include_client: bool = False,
        include_interactions: bool = False
    ) -> Optional[SessionModel]:
        """
        Pobierz sesję po ID
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            include_client: Czy dołączyć dane klienta
            include_interactions: Czy dołączyć interakcje
            
        Returns:
            Sesja lub None
        """
        query = select(SessionModel).where(SessionModel.id == session_id)
        
        # Opcjonalne ładowanie relacji
        if include_client:
            query = query.options(joinedload(SessionModel.client))
        if include_interactions:
            query = query.options(selectinload(SessionModel.interactions))
        
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            logger.debug(f"Pobrano sesję ID: {session_id}")
        else:
            logger.warning(f"Nie znaleziono sesji o ID: {session_id}")
            
        return session
    
    async def get_client_sessions(
        self,
        db: AsyncSession,
        client_id: int,
        pagination: PaginationParams,
        only_active: bool = False,
        session_type: Optional[str] = None
    ) -> PaginatedResponse:
        """
        Pobierz sesje klienta z paginacją
        
        Args:
            db: Sesja bazy danych
            client_id: ID klienta
            pagination: Parametry paginacji
            only_active: Czy tylko aktywne sesje
            session_type: Filtr typu sesji
            
        Returns:
            PaginatedResponse z sesjami
        """
        # Podstawowe zapytanie
        query = select(SessionModel).where(SessionModel.client_id == client_id)
        
        # Filtry
        if only_active:
            query = query.where(SessionModel.end_time.is_(None))
        
        if session_type:
            query = query.where(SessionModel.session_type == session_type)
        
        # Domyślne sortowanie - najnowsze pierwsze
        if not pagination.order_by:
            query = query.order_by(SessionModel.start_time.desc())
        else:
            if hasattr(SessionModel, pagination.order_by):
                order_column = getattr(SessionModel, pagination.order_by)
                if pagination.order_desc:
                    query = query.order_by(order_column.desc())
                else:
                    query = query.order_by(order_column.asc())
        
        # Wykonaj z paginacją
        result = await paginate(db, query, pagination)
        
        logger.info(f"Pobrano {len(result.items)} sesji dla klienta ID: {client_id}")
        return result
    
    async def update_session(
        self,
        db: AsyncSession,
        session_id: int,
        update_data: SessionUpdate
    ) -> Optional[SessionModel]:
        """
        Zaktualizuj dane sesji
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            update_data: Dane do aktualizacji
            
        Returns:
            Zaktualizowana sesja lub None
        """
        session = await self.get(db, session_id)
        
        if not session:
            logger.warning(f"Nie można zaktualizować - sesja o ID {session_id} nie istnieje")
            return None
        
        # Aktualizuj tylko podane pola
        update_dict = update_data.model_dump(exclude_unset=True)
        
        if update_dict:
            updated_session = await self.update(db, session, update_dict)
            logger.info(f"Zaktualizowano sesję ID: {session_id}")
            return updated_session
        else:
            logger.info(f"Brak danych do aktualizacji dla sesji ID: {session_id}")
            return session
    
    async def end_session(
        self,
        db: AsyncSession,
        session_id: int,
        end_data: Optional[SessionEnd] = None,
        auto_summary: Optional[str] = None
    ) -> Optional[SessionModel]:
        """
        Zakończ sesję
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            end_data: Dane końcowe sesji
            auto_summary: Automatyczne podsumowanie (jeśli brak end_data)
            
        Returns:
            Zakończona sesja lub None
        """
        session = await self.get(db, session_id)
        
        if not session:
            logger.warning(f"Nie można zakończyć - sesja o ID {session_id} nie istnieje")
            return None
        
        if session.end_time:
            logger.warning(f"Sesja {session_id} jest już zakończona")
            return session
        
        # Przygotuj dane aktualizacji
        update_dict = {
            "end_time": datetime.utcnow()
        }
        
        if end_data:
            update_dict.update(end_data.model_dump(exclude_unset=True))
        elif auto_summary:
            update_dict["summary"] = auto_summary
        
        # Zaktualizuj sesję
        ended_session = await self.update(db, session, update_dict)
        logger.info(f"Zakończono sesję ID: {session_id}")
        
        return ended_session
    
    async def delete_session(
        self,
        db: AsyncSession,
        session_id: int
    ) -> bool:
        """
        Usuń sesję (kaskadowo z interakcjami)
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        success = await self.delete(db, session_id)
        
        if success:
            logger.info(f"Usunięto sesję o ID: {session_id}")
        else:
            logger.warning(f"Nie można usunąć - sesja o ID {session_id} nie istnieje")
            
        return success
    
    async def get_active_session_for_client(
        self,
        db: AsyncSession,
        client_id: int
    ) -> Optional[SessionModel]:
        """
        Pobierz aktywną sesję klienta (jeśli istnieje)
        
        Args:
            db: Sesja bazy danych
            client_id: ID klienta
            
        Returns:
            Aktywna sesja lub None
        """
        query = select(SessionModel).where(
            and_(
                SessionModel.client_id == client_id,
                SessionModel.end_time.is_(None)
            )
        ).order_by(SessionModel.start_time.desc())
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_session_statistics(
        self,
        db: AsyncSession,
        session_id: int
    ) -> Dict[str, Any]:
        """
        Pobierz statystyki sesji
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            
        Returns:
            Słownik ze statystykami
        """
        # Sprawdź czy sesja istnieje
        session = await self.get(db, session_id)
        if not session:
            return {}
        
        # Policz interakcje
        interactions_count = await db.execute(
            select(func.count(Interaction.id))
            .where(Interaction.session_id == session_id)
        )
        interactions_count = interactions_count.scalar()
        
        # Suma tokenów
        total_tokens = await db.execute(
            select(func.sum(Interaction.tokens_used))
            .where(Interaction.session_id == session_id)
        )
        total_tokens = total_tokens.scalar() or 0
        
        # Średnia pewność AI
        avg_confidence = await db.execute(
            select(func.avg(Interaction.confidence_score))
            .where(Interaction.session_id == session_id)
            .where(Interaction.confidence_score.isnot(None))
        )
        avg_confidence = avg_confidence.scalar()
        
        # Czas trwania
        duration = None
        if session.start_time:
            end_time = session.end_time or datetime.utcnow()
            duration = int((end_time - session.start_time).total_seconds() / 60)  # w minutach
        
        return {
            "session_id": session_id,
            "client_id": session.client_id,
            "interactions_count": interactions_count or 0,
            "total_tokens_used": int(total_tokens),
            "avg_confidence_score": float(avg_confidence) if avg_confidence else None,
            "duration_minutes": duration,
            "is_active": session.end_time is None,
            "session_type": session.session_type,
            "sentiment_score": session.sentiment_score,
            "potential_score": session.potential_score
        }
    
    async def get_recent_sessions(
        self,
        db: AsyncSession,
        limit: int = 10,
        only_active: bool = False
    ) -> List[SessionModel]:
        """
        Pobierz ostatnie sesje
        
        Args:
            db: Sesja bazy danych
            limit: Maksymalna liczba wyników
            only_active: Czy tylko aktywne
            
        Returns:
            Lista ostatnich sesji
        """
        query = select(SessionModel).options(
            joinedload(SessionModel.client)
        )
        
        if only_active:
            query = query.where(SessionModel.end_time.is_(None))
        
        query = query.order_by(SessionModel.start_time.desc()).limit(limit)
        
        result = await db.execute(query)
        sessions = result.scalars().unique().all()
        
        logger.info(f"Pobrano {len(sessions)} ostatnich sesji")
        return sessions
    
    async def get_sessions_by_outcome(
        self,
        db: AsyncSession,
        outcome: str,
        limit: int = 100
    ) -> List[SessionModel]:
        """
        Pobierz sesje według wyniku
        
        Args:
            db: Sesja bazy danych
            outcome: Wynik sesji (np. "interested", "closed_deal")
            limit: Maksymalna liczba wyników
            
        Returns:
            Lista sesji
        """
        query = select(SessionModel).where(
            SessionModel.outcome == outcome
        ).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def calculate_client_engagement(
        self,
        db: AsyncSession,
        client_id: int
    ) -> Dict[str, Any]:
        """
        Oblicz zaangażowanie klienta na podstawie jego sesji
        
        Args:
            db: Sesja bazy danych
            client_id: ID klienta
            
        Returns:
            Metryki zaangażowania
        """
        # Całkowita liczba sesji
        total_sessions = await db.execute(
            select(func.count(SessionModel.id))
            .where(SessionModel.client_id == client_id)
        )
        total_sessions = total_sessions.scalar() or 0
        
        # Zakończone sesje
        completed_sessions = await db.execute(
            select(func.count(SessionModel.id))
            .where(
                and_(
                    SessionModel.client_id == client_id,
                    SessionModel.end_time.isnot(None)
                )
            )
        )
        completed_sessions = completed_sessions.scalar() or 0
        
        # Średni czas trwania (w minutach)
        avg_duration = await db.execute(
            select(func.avg(
                func.extract('epoch', SessionModel.end_time - SessionModel.start_time) / 60
            ))
            .where(
                and_(
                    SessionModel.client_id == client_id,
                    SessionModel.end_time.isnot(None)
                )
            )
        )
        avg_duration = avg_duration.scalar()
        
        # Średni sentiment i potencjał
        avg_sentiment = await db.execute(
            select(func.avg(SessionModel.sentiment_score))
            .where(SessionModel.client_id == client_id)
            .where(SessionModel.sentiment_score.isnot(None))
        )
        avg_sentiment = avg_sentiment.scalar()
        
        avg_potential = await db.execute(
            select(func.avg(SessionModel.potential_score))
            .where(SessionModel.client_id == client_id)
            .where(SessionModel.potential_score.isnot(None))
        )
        avg_potential = avg_potential.scalar()
        
        return {
            "client_id": client_id,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "avg_session_duration_minutes": float(avg_duration) if avg_duration else None,
            "avg_sentiment_score": float(avg_sentiment) if avg_sentiment else None,
            "avg_potential_score": float(avg_potential) if avg_potential else None,
            "engagement_level": self._calculate_engagement_level(
                total_sessions, avg_duration, avg_sentiment
            )
        }
    
    def _calculate_engagement_level(
        self,
        sessions_count: int,
        avg_duration: Optional[float],
        avg_sentiment: Optional[float]
    ) -> str:
        """
        Oblicz poziom zaangażowania na podstawie metryk
        
        Args:
            sessions_count: Liczba sesji
            avg_duration: Średni czas trwania
            avg_sentiment: Średni sentiment
            
        Returns:
            Poziom zaangażowania (low/medium/high/very_high)
        """
        score = 0
        
        # Punkty za liczbę sesji
        if sessions_count >= 5:
            score += 3
        elif sessions_count >= 3:
            score += 2
        elif sessions_count >= 1:
            score += 1
        
        # Punkty za czas trwania
        if avg_duration and avg_duration >= 30:
            score += 3
        elif avg_duration and avg_duration >= 15:
            score += 2
        elif avg_duration and avg_duration >= 5:
            score += 1
        
        # Punkty za sentiment
        if avg_sentiment and avg_sentiment >= 8:
            score += 3
        elif avg_sentiment and avg_sentiment >= 6:
            score += 2
        elif avg_sentiment and avg_sentiment >= 4:
            score += 1
        
        # Określ poziom
        if score >= 8:
            return "very_high"
        elif score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"
