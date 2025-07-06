"""
Service layer for handling all interactions with the Google Gemini API.

This module is responsible for configuration, model initialization,
and the core logic of communicating with the Gemini API.
"""
import os
from app.logging_config import logger
from typing import Any, Dict, Iterator, List, Optional

# --- Constants and Configuration ---

SAFETY_SETTINGS = {
    'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
}

def stream_chat_response(model: Optional[Any], question: str, history: List[Dict[str, Any]]) -> Iterator[str]:
    """
    Starts a chat with the Gemini model and streams the response.

    Args:
        model: The initialized Gemini model instance from the app factory.
        question: The user's question.
        history: The conversation history, a list of dicts e.g. [{'role': 'user', 'parts': ['Hi']}]

    Yields:
        Chunks of the response text from the Gemini API.
    """
    try:
        if not model:
            yield "\n\n[Błąd: Model Gemini nie został poprawnie skonfigurowany. Sprawdź logi serwera.]"
            return

        chat = model.start_chat(history=history)
        response_stream = chat.send_message(question, stream=True)
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.error(f"Błąd podczas komunikacji z API Gemini: {e}", exc_info=True)
        yield f"\n\n[Wystąpił błąd serwera podczas komunikacji z Gemini. Sprawdź logi w konsoli, aby zobaczyć szczegóły.]"