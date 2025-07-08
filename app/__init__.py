from flask import Flask, jsonify
import google.generativeai as genai
import os

from google.cloud import secretmanager
from google.api_core.exceptions import PermissionDenied, NotFound
from google.auth.exceptions import DefaultCredentialsError
from .config import config_by_name
from .logging_config import logger

def _get_api_key_from_secret_manager(config: object) -> str | None:
    """
    Prywatna funkcja pomocnicza do pobierania klucza API z Google Secret Manager.
    Hermetyzuje całą logikę i obsługę błędów.
    
    :param config: Obiekt konfiguracji aplikacji Flaska.
    :return: Klucz API jako string lub None w przypadku błędu.
    """
    project_id = config.get('GCP_PROJECT_ID')
    secret_name = config.get('GEMINI_API_KEY_SECRET_NAME')
    secret_version = config.get('GEMINI_API_KEY_SECRET_VERSION')

    if not project_id:
        logger.error("GCP_PROJECT_ID nie jest ustawione w konfiguracji. Nie można pobrać sekretu.")
        return None

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/{secret_version}"
        
        logger.info(f"Pobieranie sekretu: {name}")
        response = client.access_secret_version(request={"name": name})
        api_key = response.payload.data.decode("UTF-8")
        logger.info("Pomyślnie pobrano klucz API Gemini z Secret Managera.")
        return api_key

    except DefaultCredentialsError:
        logger.error("Błąd uwierzytelnienia (DefaultCredentialsError). Uruchom 'gcloud auth application-default login'.", exc_info=True)
    except PermissionDenied:
        logger.error(f"Brak uprawnień (PermissionDenied) do odczytu sekretu '{secret_name}'.", exc_info=True)
        logger.warning("Sprawdź, czy konto serwisowe ma rolę 'Secret Manager Secret Accessor'.")
    except NotFound:
        logger.error(f"Nie znaleziono sekretu '{secret_name}' w projekcie '{project_id}'.", exc_info=True)
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd podczas łączenia z Secret Manager: {e}", exc_info=True)
    
    return None


def create_app(config_name: str = 'default') -> Flask:
    """
    Fabryka aplikacji - tworzy i konfiguruje instancję aplikacji Flask.
    :param config_name: Nazwa konfiguracji do użycia (np. 'development', 'production').
    """
    app = Flask(__name__, template_folder='templates')
    config_object = config_by_name.get(config_name)
    app.config.from_object(config_object)

    # --- Pobieranie klucza API z Secret Managera ---
    api_key = _get_api_key_from_secret_manager(app.config)

    # --- Konfiguracja modelu Gemini ---
    if api_key:
        genai.configure(api_key=api_key)
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