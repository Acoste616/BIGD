from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.domain import Interaction, Feedback
from app.schemas.feedback import FeedbackCreate

class FeedbackRepository:
    """
    Repozytorium do zarządzania operacjami na danych
    związanymi z feedbackiem od użytkowników.
    """
    async def add_feedback(self, db: AsyncSession, feedback_data: FeedbackCreate) -> Feedback:
        """
        Dodaje nowy wpis z oceną (feedback) do bazy danych Feedback.

        Args:
            db (AsyncSession): Sesja bazy danych.
            feedback_data (FeedbackCreate): Dane nowej oceny.

        Returns:
            Feedback: Utworzony obiekt feedbacku.
            
        Raises:
            HTTPException: Jeśli interakcja o podanym ID nie zostanie znaleziona.
        """
        # Sprawdź czy interakcja istnieje
        query = select(Interaction).where(Interaction.id == feedback_data.interaction_id)
        result = await db.execute(query)
        interaction = result.scalar_one_or_none()

        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interaction with id {feedback_data.interaction_id} not found"
            )

        # Utwórz nowy rekord feedbacku
        feedback = Feedback(
            interaction_id=feedback_data.interaction_id,
            suggestion_id=feedback_data.suggestion_id,
            rating=feedback_data.score,
            feedback_type=feedback_data.suggestion_type,
            is_processed_for_learning=0  # Initially not processed for learning
        )

        db.add(feedback)
        await db.flush()
        await db.refresh(feedback)
        
        return feedback

    async def get_feedback_by_interaction_and_suggestion(
        self, 
        db: AsyncSession, 
        interaction_id: int, 
        suggestion_id: str
    ) -> Feedback:
        """
        Pobiera feedback na podstawie interaction_id i suggestion_id.

        Args:
            db (AsyncSession): Sesja bazy danych.
            interaction_id (int): ID interakcji.
            suggestion_id (str): ID sugestii.

        Returns:
            Feedback: Obiekt feedbacku lub None.
        """
        query = select(Feedback).where(
            Feedback.interaction_id == interaction_id,
            Feedback.suggestion_id == suggestion_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def mark_feedback_as_processed(self, db: AsyncSession, feedback_id: int) -> bool:
        """
        Oznacza feedback jako przetworzony dla uczenia.

        Args:
            db (AsyncSession): Sesja bazy danych.
            feedback_id (int): ID feedbacku.

        Returns:
            bool: True jeśli operacja się powiodła.
        """
        query = select(Feedback).where(Feedback.id == feedback_id)
        result = await db.execute(query)
        feedback = result.scalar_one_or_none()
        
        if not feedback:
            return False
            
        feedback.is_processed_for_learning = 1
        await db.flush()
        return True

    async def get_unprocessed_feedback(self, db: AsyncSession, limit: int = 100) -> list:
        """
        Pobiera nieprzetworzony feedback dla uczenia.

        Args:
            db (AsyncSession): Sesja bazy danych.
            limit (int): Limit wyników.

        Returns:
            list: Lista feedbacków nieprzetworzonych.
        """
        query = select(Feedback).where(Feedback.is_processed_for_learning == 0).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())