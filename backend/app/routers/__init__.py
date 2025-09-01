"""
Moduł routerów - endpointy API
"""

# Import wszystkich routerów dla rejestracji w main.py
from .clients import router as clients_router
from .sessions import router as sessions_router
from .interactions import router as interactions_router
from .feedback import router as feedback_router
from .knowledge import router as knowledge_router
from .dojo import router as dojo_router

# Dla kompatybilności wstecznej - bezpośrednie importy
from . import clients, sessions, interactions, feedback, knowledge, dojo