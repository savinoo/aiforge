"""
Embedding service.
Generates vector embeddings for text using OpenAI models.
"""

import logging
from typing import List
import asyncio

from openai import AsyncOpenAI

from app.core.config import settings
from app.services.rag.config import rag_config

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        """Initialize embedding service with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = rag_config.embedding_model
        self.dimensions = rag_config.embedding_dimensions
        self.batch_size = rag_config.embedding_batch_size

        # Simple in-memory cache (can be replaced with Redis for production)
        self._cache: dict[str, List[float]] = {}

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats

        Raises:
            RuntimeError: If embedding generation fails
        """
        # Check cache
        cache_key = self._get_cache_key(text)
        if cache_key in self._cache:
            logger.debug("Cache hit for embedding")
            return self._cache[cache_key]

        try:
            # Clean and truncate text if needed
            text = self._prepare_text(text)

            # Generate embedding
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
            )

            embedding = response.data[0].embedding

            # Cache the result
            self._cache[cache_key] = embedding

            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise RuntimeError(f"Embedding generation failed: {str(e)}") from e

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            RuntimeError: If batch embedding fails
        """
        if not texts:
            return []

        # Process in batches to avoid API limits
        all_embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = await self._embed_batch_internal(batch)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    async def _embed_batch_internal(self, texts: List[str]) -> List[List[float]]:
        """
        Internal method to embed a single batch.

        Args:
            texts: Batch of texts (up to batch_size)

        Returns:
            List of embeddings
        """
        # Check cache for each text
        embeddings = []
        texts_to_embed = []
        text_indices = []

        for idx, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                embeddings.append((idx, self._cache[cache_key]))
            else:
                texts_to_embed.append(self._prepare_text(text))
                text_indices.append(idx)

        # If all texts were cached
        if not texts_to_embed:
            return [emb for _, emb in sorted(embeddings)]

        try:
            # Generate embeddings for uncached texts
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts_to_embed,
            )

            # Cache and collect new embeddings
            for idx, embedding_obj in enumerate(response.data):
                original_idx = text_indices[idx]
                embedding = embedding_obj.embedding

                # Cache
                cache_key = self._get_cache_key(texts[original_idx])
                self._cache[cache_key] = embedding

                embeddings.append((original_idx, embedding))

            # Sort by original index and return
            embeddings.sort(key=lambda x: x[0])
            return [emb for _, emb in embeddings]

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            raise RuntimeError(f"Batch embedding failed: {str(e)}") from e

    def _prepare_text(self, text: str) -> str:
        """
        Prepare text for embedding.

        Args:
            text: Raw text

        Returns:
            Cleaned and truncated text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())

        # Truncate if too long (OpenAI has ~8k token limit)
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = 8000 * 4
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning(f"Truncated text from {len(text)} to {max_chars} characters")

        return text

    def _get_cache_key(self, text: str) -> str:
        """
        Generate cache key for text.

        Args:
            text: Text to hash

        Returns:
            Cache key string
        """
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("Embedding cache cleared")

    def get_cache_size(self) -> int:
        """Get current cache size."""
        return len(self._cache)


# Singleton instance
embedding_service = EmbeddingService()
