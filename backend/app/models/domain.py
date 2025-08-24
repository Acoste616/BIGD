import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, index=True, nullable=True)
    notes = Column(Text, nullable=True)
    archetype = Column(String, nullable=True)
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
