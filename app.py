from dotenv import load_dotenv
import os

# KROK 1: Wczytaj zmienne środowiskowe z pliku .env
# To musi być jedna z pierwszych operacji w aplikacji,
# zanim zostaną zaimportowane moduły, które z nich korzystają.
load_dotenv()

# --- Linia do debugowania (opcjonalna, ale pomocna) ---
# Sprawdźmy, czy klucz został poprawnie załadowany.
# Po uruchomieniu aplikacji w terminalu powinna pojawić się ta linia.
print(f"DEBUG: Wczytany GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')}")

# KROK 2: Tutaj zaczyna się reszta Twojej aplikacji
from flask import Flask, render_template
from flask_cors import CORS

# Utworzenie aplikacji Flask
app = Flask(__name__)

# --- Konfiguracja CORS ---
# Włączamy CORS dla całej aplikacji. To pozwala przeglądarce (frontendowi)
# bezpiecznie komunikować się z naszym serwerem (backendem).
# W środowisku produkcyjnym warto ograniczyć dostęp tylko do zaufanej domeny:
# CORS(app, resources={r"/gemini/*": {"origins": "https://twoja-domena.com"}})
CORS(app)

# WAŻNE: Importowanie Twoich "routes" (tras) musi nastąpić
# PO załadowaniu zmiennych środowiskowych.
from app.routes.gemini_routes import gemini_bp

# Rejestracja blueprintu
app.register_blueprint(gemini_bp)

@app.route('/')
def index():
    return render_template('index.html')

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)
