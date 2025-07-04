from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

# KROK 1: Wczytaj zmienne środowiskowe z pliku .env
# To musi być jedna z pierwszych operacji w aplikacji,
# zanim zostaną zaimportowane moduły, które z nich korzystają.
load_dotenv()

# KROK 2: Tutaj zaczyna się reszta Twojej aplikacji
from flask import Flask, render_template
from flask_cors import CORS

# Utworzenie aplikacji Flask
app = Flask(__name__)
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = (app.config['ENV'] == 'development')

def configure_logging(app):
    """Konfiguruje system logowania dla aplikacji."""
    # Usuń domyślny handler Flaska, aby uniknąć podwójnych logów
    del app.logger.handlers[:]

    # Zdefiniuj format logów
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]')

    # --- Handler do zapisu logów do pliku (zawsze aktywny) ---
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Użyj RotatingFileHandler, aby pliki logów nie rosły w nieskończoność
    file_handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=10240, backupCount=10)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO) # Zapisuj do pliku logi od poziomu INFO wzwyż
    app.logger.addHandler(file_handler)

    # --- Handler do wyświetlania logów w konsoli (tylko w trybie deweloperskim) ---
    if app.config['DEBUG']:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        stream_handler.setLevel(logging.DEBUG) # W konsoli pokazuj wszystko od poziomu DEBUG
        app.logger.addHandler(stream_handler)

configure_logging(app)

# --- Konfiguracja CORS ---
# Włączamy CORS dla całej aplikacji. To pozwala przeglądarce (frontendowi)
# bezpiecznie komunikować się z naszym serwerem (backendem).

allowed_origin = os.getenv('FRONTEND_ORIGIN') # np. https://twoja-domena.com

if allowed_origin:
    # Ogranicz dostęp tylko do zaufanej domeny, jeśli jest zdefiniowana
    CORS(app, resources={r"/gemini/*": {"origins": allowed_origin}})
    app.logger.info(f"CORS skonfigurowany na zezwalanie tylko dla źródła: {allowed_origin}")
elif app.config['DEBUG']:
    # W trybie deweloperskim, pozwól na dostęp z dowolnego źródła dla wygody
    CORS(app)
    app.logger.info("Tryb deweloperski: CORS skonfigurowany na zezwalanie wszystkim źródłom.")
else:
    # W trybie produkcyjnym, jeśli origin nie jest zdefiniowany, rzuć błędem.
    raise RuntimeError("KRYTYCZNY BŁĄD BEZPIECZEŃSTWA: Zmienna FRONTEND_ORIGIN nie jest ustawiona w trybie produkcyjnym!")

# --- Logowanie deweloperskie ---
# Wyświetlaj pomocne komunikaty tylko w trybie deweloperskim.
if app.config['DEBUG']:
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        app.logger.info("Tryb deweloperski: Zmienna GOOGLE_API_KEY została wczytana.")
    else:
        app.logger.warning("Tryb deweloperski: Zmienna GOOGLE_API_KEY nie została znaleziona.")

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
    app.run(debug=app.config['DEBUG'])
