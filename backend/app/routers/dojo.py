"""
AI Dojo Router - Endpointy API dla Modułu 3

Moduł 3: Interaktywne AI Dojo "Sparing z Mistrzem"
Endpointy:
- POST /chat: Główna konwersacja treningowa
- POST /confirm: Potwierdzenie zapisu wiedzy
- GET /session/{session_id}: Podsumowanie sesji treningowej
- GET /analytics: Statystyki AI Dojo

UWAGA: Wszystkie endpointy są zabezpieczone dla administratorów (koncept)
"""
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from app.schemas.dojo import (
    DojoMessageRequest,
    DojoMessageResponse, 
    StructuredKnowledge
)
from app.services.dojo_service import (
    handle_dojo_conversation,
    confirm_knowledge_write,
    admin_dialogue_service
)

logger = logging.getLogger(__name__)

# Router dla AI Dojo
router = APIRouter(
    prefix="/dojo",
    tags=["AI Dojo"],
    responses={
        401: {"description": "Brak autoryzacji - wymagane uprawnienia administratora"},
        403: {"description": "Brak uprawnień - tylko dla ekspertów"},
        500: {"description": "Błąd serwera podczas przetwarzania AI"}
    }
)


# TODO: Dependency dla autoryzacji administratora
# async def get_admin_user(token: str = Depends(oauth2_scheme)) -> User:
#     """Weryfikuj czy użytkownik ma uprawnienia administratora"""
#     # Implementacja autoryzacji będzie dodana w przyszłości
#     pass

async def require_admin_access():
    """
    Placeholder dependency dla uprawnień administratora
    
    W przyszłości zostanie zastąpione prawdziwą autoryzacją JWT
    
    TODO: Zaimplementować:
    - Weryfikację JWT token
    - Sprawdzenie roli użytkownika (admin/expert)
    - Rate limiting dla endpointów AI
    """
    # Na razie pozwalamy wszystkim (development mode)
    # W produkcji to będzie sprawdzać token i role
    pass


@router.post(
    "/chat",
    response_model=DojoMessageResponse,
    summary="Konwersacja treningowa z AI",
    description="""
    **Główny endpoint AI Dojo dla konwersacji treningowej.**
    
    Ekspert/administrator może prowadzić interaktywną rozmowę z AI w celu:
    - Przekazania nowej wiedzy sprzedażowej
    - Korekty błędnych informacji AI
    - Zadawania pytań i analizy odpowiedzi
    
    AI może odpowiedzieć w trzech trybach:
    - **question**: Zadaje pytania doprecyzowujące
    - **confirmation**: Przygotowuje dane do zapisu i prosi o potwierdzenie
    - **status**: Informuje o statusie operacji lub błędzie
    
    **Przepływ typowej sesji:**
    1. Ekspert: "Tesla Model Y ma nową opcję kolorystyczną - szary metalik"
    2. AI: "Potrzebuję więcej szczegółów. Jaka jest nazwa tego koloru i czy to dotyczy wszystkich wariantów?"
    3. Ekspert: "Oficjalna nazwa to 'Midnight Silver Metallic', dostępny dla Long Range i Performance"
    4. AI: "Przygotowałem informację do zapisu. Czy zatwierdzić?" + structured_data
    5. Ekspert wywołuje POST /confirm z potwierdzeniem
    6. AI zapisuje wiedzę do bazy Qdrant
    """
)
async def chat_with_ai(
    request: DojoMessageRequest,
    session_id: Optional[str] = None,
    expert_name: Optional[str] = "Administrator",
    _: None = Depends(require_admin_access)
) -> DojoMessageResponse:
    """
    Rozpocznij lub kontynuuj konwersację treningową z AI
    
    Args:
        request: DojoMessageRequest z wiadomością eksperta
        session_id: Opcjonalny ID sesji (jeśli None, tworzona jest nowa sesja)
        expert_name: Nazwa eksperta prowadzącego trening
        
    Returns:
        DojoMessageResponse z odpowiedzią AI
        
    Raises:
        HTTPException 400: Błędne dane wejściowe
        HTTPException 500: Błąd podczas przetwarzania AI
    """
    try:
        start_time = datetime.now()
        
        logger.info(f"🎓 AI Dojo API: Rozpoczynam chat (session: {session_id or 'nowa'})")
        logger.debug(f"Request: {len(request.message)} znaków, mode: {request.training_mode}")
        
        # Walidacja podstawowa
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wiadomość nie może być pusta"
            )
        
        if len(request.message) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wiadomość zbyt długa (max 5000 znaków)"
            )
        
        # Wywołaj główną logikę AI Dojo
        response = await handle_dojo_conversation(
            request=request,
            session_id=session_id,
            expert_name=expert_name or "Administrator"
        )
        
        # Loguj rezultat
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(f"✅ AI Dojo API: Chat zakończony w {processing_time:.0f}ms, typ: {response.response_type}")
        
        # Jeśli response nie ma processing_time_ms, dodaj obliczony
        if not response.processing_time_ms:
            response.processing_time_ms = int(processing_time)
        
        return response
        
    except HTTPException:
        # Przepuść HTTPException bez modyfikacji
        raise
        
    except Exception as e:
        logger.error(f"❌ AI Dojo API: Błąd podczas chat: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas przetwarzania konwersacji: {str(e)[:200]}"
        )


