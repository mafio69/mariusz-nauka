import os
from app import create_app
from app.logging_config import logger

# Odczytaj konfigurację ze zmiennej środowiskowej lub użyj domyślnej ('development')
config_name = os.getenv('FLASK_CONFIG', 'development')

# Tworzymy instancję aplikacji za pomocą naszej fabryki
app = create_app(config_name)

if __name__ == "__main__":
    # Uruchamiamy serwer deweloperski Flaska.
    # Używamy ustawień z załadowanej konfiguracji, aby zachować spójność.
    # Pozwala to na łatwe przełączanie trybu debugowania przez zmienną FLASK_CONFIG.
    host = '0.0.0.0'
    port = 8080
    debug_mode = app.config.get('DEBUG', False)
    logger.info(f"Uruchamianie serwera w trybie '{config_name}' (debug={debug_mode}) na http://{host}:{port}")
    app.run(host=host, port=port, debug=debug_mode)
