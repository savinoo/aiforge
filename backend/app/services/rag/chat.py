"""
RAG chat service.
Main entry point for conversational RAG with streaming support.
"""

import logging
from typing import List, Dict, Any, AsyncIterator
import json

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.core.config import settings
from app.services.rag.retriever import retriever
from app.services.rag.prompts import build_rag_prompt, get_prompt_by_style
from app.services.rag.config import rag_config

logger = logging.getLogger(__name__)


class RAGChatService:
    """Service for RAG-powered conversational chat."""

    def __init__(self):
        """Initialize chat service with LLM clients."""
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def chat(
        self,
        message: str,
        tenant_id: str,
        conversation_history: List[Dict[str, str]] | None = None,
        document_ids: List[str] | None = None,
        model: str = "gpt-4o-mini",
        provider: str = "openai",
        stream: bool = True,
        custom_instructions: str | None = None,
        prompt_style: str = "default",
    ) -> AsyncIterator[str] | Dict[str, Any]:
        """
        Chat with RAG context.

        Args:
            message: User's message
            tenant_id: User/tenant ID
            conversation_history: Previous messages
            document_ids: Optional filter for specific documents
            model: LLM model to use
            provider: LLM provider ("openai" or "anthropic")
            stream: Whether to stream the response
            custom_instructions: Optional custom system instructions
            prompt_style: Prompt style ("default", "concise", "detailed", "conversational")

        Returns:
            Async iterator of response chunks if streaming, else complete response

        Raises:
            ValueError: If provider is invalid
            RuntimeError: If chat fails
        """
        try:
            # Retrieve relevant context
            context_chunks = await retriever.retrieve(
                query=message,
                tenant_id=tenant_id,
                document_ids=document_ids,
            )

            # Build prompt
            system_prompt = get_prompt_by_style(prompt_style)
            if custom_instructions:
                system_prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}"

            # Format context for prompt
            context_for_prompt = [
                {
                    "content": chunk["content"],
                    "source": chunk["citation"]["source"],
                    "page": chunk["citation"]["page"],
                }
                for chunk in context_chunks
            ]

            # Route to appropriate provider
            if provider == "openai":
                return await self._chat_openai(
                    message=message,
                    system_prompt=system_prompt,
                    context_chunks=context_for_prompt,
                    conversation_history=conversation_history,
                    model=model,
                    stream=stream,
                    source_chunks=context_chunks,
                )
            elif provider == "anthropic":
                return await self._chat_anthropic(
                    message=message,
                    system_prompt=system_prompt,
                    context_chunks=context_for_prompt,
                    conversation_history=conversation_history,
                    model=model,
                    stream=stream,
                    source_chunks=context_chunks,
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

        except Exception as e:
            logger.error(f"Chat failed: {str(e)}")
            raise RuntimeError(f"Chat failed: {str(e)}") from e

    async def _chat_openai(
        self,
        message: str,
        system_prompt: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] | None,
        model: str,
        stream: bool,
        source_chunks: List[Dict[str, Any]],
    ) -> AsyncIterator[str] | Dict[str, Any]:
        """
        Chat using OpenAI API.

        Args:
            message: User message
            system_prompt: System prompt
            context_chunks: Context chunks for prompt
            conversation_history: Previous messages
            model: Model name
            stream: Whether to stream
            source_chunks: Original chunks with citations

        Returns:
            Stream or complete response
        """
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add context
        if context_chunks:
            context_text = "\n\n---\n\n".join([
                f"Document: {chunk['source']}\n"
                f"Page: {chunk['page']}\n"
                f"Content:\n{chunk['content']}"
                for chunk in context_chunks
            ])
            messages.append({
                "role": "system",
                "content": f"CONTEXT FROM KNOWLEDGE BASE:\n{context_text}"
            })

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add current message
        messages.append({"role": "user", "content": message})

        # Call OpenAI API
        if stream:
            return self._stream_openai(messages, model, source_chunks)
        else:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )
            content = response.choices[0].message.content

            return {
                "content": content,
                "sources": [
                    {
                        "source": chunk["citation"]["source"],
                        "page": chunk["citation"]["page"],
                        "similarity": chunk["similarity"],
                    }
                    for chunk in source_chunks
                ],
                "model": model,
                "provider": "openai",
            }

    async def _stream_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        source_chunks: List[Dict[str, Any]],
    ) -> AsyncIterator[str]:
        """
        Stream OpenAI chat response.

        Args:
            messages: Chat messages
            model: Model name
            source_chunks: Source chunks for citations

        Yields:
            Response chunks as JSON strings
        """
        try:
            stream = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                stream=True,
            )

            # First, yield sources metadata
            sources_data = {
                "type": "sources",
                "sources": [
                    {
                        "source": chunk["citation"]["source"],
                        "page": chunk["citation"]["page"],
                        "similarity": chunk["similarity"],
                    }
                    for chunk in source_chunks
                ],
            }
            yield f"data: {json.dumps(sources_data)}\n\n"

            # Then stream content
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"

            # Send done signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    async def _chat_anthropic(
        self,
        message: str,
        system_prompt: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] | None,
        model: str,
        stream: bool,
        source_chunks: List[Dict[str, Any]],
    ) -> AsyncIterator[str] | Dict[str, Any]:
        """
        Chat using Anthropic API.

        Args:
            message: User message
            system_prompt: System prompt
            context_chunks: Context chunks
            conversation_history: Previous messages
            model: Model name
            stream: Whether to stream
            source_chunks: Source chunks for citations

        Returns:
            Stream or complete response
        """
        # Build system prompt with context
        full_system = system_prompt

        if context_chunks:
            context_text = "\n\n---\n\n".join([
                f"Document: {chunk['source']}\n"
                f"Page: {chunk['page']}\n"
                f"Content:\n{chunk['content']}"
                for chunk in context_chunks
            ])
            full_system += f"\n\nCONTEXT FROM KNOWLEDGE BASE:\n{context_text}"

        # Build messages (Anthropic format)
        messages = []

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": message})

        # Call Anthropic API
        if stream:
            return self._stream_anthropic(
                system=full_system,
                messages=messages,
                model=model or "claude-3-5-sonnet-20241022",
                source_chunks=source_chunks,
            )
        else:
            response = await self.anthropic_client.messages.create(
                model=model or "claude-3-5-sonnet-20241022",
                system=full_system,
                messages=messages,
                max_tokens=4096,
            )
            content = response.content[0].text

            return {
                "content": content,
                "sources": [
                    {
                        "source": chunk["citation"]["source"],
                        "page": chunk["citation"]["page"],
                        "similarity": chunk["similarity"],
                    }
                    for chunk in source_chunks
                ],
                "model": model,
                "provider": "anthropic",
            }

    async def _stream_anthropic(
        self,
        system: str,
        messages: List[Dict[str, str]],
        model: str,
        source_chunks: List[Dict[str, Any]],
    ) -> AsyncIterator[str]:
        """
        Stream Anthropic chat response.

        Args:
            system: System prompt
            messages: Chat messages
            model: Model name
            source_chunks: Source chunks

        Yields:
            Response chunks as JSON strings
        """
        try:
            # First, yield sources
            sources_data = {
                "type": "sources",
                "sources": [
                    {
                        "source": chunk["citation"]["source"],
                        "page": chunk["citation"]["page"],
                        "similarity": chunk["similarity"],
                    }
                    for chunk in source_chunks
                ],
            }
            yield f"data: {json.dumps(sources_data)}\n\n"

            # Stream content
            async with self.anthropic_client.messages.stream(
                model=model,
                system=system,
                messages=messages,
                max_tokens=4096,
            ) as stream:
                async for text in stream.text_stream:
                    yield f"data: {json.dumps({'type': 'content', 'content': text})}\n\n"

            # Send done signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"Anthropic streaming failed: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"


# Singleton instance
rag_chat = RAGChatService()
