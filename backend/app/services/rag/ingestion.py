"""
Document ingestion service.
Handles loading and parsing of multiple document formats.
"""

import io
import logging
from typing import List, BinaryIO
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    CSVLoader,
    UnstructuredHTMLLoader,
)
from langchain_core.documents import Document
import httpx

from app.services.rag.config import rag_config

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """Service for ingesting documents from various sources and formats."""

    async def ingest_file(
        self,
        file_content: bytes,
        filename: str,
        mime_type: str | None = None,
    ) -> List[Document]:
        """
        Ingest a document from file bytes.

        Args:
            file_content: Raw file bytes
            filename: Original filename (used for format detection)
            mime_type: Optional MIME type

        Returns:
            List of Document objects with text and metadata

        Raises:
            ValueError: If file format is not supported
            RuntimeError: If document processing fails
        """
        # Validate file size
        size_mb = len(file_content) / (1024 * 1024)
        if size_mb > rag_config.max_file_size_mb:
            raise ValueError(
                f"File size ({size_mb:.2f}MB) exceeds maximum allowed "
                f"({rag_config.max_file_size_mb}MB)"
            )

        # Detect format from extension
        extension = Path(filename).suffix.lower()
        if extension not in rag_config.supported_extensions:
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(rag_config.supported_extensions)}"
            )

        try:
            # Route to appropriate loader
            if extension == ".pdf":
                documents = await self._load_pdf(file_content, filename)
            elif extension == ".docx":
                documents = await self._load_docx(file_content, filename)
            elif extension == ".txt":
                documents = await self._load_text(file_content, filename)
            elif extension == ".csv":
                documents = await self._load_csv(file_content, filename)
            elif extension in [".md", ".html"]:
                documents = await self._load_html_or_markdown(file_content, filename)
            else:
                raise ValueError(f"Unsupported file format: {extension}")

            # Enrich metadata
            for doc in documents:
                doc.metadata["source"] = filename
                doc.metadata["file_type"] = extension
                if "page" not in doc.metadata:
                    doc.metadata["page"] = 1

            logger.info(f"Successfully ingested {filename}: {len(documents)} pages/sections")
            return documents

        except Exception as e:
            logger.error(f"Failed to ingest {filename}: {str(e)}")
            raise RuntimeError(f"Failed to process document: {str(e)}") from e

    async def ingest_url(self, url: str) -> List[Document]:
        """
        Ingest content from a URL.

        Args:
            url: Web page URL

        Returns:
            List of Document objects

        Raises:
            ValueError: If URL is invalid or unreachable
            RuntimeError: If content extraction fails
        """
        try:
            # Fetch URL content
            async with httpx.AsyncClient(
                timeout=rag_config.url_timeout_seconds
            ) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            # Handle different content types
            if "text/html" in content_type:
                documents = await self._load_html_or_markdown(
                    response.content,
                    url,
                )
            elif "text/plain" in content_type:
                documents = await self._load_text(response.content, url)
            elif "application/pdf" in content_type:
                documents = await self._load_pdf(response.content, url)
            else:
                # Default to HTML parsing
                documents = await self._load_html_or_markdown(
                    response.content,
                    url,
                )

            # Add URL metadata
            for doc in documents:
                doc.metadata["source"] = url
                doc.metadata["source_type"] = "url"

            logger.info(f"Successfully ingested URL {url}: {len(documents)} sections")
            return documents

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch URL {url}: {str(e)}")
            raise ValueError(f"Failed to fetch URL: {str(e)}") from e
        except Exception as e:
            logger.error(f"Failed to process URL {url}: {str(e)}")
            raise RuntimeError(f"Failed to process URL content: {str(e)}") from e

    async def _load_pdf(
        self,
        file_content: bytes,
        source: str,
    ) -> List[Document]:
        """Load PDF document."""
        # Write to temporary file for PyPDFLoader
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
            return documents
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    async def _load_docx(
        self,
        file_content: bytes,
        source: str,
    ) -> List[Document]:
        """Load DOCX document."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            loader = UnstructuredWordDocumentLoader(tmp_path)
            documents = loader.load()
            return documents
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    async def _load_text(
        self,
        file_content: bytes,
        source: str,
    ) -> List[Document]:
        """Load plain text document."""
        try:
            text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            # Try with latin-1 as fallback
            text = file_content.decode("latin-1")

        return [
            Document(
                page_content=text,
                metadata={"source": source, "page": 1},
            )
        ]

    async def _load_csv(
        self,
        file_content: bytes,
        source: str,
    ) -> List[Document]:
        """Load CSV document."""
        import tempfile
        with tempfile.NamedTemporaryFile(
            suffix=".csv",
            delete=False,
            mode="wb",
        ) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            loader = CSVLoader(tmp_path)
            documents = loader.load()
            return documents
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    async def _load_html_or_markdown(
        self,
        file_content: bytes,
        source: str,
    ) -> List[Document]:
        """Load HTML or Markdown document."""
        import tempfile
        suffix = ".html" if source.endswith(".html") else ".md"
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
            mode="wb",
        ) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            loader = UnstructuredHTMLLoader(tmp_path)
            documents = loader.load()
            return documents
        finally:
            Path(tmp_path).unlink(missing_ok=True)


# Singleton instance
ingestion_service = DocumentIngestionService()
