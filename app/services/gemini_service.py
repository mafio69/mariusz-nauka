"""
Service layer for handling all interactions with the Google Gemini API.

This module is responsible for configuration, model initialization,
and the core logic of communicating with the Gemini API.
"""
import os
from typing import Any, Dict, Iterator, List
import google.generativeai as genai

# --- Constants and Configuration ---

# Use a modern, recommended model. 'gemini-1.5-flash-latest' is fast and capable.
# The old 'gemini-pro' model name can cause errors with current API versions.
GEMINI_MODEL_NAME = 'gemini-1.5-flash-latest'

SAFETY_SETTINGS = {
    'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
}

# --- API Configuration and Model Initialization ---

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    # Create the model instance once when the service is loaded.
    _model = genai.GenerativeModel(GEMINI_MODEL_NAME, safety_settings=SAFETY_SETTINGS)
except KeyError:
    raise RuntimeError(
        "GOOGLE_API_KEY not found in environment variables. "
        "Please set it in your .env file or environment."
    ) from None


def stream_chat_response(question: str, history: List[Dict[str, Any]]) -> Iterator[str]:
    """
    Starts a chat with the Gemini model and streams the response.

    Args:
        question: The user's question.
        history: The conversation history, a list of dicts e.g. [{'role': 'user', 'parts': ['Hi']}]

    Yields:
        Chunks of the response text from the Gemini API.
    """
    try:
        chat = _model.start_chat(history=history)
        response_stream = chat.send_message(question, stream=True)
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        print(f"!!! ERROR COMMUNICATING WITH GEMINI API: {e}")
        yield f"\n\n[Wystąpił błąd serwera. Sprawdź logi w konsoli, aby zobaczyć szczegóły.]"