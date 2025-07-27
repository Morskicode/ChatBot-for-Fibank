"""
Semantic search service with lazy initialization

This service provides semantic similarity search capabilities using sentence transformers
with lazy loading for improved startup performance.
"""

import logging
import os
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logger = logging.getLogger(__name__)


class SemanticService:
    """
    Semantic search service with lazy initialization
    
    This service manages sentence transformer models and product embeddings
    with lazy loading to improve startup time. Embeddings are only built
    when first needed.
    """
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Initialize semantic service
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self._model = None
        self._embeddings = None
        self._product_texts = []
        self._product_keys = []
        self._knowledge_base = None
        
        # Check if sentence transformers is available
        if SentenceTransformer is None:
            logger.error("sentence-transformers not available. Install with: pip install sentence-transformers")
            raise ImportError("sentence-transformers is required for semantic search")
    
    @property
    def model(self) -> 'SentenceTransformer':
        """
        Lazy-loaded sentence transformer model
        
        Returns:
            SentenceTransformer model instance
        """
        if self._model is None:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            try:
                self._model = SentenceTransformer(self.model_name)
                logger.info("Sentence transformer model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load sentence transformer model: {e}")
                raise
        return self._model
    
    def set_knowledge_base(self, knowledge_base: Dict[str, Any]):
        """
        Set the knowledge base for building embeddings
        
        Args:
            knowledge_base: Dictionary containing product information
        """
        self._knowledge_base = knowledge_base
        # Clear cached embeddings when knowledge base changes
        self._embeddings = None
        self._product_texts = []
        self._product_keys = []
    
    def _prepare_product_texts(self):
        """Prepare product texts for embedding generation"""
        if self._product_texts or not self._knowledge_base:
            return
        
        products = self._knowledge_base.get('products', {})
        if not products:
            logger.warning("No products found in knowledge base")
            return
        
        for key, product in products.items():
            # Create comprehensive text representation
            text = f"{product['name']} {product['description']}"
            
            # Add additional information from raw data if available
            if 'raw_data' in product:
                raw = product['raw_data']
                if 'информация за продукта' in raw:
                    text += f" {raw['информация за продукта']}"
                if 'features' in raw:
                    if isinstance(raw['features'], list):
                        text += f" {' '.join(raw['features'])}"
                    else:
                        text += f" {raw['features']}"
                if 'benefits' in raw:
                    if isinstance(raw['benefits'], list):
                        text += f" {' '.join(raw['benefits'])}"
                    else:
                        text += f" {raw['benefits']}"
            
            self._product_texts.append(text)
            self._product_keys.append(key)
        
        logger.info(f"Prepared {len(self._product_texts)} product texts for embedding")
    
    def build_embeddings(self) -> np.ndarray:
        """
        Build product embeddings (lazy-loaded)
        
        Returns:
            NumPy array of product embeddings
        """
        if self._embeddings is not None:
            return self._embeddings
        
        self._prepare_product_texts()
        
        if not self._product_texts:
            logger.warning("No product texts available for embedding generation")
            return np.array([])
        
        try:
            logger.info(f"Generating embeddings for {len(self._product_texts)} products")
            self._embeddings = self.model.encode(self._product_texts)
            logger.info("Product embeddings generated successfully")
            return self._embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return np.array([])
    
    def find_similar_products(self, query: str, top_k: int = 3, threshold: float = 0.3) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Find products similar to the query using semantic search
        
        Args:
            query: User's search query
            top_k: Maximum number of products to return
            threshold: Minimum similarity threshold (0.0 to 1.0)
            
        Returns:
            List of tuples (product_key, product_data, similarity_score)
        """
        try:
            embeddings = self.build_embeddings()
            
            if embeddings.size == 0:
                logger.warning("No embeddings available for similarity search")
                return []
            
            # Encode user query
            query_embedding = self.model.encode([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_embedding, embeddings)[0]
            
            # Get indices of most similar products
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                similarity = similarities[idx]
                if similarity > threshold:
                    product_key = self._product_keys[idx]
                    product_data = self._knowledge_base['products'][product_key]
                    results.append((product_key, product_data, similarity))
            
            logger.info(f"Found {len(results)} similar products for query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar products: {e}")
            return []
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the embeddings
        
        Returns:
            Dictionary with embedding statistics
        """
        embeddings = self.build_embeddings()
        
        if embeddings.size == 0:
            return {"status": "no_embeddings"}
        
        return {
            "status": "ready",
            "num_products": len(self._product_keys),
            "embedding_dimension": embeddings.shape[1] if len(embeddings.shape) > 1 else 0,
            "model_name": self.model_name,
            "total_texts_length": sum(len(text) for text in self._product_texts)
        } 