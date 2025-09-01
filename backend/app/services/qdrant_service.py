"""
Serwis zarządzania bazą wektorową Qdrant
Obsługuje tworzenie, pobieranie i usuwanie wskazówek sprzedażowych
"""
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer

from ..core.config import settings

logger = logging.getLogger(__name__)


class QdrantService:
    """
    Serwis do zarządzania bazą wektorową Qdrant
    Odpowiada za przechowywanie i wyszukiwanie wskazówek sprzedażowych
    """
    
    def __init__(self):
        """Inicjalizacja połączenia z Qdrant i modelu embeddings"""
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            check_compatibility=False,  # Wyłącz sprawdzenie kompatybilności wersji
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        
        # Model do tworzenia embeddings
        self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Inicjalizacja kolekcji
        self._initialize_collection()
    
    def _initialize_collection(self) -> None:
        """
        Tworzy kolekcję w Qdrant jeśli nie istnieje
        """
        try:
            # Sprawdź czy kolekcja istnieje
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Tworzę nową kolekcję: {self.collection_name}")
                
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # Rozmiar wektora dla MiniLM
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Kolekcja {self.collection_name} została utworzona")
            else:
                logger.info(f"Kolekcja {self.collection_name} już istnieje")
                
        except Exception as e:
            logger.error(f"Błąd podczas inicjalizacji kolekcji: {e}")
            raise
    
    def add_knowledge(
        self, 
        content: str,
        title: str = None,
        knowledge_type: str = "general",
        archetype: str = None,
        tags: List[str] = None,
        source: str = "manual"
    ) -> str:
        """
        Dodaje nową wskazówkę do bazy wiedzy
        
        Args:
            content: Treść wskazówki
            title: Tytuł wskazówki (opcjonalny)
            knowledge_type: Typ wiedzy (general, objection, closing, etc.)
            archetype: Archetyp klienta którego dotyczy
            tags: Lista tagów
            source: Źródło wiedzy (manual, import, ai_generated)
            
        Returns:
            str: ID utworzonego punktu
        """
        try:
            # Generuj embedding dla treści
            vector = self.encoder.encode(content).tolist()
            
            # Wygeneruj unikatowy ID
            point_id = str(uuid.uuid4())
            
            # Przygotuj metadane
            payload = {
                "content": content,
                "title": title or f"Wskazówka {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "knowledge_type": knowledge_type,
                "archetype": archetype,
                "tags": tags or [],
                "source": source,
                "created_at": datetime.utcnow().isoformat(),
                "content_length": len(content),
                "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
            }
            
            # Utwórz punkt w Qdrant
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Dodano wiedzę do Qdrant: {point_id} - {title}")
            return point_id
            
        except Exception as e:
            logger.error(f"Błąd podczas dodawania wiedzy: {e}")
            raise
    
    def add_many_knowledge_points(self, knowledge_items: List[Dict[str, Any]]) -> List[str]:
        """
        Masowo dodaje wiele wskazówek do bazy wiedzy w jednej operacji
        
        Args:
            knowledge_items: Lista obiektów wiedzy do dodania
            
        Returns:
            List[str]: Lista ID utworzonych punktów
        """
        try:
            if not knowledge_items:
                return []
            
            logger.info(f"Masowe dodawanie {len(knowledge_items)} wskazówek do Qdrant")
            
            points = []
            created_ids = []
            
            for knowledge_data in knowledge_items:
                # Wygeneruj embedding dla treści
                vector = self.encoder.encode(knowledge_data["content"]).tolist()
                
                # Wygeneruj unikatowy ID
                point_id = str(uuid.uuid4())
                created_ids.append(point_id)
                
                # Przygotuj metadane
                payload = {
                    "content": knowledge_data["content"],
                    "title": knowledge_data.get("title") or f"Wskazówka {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    "knowledge_type": knowledge_data.get("knowledge_type", "general"),
                    "archetype": knowledge_data.get("archetype"),
                    "tags": knowledge_data.get("tags", []),
                    "source": knowledge_data.get("source", "import"),
                    "created_at": datetime.utcnow().isoformat(),
                    "content_length": len(knowledge_data["content"]),
                    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
                }
                
                # Utwórz punkt w Qdrant
                point = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
                points.append(point)
            
            # Wykonaj masowy upsert do Qdrant (jedna operacja)
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Pomyślnie dodano {len(points)} wskazówek do Qdrant w jednej operacji")
            return created_ids
            
        except Exception as e:
            logger.error(f"Błąd podczas masowego dodawania wiedzy: {e}")
            raise
    
    def get_all_knowledge(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Pobiera wszystkie wskazówki z bazy wiedzy
        
        Args:
            limit: Maksymalna liczba wyników
            
        Returns:
            List[Dict]: Lista wskazówek z metadanymi
        """
        try:
            # Pobierz wszystkie punkty z kolekcji
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False  # Nie potrzebujemy wektorów do wyświetlania
            )
            
            knowledge_items = []
            for point in result[0]:  # result[0] zawiera punkty
                knowledge_item = {
                    "id": point.id,
                    "content": point.payload.get("content", ""),
                    "title": point.payload.get("title", ""),
                    "knowledge_type": point.payload.get("knowledge_type", "general"),
                    "archetype": point.payload.get("archetype"),
                    "tags": point.payload.get("tags", []),
                    "source": point.payload.get("source", "manual"),
                    "created_at": point.payload.get("created_at"),
                    "content_length": point.payload.get("content_length", 0)
                }
                knowledge_items.append(knowledge_item)
            
            # Sortuj według daty utworzenia (najnowsze pierwsze)
            knowledge_items.sort(
                key=lambda x: x.get("created_at", ""), 
                reverse=True
            )
            
            logger.info(f"Pobrano {len(knowledge_items)} wskazówek z Qdrant")
            return knowledge_items
            
        except Exception as e:
            logger.error(f"Błąd podczas pobierania wiedzy: {e}")
            raise
    
    def delete_knowledge(self, point_id: str) -> bool:
        """
        Usuwa wskazówkę z bazy wiedzy
        
        Args:
            point_id: ID punktu do usunięcia
            
        Returns:
            bool: True jeśli usunięto pomyślnie
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[point_id]
                )
            )
            
            logger.info(f"Usunięto wiedzę z Qdrant: {point_id}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd podczas usuwania wiedzy: {e}")
            raise
    
    def search_knowledge(
        self, 
        query: str, 
        limit: int = 5,
        knowledge_type: Optional[str] = None,
        archetype: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Wyszukuje wskazówki podobne do zapytania
        
        Args:
            query: Zapytanie wyszukiwania
            limit: Maksymalna liczba wyników
            knowledge_type: Filtr typu wiedzy
            archetype: Filtr archetypu
            
        Returns:
            List[Dict]: Lista podobnych wskazówek z score
        """
        try:
            # Generuj embedding dla zapytania
            query_vector = self.encoder.encode(query).tolist()
            
            # Przygotuj filtry
            must_conditions = []
            if knowledge_type:
                must_conditions.append(
                    models.FieldCondition(
                        key="knowledge_type",
                        match=models.MatchValue(value=knowledge_type)
                    )
                )
            if archetype:
                must_conditions.append(
                    models.FieldCondition(
                        key="archetype",
                        match=models.MatchValue(value=archetype)
                    )
                )
            
            query_filter = None
            if must_conditions:
                query_filter = models.Filter(
                    must=must_conditions
                )
            
            # Wykonaj wyszukiwanie
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True
            )
            
            results = []
            for scored_point in search_result:
                result = {
                    "id": scored_point.id,
                    "score": scored_point.score,
                    "content": scored_point.payload.get("content", ""),
                    "title": scored_point.payload.get("title", ""),
                    "knowledge_type": scored_point.payload.get("knowledge_type", "general"),
                    "archetype": scored_point.payload.get("archetype"),
                    "tags": scored_point.payload.get("tags", [])
                }
                results.append(result)
            
            logger.info(f"Znaleziono {len(results)} podobnych wskazówek dla: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Błąd podczas wyszukiwania wiedzy: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Pobiera informacje o kolekcji (statystyki)
        
        Returns:
            Dict: Informacje o kolekcji
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "name": self.collection_name,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "status": collection_info.status,
                "optimizer_status": collection_info.optimizer_status,
                "segments_count": collection_info.segments_count
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas pobierania informacji o kolekcji: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Sprawdza połączenie z Qdrant
        
        Returns:
            Dict: Status połączenia
        """
        try:
            collections = self.client.get_collections()
            collection_exists = self.collection_name in [col.name for col in collections.collections]
            
            return {
                "status": "healthy",
                "qdrant_version": "1.7.0+",  # Możemy sprawdzić wersję API
                "collection_exists": collection_exists,
                "collection_name": self.collection_name,
                "collections_count": len(collections.collections)
            }
            
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "collection_name": self.collection_name
            }


# Singleton instance - używamy globalnie w aplikacji
qdrant_service = QdrantService()
