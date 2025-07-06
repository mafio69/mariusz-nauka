import os

class Config:
    """Podstawowa, bazowa konfiguracja."""
    # Klucz sekretny Flaska, używany np. do sesji. Dobra praktyka, aby go mieć.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'domyslny-bardzo-sekretny-klucz')
    DEBUG = False
    TESTING = False

    # Konfiguracja specyficzna dla naszej aplikacji
    GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
    GEMINI_API_KEY_SECRET_NAME = os.environ.get('GEMINI_API_KEY_SECRET_NAME', 'gemini-api-key')
    GEMINI_API_KEY_SECRET_VERSION = os.environ.get('GEMINI_API_KEY_SECRET_VERSION', 'latest')

class DevelopmentConfig(Config):
    """Konfiguracja dla środowiska deweloperskiego."""
    DEBUG = True

class ProductionConfig(Config):
    """Konfiguracja dla środowiska produkcyjnego."""
    # W produkcji DEBUG musi być wyłączony
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}