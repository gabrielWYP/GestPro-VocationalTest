# syntax=docker/dockerfile:1

# Usar imagen base de Python con soporte multiplataforma
# Soporta: linux/amd64, linux/arm64
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos del backend
COPY backend/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar el código del backend
COPY backend/ .

# Copiar los archivos del frontend (templates y static)
COPY frontend/templates ./templates
COPY frontend/static ./static

# Crear usuario no-root por seguridad
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Crear directorio para datos persistentes
RUN mkdir -p /app/data

# Exponer puerto 8000
EXPOSE 8000

# Variables de entorno
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/app/data/vocational_test.db

# Comando para ejecutar la aplicación con Gunicorn
# 4 workers para ~5 usuarios concurrentes, 2 threads por worker
CMD ["gunicorn", "--workers=4", "--threads=2", "--worker-class=gthread", "--bind=0.0.0.0:8000", "--timeout=30", "--access-logfile=-", "app:app"]
