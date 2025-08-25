"""
InteractionRepository - Wyczyszczona wersja (tylko operacje DB)

REFAKTORYZACJA: Usunięto 150+ linii logiki AI
- Przeniesiono do InteractionService
- Repository zawiera tylko CRUD operations
- Clean Architecture - separacja warstw

Porównaj z interaction_repository.py (stara wersja)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import Optional, List, Dict, Any
import logging

from app.models.domain import Interaction, Session as SessionModel, Client
from app.schemas.interaction import InteractionCreateNested

logger = logging.getLogger(__name__)


class InteractionRepository:
    """
    CZYSTE REPOZYTORIUM - tylko operacje bazodanowe
    
    Usunięte (przeniesione do InteractionService):
    ❌ Analiza psychometryczna (session_psychology_engine)
    ❌ Holistyczna synteza (_run_holistic_synthesis)
    ❌ Generowanie wskaźników sprzedażowych
    ❌ Parallel processing (asyncio.gather)
    ❌ AI strategy generation (generate_sales_analysis)
    ❌ 150+ linii logiki biznesowej
    
    Zostaje tylko:
    ✅ CRUD operations na Interaction
    ✅ Database queries
    ✅ Data persistence
    """
    
    # === QUERY OPERATIONS ===
    
    async def get_interaction(self, db: AsyncSession, interaction_id: int) -> Optional[Interaction]:
        """
        Pobiera interakcję po ID z eager loading session data
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            
        Returns:
            Optional[Interaction]: Interakcja lub None
        """
        try:
            query = (
                select(Interaction)
                .options(joinedload(Interaction.session))
                .where(Interaction.id == interaction_id)
            )
            result = await db.execute(query)
            interaction = result.scalar_one_or_none()
            
            if interaction:
                logger.debug(f"📄 [REPO] Retrieved interaction {interaction_id}")
            
            return interaction
            
        except Exception as e:
            logger.error(f"❌ [REPO] Error retrieving interaction {interaction_id}: {e}")
            return None
    
    async def get_session_interactions(
        self, 
        db: AsyncSession, 
        session_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Interaction]:
        """
        Pobiera interakcje dla sesji z paginacją
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            skip: Ile interakcji pominąć
            limit: Maksymalna liczba interakcji
            
        Returns:
            List[Interaction]: Lista interakcji
        """
        try:
            query = (
                select(Interaction)
                .where(Interaction.session_id == session_id)
                .order_by(Interaction.timestamp.desc())  # Najnowsze pierwsze
                .offset(skip)
                .limit(limit)
            )
            result = await db.execute(query)
            interactions = list(result.scalars().all())
            
            logger.debug(f"📄 [REPO] Retrieved {len(interactions)} interactions for session {session_id}")
            return interactions
            
        except Exception as e:
            logger.error(f"❌ [REPO] Error retrieving interactions for session {session_id}: {e}")
            return []
    
    async def get_interactions_count(self, db: AsyncSession, session_id: int) -> int:
        """
        Zlicza interakcje w sesji
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            
        Returns:
            int: Liczba interakcji
        """
        try:
            query = select(func.count(Interaction.id)).where(Interaction.session_id == session_id)
            result = await db.execute(query)
            count = result.scalar() or 0
            
            logger.debug(f"📊 [REPO] Session {session_id} has {count} interactions")
            return count
            
        except Exception as e:
            logger.error(f"❌ [REPO] Error counting interactions for session {session_id}: {e}")
            return 0
    
    # === CREATE OPERATIONS ===
    
    async def create_interaction_simple(
        self,
        db: AsyncSession,
        interaction_data: Dict[str, Any]
    ) -> Interaction:
        """
        NOWA METODA: Tworzy interakcję bez logiki AI (czysta operacja DB)
        
        Args:
            db: Sesja bazy danych
            interaction_data: Dane interakcji (już przygotowane przez Service)
            
        Returns:
            Interaction: Utworzona interakcja
            
        Raises:
            ValueError: Jeśli wystąpi błąd podczas tworzenia
        """
        try:
            # Walidacja podstawowych danych
            if not interaction_data.get('session_id'):
                raise ValueError("session_id is required")
            if not interaction_data.get('user_input'):
                raise ValueError("user_input is required")
            
            # Utwórz instancję Interaction
            db_interaction = Interaction(**interaction_data)
            
            # Zapisz do bazy
            db.add(db_interaction)
            await db.flush()  # Flush żeby dostać ID
            await db.refresh(db_interaction)  # Refresh żeby dostać timestamp
            
            logger.info(f"✅ [REPO] Created interaction {db_interaction.id} for session {interaction_data['session_id']}")
            return db_interaction
            
        except Exception as e:
            logger.error(f"❌ [REPO] Error creating interaction: {e}")
            raise ValueError(f"Database error during interaction creation: {e}")
    
    async def create_interaction_legacy(
        self, 
        db: AsyncSession, 
        session_id: int, 
        interaction_data: InteractionCreateNested
    ) -> Interaction:
        """
        LEGACY METHOD: Stara metoda z AI logiką - DEPRECATED
        
        ⚠️ UWAGA: Ta metoda zawiera 150+ linii logiki AI
        ⚠️ UŻYWAJ: InteractionService.create_interaction_with_ai_analysis()
        
        Pozostaje dla compatibility, ale powinna być usunięta po migracji.
        """
        logger.warning("⚠️ [REPO] Using LEGACY create_interaction method - should use InteractionService!")
        
        # Import legacy logic (jeśli potrzebny jako fallback)
        # Można zaimportować starą wersję z backup file jeśli potrzeba
        
        # Dla teraz - prosta implementacja bez AI
        basic_data = {
            "session_id": session_id,
            "user_input": interaction_data.user_input,
            "ai_response_json": {
                "main_analysis": "Legacy mode - brak analizy AI",
                "quick_response": "Rozumiem. Kontynuujmy rozmowę.",
                "is_legacy": True
            },
            "feedback_data": []
        }
        
        return await self.create_interaction_simple(db, basic_data)
    
    # === UPDATE OPERATIONS ===
    
    async def update_interaction(
        self, 
        db: AsyncSession, 
        interaction_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[Interaction]:
        """
        Aktualizuje interakcję
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            update_data: Dane do aktualizacji
            
        Returns:
            Optional[Interaction]: Zaktualizowana interakcja lub None
        """
        try:
            # Pobierz interakcję
            interaction = await self.get_interaction(db, interaction_id)
            if not interaction:
                logger.warning(f"⚠️ [REPO] Interaction {interaction_id} not found for update")
                return None
            
            # Aktualizuj pola
            for key, value in update_data.items():
                if hasattr(interaction, key):
                    setattr(interaction, key, value)
                else:
                    logger.warning(f"⚠️ [REPO] Unknown field '{key}' for Interaction model")
            
            # Zapisz zmiany
            await db.flush()
            await db.refresh(interaction)
            
            logger.info(f"✅ [REPO] Updated interaction {interaction_id}")
            return interaction
            
        except Exception as e:
            logger.error(f"❌ [REPO] Error updating interaction {interaction_id}: {e}")
            return None
    
    async def update_ai_response(
        self,
        db: AsyncSession,
        interaction_id: int,
        ai_response: Dict[str, Any]
    ) -> Optional[Interaction]:
        """
        Aktualizuje tylko AI response w interakcji
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            ai_response: Nowa odpowiedź AI
            
        Returns:
            Optional[Interaction]: Zaktualizowana interakcja
        """
        return await self.update_interaction(
            db, 
            interaction_id, 
            {"ai_response_json": ai_response}
        )
    
    # === DELETE OPERATIONS ===
    
    async def delete_interaction(self, db: AsyncSession, interaction_id: int) -> bool:
        """
        Usuwa interakcję
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            
        Returns:
            bool: True jeśli usunięto, False jeśli nie znaleziono
        """
        try:
            # Pobierz interakcję
            interaction = await self.get_interaction(db, interaction_id)
            if not interaction:
                logger.warning(f"⚠️ [REPO] Interaction {interaction_id} not found for deletion")
                return False
            
            # Usuń z bazy
            await db.delete(interaction)
            await db.flush()
            
            logger.info(f"✅ [REPO] Deleted interaction {interaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ [REPO] Error deleting interaction {interaction_id}: {e}")
            return False
    
    # === HELPER METHODS ===
    
    async def interaction_exists(self, db: AsyncSession, interaction_id: int) -> bool:
        """
        Sprawdza czy interakcja istnieje
        
        Args:
            db: Sesja bazy danych
            interaction_id: ID interakcji
            
        Returns:
            bool: True jeśli istnieje
        """
        try:
            query = select(Interaction.id).where(Interaction.id == interaction_id)
            result = await db.execute(query)
            exists = result.scalar_one_or_none() is not None
            
            logger.debug(f"📄 [REPO] Interaction {interaction_id} exists: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"❌ [REPO] Error checking interaction {interaction_id} existence: {e}")
            return False
    
    async def get_latest_interaction(self, db: AsyncSession, session_id: int) -> Optional[Interaction]:
        """
        Pobiera najnowszą interakcję w sesji
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            
        Returns:
            Optional[Interaction]: Najnowsza interakcja lub None
        """
        try:
            query = (
                select(Interaction)
                .where(Interaction.session_id == session_id)
                .order_by(Interaction.timestamp.desc())
                .limit(1)
            )
            result = await db.execute(query)
            interaction = result.scalar_one_or_none()
            
            if interaction:
                logger.debug(f"📄 [REPO] Latest interaction for session {session_id}: {interaction.id}")
            
            return interaction
            
        except Exception as e:
            logger.error(f"❌ [REPO] Error getting latest interaction for session {session_id}: {e}")
            return None
    
    # === STATISTICS & ANALYTICS ===
    
    async def get_interaction_stats(self, db: AsyncSession, session_id: int) -> Dict[str, Any]:
        """
        Pobiera statystyki interakcji dla sesji
        
        Args:
            db: Sesja bazy danych
            session_id: ID sesji
            
        Returns:
            Dict: Statystyki interakcji
        """
        try:
            # Podstawowe statystyki
            total_count = await self.get_interactions_count(db, session_id)
            latest_interaction = await self.get_latest_interaction(db, session_id)
            
            # Dodatkowe metryki (można rozbudować)
            stats = {
                'total_interactions': total_count,
                'latest_interaction_id': latest_interaction.id if latest_interaction else None,
                'latest_timestamp': latest_interaction.timestamp.isoformat() if latest_interaction else None,
                'session_id': session_id
            }
            
            logger.debug(f"📊 [REPO] Interaction stats for session {session_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ [REPO] Error getting interaction stats for session {session_id}: {e}")
            return {
                'error': str(e),
                'session_id': session_id,
                'total_interactions': 0
            }
