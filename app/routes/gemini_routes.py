from flask import Blueprint, request, jsonify, Response, stream_with_context
from ..services.gemini_service import stream_chat_response

# Stwórz Blueprint dla tras związanych z Gemini
# Wszystkie trasy w tym pliku będą miały prefiks /gemini
gemini_bp = Blueprint('gemini', __name__, url_prefix='/gemini')

@gemini_bp.route('/ask', methods=['POST'], strict_slashes=False)
def ask_gemini():
    """
    Obsługuje żądanie POST do /gemini/ask.
    Odbiera pytanie oraz historię, a następnie streamuje odpowiedź
    z serwisu Gemini, który zarządza logiką i historią.
    """
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Brak pytania w żądaniu"}), 400

    question = data['question']
    # Pobieramy historię z żądania; jeśli nie istnieje, używamy pustej listy.
    history = data.get('history', [])

    # Dodatkowa walidacja: upewniamy się, że historia jest listą, aby uniknąć błędów.
    if not isinstance(history, list):
        return jsonify({"error": "Pole 'history' musi być listą (array)."}), 400

    # Frontend wysyła całą historię, łącznie z bieżącym pytaniem.
    # Usuwamy ostatni element, ponieważ przekazujemy go osobno do funkcji.
    chat_history = history[:-1] if history else []

    # Wywołujemy funkcję z warstwy serwisowej, przekazując jej pytanie i historię.
    response_generator = stream_chat_response(question, chat_history)

    # Streamujemy odpowiedź z generatora z powrotem do klienta.
    return Response(stream_with_context(response_generator), mimetype='text/plain')