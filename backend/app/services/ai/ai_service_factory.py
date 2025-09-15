"""AIServiceFactory - Factory Pattern dla serwisów AI
Odpowiedzialny za: dependency injection, inicjalizację, zarządzanie zależnościami
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .base_ai_service import BaseAIService
from .psychology_service import PsychologyService
from .sales_strategy_service import SalesStrategyService
from .holistic_synthesis_service import HolisticSynthesisService
from ..qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class AIServiceFactory:
    """
    Factory do tworzenia serwisów AI z dependency injection.
    
    Każdy serwis wymaga AsyncSession, więc nie używamy singletonów.
    """
    
    _qdrant_service = None
    
    @classmethod
    def set_qdrant_service(cls, qdrant_service: QdrantService):
        """Ustawia instancję QdrantService dla factory"""
        cls._qdrant_service = qdrant_service
        logger.info("✅ QdrantService zarejestrowany w AIServiceFactory")
    
    @classmethod
    def get_base_ai_service(cls, session: AsyncSession) -> BaseAIService:
        """
        Tworzy nową instancję BaseAIService
        
        Args:
            session: AsyncSession dla bazy danych
            
        Returns:
            BaseAIService: Bazowy serwis AI
        """
        return BaseAIService(session)
    
    @classmethod
    def get_psychology_service(cls, session: AsyncSession) -> PsychologyService:
        """
        Tworzy nową instancję PsychologyService
        
        Args:
            session: AsyncSession dla bazy danych
            
        Returns:
            PsychologyService: Serwis analizy psychometrycznej
        """
        return PsychologyService(session)
    
    @classmethod
    def get_sales_strategy_service(cls, session: AsyncSession) -> SalesStrategyService:
        """
        Tworzy nową instancję SalesStrategyService
        
        Args:
            session: AsyncSession dla bazy danych
            
        Returns:
            SalesStrategyService: Serwis strategii sprzedażowych
        """
        return SalesStrategyService(
            session=session,
            qdrant_service=cls._qdrant_service
        )
    
    @classmethod
    def get_holistic_synthesis_service(cls, session: AsyncSession) -> HolisticSynthesisService:
        """
        Tworzy nową instancję HolisticSynthesisService
        
        Args:
            session: AsyncSession dla bazy danych
            
        Returns:
            HolisticSynthesisService: Serwis syntezy holistycznej
        """
        return HolisticSynthesisService(session)
    
    @classmethod
    def get_all_services(cls) -> dict:
        """
        Zwraca wszystkie dostępne serwisy AI
        
        Returns:
            dict: Słownik z wszystkimi serwisami
        """
        return {
            'base': cls.get_base_ai_service(),
            'psychology': cls.get_psychology_service(),
            'sales_strategy': cls.get_sales_strategy_service(),
            'holistic_synthesis': cls.get_holistic_synthesis_service()
        }
    
    @classmethod
    def get_service_status(cls) -> dict:
        """
        Zwraca status wszystkich serwisów
        
        Returns:
            dict: Status każdego serwisu
        """
        status = {}
        
        try:
            base_service = cls.get_base_ai_service()
            status['base_ai_service'] = {
                'status': 'active',
                'model': base_service.model_name,
                'cache_stats': base_service.get_cache_stats()
            }
        except Exception as e:
            status['base_ai_service'] = {'status': 'error', 'error': str(e)}
        
        try:
            psychology_service = cls.get_psychology_service()
            status['psychology_service'] = {
                'status': 'active',
                'model': psychology_service.model_name,
                'cache_stats': psychology_service.get_cache_stats()
            }
        except Exception as e:
            status['psychology_service'] = {'status': 'error', 'error': str(e)}
        
        try:
            sales_strategy_service = cls.get_sales_strategy_service()
            status['sales_strategy_service'] = {
                'status': 'active',
                'model': sales_strategy_service.model_name,
                'qdrant_available': sales_strategy_service.qdrant_service is not None,
                'cache_stats': sales_strategy_service.get_cache_stats()
            }
        except Exception as e:
            status['sales_strategy_service'] = {'status': 'error', 'error': str(e)}
        
        try:
            holistic_service = cls.get_holistic_synthesis_service()
            status['holistic_synthesis_service'] = {
                'status': 'active',
                'model': holistic_service.model_name,
                'cache_stats': holistic_service.get_cache_stats()
            }
        except Exception as e:
            status['holistic_synthesis_service'] = {'status': 'error', 'error': str(e)}
        
        return status
    
    @classmethod
    def clear_all_caches(cls):
        """Czyści cache wszystkich serwisów"""
        cleared_count = 0
        
        for service_name, service in cls._instances.items():
            try:
                service.clear_cache()
                cleared_count += 1
                logger.info(f"🧹 Cache cleared for {service_name}")
            except Exception as e:
                logger.error(f"❌ Failed to clear cache for {service_name}: {e}")
        
        logger.info(f"✅ Cache cleared for {cleared_count} services")
    
    @classmethod
    def shutdown(cls):
        """Zamyka wszystkie serwisy i czyści instancje"""
        logger.info("🔄 Shutting down AIServiceFactory...")
        
        # Wyczyść cache
        cls.clear_all_caches()
        
        # Wyczyść instancje
        cls._instances.clear()
        cls._qdrant_service = None
        
        # Wyczyść LRU cache
        cls.get_base_ai_service.cache_clear()
        cls.get_psychology_service.cache_clear()
        cls.get_sales_strategy_service.cache_clear()
        cls.get_holistic_synthesis_service.cache_clear()
        
        logger.info("✅ AIServiceFactory shutdown complete")


# Funkcje pomocnicze dla łatwego użytkowania w kodzie

def get_psychology_service(session: AsyncSession) -> PsychologyService:
    """Shortcut do pobrania PsychologyService"""
    return AIServiceFactory.get_psychology_service(session)


def get_sales_strategy_service(session: AsyncSession) -> SalesStrategyService:
    """Shortcut do pobrania SalesStrategyService"""
    return AIServiceFactory.get_sales_strategy_service(session)


def get_holistic_synthesis_service(session: AsyncSession) -> HolisticSynthesisService:
    """Shortcut do pobrania HolisticSynthesisService"""
    return AIServiceFactory.get_holistic_synthesis_service(session)


# Dependency injection helper
def initialize_ai_services(qdrant_service: Optional[QdrantService] = None):
    """
    Inicjalizuje wszystkie serwisy AI
    
    Args:
        qdrant_service: Instancja QdrantService (opcjonalna)
    """
    logger.info("🚀 Initializing AI Services...")
    
    # Zarejestruj QdrantService jeśli dostępny
    if qdrant_service:
        AIServiceFactory.set_qdrant_service(qdrant_service)
    
    # Inicjalizuj wszystkie serwisy (lazy loading przez factory)
    services = AIServiceFactory.get_all_services()
    
    logger.info(f"✅ AI Services initialized: {list(services.keys())}")
    return services


# Health check function
def check_ai_services_health() -> dict:
    """
    Sprawdza stan zdrowia wszystkich serwisów AI
    
    Returns:
        dict: Status healthcheck
    """
    try:
        service_status = AIServiceFactory.get_service_status()
        
        # Sprawdź czy wszystkie serwisy są aktywne
        all_active = all(
            status.get('status') == 'active' 
            for status in service_status.values()
        )
        
        return {
            'overall_status': 'healthy' if all_active else 'degraded',
            'services': service_status,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            'overall_status': 'unhealthy',
            'error': str(e),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
