#!/bin/bash

# Script de instalación rápida del Test de Orientación Vocacional

echo "🎯 Test de Orientación Vocacional - Instalación Rápida"
echo "========================================================="
echo ""

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor, instala Docker primero."
    echo "Descarga desde: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✓ Docker detectado"
echo ""

# Ir al directorio del proyecto
cd /mnt/tesis_data/codigo/vocational_test

# Construir la imagen
echo "🔨 Construyendo imagen Docker..."
docker build -t vocational-test:latest . --quiet

if [ $? -eq 0 ]; then
    echo "✓ Imagen construida exitosamente"
else
    echo "❌ Error al construir la imagen"
    exit 1
fi

echo ""
echo "🚀 Iniciando contenedor..."

# Verificar si el contenedor ya existe y detenerlo
if [ "$(docker ps -aq -f name=vocational-test-container)" ]; then
    echo "  Deteniendo contenedor anterior..."
    docker stop vocational-test-container > /dev/null
    docker rm vocational-test-container > /dev/null
fi

# Iniciar el contenedor
docker run -d -p 80:80 --name vocational-test-container vocational-test:latest > /dev/null

if [ $? -eq 0 ]; then
    sleep 2
    echo "✓ Contenedor iniciado exitosamente"
else
    echo "❌ Error al iniciar el contenedor"
    exit 1
fi

echo ""
echo "========================================================="
echo "✨ ¡La aplicación está lista!"
echo "========================================================="
echo ""
echo "📍 Accede a: http://localhost"
echo ""
echo "Comandos útiles:"
echo "  ./manage.sh start   - Iniciar la aplicación"
echo "  ./manage.sh stop    - Detener la aplicación"
echo "  ./manage.sh logs    - Ver los logs"
echo "  ./manage.sh status  - Ver estado"
echo ""
echo "Página principal: http://localhost"
echo "Página de carreras: http://localhost/careers"
echo "Test: http://localhost/test"
echo "Asesoría: http://localhost/advisory"
echo ""
