# Użyj oficjalnego, lekkiego obrazu Pythona jako obrazu bazowego
FROM python:3.11-slim
# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Stwórz dedykowanego użytkownika i grupę dla aplikacji, aby unikać uruchamiania jako root
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Zainstaluj curl dla HEALTHCHECK i wyczyść cache apt, aby utrzymać mały rozmiar obrazu
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Skopiuj plik z zależnościami do katalogu roboczego
COPY requirements.txt .

# Zainstaluj zależności, nie tworząc cache, aby obraz był mniejszy
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę kodu aplikacji do katalogu roboczego i ustaw odpowiedniego właściciela
# Użycie --chown jest bardziej wydajne niż osobna komenda RUN chown
COPY --chown=appuser:appuser . .

# Przełącz na użytkownika non-root
USER appuser

# Wystaw port, na którym aplikacja będzie nasłuchiwać
EXPOSE 8080

# Dodaj healthcheck, aby umożliwić systemom orkiestracji (np. Kubernetes) monitorowanie stanu aplikacji
# Pamiętaj o zaimplementowaniu endpointu /health w swojej aplikacji, który zwraca status 200 OK.
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Komenda do uruchomienia aplikacji przy starcie kontenera
# Używamy Gunicorn jako serwera produkcyjnego WSGI, wskazując na fabrykę aplikacji
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()"]