"""
Nowy główny AIService - Orchestrator wykorzystujący wyspecjalizowane serwisy AI

REFAKTORYZACJA: Zastąpienie 28k tokenów ai_service.py przez orchestrator wykorzystujący:
- PsychologyService: analiza psychometryczna
- SalesStrategyService: strategie sprzedażowe  
- HolisticSynthesisService: DNA Klienta
- AIServiceFactory: dependency injection

Utrzymuje BACKWARD COMPATIBILITY z istniejącym API
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from .ai import (
    get_psychology_service,
    get_sales_strategy_service, 
    get_holistic_synthesis_service,
    initialize_ai_services
)
from .qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class AIService:
    """
    Główny orchestrator serwisów AI - zastępuje stary ai_service.py (28k tokenów)
    
    Utrzymuje backward compatibility z istniejącym API, ale używa
    wyspecjalizowanych serwisów wewnętrznie.
    
    Funkcjonalności:
    - generate_analysis: Główna metoda generowania strategii
    - generate_psychometric_analysis: Analiza psychometryczna
    - _run_holistic_synthesis: Synteza DNA Klienta  
    - _run_sales_indicators_generation: Wskaźniki sprzedażowe
    - _call_llm_with_retry: Komunikacja z LLM
    """
    
    def __init__(self, qdrant_service: QdrantService):
        """
        Inicjalizacja orchestratora AI
        
        Args:
            qdrant_service: Instancja serwisu Qdrant dla RAG
        """
        self.qdrant_service = qdrant_service
        
        # Inicjalizuj wyspecjalizowane serwisy
        initialize_ai_services(qdrant_service)
        
        # Pobierz referencje do serwisów
        self._psychology_service = get_psychology_service()
        self._sales_strategy_service = get_sales_strategy_service()
        self._holistic_service = get_holistic_synthesis_service()
        
        logger.info("✅ AIService orchestrator initialized with specialized services")
    
    # === METODY POMOCNICZE ===
    
    def _analyze_archetype_evolution(
        self,
        session_history: list[dict],
        current_archetype: str | None
    ) -> dict:
        """Analizuje ewolucję archetypu klienta w trakcie sesji."""
        evolution_data = {
            'initial_archetype': None,
            'current_archetype': current_archetype,
            'changes': [],
            'is_stable': True
        }

        archetype_history = [
            interaction.get('customer_archetype', {}).get('archetype_name')
            for interaction in session_history
            if interaction.get('customer_archetype')
        ]

        if not archetype_history:
            return evolution_data

        evolution_data['initial_archetype'] = archetype_history[0]

        previous_archetype = archetype_history[0]
        for i, archetype in enumerate(archetype_history[1:]):
            if archetype != previous_archetype:
                evolution_data['is_stable'] = False
                evolution_data['changes'].append({
                    'from': previous_archetype,
                    'to': archetype,
                    'interaction_index': i + 1 
                })
            previous_archetype = archetype

        return evolution_data
    
    # === GŁÓWNE API METODY (BACKWARD COMPATIBILITY) ===
    
    async def generate_analysis(
        self,
        user_input: str,
        client_profile: Dict[str, Any],
        session_history: List[Dict[str, Any]],
        session_context: Dict[str, Any],
        holistic_profile: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        GŁÓWNA METODA: Generuje kompletną analizę sprzedażową z ewolucją archetypu.
        """
        try:
            logger.info("🚀 [ORCHESTRATOR] Rozpoczynam generate_analysis...")

            # Pobierz aktualny archetyp z kwargs, jeśli istnieje
            current_archetype_data = kwargs.get('customer_archetype', {})
            current_archetype_name = current_archetype_data.get('archetype_name') if current_archetype_data else None

            # 1. Analizuj ewolucję archetypu
            archetype_evolution = self._analyze_archetype_evolution(session_history, current_archetype_name)

            # 2. Użyj SalesStrategyService do wygenerowania strategii
            strategy = await self._sales_strategy_service.generate_sales_strategy(
                user_input=user_input,
                client_profile=client_profile,
                session_history=session_history,
                psychology_profile=kwargs.get('session_psychology'),
                holistic_profile=holistic_profile,
                customer_archetype=current_archetype_data
            )

            # 3. Wzbogać wynik o dane ewolucji
            final_result = strategy
            final_result['archetype_evolution_analysis'] = archetype_evolution

            logger.info("✅ [ORCHESTRATOR] Generate_analysis zakończone sukcesem.")
            return final_result

        except Exception as e:
            logger.error(f"❌ [ORCHESTRATOR] Krytyczny błąd w generate_analysis: {e}", exc_info=True)
            # Zwróć strukturę awaryjną, aby frontend nie uległ awarii
            return {
                "response": "Przepraszam, wystąpił błąd podczas analizy. Skupmy się na kliencie.",
                "suggested_actions": ["Zadaj otwarte pytanie, aby dowiedzieć się więcej o potrzebach klienta."],
                "reasoning": "Błąd systemowy uniemożliwił głęboką analizę.",
                "error": str(e)
            }
    
    async def generate_psychometric_analysis(
        self,
        conversation_history: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        COMPATIBILITY METHOD: Generuje analizę psychometryczną
        
        Args:
            conversation_history: Historia rozmowy
            additional_context: Dodatkowy kontekst
            
        Returns:
            Dict: Profil psychometryczny (Big Five + DISC + Schwartz)
        """
        try:
            logger.info("🧠 [ORCHESTRATOR] Delegating to PsychologyService...")
            
            return await self._psychology_service.generate_psychometric_analysis(
                conversation_history=conversation_history,
                additional_context=additional_context
            )
            
        except Exception as e:
            logger.error(f"❌ [ORCHESTRATOR] Błąd w generate_psychometric_analysis: {e}")
            return self._psychology_service._create_psychology_error_fallback(str(e))
    
    async def _run_holistic_synthesis(
        self,
        raw_psychology_profile: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        COMPATIBILITY METHOD: Tworzy DNA Klienta (holistyczną syntezę)
        
        Args:
            raw_psychology_profile: Surowy profil psychometryczny
            additional_context: Dodatkowy kontekst
            
        Returns:
            Dict: Holistyczny profil (DNA Klienta)
        """
        try:
            logger.info("🧬 [ORCHESTRATOR] Delegating to HolisticSynthesisService...")
            
            return await self._holistic_service.run_holistic_synthesis(
                raw_psychology_profile=raw_psychology_profile,
                additional_context=additional_context
            )
            
        except Exception as e:
            logger.error(f"❌ [ORCHESTRATOR] Błąd w _run_holistic_synthesis: {e}")
            return self._holistic_service._create_holistic_error_fallback(str(e))
    
    async def _run_sales_indicators_generation(
        self,
        holistic_profile: Dict[str, Any],
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        COMPATIBILITY METHOD: Generuje wskaźniki sprzedażowe
        
        Args:
            holistic_profile: DNA Klienta
            session_context: Kontekst sesji
            
        Returns:
            Dict: Wskaźniki sprzedażowe
        """
        try:
            logger.info("📊 [ORCHESTRATOR] Delegating to HolisticSynthesisService for indicators...")
            
            return await self._holistic_service.run_sales_indicators_generation(
                holistic_profile=holistic_profile,
                session_context=session_context
            )
            
        except Exception as e:
            logger.error(f"❌ [ORCHESTRATOR] Błąd w _run_sales_indicators_generation: {e}")
            return self._holistic_service._create_indicators_error_fallback(str(e))
    
    async def _call_llm_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        cache_prefix: str = "general"
    ) -> Dict[str, Any]:
        """
        COMPATIBILITY METHOD: Wywołuje LLM z retry
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            cache_prefix: Prefix cache
            
        Returns:
            Dict: Odpowiedź LLM
        """
        try:
            logger.info("🤖 [ORCHESTRATOR] Delegating to BaseAIService...")
            
            # Użyj któregoś z dostępnych serwisów (wszystkie dziedziczą z BaseAIService)
            return await self._sales_strategy_service._call_llm_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                use_cache=True,
                cache_prefix=cache_prefix
            )
            
        except Exception as e:
            logger.error(f"❌ [ORCHESTRATOR] Błąd w _call_llm_with_retry: {e}")
            return {
                'content': 'Wystąpił błąd podczas komunikacji z AI.',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    # === AI DOJO COMPATIBILITY (dla dojo_service.py) ===
    
    async def _handle_training_conversation(
        self,
        message: str,
        training_mode: str = "knowledge_update",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        COMPATIBILITY METHOD: Obsługa AI Dojo training
        
        UWAGA: To może wymagać dodatkowej implementacji jeśli AI Dojo używa specjalnych funkcji
        """
        try:
            logger.info("🎓 [ORCHESTRATOR] Handling AI Dojo training conversation...")
            
            # Użyj SalesStrategyService z kontekstem treningowym
            training_context = {
                'session_type': 'dojo_training',
                'training_mode': training_mode,
                **(context or {})
            }
            
            return await self._sales_strategy_service.generate_quick_response(
                user_input=message,
                context=training_context
            )
            
        except Exception as e:
            logger.error(f"❌ [ORCHESTRATOR] Błąd w AI Dojo: {e}")
            return {
                'quick_response': {
                    'text': 'Wystąpił błąd w systemie treningowym.',
                    'tone': 'professional'
                },
                'error': str(e)
            }
    
    # === HELPER METHODS ===
    
    def _create_fallback_sales_indicators(self) -> Dict[str, Any]:
        """COMPATIBILITY: Fallback wskaźniki sprzedażowe"""
        return self._holistic_service._create_indicators_fallback()
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Zwraca status wszystkich wyspecjalizowanych serwisów
        
        Returns:
            Dict: Status orchestratora i serwisów
        """
        from .ai import check_ai_services_health
        
        health_status = check_ai_services_health()
        
        return {
            'orchestrator_status': 'active',
            'qdrant_available': self.qdrant_service is not None,
            'specialized_services': health_status,
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_all_caches(self):
        """Czyści cache wszystkich wyspecjalizowanych serwisów"""
        from .ai import AIServiceFactory
        AIServiceFactory.clear_all_caches()
        logger.info("🧹 [ORCHESTRATOR] All caches cleared")


# === GLOBAL INSTANCE (COMPATIBILITY) ===

# Globalna instancja do backward compatibility
ai_service: Optional[AIService] = None


def initialize_ai_service(qdrant_service: QdrantService) -> AIService:
    """
    Inicjalizuje globalną instancję AIService
    
    Args:
        qdrant_service: Instancja QdrantService
        
    Returns:
        AIService: Zainicjalizowany orchestrator
    """
    global ai_service
    
    if ai_service is None:
        ai_service = AIService(qdrant_service)
        logger.info("✅ Global AIService orchestrator initialized")
    
    return ai_service


def get_ai_service() -> Optional[AIService]:
    """
    Zwraca globalną instancję AIService
    
    Returns:
        Optional[AIService]: Instancja orchestratora lub None
    """
    return ai_service


# === COMPATIBILITY FUNCTIONS (dla InteractionRepository i innych) ===

async def generate_sales_analysis(
    user_input: str,
    client_profile: Dict[str, Any],
    session_history: List[Dict[str, Any]],
    session_context: Dict[str, Any],
    session_psychology: Optional[Dict[str, Any]] = None,  # DEPRECATED v4.0
    holistic_profile: Optional[Dict[str, Any]] = None,     # NOWY v4.0: DNA Klienta
    sales_indicators: Optional[Dict[str, Any]] = None,     # NOWY v4.1: PRIORYTET 3
    customer_archetype: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    MAIN COMPATIBILITY FUNCTION: Zastępuje duplikowane funkcje z starego ai_service.py
    
    Używa globalnej instancji AIService orchestratora.
    """
    global ai_service
    
    if ai_service is None:
        logger.error("❌ AIService not initialized! Call initialize_ai_service first.")
        return {
            'error': 'AI Service not initialized',
            'quick_response': 'Wystąpił błąd systemu. Spróbuj ponownie.',
            'is_fallback': True
        }
    
    try:
        # Użyj orchestratora
        response = await ai_service.generate_analysis(
            user_input=user_input,
            client_profile=client_profile,
            session_history=session_history,
            session_context=session_context,
            holistic_profile=holistic_profile,
            session_psychology=session_psychology,  # Legacy
            customer_archetype=customer_archetype
        )
        
        # Dołącz sales_indicators jeśli dostępne (PRIORYTET 3)
        if sales_indicators and not response.get('sales_indicators'):
            response['sales_indicators'] = sales_indicators
            logger.info("📊 [COMPATIBILITY] Sales indicators dołączone do response")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ [COMPATIBILITY] generate_sales_analysis failed: {e}")
        return {
            'error': str(e),
            'quick_response': 'Wystąpił błąd podczas analizy. Kontynuuj rozmowę.',
            'suggested_actions': ['Zbieraj więcej informacji'],
            'is_fallback': True
        }


# Inne compatibility functions można dodać tutaj w razie potrzeby...

async def generate_psychometric_analysis(
    conversation_history: List[Dict[str, Any]],
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """COMPATIBILITY: Analiza psychometryczna"""
    global ai_service
    
    if ai_service is None:
        logger.error("❌ AIService not initialized!")
        return {'error': 'AI Service not initialized', 'is_fallback': True}
    
    return await ai_service.generate_psychometric_analysis(
        conversation_history, additional_context
    )
