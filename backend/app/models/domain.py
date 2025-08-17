"""
Modele domenowe aplikacji - definicje tabel SQLAlchemy
Zgodnie z "Finalnym Planem Projektowym" - schemat bazy danych
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, List
from datetime import datetime


class Client(Base):
    """
    Model klienta - przechowuje podstawowe informacje o kliencie
    """
    __tablename__ = "clients"
    
    # Kolumny podstawowe
    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String(50), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Pola profilujące (bez danych osobowych)
    notes = Column(Text, nullable=True)  # Notatki analityczne o kliencie
    archetype = Column(String(100), nullable=True)  # Archetyp klienta z RAG
    tags = Column(JSON, nullable=True)  # Tagi/etykiety profilujące
    
    # Relacje
    sessions = relationship("Session", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client(id={self.id}, alias='{self.alias}')>"


class Session(Base):
    """
    Model sesji rozmowy - reprezentuje pojedynczą sesję/rozmowę z klientem
    """
    __tablename__ = "sessions"
    
    # Kolumny podstawowe
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)  # NULL = sesja w trakcie
    summary = Column(Text, nullable=True)  # Podsumowanie sesji generowane przez AI
    key_facts = Column(JSON, nullable=True)  # Kluczowe fakty wyekstrahowane z rozmowy
    
    # Dodatkowe pola
    session_type = Column(String(50), nullable=True)  # np. "initial", "follow-up", "negotiation"
    outcome = Column(String(100), nullable=True)  # np. "interested", "needs_time", "closed_deal"
    sentiment_score = Column(Integer, nullable=True)  # Ogólny sentyment sesji (1-10)
    potential_score = Column(Integer, nullable=True)  # Ocena potencjału sprzedażowego (1-10)
    risk_indicators = Column(JSON, nullable=True)  # Wskaźniki ryzyka (fundrive, etc.)
    
    # Relacje
    client = relationship("Client", back_populates="sessions")
    interactions = relationship("Interaction", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session(id={self.id}, client_id={self.client_id}, start={self.start_time})>"


class Interaction(Base):
    """
    Model interakcji - pojedyncza wymiana między użytkownikiem a AI w ramach sesji
    """
    __tablename__ = "interactions"
    
    # Kolumny podstawowe
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_input = Column(Text, nullable=False)  # To, co użytkownik wpisał/powiedział
    ai_response_json = Column(JSON, nullable=False)  # Pełna odpowiedź AI jako JSON
    
    # Dodatkowe pola dla analizy
    interaction_type = Column(String(50), nullable=True)  # np. "observation", "question", "objection"
    confidence_score = Column(Integer, nullable=True)  # Pewność AI co do odpowiedzi (0-100)
    tokens_used = Column(Integer, nullable=True)  # Liczba tokenów zużytych
    processing_time_ms = Column(Integer, nullable=True)  # Czas przetwarzania w ms
    
    # Pola dla strukturyzowanych danych z odpowiedzi AI
    suggested_actions = Column(JSON, nullable=True)  # Lista sugerowanych akcji
    identified_signals = Column(JSON, nullable=True)  # Zidentyfikowane sygnały kupna/ryzyka
    archetype_match = Column(String(100), nullable=True)  # Dopasowany archetyp
    
    # Relacje
    session = relationship("Session", back_populates="interactions")
    feedbacks = relationship("Feedback", back_populates="interaction", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Interaction(id={self.id}, session_id={self.session_id}, timestamp={self.timestamp})>"


class Feedback(Base):
    """
    Model feedback - ocena użytkownika dotycząca sugestii AI
    """
    __tablename__ = "feedbacks"
    
    # Kolumny podstawowe
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 dla "thumbs up", -1 dla "thumbs down"
    
    # Dodatkowe pola
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    feedback_type = Column(String(50), nullable=True)  # np. "accuracy", "relevance", "usefulness"
    comment = Column(Text, nullable=True)  # Opcjonalny komentarz użytkownika
    applied = Column(Integer, nullable=True)  # Czy sugestia została zastosowana (1=tak, 0=nie)
    
    # Relacje
    interaction = relationship("Interaction", back_populates="feedbacks")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, interaction_id={self.interaction_id}, rating={self.rating})>"



