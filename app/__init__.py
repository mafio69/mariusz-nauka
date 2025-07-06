from flask import Flask, jsonify
import google.generativeai as genai
import os

from google.cloud import secretmanager
from google.api_core.exceptions import PermissionDenied, NotFound
from google.auth.exceptions import DefaultCredentialsError
from .logging_config import logger
from .config import config_by_name

def create_app(config_name: str = 'default') -> Flask:
    """
    Fabryka aplikacji - tworzy i konfiguruje instancję aplikacji Flask.
    :param config_name: Nazwa konfiguracji do użycia (np. 'development', 'production').
    """
    app = Flask(__name__, template_folder='templates')
    config_object = config_by_name.get(config_name)
    app.config.from_object(config_by_name[config_name])

    # --- Pobieranie klucza API z Secret Managera ---
    api_key = None
    # Definiujemy zmienne przed blokiem try, aby były dostępne w blokach except
    project_id = app.config.get('GCP_PROJECT_ID')
    secret_name = app.config.get('GEMINI_API_KEY_SECRET_NAME')

    try: # Ten blok jest najczęstszym źródłem błędów przy starcie.
        if not project_id:
            raise ValueError("Zmienna środowiskowa GCP_PROJECT_ID nie jest ustawiona.")

        secret_version = app.config.get('GEMINI_API_KEY_SECRET_VERSION')

        # Inicjalizacja klienta i pobranie sekretu
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/{secret_version}"
        
        logger.info(f"Pobieranie sekretu: {name}")
        response = client.access_secret_version(request={"name": name})
        api_key = response.payload.data.decode("UTF-8")
        logger.info("Pomyślnie pobrano klucz API Gemini z Secret Managera.")

    except DefaultCredentialsError:
        logger.error("Błąd uwierzytelnienia (DefaultCredentialsError).", exc_info=True)
        logger.warning("Upewnij się, że jesteś uwierzytelniony. Uruchom 'gcloud auth application-default login' w terminalu.")
        api_key = None
    except PermissionDenied:
        logger.error("Brak uprawnień (PermissionDenied) do odczytu sekretu.", exc_info=True)
        logger.warning(f"Sprawdź, czy konto serwisowe ma rolę 'Secret Manager Secret Accessor' dla sekretu '{secret_name}'.")
        api_key = None
    except NotFound:
        logger.error("Nie znaleziono sekretu (NotFound).", exc_info=True)
        logger.warning(f"Sprawdź, czy sekret '{secret_name}' na pewno istnieje w projekcie '{project_id}'.")
        api_key = None
    except Exception as e:
        logger.error(f"Wystąpił nieoczekiwany błąd podczas łączenia z Secret Manager: {e}", exc_info=True)
        api_key = None

    # --- Konfiguracja modelu Gemini ---
    if api_key:
        genai.configure(api_key=api_key)
        # POPRAWKA: Zaktualizowano nazwę modelu do najnowszej stabilnej wersji.
        model_name = 'gemini-1.5-pro-latest'
        app.model = genai.GenerativeModel(model_name)
        logger.info(f"Model Gemini ('{model_name}') został pomyślnie skonfigurowany.")
    else:
        app.model = None
        logger.warning("Model Gemini NIE został skonfigurowany z powodu braku klucza API.")

    # --- Rejestracja tras ---
  # --- Rejestracja tras ---

    @app.route("/health")
    def health_check():
        """Prosty endpoint 'health check' do sprawdzania, czy serwer działa."""
        return jsonify({"status": "ok", "message": "Serwer Gemini-Flask działa!"})

    # Import i rejestracja blueprintu dla głównej strony (interfejsu czatu)
    from .routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    # Import i rejestracja blueprintu dla tras Gemini
    from .routes.gemini_routes import gemini_bp
    app.register_blueprint(gemini_bp)

    return app