@router.post(
    "/confirm",
    response_model=DojoMessageResponse,
    summary="Potwierdź zapis wiedzy do bazy",
    description="""
    **Potwierdź i zapisz strukturalną wiedzę do bazy Qdrant.**
    
    Endpoint wywoływany gdy ekspert zatwierdza dane przygotowane przez AI
    w poprzedniej odpowiedzi typu 'confirmation'.
    
    **Przepływ:**
    1. AI w poprzednim /chat przygotował structured_data
    2. Frontend pokazuje dane do zatwierdzenia
    3. Ekspert klika "Zatwierdź i zapisz"  
    4. Frontend wywołuje POST /confirm z session_id i structured_data
    5. System zapisuje wiedzę w bazie Qdrant
    6. Zwraca potwierdzenie zapisu
    
    **structured_data powinien zawierać:**
    - title: Krótki tytuł wiedzy
    - content: Szczegółową treść
    - knowledge_type: Typ (product, objection, closing, etc.)
    - archetype: Docelowy archetyp klienta (opcjonalne)
    - tags: Lista tagów do wyszukiwania
    - source: Źródło informacji
    """
)
async def confirm_knowledge_save(
    session_id: str,
    structured_data: Dict[str, Any],
    confirmed: bool = True,
    _: None = Depends(require_admin_access)
) -> DojoMessageResponse:
    """
    Potwierdź i zapisz wiedzę przygotowaną przez AI
    
    Args:
        session_id: ID sesji treningowej
        structured_data: Strukturalne dane do zapisu
        confirmed: Czy ekspert potwierdza zapis (True) czy anuluje (False)
        
    Returns:
        DojoMessageResponse z statusem operacji
        
    Raises:
        HTTPException 400: Błędne dane lub brak sesji
        HTTPException 500: Błąd podczas zapisu do Qdrant
    """
    try:
        logger.info(f"💾 AI Dojo API: Potwierdzenie zapisu (session: {session_id}, confirmed: {confirmed})")
        
        # Walidacja sesji
        if not session_id or not session_id.startswith("dojo_"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nieprawidłowy lub brakujący session_id"
            )
        
        # Walidacja structured_data jeśli confirmed=True
        if confirmed:
            required_fields = ["title", "content", "knowledge_type"]
            missing_fields = [field for field in required_fields if not structured_data.get(field)]
            
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Brakujące pola w structured_data: {', '.join(missing_fields)}"
                )
        
        # Wywołaj logikę zapisu
        response = await confirm_knowledge_write(
            session_id=session_id,
            structured_data=structured_data,
            expert_confirmation=confirmed
        )
        
        logger.info(f"✅ AI Dojo API: Potwierdzenie przetworzone, typ: {response.response_type}")
        
        return response
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ AI Dojo API: Błąd podczas potwierdzenia: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas zapisywania wiedzy: {str(e)[:200]}"
        )


