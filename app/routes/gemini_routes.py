import os
import google.generativeai as genai
from flask import Blueprint, request, jsonify, Response, stream_with_context, current_app

# Stwórz Blueprint dla tras związanych z Gemini
# Wszystkie trasy w tym pliku będą miały prefiks /gemini
gemini_bp = Blueprint('gemini', __name__, url_prefix='/gemini')

# Konfiguracja klucza API dla Gemini
try:
    # Upewnij się, że zmienna GOOGLE_API_KEY jest w pliku .env
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    raise RuntimeError("Nie znaleziono GOOGLE_API_KEY w pliku .env. Ustaw go.")

# Inicjalizuj model raz, przy starcie aplikacji, a nie przy każdym żądaniu.
# To znacznie poprawia wydajność.
try:
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    model = None
    # Użyj loggera zamiast print. To jest błąd krytyczny dla działania aplikacji.
    # current_app jest dostępne, ponieważ ten kod jest importowany po utworzeniu aplikacji.
    current_app.logger.critical(f"Nie udało się zainicjalizować modelu Gemini: {e}", exc_info=True)

@gemini_bp.route('/ask', methods=['POST'])
def ask_gemini():
    """
    Obsługuje żądanie POST do /gemini/ask.
    Odbiera pytanie i streamuje odpowiedź z Gemini API.
    """
    data = request.get_json()
    if not model:
        # Zwróć ogólny, bezpieczny komunikat. Szczegóły są w pliku logów.
        error_payload = {"error": "Aplikacja nie jest w stanie przetworzyć Twojego zapytania w tym momencie."}
        if current_app.config['DEBUG']:
            error_payload['developer_details'] = "Model Gemini nie został poprawnie zainicjalizowany. Sprawdź logi startowe."

        return jsonify(error_payload), 503

    if not data or 'question' not in data:
        return jsonify({"error": "Brak pytania w żądaniu"}), 400

    question = data.get('question')
    # Pobierz historię z żądania, jeśli nie ma, użyj pustej listy.
    # Frontend będzie musiał wysyłać tablicę z poprzednimi wiadomościami.
    history = data.get('history', [])
    
    # --- Wzmocnienie bezpieczeństwa: Walidacja i ograniczenie danych wejściowych ---
    MAX_HISTORY_LENGTH = 50 # Ogranicz historię do 50 ostatnich wiadomości (25 tur)
    
    if not isinstance(question, str) or not isinstance(history, list):
        return jsonify({"error": "Nieprawidłowy format danych. 'question' musi być tekstem, a 'history' listą."}), 400

    if len(question) > 4000: # Ogranicz długość pojedynczego pytania
        return jsonify({"error": "Pytanie jest zbyt długie."}), 413 # Payload Too Large

    if len(history) > MAX_HISTORY_LENGTH:
        history = history[-MAX_HISTORY_LENGTH:] # Weź tylko N ostatnich elementów

    def generate_response():
        """Generator, który zwraca fragmenty odpowiedzi od Gemini."""
        try:
            # Rozpocznij sesję czatu z przekazaną historią, aby model miał kontekst
            chat = model.start_chat(history=history)

            # Wyślij nowe pytanie w kontekście tej sesji
            response_stream = chat.send_message(question, stream=True)

            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            # Zaloguj pełny błąd do pliku, a użytkownikowi pokaż ogólny komunikat.
            current_app.logger.error(f"Błąd podczas streamowania odpowiedzi z Gemini API: {e}", exc_info=True)
            yield "\n\n[Wystąpił błąd serwera. Spróbuj ponownie później.]"

    return Response(stream_with_context(generate_response()), mimetype='text/plain')