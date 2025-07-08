# Użyj oficjalnego, lekkiego obrazu Python z przypiętą wersją dla powtarzalności i bezpieczeństwa
FROM python:3.10-slim@sha256:a4163914b5ab027218525396f1349f2b0a8807b190983e5455c51482880e69de

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Stwórz dedykowanego użytkownika i grupę dla aplikacji, aby unikać uruchamiania jako root
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Skopiuj plik z zależnościami do katalogu roboczego
COPY requirements.txt .

# Zainstaluj zależności, nie tworząc cache, aby obraz był mniejszy
RUN pip install --no-cache-dir -r requirements.txt

# Zmień właściciela plików aplikacji na nowo utworzonego użytkownika
COPY . .
RUN chown -R appuser:appuser /app

# Skopiuj resztę kodu aplikacji do katalogu roboczego

# Przełącz na użytkownika non-root
USER appuser

# Wystaw port, na którym aplikacja będzie nasłuchiwać
EXPOSE 8080

# Komenda do uruchomienia aplikacji przy starcie kontenera
# Używamy Gunicorn jako serwera produkcyjnego WSGI, wskazując na fabrykę aplikacji
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()"]