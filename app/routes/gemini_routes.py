from flask import Blueprint, request, jsonify, Response, stream_with_context, current_app
from app.services.gemini_service import stream_chat_response
from app.logging_config import logger

# Stwórz Blueprint dla tras związanych z Gemini
# Wszystkie trasy w tym pliku będą miały prefiks /gemini
gemini_bp = Blueprint('gemini', __name__, url_prefix='/gemini')

@gemini_bp.route('/ask', methods=['POST'])
def ask_gemini():
    """
    Obsługuje żądanie POST do /gemini/ask.
    Odbiera pytanie oraz historię czatu i streamuje odpowiedź z Gemini API
    przy użyciu warstwy serwisowej.
    """
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Brak pytania w żądaniu"}), 400

    question = data['question']
    # Historia jest opcjonalna, jeśli nie ma jej w żądaniu, użyj pustej listy
    history = data.get('history', [])
    logger.info(f"Odebrano pytanie: '{question}' z historią o długości {len(history)}")

    # Pobieramy model z kontekstu aplikacji, skonfigurowany w create_app
    model = current_app.model

    # Używamy stream_with_context, aby odpowiedzi były wysyłane na bieżąco
    return Response(
        stream_with_context(stream_chat_response(model, question, history)),
        mimetype='text/plain'
    )