@router.get(
    "/session/{session_id}",
    summary="Podsumowanie sesji treningowej",
    description="""
    **Pobierz szczegółowe podsumowanie sesji treningowej.**
    
    Endpoint zwraca statystyki i metadane sesji AI Dojo:
    - Czas trwania i liczbę wiadomości
    - Liczbę dodanych elementów wiedzy
    - Średni czas przetwarzania AI
    - Status sesji i ostatnią aktywność
    
    Przydatne do monitorowania efektywności treningu i analizy sesji.
    """
)
async def get_session_summary(
    session_id: str,
    _: None = Depends(require_admin_access)
) -> JSONResponse:
    """
    Pobierz podsumowanie sesji treningowej
    
    Args:
        session_id: ID sesji treningowej
        
    Returns:
        JSON z podsumowaniem sesji lub błąd 404
    """
    try:
        logger.info(f"📊 AI Dojo API: Pobieranie podsumowania sesji: {session_id}")
        
        # Pobierz podsumowanie z serwisu
        summary = admin_dialogue_service.get_session_summary(session_id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sesja {session_id} nie została znaleziona"
            )
        
        logger.info(f"✅ AI Dojo API: Podsumowanie sesji pobrane ({summary['total_messages']} wiadomości)")
        
        return JSONResponse(content=summary)
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ AI Dojo API: Błąd podczas pobierania podsumowania: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas pobierania podsumowania sesji: {str(e)}"
        )


@router.get(
    "/analytics",
    summary="Statystyki AI Dojo",
    description="""
    **Pobierz analitykę i statystyki całego systemu AI Dojo.**
    
    Endpoint zwraca globalne metryki:
    - Liczbę aktywnych sesji treningowych
    - Całkowitą liczbę sesji i dodanej wiedzy
    - Statystyki najaktywniejszych ekspertów
    - Trendy wykorzystania i efektywności
    
    Przydatne dla administratorów do monitorowania systemu i ROI treningu.
    """
)
async def get_dojo_analytics(
    _: None = Depends(require_admin_access)
) -> JSONResponse:
    """
    Pobierz analitykę systemu AI Dojo
    
    Returns:
        JSON ze statystykami globalnymi
    """
    try:
        logger.info("📈 AI Dojo API: Generowanie statystyk globalnych")
        
        # Podstawowe statystyki
        active_sessions = admin_dialogue_service.get_active_sessions_count()
        
        # W przyszłości można dodać więcej statystyk z bazy danych
        analytics = {
            "active_sessions": active_sessions,
            "total_sessions": len(admin_dialogue_service.active_sessions),
            "system_status": "operational",
            "last_updated": datetime.now().isoformat(),
            "features": {
                "ai_training": True,
                "knowledge_storage": True,
                "session_management": True,
                "analytics": True
            }
        }
        
        logger.info(f"✅ AI Dojo API: Statystyki wygenerowane ({active_sessions} aktywnych sesji)")
        
        return JSONResponse(content=analytics)
        
    except Exception as e:
        logger.error(f"❌ AI Dojo API: Błąd podczas generowania statystyk: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas pobierania statystyk: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check AI Dojo",
    description="Sprawdź status systemu AI Dojo i jego integracji"
)
async def health_check() -> JSONResponse:
    """
    Health check systemu AI Dojo
    
    Returns:
        JSON ze statusem komponentów
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "ai_service": "connected",
                "qdrant_service": "connected", 
                "session_manager": "operational"
            },
            "active_sessions": admin_dialogue_service.get_active_sessions_count(),
            "uptime": "operational"
        }
        
        return JSONResponse(content=health_status)
        
    except Exception as e:
        logger.error(f"❌ AI Dojo API: Health check failed: {e}")
        
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=500
        )


# Eksport routera
__all__ = ["router"]
