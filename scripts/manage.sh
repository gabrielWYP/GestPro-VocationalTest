#!/bin/bash

# Script para administrar la aplicación de Test de Orientación Vocacional

CONTAINER_NAME="${2:-vocational-test-container}"
IMAGE_NAME="${3:-vocational-test:latest}"
APP_PATH="/mnt/tesis_data/codigo/vocational_test"

case "$1" in
    start)
        echo "🚀 Iniciando la aplicación..."
        cd "$APP_PATH"
        docker run -d -p 80:80 --name "$CONTAINER_NAME" "$IMAGE_NAME"
        echo "✓ Aplicación iniciada en http://localhost"
        ;;
    stop)
        echo "⛔ Deteniendo la aplicación..."
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        echo "✓ Aplicación detenida"
        ;;
    restart)
        echo "🔄 Reiniciando la aplicación..."
        docker restart "$CONTAINER_NAME"
        echo "✓ Aplicación reiniciada"
        ;;
    logs)
        echo "📋 Mostrando logs..."
        docker logs -f "$CONTAINER_NAME"
        ;;
    build)
        echo "🔨 Construyendo imagen Docker..."
        cd "$APP_PATH"
        docker buildx build -t "$IMAGE_NAME" .
        echo "✓ Imagen construida"
        ;;
    rebuild)
        echo "🔨 Reconstruyendo y reiniciando..."
        docker stop "$CONTAINER_NAME" 2>/dev/null
        docker rm "$CONTAINER_NAME" 2>/dev/null
        cd "$APP_PATH"
        docker buildx build -t "$IMAGE_NAME" .
        docker run -d -p 80:80 --name "$CONTAINER_NAME" "$IMAGE_NAME"
        echo "✓ Aplicación reconstruida y reiniciada"
        ;;
    status)
        echo "📊 Estado de la aplicación:"
        docker ps | grep "$CONTAINER_NAME" || echo "No hay contenedor ejecutándose"
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|logs|build|rebuild|status} [container_name] [image_name]"
        echo ""
        echo "Comandos disponibles:"
        echo "  start    - Inicia la aplicación"
        echo "  stop     - Detiene la aplicación"
        echo "  restart  - Reinicia la aplicación"
        echo "  logs     - Muestra los logs"
        echo "  build    - Construye la imagen Docker"
        echo "  rebuild  - Reconstruye y reinicia todo"
        echo "  status   - Muestra el estado de la aplicación"
        echo ""
        echo "Parámetros opcionales:"
        echo "  container_name - Nombre del contenedor (default: vocational-test-container)"
        echo "  image_name     - Nombre de la imagen (default: vocational-test:latest)"
        ;;
esac
