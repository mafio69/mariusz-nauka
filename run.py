# /home/mf1969/mariusz-nauka/run.py
# Główny punkt startowy aplikacji do uruchamiania lokalnego serwera deweloperskiego.

import os
from dotenv import load_dotenv
from app.logging_config import logger
from app import create_app

# Jawne załadowanie zmiennych z pliku .env.
# To dobra praktyka, aby upewnić się, że konfiguracja jest dostępna
# od samego początku, niezależnie od sposobu uruchomienia skryptu.
load_dotenv()

# Odczytaj konfigurację ze zmiennej środowiskowej lub użyj domyślnej ('development')
config_name = os.getenv('FLASK_CONFIG', 'development')

# Tworzymy instancję aplikacji za pomocą naszej fabryki
app = create_app(config_name)

if __name__ == "__main__":
    # Ten blok jest wykonywany tylko przy bezpośrednim uruchomieniu `python run.py`.
    # W środowisku produkcyjnym serwer WSGI (np. Gunicorn) importuje obiekt `app`
    # i uruchamia go samodzielnie, ignorując ten fragment kodu.

    # Użyj zmiennych środowiskowych do konfiguracji hosta i portu, z rozsądnymi domyślnymi.
    # Jest to standard w aplikacjach chmurowych (np. Cloud Run).
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    debug_mode = app.config.get('DEBUG', False)
    logger.info(f"Uruchamianie serwera w trybie '{config_name}' (debug={debug_mode}) na http://{host}:{port}")
    app.run(host=host, port=port, debug=debug_mode)
