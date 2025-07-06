# Użyj oficjalnego, lekkiego obrazu Python jako obrazu bazowego
FROM python:3.10-slim

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj plik z zależnościami do katalogu roboczego
COPY requirements.txt .

# Zainstaluj zależności, nie tworząc cache, aby obraz był mniejszy
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę kodu aplikacji do katalogu roboczego
COPY . .

# Wystaw port, na którym aplikacja będzie nasłuchiwać
EXPOSE 8080

# Komenda do uruchomienia aplikacji przy starcie kontenera
# Używamy Gunicorn jako serwera produkcyjnego WSGI, wskazując na fabrykę aplikacji
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()"]