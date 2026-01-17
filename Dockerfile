# syntax=docker/dockerfile:1

# Usar imagen base de Python con soporte multiplataforma
# Soporta: linux/amd64, linux/arm64, linux/arm/v7
FROM --platform=$BUILDPLATFORM python:3.10-slim AS builder

# Argumentos de plataforma para build multiplataforma
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Imagen final
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos del backend
COPY backend/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY backend/app.py .

# Copiar los archivos del frontend (templates y static)
COPY frontend/templates ./templates
COPY frontend/static ./static

# Crear directorio para datos persistentes
RUN mkdir -p /app/data

# Exponer puerto 8000
EXPOSE 8000

# Variables de entorno
ENV FLASK_ENV=production
ENV DATABASE_PATH=/app/data/vocational_test.db

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
