from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.domain import Interaction
from app.schemas.feedback import FeedbackCreate

class FeedbackRepository:
    """
    Repozytorium do zarządzania operacjami na danych
    związanymi z feedbackiem od użytkowników.
    """
    async def add_feedback(self, db: AsyncSession, feedback_data: FeedbackCreate) -> Interaction:
        """
        Dodaje nowy wpis z oceną (feedback) do konkretnej interakcji.

        Args:
            db (AsyncSession): Sesja bazy danych.
            feedback_data (FeedbackCreate): Dane nowej oceny.

        Returns:
            Interaction: Zaktualizowany obiekt interakcji.
            
        Raises:
            HTTPException: Jeśli interakcja o podanym ID nie zostanie znaleziona.
        """
        query = select(Interaction).where(Interaction.id == feedback_data.interaction_id)
        result = await db.execute(query)
        interaction = result.scalar_one_or_none()

        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interaction with id {feedback_data.interaction_id} not found"
            )

        new_feedback_entry = {
            "suggestion_id": feedback_data.suggestion_id,
            "suggestion_type": feedback_data.suggestion_type,
            "score": feedback_data.score
        }

        # Inicjalizujemy listę, jeśli jest None
        if interaction.feedback_data is None:
            interaction.feedback_data = []

        interaction.feedback_data.append(new_feedback_entry)
        
        # Oznaczamy pole JSONB jako zmodyfikowane, aby SQLAlchemy wykryło zmianę
        flag_modified(interaction, "feedback_data")

        await db.flush()
        await db.refresh(interaction)
        
        return interaction