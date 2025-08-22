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

    session = relationship("Session", back_populates="interactions")
