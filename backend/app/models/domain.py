import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base

# Enum dla statusu promptów
class PromptStatus(enum.Enum):
    ACTIVE = "active"
    EXPERIMENTAL = "experimental"
    ARCHIVED = "archived"

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, index=True, nullable=True)
    notes = Column(Text, nullable=True)
    archetype = Column(String(100), nullable=True)
    tags = Column(JSONB, nullable=True, comment="Lista tagów klienta")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    sessions = relationship("Session", back_populates="client")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    is_active = Column(Integer, default=1)
    start_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    end_timestamp = Column(DateTime, nullable=True)
    
    # Zmiany z Planu v2.4 (Moduł 5)
    status = Column(String, default='active', nullable=False)
    outcome_data = Column(JSONB, nullable=True)
    
    # NOWA ARCHITEKTURA v3.0: SESSION-LEVEL CUMULATIVE PSYCHOLOGY
    cumulative_psychology = Column(JSONB, nullable=True, comment="Ciągły, ewoluujący profil psychologiczny całej sesji")
    psychology_confidence = Column(Integer, default=0, nullable=True, comment="Poziom pewności AI co do profilu (0-100%)")
    active_clarifying_questions = Column(JSONB, nullable=True, comment="Aktywne pytania pomocnicze czekające na odpowiedź sprzedawcy")
    customer_archetype = Column(JSONB, nullable=True, comment="Finalny, zsyntetyzowany archetyp klienta i kluczowe porady")
    psychology_updated_at = Column(DateTime, nullable=True, comment="Ostatnia aktualizacja profilu psychologicznego")
    
    # MODUŁ 4: Zaawansowane Wskaźniki Sprzedażowe
    sales_indicators = Column(JSONB, nullable=True, comment="Predykcyjne wskaźniki sprzedażowe dla sesji: temperatura, etap podróży, ryzyko, potencjał")
    
    # FAZA 1 ULTRA MÓZGU: Pole dla przyszłego Syntezatora
    holistic_psychometric_profile = Column(JSONB, nullable=True, comment="Holistyczny profil psychometryczny z przyszłego Syntezatora - łączy wszystkie aspekty w jeden spójny obraz klienta")

    client = relationship("Client", back_populates="sessions")
    interactions = relationship("Interaction", back_populates="session")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    user_input = Column(Text, nullable=False)
    ai_response_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Zmiana z Planu v2.4 (Moduł 1)
    feedback_data = Column(JSONB, nullable=True, default=lambda: [])
    
    # UWAGA: psychometric_analysis USUNIĘTE - przeniesione na poziom Session jako cumulative_psychology

    session = relationship("Session", back_populates="interactions")

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True, unique=True)
    content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, server_default="1")
    status = Column(SQLAlchemyEnum(PromptStatus), nullable=False, default=PromptStatus.ACTIVE)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<PromptTemplate(name='{self.name}', version={self.version}, status='{self.status.value}')>"

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False)
    suggestion_id = Column(String(36), nullable=True, index=True, comment="ID ocenionej porady (quick_response lub suggested_action)")
    rating = Column(Integer, nullable=False, comment="Ocena: 1 (pozytywna) lub -1 (negatywna)")
    feedback_type = Column(String, nullable=True, comment="Typ feedbacku: quick_response, suggested_action, etc.")
    comment = Column(Text, nullable=True, comment="Opcjonalny komentarz użytkownika")
    is_processed_for_learning = Column(Integer, nullable=False, default=0, index=True, comment="Czy feedback został przetworzony przez system uczenia")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relacje
    interaction = relationship("Interaction", backref="feedbacks")

    def __repr__(self):
        return f"<Feedback(id={self.id}, interaction_id={self.interaction_id}, rating={self.rating})>"
