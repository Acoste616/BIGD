"""
Repozytorium dla operacji na ocenach (feedback) interakcji
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, case
from sqlalchemy.orm import selectinload, joinedload

from app.core.db_utils import DatabaseRepository, PaginationParams, PaginatedResponse, paginate
from app.models.domain import Feedback, Interaction, Session as SessionModel
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate
import logging

logger = logging.getLogger(__name__)


class FeedbackRepository(DatabaseRepository):
    """
    Repozytorium dla modelu Feedback z rozszerzonymi funkcjonalnościami
    """
    
    def __init__(self):
        super().__init__(Feedback)
    
    async def create_feedback(
        self,
        db: AsyncSession,
        interaction_id: int,
        feedback_data: FeedbackCreate
    ) -> Feedback:
        """
        Utwórz nową ocenę dla interakcji
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            feedback_data: Dane oceny
            
        Returns:
            Utworzona ocena
            
        Raises:
            ValueError: Gdy interakcja nie istnieje lub już ma ocenę
        """
        try:
            # Sprawdź czy interakcja istnieje
            interaction = await db.execute(
                select(Interaction).where(Interaction.id == interaction_id)
            )
            interaction = interaction.scalar_one_or_none()
            
            if not interaction:
                raise ValueError(f"Interakcja o ID {interaction_id} nie istnieje")
            
            # Sprawdź czy nie ma już feedbacku (opcjonalnie - możemy pozwolić na wiele)
            existing_feedback = await self.get_interaction_feedback(db, interaction_id)
            if existing_feedback and len(existing_feedback) > 0:
                logger.warning(f"Interakcja {interaction_id} ma już {len(existing_feedback)} ocen")
                # Możemy ograniczyć do jednej oceny lub pozwolić na wiele
                # Tutaj pozwalamy na wiele ocen (np. od różnych użytkowników w przyszłości)
            
            # Przygotuj dane feedbacku
            feedback_dict = {
                "interaction_id": interaction_id,
                "rating": feedback_data.rating,
                "feedback_type": feedback_data.feedback_type,
                "comment": feedback_data.comment,
                "applied": feedback_data.applied,
                "created_at": datetime.utcnow()
            }
            
            # Utwórz feedback
            db_feedback = await self.create(db, feedback_dict)
            
            # Zaktualizuj metryki AI na podstawie feedbacku
            await self._update_ai_metrics(db, interaction, feedback_data.rating)
            
            # Analizuj trend feedbacku
            await self._analyze_feedback_trend(db, interaction.session_id)
            
            logger.info(f"Utworzono feedback ID: {db_feedback.id} dla interakcji {interaction_id} (rating: {feedback_data.rating})")
            return db_feedback
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia feedbacku: {e}")
            raise
    
    async def _update_ai_metrics(
        self,
        db: AsyncSession,
        interaction: Interaction,
        rating: int
    ) -> None:
        """
        Zaktualizuj metryki AI na podstawie feedbacku
        
        Args:
            db: Sesja bazy danych
            interaction: Obiekt interakcji
            rating: Ocena (+1 lub -1)
        """
        try:
            # Modyfikuj confidence score na podstawie feedbacku
            if interaction.confidence_score is not None:
                if rating == 1:
                    # Pozytywny feedback - zwiększ pewność
                    interaction.confidence_score = min(100, interaction.confidence_score + 5)
                else:
                    # Negatywny feedback - zmniejsz pewność
                    interaction.confidence_score = max(0, interaction.confidence_score - 10)
                
                await db.commit()
                logger.debug(f"Zaktualizowano confidence score interakcji {interaction.id} na {interaction.confidence_score}")
            
            # Zapisz informację o problemach jeśli feedback negatywny
            if rating == -1 and interaction.ai_response_json:
                if "feedback_issues" not in interaction.ai_response_json:
                    interaction.ai_response_json["feedback_issues"] = []
                
                interaction.ai_response_json["feedback_issues"].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "issue": "negative_feedback"
                })
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Błąd podczas aktualizacji metryk AI: {e}")
    
    async def _analyze_feedback_trend(
        self,
        db: AsyncSession,
        session_id: int
    ) -> None:
        """
        Analizuj trend feedbacku w sesji
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
        """
        try:
            # Pobierz wszystkie feedbacki dla sesji
            query = select(Feedback).join(Interaction).where(
                Interaction.session_id == session_id
            ).order_by(Feedback.created_at.desc()).limit(10)
            
            result = await db.execute(query)
            recent_feedbacks = result.scalars().all()
            
            if len(recent_feedbacks) >= 3:
                # Oblicz trend ostatnich feedbacków
                recent_ratings = [f.rating for f in recent_feedbacks[:5]]
                negative_count = sum(1 for r in recent_ratings if r == -1)
                
                # Jeśli więcej niż połowa to negatywne, oznacz sesję
                if negative_count >= 3:
                    session = await db.execute(
                        select(SessionModel).where(SessionModel.id == session_id)
                    )
                    session = session.scalar_one_or_none()
                    
                    if session:
                        if not session.risk_indicators:
                            session.risk_indicators = {}
                        
                        session.risk_indicators["negative_feedback_trend"] = True
                        session.risk_indicators["last_negative_trend"] = datetime.utcnow().isoformat()
                        
                        await db.commit()
                        logger.warning(f"Wykryto negatywny trend feedbacku w sesji {session_id}")
                        
        except Exception as e:
            logger.error(f"Błąd podczas analizy trendu feedbacku: {e}")
    
    async def get_feedback(
        self,
        db: AsyncSession,
        feedback_id: int
    ) -> Optional[Feedback]:
        """
        Pobierz feedback po ID
        
        Args:
            db: Sesja bazy danych
            feedback_id: ID feedbacku
            
        Returns:
            Feedback lub None
        """
        result = await db.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )
        feedback = result.scalar_one_or_none()
        
        if feedback:
            logger.debug(f"Pobrano feedback ID: {feedback_id}")
        else:
            logger.warning(f"Nie znaleziono feedbacku o ID: {feedback_id}")
            
        return feedback
    
    async def get_interaction_feedback(
        self,
        db: AsyncSession,
        interaction_id: int
    ) -> List[Feedback]:
        """
        Pobierz wszystkie oceny dla interakcji
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            
        Returns:
            Lista feedbacków
        """
        result = await db.execute(
            select(Feedback)
            .where(Feedback.interaction_id == interaction_id)
            .order_by(Feedback.created_at.desc())
        )
        feedbacks = result.scalars().all()
        
        logger.info(f"Pobrano {len(feedbacks)} ocen dla interakcji {interaction_id}")
        return feedbacks
    
    async def update_feedback(
        self,
        db: AsyncSession,
        feedback_id: int,
        update_data: FeedbackUpdate
    ) -> Optional[Feedback]:
        """
        Zaktualizuj dane feedbacku
        
        Args:
            db: Sesja bazy danych
            feedback_id: ID feedbacku
            update_data: Dane do aktualizacji
            
        Returns:
            Zaktualizowany feedback lub None
        """
        feedback = await self.get(db, feedback_id)
        
        if not feedback:
            logger.warning(f"Nie można zaktualizować - feedback o ID {feedback_id} nie istnieje")
            return None
        
        # Zapisz poprzednią ocenę
        old_rating = feedback.rating
        
        # Aktualizuj tylko podane pola
        update_dict = update_data.model_dump(exclude_unset=True)
        
        if update_dict:
            updated_feedback = await self.update(db, feedback, update_dict)
            
            # Jeśli zmieniono rating, zaktualizuj metryki
            if "rating" in update_dict and update_dict["rating"] != old_rating:
                interaction = await db.execute(
                    select(Interaction).where(Interaction.id == feedback.interaction_id)
                )
                interaction = interaction.scalar_one_or_none()
                
                if interaction:
                    # Cofnij efekt starej oceny i zastosuj nową
                    await self._update_ai_metrics(db, interaction, update_dict["rating"])
            
            logger.info(f"Zaktualizowano feedback ID: {feedback_id}")
            return updated_feedback
        else:
            logger.info(f"Brak danych do aktualizacji dla feedbacku ID: {feedback_id}")
            return feedback
    
    async def delete_feedback(
        self,
        db: AsyncSession,
        feedback_id: int
    ) -> bool:
        """
        Usuń feedback
        
        Args:
            db: Sesja bazy danych
            feedback_id: ID feedbacku
            
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        success = await self.delete(db, feedback_id)
        
        if success:
            logger.info(f"Usunięto feedback o ID: {feedback_id}")
        else:
            logger.warning(f"Nie można usunąć - feedback o ID {feedback_id} nie istnieje")
            
        return success
    
    async def get_feedback_statistics(
        self,
        db: AsyncSession,
        entity_type: str = "global",
        entity_id: Optional[int] = None,
        time_period: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Pobierz statystyki feedbacku
        
        Args:
            db: Sesja bazy danych
            entity_type: Typ encji (global, session, client)
            entity_id: ID encji (dla session/client)
            time_period: Okres czasu w dniach (None = wszystkie)
            
        Returns:
            Słownik ze statystykami
        """
        # Podstawowe zapytanie
        query = select(
            func.count(Feedback.id).label("total"),
            func.sum(case((Feedback.rating == 1, 1), else_=0)).label("positive"),
            func.sum(case((Feedback.rating == -1, 1), else_=0)).label("negative"),
            func.avg(Feedback.rating).label("avg_rating")
        )
        
        # Dodaj JOIN w zależności od typu
        if entity_type == "session" and entity_id:
            query = query.join(Interaction).where(Interaction.session_id == entity_id)
        elif entity_type == "client" and entity_id:
            query = query.join(Interaction).join(SessionModel).where(SessionModel.client_id == entity_id)
        
        # Filtr czasowy
        if time_period:
            cutoff_date = datetime.utcnow() - timedelta(days=time_period)
            query = query.where(Feedback.created_at >= cutoff_date)
        
        result = await db.execute(query)
        stats = result.one()
        
        # Oblicz dodatkowe metryki
        total = stats.total or 0
        positive = stats.positive or 0
        negative = stats.negative or 0
        
        # Pobierz najczęstsze typy feedbacku
        type_query = select(
            Feedback.feedback_type,
            func.count(Feedback.id).label("count")
        ).group_by(Feedback.feedback_type)
        
        if entity_type == "session" and entity_id:
            type_query = type_query.join(Interaction).where(Interaction.session_id == entity_id)
        elif entity_type == "client" and entity_id:
            type_query = type_query.join(Interaction).join(SessionModel).where(SessionModel.client_id == entity_id)
        
        type_result = await db.execute(type_query)
        feedback_types = {row.feedback_type: row.count for row in type_result if row.feedback_type}
        
        # Pobierz przykładowe komentarze
        comments_query = select(Feedback.comment, Feedback.rating).where(
            Feedback.comment.isnot(None)
        ).limit(5)
        
        if entity_type == "session" and entity_id:
            comments_query = comments_query.join(Interaction).where(Interaction.session_id == entity_id)
        
        comments_result = await db.execute(comments_query)
        recent_comments = [
            {"comment": row.comment, "rating": row.rating}
            for row in comments_result
        ]
        
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "time_period_days": time_period,
            "total_feedbacks": total,
            "positive_count": positive,
            "negative_count": negative,
            "positive_rate": (positive / total * 100) if total > 0 else 0,
            "negative_rate": (negative / total * 100) if total > 0 else 0,
            "avg_rating": float(stats.avg_rating) if stats.avg_rating else 0,
            "feedback_types": feedback_types,
            "recent_comments": recent_comments,
            "has_issues": negative > positive if total > 10 else False
        }
    
    async def get_problematic_interactions(
        self,
        db: AsyncSession,
        threshold: int = -2,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Znajdź interakcje z najbardziej negatywnym feedbackiem
        
        Args:
            db: Sesja bazy danych
            threshold: Próg sumy ocen (domyślnie -2)
            limit: Maksymalna liczba wyników
            
        Returns:
            Lista problematycznych interakcji
        """
        # Zapytanie agregujące feedback dla interakcji
        query = select(
            Interaction.id,
            Interaction.session_id,
            Interaction.user_input,
            Interaction.timestamp,
            func.sum(Feedback.rating).label("total_rating"),
            func.count(Feedback.id).label("feedback_count")
        ).join(
            Feedback
        ).group_by(
            Interaction.id
        ).having(
            func.sum(Feedback.rating) <= threshold
        ).order_by(
            func.sum(Feedback.rating).asc()
        ).limit(limit)
        
        result = await db.execute(query)
        problematic = []
        
        for row in result:
            problematic.append({
                "interaction_id": row.id,
                "session_id": row.session_id,
                "user_input": row.user_input[:100] + "..." if len(row.user_input) > 100 else row.user_input,
                "timestamp": row.timestamp,
                "total_rating": row.total_rating,
                "feedback_count": row.feedback_count,
                "avg_rating": row.total_rating / row.feedback_count if row.feedback_count > 0 else 0
            })
        
        logger.info(f"Znaleziono {len(problematic)} problematycznych interakcji")
        return problematic
    
    async def get_improvement_suggestions(
        self,
        db: AsyncSession,
        session_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generuj sugestie poprawy na podstawie feedbacku
        
        Args:
            db: Sesja bazy danych
            session_id: Opcjonalny ID sesji dla kontekstu
            
        Returns:
            Sugestie poprawy
        """
        # Pobierz statystyki feedbacku
        if session_id:
            stats = await self.get_feedback_statistics(db, "session", session_id)
        else:
            stats = await self.get_feedback_statistics(db, "global", time_period=7)
        
        suggestions = {
            "performance_score": 100 - stats["negative_rate"],
            "areas_of_concern": [],
            "recommendations": [],
            "positive_patterns": [],
            "training_priorities": []
        }
        
        # Analizuj problemy
        if stats["negative_rate"] > 30:
            suggestions["areas_of_concern"].append("Wysoki odsetek negatywnych ocen")
            suggestions["recommendations"].append("Przegląd jakości odpowiedzi AI")
        
        # Analizuj typy feedbacku
        for feedback_type, count in stats["feedback_types"].items():
            if feedback_type == "accuracy" and count > 5:
                suggestions["training_priorities"].append("Poprawa dokładności odpowiedzi")
            elif feedback_type == "relevance" and count > 5:
                suggestions["training_priorities"].append("Lepsza analiza kontekstu")
            elif feedback_type == "usefulness" and count > 5:
                suggestions["training_priorities"].append("Bardziej praktyczne sugestie")
        
        # Znajdź pozytywne wzorce
        if stats["positive_rate"] > 70:
            suggestions["positive_patterns"].append("Ogólnie wysoka satysfakcja użytkowników")
        
        # Pobierz problematyczne interakcje
        problematic = await self.get_problematic_interactions(db, limit=3)
        if problematic:
            suggestions["areas_of_concern"].append(f"Znaleziono {len(problematic)} problematycznych interakcji")
            suggestions["recommendations"].append("Analiza i poprawa problematycznych przypadków")
        
        return suggestions
    
    async def calculate_ai_performance_metrics(
        self,
        db: AsyncSession,
        time_period: int = 30
    ) -> Dict[str, Any]:
        """
        Oblicz metryki wydajności AI na podstawie feedbacku
        
        Args:
            db: Sesja bazy danych
            time_period: Okres w dniach
            
        Returns:
            Metryki wydajności
        """
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        
        # Podstawowe metryki
        base_stats = await self.get_feedback_statistics(db, "global", time_period=time_period)
        
        # Trend w czasie - porównaj pierwszą i drugą połowę okresu
        mid_date = datetime.utcnow() - timedelta(days=time_period // 2)
        
        first_half = await db.execute(
            select(func.avg(Feedback.rating))
            .where(and_(
                Feedback.created_at >= cutoff_date,
                Feedback.created_at < mid_date
            ))
        )
        first_half_avg = first_half.scalar() or 0
        
        second_half = await db.execute(
            select(func.avg(Feedback.rating))
            .where(Feedback.created_at >= mid_date)
        )
        second_half_avg = second_half.scalar() or 0
        
        # Określ trend
        trend = "stable"
        if second_half_avg > first_half_avg + 0.1:
            trend = "improving"
        elif second_half_avg < first_half_avg - 0.1:
            trend = "declining"
        
        # Wskaźnik zastosowania sugestii
        applied_count = await db.execute(
            select(func.count(Feedback.id))
            .where(and_(
                Feedback.created_at >= cutoff_date,
                Feedback.applied == 1
            ))
        )
        applied = applied_count.scalar() or 0
        
        return {
            "time_period_days": time_period,
            "overall_satisfaction": base_stats["positive_rate"],
            "total_feedback_collected": base_stats["total_feedbacks"],
            "positive_feedback_rate": base_stats["positive_rate"],
            "negative_feedback_rate": base_stats["negative_rate"],
            "average_rating": base_stats["avg_rating"],
            "performance_trend": trend,
            "first_half_avg": float(first_half_avg),
            "second_half_avg": float(second_half_avg),
            "suggestions_applied_count": applied,
            "application_rate": (applied / base_stats["total_feedbacks"] * 100) if base_stats["total_feedbacks"] > 0 else 0,
            "quality_score": self._calculate_quality_score(
                base_stats["positive_rate"],
                applied / base_stats["total_feedbacks"] if base_stats["total_feedbacks"] > 0 else 0,
                trend
            )
        }
    
    def _calculate_quality_score(
        self,
        positive_rate: float,
        application_rate: float,
        trend: str
    ) -> float:
        """
        Oblicz ogólny wskaźnik jakości AI
        
        Args:
            positive_rate: Procent pozytywnych ocen
            application_rate: Wskaźnik zastosowania sugestii
            trend: Trend wydajności
            
        Returns:
            Wskaźnik jakości (0-100)
        """
        # Bazowy wynik z positive rate (waga 60%)
        score = positive_rate * 0.6
        
        # Dodaj punkty za application rate (waga 30%)
        score += application_rate * 100 * 0.3
        
        # Modyfikator za trend (waga 10%)
        if trend == "improving":
            score += 10
        elif trend == "declining":
            score -= 5
        
        return min(100, max(0, score))
