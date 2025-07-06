import logging
import sys

# 1. Pobierz instancję loggera. Używanie tej samej nazwy w całej aplikacji
#    zapewni, że używasz tej samej, skonfigurowanej instancji.
logger = logging.getLogger('moja_aplikacja')
logger.setLevel(logging.DEBUG) # Ustaw najniższy poziom, który ma być przechwytywany

# 2. Stwórz formatter, aby logi były czytelne i spójne
#    Format: Czas - Nazwa loggera - [POZIOM] - Wiadomość
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 3. Skonfiguruj handler do konsoli (dla wszystkich logów od poziomu DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# 4. Skonfiguruj handler do pliku (tylko dla poważnych błędów od poziomu ERROR)
file_handler = logging.FileHandler('logs/errors.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

# 5. Dodaj handlery do loggera.
#    Ten warunek jest kluczowy, aby uniknąć duplikowania logów,
#    jeśli ten moduł zostanie zaimportowany wielokrotnie.
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)