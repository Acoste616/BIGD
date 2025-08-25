"""
AI Services Module - Refaktoryzowane serwisy AI dla Tesla Co-Pilot

Ten moduł zawiera wyspecjalizowane serwisy AI po refaktoryzacji:
- BaseAIService: Podstawowa komunikacja z Ollama
- PsychologyService: Analiza psychometryczna (Big Five, DISC, Schwartz)
- SalesStrategyService: Generowanie strategii sprzedażowych
- HolisticSynthesisService: Synteza DNA Klienta i wskaźniki sprzedażowe
- AIServiceFactory: Dependency injection i zarządzanie serwisami

Migracja z ai_service.py (28k tokenów) -> Wyspecjalizowane klasy
"""

from .base_ai_service import BaseAIService
from .psychology_service import PsychologyService
from .sales_strategy_service import SalesStrategyService
from .holistic_synthesis_service import HolisticSynthesisService
from .ai_service_factory import (
    AIServiceFactory,
    get_psychology_service,
    get_sales_strategy_service,
    get_holistic_synthesis_service,
    initialize_ai_services,
    check_ai_services_health
)

# Wersja modułu
__version__ = "1.0.0"

# Publiczne API
__all__ = [
    # Klasy serwisów
    "BaseAIService",
    "PsychologyService", 
    "SalesStrategyService",
    "HolisticSynthesisService",
    
    # Factory i helpers
    "AIServiceFactory",
    "get_psychology_service",
    "get_sales_strategy_service",
    "get_holistic_synthesis_service",
    "initialize_ai_services",
    "check_ai_services_health",
]

# Metadata
__author__ = "Tesla Co-Pilot AI Team"
__description__ = "Refactored AI services for Tesla sales assistant"
