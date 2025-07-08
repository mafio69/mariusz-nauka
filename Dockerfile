# Użyj oficjalnego, lekkiego obrazu Python z przypiętą wersją dla powtarzalności i bezpieczeństwa
# Użyj oficjalnego, lekkiego obrazu Pythona jako bazy.
FROM python:3.11-slim
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