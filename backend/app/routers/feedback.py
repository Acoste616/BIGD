from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate
from app.services.dojo_service import admin_dialogue_service

router = APIRouter(
    tags=["Feedback"],
    responses={404: {"description": "Not found"}},
)

feedback_repository = FeedbackRepository()
logger = logging.getLogger(__name__)

@router.post("/interactions/{interaction_id}/feedback/", status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: FeedbackCreate,
    interaction_id: int = Path(..., description="ID interakcji"), 
    db: AsyncSession = Depends(get_db)
):
    """
    Tworzy nowy wpis z oceną (feedback) dla konkretnej interakcji.

    - **interaction_id**: ID interakcji, której dotyczy ocena.
    - **suggestion_id**: Unikalne ID ocenianej sugestii.
    - **suggestion_type**: Typ sugestii (np. 'quick_response').
    - **score**: Ocena (+1 dla kciuka w górę, -1 dla kciuka w dół).
    """
    # Store feedback in the dedicated Feedback model
    created_feedback = await feedback_repository.add_feedback(db=db, feedback_data=feedback)
    
    # Trigger learning process (new functionality)
    try:
        # Call the new process_feedback_for_learning method in DojoService
        await admin_dialogue_service.process_feedback_for_learning(
            feedback_id=created_feedback.id,
            interaction_id=interaction_id,
            suggestion_id=feedback.suggestion_id,
            suggestion_type=feedback.suggestion_type,
            rating=feedback.score
        )
    except Exception as e:
        # Log error but don't fail the feedback storage
        logger.error(f"Failed to process feedback for learning: {e}")
    
    return created_feedback