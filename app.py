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
from flask import Flask

# Utworzenie aplikacji Flask
app = Flask(__name__)

# WAŻNE: Importowanie Twoich "routes" (tras) musi nastąpić
# PO załadowaniu zmiennych środowiskowych.
from app.routes.gemini_routes import gemini_bp

# Rejestracja blueprintu
app.register_blueprint(gemini_bp)

@app.route('/')
def index():
    return "Aplikacja Gemini działa!"

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)
