# Stage 1: Base
FROM python:3.11-slim as base

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies
FROM base as dependencies

# Copier requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 3: Development (avec hot-reload via runserver)
FROM dependencies as development

# Le code source sera monté via volume en dev
# Pas besoin de COPY . . ici

# Exposer le port
EXPOSE 8000

# Commande par défaut (peut être overridée dans docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Stage 4: Production
FROM dependencies as production

# Copier le code de l'application
COPY . .

# Créer un utilisateur non-root
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Créer le dossier logs
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Exposer le port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')" || exit 1

# Commande par défaut (sera overridée par docker-compose)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
