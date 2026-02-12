"""
RAG prompt templates.
Configurable system prompts for RAG chat with citation support.
"""

from typing import List, Dict, Any


DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant with access to a knowledge base.

Your task is to answer user questions based on the provided context from the knowledge base.

IMPORTANT INSTRUCTIONS:
1. Always base your answers on the provided context
2. If the context doesn't contain relevant information, say so clearly
3. Always cite your sources using the format: [Source: document_name, page X]
4. Be concise but thorough
5. If you're uncertain, acknowledge it
6. Never make up information not present in the context

When citing sources:
- Use the exact document name and page/chunk number provided
- Format citations as: [Source: filename.pdf, page 5]
- Include citations inline where relevant information is used
- You can cite multiple sources if the answer draws from multiple documents
"""


def build_rag_prompt(
    query: str,
    context_chunks: List[Dict[str, Any]],
    conversation_history: List[Dict[str, str]] | None = None,
    custom_instructions: str | None = None,
) -> str:
    """
    Build a complete RAG prompt with context and conversation history.

    Args:
        query: User's current question
        context_chunks: Retrieved chunks with metadata (source, page, content)
        conversation_history: Previous messages in the conversation
        custom_instructions: Optional tenant-specific instructions

    Returns:
        Formatted prompt string ready for LLM
    """
    # Start with system prompt
    system_prompt = DEFAULT_SYSTEM_PROMPT
    if custom_instructions:
        system_prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}"

    # Format context chunks
    context_text = "\n\n---\n\n".join([
        f"Document: {chunk.get('source', 'Unknown')}\n"
        f"Page/Section: {chunk.get('page', chunk.get('chunk_index', 'N/A'))}\n"
        f"Content:\n{chunk.get('content', '')}"
        for chunk in context_chunks
    ])

    # Build the prompt
    prompt_parts = [system_prompt]

    if context_text:
        prompt_parts.append(f"\nCONTEXT FROM KNOWLEDGE BASE:\n{context_text}")

    # Add conversation history if provided
    if conversation_history:
        history_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history
        ])
        prompt_parts.append(f"\nCONVERSATION HISTORY:\n{history_text}")

    # Add current query
    prompt_parts.append(f"\nCURRENT QUESTION:\n{query}")

    prompt_parts.append(
        "\nProvide your answer based on the context above. "
        "Remember to cite your sources using the format: [Source: document_name, page X]"
    )

    return "\n\n".join(prompt_parts)


def build_citation_extraction_prompt(response: str) -> str:
    """
    Build a prompt to extract citations from a RAG response.

    This can be used if you want to post-process the response to
    extract structured citation data.

    Args:
        response: LLM response with inline citations

    Returns:
        Prompt for citation extraction
    """
    return f"""Extract all citations from the following text.
Return them as a JSON array with format: [{{"source": "filename", "page": "X"}}]

Text:
{response}

Citations (JSON only, no explanation):"""


# Alternative prompt styles for different use cases
CONCISE_PROMPT = """You are a helpful AI assistant. Answer questions based only on the provided context.
Keep answers brief and always cite sources using [Source: filename, page X] format.
If information is not in the context, say "I don't have that information in my knowledge base."
"""

DETAILED_PROMPT = """You are an expert AI assistant with access to a comprehensive knowledge base.

Answer the user's question with detailed, well-structured responses based on the provided context.

Guidelines:
- Provide thorough explanations with examples when relevant
- Break down complex topics into digestible sections
- Use bullet points or numbered lists for clarity when appropriate
- Always cite sources: [Source: document_name, page X]
- If multiple sources support your answer, cite all of them
- Acknowledge limitations if the context doesn't fully answer the question
- Suggest related topics the user might want to explore

Maintain a professional, informative tone throughout your response.
"""

CONVERSATIONAL_PROMPT = """You are a friendly and knowledgeable AI assistant helping users understand their documents.

Chat naturally with the user while staying grounded in the provided context.

Your style:
- Warm and approachable tone
- Clear and easy to understand
- Patient with follow-up questions
- Honest about limitations
- Always cite sources: [Source: filename, page X]

Remember: Never invent information. If it's not in the context, say so in a friendly way.
"""


def get_prompt_by_style(style: str = "default") -> str:
    """
    Get system prompt by style name.

    Args:
        style: Prompt style ("default", "concise", "detailed", "conversational")

    Returns:
        System prompt string
    """
    prompts = {
        "default": DEFAULT_SYSTEM_PROMPT,
        "concise": CONCISE_PROMPT,
        "detailed": DETAILED_PROMPT,
        "conversational": CONVERSATIONAL_PROMPT,
    }
    return prompts.get(style, DEFAULT_SYSTEM_PROMPT)
