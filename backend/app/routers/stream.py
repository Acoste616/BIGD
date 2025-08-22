# Plik: backend/app/routers/stream.py
# Autor: ULTBIGD
# Opis: Router obsługujący wszystkie endpointy streamingowe (Server-Sent Events) dla AI.

import logging
import asyncio
import json
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.ai_service import AIService, generate_sales_analysis
from app.repositories.session_repository import SessionRepository
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.stream import SessionStreamRequest

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pomocnicza funkcja do ekstrakcji profilu klienta
def extract_client_profile(client) -> dict:
    """Wyciągnij profil klienta do przekazania do AI"""
    if not client:
        return {
            "alias": "Nieznany klient",
            "archetype": "Niezdecydowany Odkrywca",
            "tags": [],
            "notes": None
        }
    
    return {
        "alias": client.alias,
        "archetype": client.archetype or "Niezdecydowany Odkrywca",
        "tags": client.tags or [],
        "notes": client.notes,
        "created_at": client.created_at.isoformat() if client.created_at else None,
        "updated_at": client.updated_at.isoformat() if client.updated_at else None
    }

# Funkcja do streamingu odpowiedzi AI
async def stream_sales_analysis(user_input: str, client_profile: dict, session_history: list, session_context: dict):
    """Generator do streamingu odpowiedzi AI token po token"""
    try:
        logger.info("--- 🔍 DEBUG: ROZPOCZĘCIE STREAMING ANALYSIS ---")
        logger.info(f"🔍 DEBUG: user_input = {user_input}")
        logger.info(f"🔍 DEBUG: client_profile = {client_profile}")
        
        # Krok 1: Pobierz pełną analizę z AI
        logger.info("🔍 DEBUG: Wywołuję generate_sales_analysis...")
        analysis_result = await generate_sales_analysis(
            user_input=user_input,
            client_profile=client_profile,
            session_history=session_history,
            session_context=session_context
        )
        logger.info(f"🔍 DEBUG: Otrzymano analysis_result: {analysis_result}")
        
        # Krok 2: Wyodrębnij quick_response do streamingu
        quick_response = analysis_result.get("quick_response", "Przepraszam, nie mogę wygenerować odpowiedzi.")
        logger.info(f"🔍 DEBUG: Ekstraktowana quick_response: {quick_response}")
        
        # Krok 3: SYMULACJA STREAMINGU - dziel na słowa i wyślij token po token
        words = quick_response.split()
        logger.info(f"🔍 DEBUG: Podzielono na {len(words)} słów")
        
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            logger.info(f"🔍 DEBUG: Wysyłam token {i+1}/{len(words)}: '{token}'")
            
            # Wyślij token jako event
            yield f"data: {{\"event\": \"token\", \"data\": \"{token}\"}}\n\n"
            
            # Małe opóźnienie dla realizmu
            await asyncio.sleep(0.1)
        
        # Krok 4: Wyślij finalne dane z pełną analizą
        logger.info("🔍 DEBUG: Wysyłam stream_end event z pełną analizą...")
        yield f"data: {{\"event\": \"stream_end\", \"data\": {json.dumps(analysis_result)}}}\n\n"
        
        logger.info("--- 🔍 DEBUG: ZAKOŃCZENIE STREAMING ANALYSIS ---")
        
    except Exception as e:
        logger.error(f"🔍 DEBUG: BŁĄD w stream_sales_analysis: {e}", exc_info=True)
        yield f"data: {{\"event\": \"error\", \"data\": \"{str(e)}\"}}\n\n"


@router.post(
    "/sessions/{session_id}/interactions/stream",
    summary="Stream AI analysis for a session",
    description="Provides real-time, token-by-token AI analysis for a given session using Server-Sent Events.",
)
async def stream_session_interaction(
    session_id: int,
    request_data: SessionStreamRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    session_repo: SessionRepository = Depends(SessionRepository),
):
    """
    Główny endpoint do streamingu odpowiedzi AI w kokpicie sesji.
    """
    print("🔥🔥🔥 ENDPOINT STREAMING ZOSTAŁ WYWOŁANY! 🔥🔥🔥")
    logger.info(f"🔥🔥🔥 ENDPOINT STREAMING: session_id={session_id}, user_input={request_data.user_input}")
    try:
        session = await session_repo.get_session(db, session_id, include_client=True)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Przygotowanie kontekstu dla AI
        client_profile = extract_client_profile(session.client)
        
        # Pobranie historii interakcji (opcjonalne, ale zgodne z planem)
        # Dla uproszczenia, na razie przekazujemy tylko profil
        session_history = [] 

        # Wykorzystaj history z requestu lub pobierz z bazy jako fallback
        session_history = request_data.session_history or []
        
        analysis_generator = stream_sales_analysis(
            user_input=request_data.user_input,
            client_profile=client_profile,
            session_history=session_history,
            session_context={"session_type": session.session_type}
        )
        
        return StreamingResponse(analysis_generator, media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Error streaming session interaction for session {session_id}: {e}")
        async def error_generator():
            yield f"data: {{\"event\": \"error\", \"data\": \"{str(e)}\"}}\n\n"
        return StreamingResponse(error_generator(), media_type="text/event-stream", status_code=500)


@router.post(
    "/dojo/chat/stream",
    summary="Stream AI response for AI Dojo",
    description="Provides a real-time, token-by-token chat response from the AI in the Dojo training interface.",
)
async def stream_dojo_chat(
    request_data: DojoMessageCreate,
    request: Request,
):
    """
    Endpoint obsługujący interaktywny trening AI w module 'AI Dojo'.
    """
    try:
        # W Dojo nie mamy kontekstu klienta, używamy domyślnego profilu "eksperta"
        # aby AI wiedziało, że rozmawia z administratorem/trenerem
        client_profile = {"archetype": "Ekspert Sprzedaży"}
        session_history = []  # W DojoMessageCreate nie ma session_history

        analysis_generator = stream_sales_analysis(
            user_input=request_data.content,
            client_profile=client_profile,
            session_history=session_history,
            session_context={"session_type": "dojo_training"}
        )
        
        return StreamingResponse(analysis_generator, media_type="text/event-stream")
        
    except Exception as e:
        logger.error(f"Error streaming dojo chat: {e}")
        async def error_generator():
            yield f"data: {{\"event\": \"error\", \"data\": \"{str(e)}\"}}\n\n"
        return StreamingResponse(error_generator(), media_type="text/event-stream", status_code=500)
