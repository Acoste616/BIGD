from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate
# Zmieniamy import, aby używać schematu Pydantic dla odpowiedzi, a nie modelu SQLAlchemy
from app.schemas.interaction import Interaction

router = APIRouter(
    tags=["Feedback"],
    responses={404: {"description": "Not found"}},
)

feedback_repository = FeedbackRepository()

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
    return await feedback_repository.add_feedback(db=db, feedback_data=feedback)