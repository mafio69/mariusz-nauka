"""
Blueprint for handling all Gemini AI related routes.
"""
import os
from typing import Iterator
import google.generativeai as genai
from flask import (
    Blueprint,
    Response,
    jsonify,
    request,
    stream_with_context,
)

# Define the model name as a constant for easier updates
GEMINI_MODEL_NAME = 'gemini-pro'

# Create a Blueprint for Gemini-related routes.
# All routes defined in this file will be prefixed with /gemini.
gemini_bp = Blueprint('gemini', __name__, url_prefix='/gemini')

# Configure the Gemini API key at the module level.
# This will run once when the module is imported.
try:
    # Ensure the GOOGLE_API_KEY is set in the environment variables (e.g., in a .env file).
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    # This is a critical failure. The application cannot start without the API key.
    raise RuntimeError(
        "GOOGLE_API_KEY not found in environment variables. "
        "Please set it in your .env file or environment."
    ) from None


@gemini_bp.route('/ask', methods=['POST'])
def ask_gemini() -> Response:
    """
    Handles POST requests to /gemini/ask.
    Receives a question in the JSON body and streams a response from the Gemini API.

    Returns:
        A Flask Response object streaming the text from the Gemini API.
    """
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    question = data['question']

    def generate_response_stream() -> Iterator[str]:
        """A generator function that yields chunks of the response from the Gemini API."""
        try:
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            response_stream = model.generate_content(question, stream=True)
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            # Use print() to see the exact error in the server console.
            # This is more reliable inside a generator than a logger.
            print(f"!!! ERROR COMMUNICATING WITH GEMINI API: {e}")
            # Return a user-friendly message indicating a server-side issue.
            yield f"\n\n[Wystąpił błąd serwera. Sprawdź logi w konsoli, aby zobaczyć szczegóły.]"

    return Response(stream_with_context(generate_response_stream()), mimetype='text/plain')
