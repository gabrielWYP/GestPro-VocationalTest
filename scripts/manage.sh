#!/bin/bash

# Script para administrar la aplicación de Test de Orientación Vocacional

case "$1" in
    start)
        echo "🚀 Iniciando la aplicación..."
        cd /mnt/tesis_data/codigo/vocational_test
        docker run -d -p 80:80 --name vocational-test-container vocational-test:latest
        echo "✓ Aplicación iniciada en http://localhost"
        ;;
    stop)
        echo "⛔ Deteniendo la aplicación..."
        docker stop vocational-test-container
        docker rm vocational-test-container
        echo "✓ Aplicación detenida"
        ;;
    restart)
        echo "🔄 Reiniciando la aplicación..."
        docker restart vocational-test-container
        echo "✓ Aplicación reiniciada"
        ;;
    logs)
        echo "📋 Mostrando logs..."
        docker logs -f vocational-test-container
        ;;
    build)
        echo "🔨 Construyendo imagen Docker..."
        cd /mnt/tesis_data/codigo/vocational_test
        docker build -t vocational-test:latest .
        echo "✓ Imagen construida"
        ;;
    rebuild)
        echo "🔨 Reconstruyendo y reiniciando..."
        docker stop vocational-test-container 2>/dev/null
        docker rm vocational-test-container 2>/dev/null
        cd /mnt/tesis_data/codigo/vocational_test
        docker build -t vocational-test:latest .
        docker run -d -p 80:80 --name vocational-test-container vocational-test:latest
        echo "✓ Aplicación reconstruida y reiniciada"
        ;;
    status)
        echo "📊 Estado de la aplicación:"
        docker ps | grep vocational-test || echo "No hay contenedor ejecutándose"
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|logs|build|rebuild|status}"
        echo ""
        echo "Comandos disponibles:"
        echo "  start    - Inicia la aplicación"
        echo "  stop     - Detiene la aplicación"
        echo "  restart  - Reinicia la aplicación"
        echo "  logs     - Muestra los logs"
        echo "  build    - Construye la imagen Docker"
        echo "  rebuild  - Reconstruye y reinicia todo"
        echo "  status   - Muestra el estado de la aplicación"
        ;;
esac
