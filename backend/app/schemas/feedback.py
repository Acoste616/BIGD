"""
Schematy Pydantic dla modelu Feedback
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Literal, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .interaction import Interaction


class FeedbackBase(BaseModel):
    """
    Bazowy schemat feedbacku - wspólne pola
    """
    interaction_id: int = Field(..., description="ID interakcji")
    rating: Literal[1, -1] = Field(..., description="Ocena: 1 (pozytywna) lub -1 (negatywna)")
    feedback_type: Optional[str] = Field(None, max_length=50, description="Typ feedbacku (accuracy/relevance/usefulness)")
    comment: Optional[str] = Field(None, description="Opcjonalny komentarz użytkownika")
    applied: Optional[Literal[0, 1]] = Field(None, description="Czy sugestia została zastosowana (1=tak, 0=nie)")
    
    @field_validator('rating')
    def validate_rating(cls, v):
        """Walidacja wartości ratingu"""
        if v not in [1, -1]:
            raise ValueError('Rating musi być 1 (pozytywny) lub -1 (negatywny)')
        return v


class FeedbackCreate(FeedbackBase):
    """
    Schemat do tworzenia nowego feedbacku
    """
    pass


class FeedbackUpdate(BaseModel):
    """
    Schemat do aktualizacji feedbacku
    """
    rating: Optional[Literal[1, -1]] = None
    feedback_type: Optional[str] = Field(None, max_length=50)
    comment: Optional[str] = None
    applied: Optional[Literal[0, 1]] = None


class Feedback(FeedbackBase):
    """
    Schemat pełny feedbacku - zwracany przez API
    """
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackWithInteraction(Feedback):
    """
    Schemat feedbacku z danymi interakcji
    """

    
    interaction: Optional["Interaction"] = None
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackSummary(BaseModel):
    """
    Schemat podsumowania feedbacku - statystyki
    """
    total_feedbacks: int = Field(..., description="Całkowita liczba feedbacków")
    positive_count: int = Field(..., description="Liczba pozytywnych ocen")
    negative_count: int = Field(..., description="Liczba negatywnych ocen")
    positive_rate: float = Field(..., ge=0, le=1, description="Wskaźnik pozytywnych ocen")
    
    # Szczegóły po typie
    by_type: dict[str, dict[str, int]] = Field(default={}, description="Statystyki według typu")
    
    # Wskaźniki zastosowania
    applied_count: int = Field(default=0, description="Liczba zastosowanych sugestii")
    application_rate: Optional[float] = Field(None, ge=0, le=1, description="Wskaźnik zastosowania")
    
    # Najczęstsze problemy
    common_issues: list[str] = Field(default=[], description="Najczęstsze problemy z komentarzy")
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackAnalytics(BaseModel):
    """
    Schemat analityki feedbacku dla sesji/klienta
    """
    entity_id: int = Field(..., description="ID encji (sesji/klienta)")
    entity_type: Literal["session", "client"] = Field(..., description="Typ encji")
    period: Optional[str] = Field(None, description="Okres analizy")
    
    # Metryki ogólne
    total_interactions: int = Field(..., description="Całkowita liczba interakcji")
    interactions_with_feedback: int = Field(..., description="Interakcje z feedbackiem")
    feedback_coverage: float = Field(..., ge=0, le=1, description="Pokrycie feedbackiem")
    
    # Metryki jakości
    avg_rating: float = Field(..., ge=-1, le=1, description="Średnia ocena")
    quality_score: float = Field(..., ge=0, le=100, description="Ogólny wskaźnik jakości")
    
    # Trendy
    improvement_trend: Optional[str] = Field(None, description="Trend poprawy (improving/stable/declining)")
    best_performing_areas: list[str] = Field(default=[], description="Najlepiej oceniane obszary")
    areas_for_improvement: list[str] = Field(default=[], description="Obszary do poprawy")
    
    model_config = ConfigDict(from_attributes=True)


# Import cykliczny - rozwiązanie dla typowania  
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .interaction import Interaction

# Aktualizacja modelu po imporcie
# FeedbackWithInteraction.model_rebuild()  # Przeniesione do __init__.py
