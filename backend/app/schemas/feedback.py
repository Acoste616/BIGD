from pydantic import BaseModel

class FeedbackCreate(BaseModel):
    """
    Schemat Pydantic do walidacji danych przychodzących
    dla nowej oceny (feedbacku) od użytkownika.
    """
    interaction_id: int
    suggestion_id: str
    suggestion_type: str
    score: int