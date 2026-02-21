#!/usr/bin/env python3
"""
Script para ver todas las imágenes disponibles en OCI Object Storage
Usa la URL de preautenticación del .env
"""

import os
import sys
from urllib.parse import urljoin
from pathlib import Path

# Cargar variables de entorno manualmente
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

try:
    import requests
except ImportError:
    print("❌ Error: requests no está instalado")
    print("Instala con: pip install requests")
    sys.exit(1)

OCI_PREAUTH_URL_READ = os.getenv('OCI_PREAUTH_URL_READ')

def get_oci_images():
    """
    Obtiene la lista de todas las imágenes en el bucket OCI
    """
    if not OCI_PREAUTH_URL_READ:
        print("❌ Error: OCI_PREAUTH_URL_READ no está configurado en el .env")
        return []
    
    try:
        print("📡 Conectando a OCI Object Storage...")
        print(f"🔗 URL: {OCI_PREAUTH_URL_READ}")
        
        # Realizar petición para listar objetos
        response = requests.get(OCI_PREAUTH_URL_READ, timeout=10)
        response.raise_for_status()
        
        # Parsear respuesta XML
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        
        # Extraer información de los objetos
        images = []
        namespace = {'s3': 'http://s3.amazonaws.com/doc/2006-03-01/'}
        
        for obj in root.findall('.//s3:Contents', namespace):
            name_elem = obj.find('s3:Key', namespace)
            size_elem = obj.find('s3:Size', namespace)
            modified_elem = obj.find('s3:LastModified', namespace)
            
            if name_elem is not None:
                images.append({
                    'name': name_elem.text,
                    'size': int(size_elem.text) if size_elem is not None else 0,
                    'modified': modified_elem.text if modified_elem is not None else 'N/A',
                    'url': urljoin(OCI_PREAUTH_URL_READ, name_elem.text)
                })
        
        return images
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return []
    except Exception as e:
        print(f"❌ Error procesando datos: {e}")
        return []


def format_size(bytes_size):
    """Convierte bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"


def display_images(images):
    """Muestra las imágenes en formato tabla"""
    if not images:
        print("\n⚠️  No se encontraron imágenes")
        return
    
    print(f"\n✅ Se encontraron {len(images)} archivo(s):\n")
    print("=" * 100)
    print(f"{'Nombre':<50} {'Tamaño':<15} {'Última Modificación':<20} {'Url Descarga':<15}")
    print("=" * 100)
    
    for img in images:
        name = img['name'][:47] + "..." if len(img['name']) > 50 else img['name']
        size = format_size(img['size'])
        modified = img['modified'][:19] if img['modified'] != 'N/A' else 'N/A'
        
        print(f"{name:<50} {size:<15} {modified:<20} {'✓':<15}")
    
    print("=" * 100)
    print(f"\nTamaño total: {format_size(sum(img['size'] for img in images))}")


def download_image(images, index, output_dir="./descargas"):
    """Descarga una imagen específica"""
    if index < 0 or index >= len(images):
        print(f"❌ Índice inválido: {index}")
        return
    
    image = images[index]
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print(f"\n📥 Descargando: {image['name']}...")
        response = requests.get(image['url'], timeout=30)
        response.raise_for_status()
        
        file_path = os.path.join(output_dir, image['name'].split('/')[-1])
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Descargado exitosamente: {file_path}")
    except Exception as e:
        print(f"❌ Error descargando: {e}")


def main():
    """Función principal"""
    print("\n" + "="*50)
    print("🖼️  VISOR DE IMÁGENES - OCI Object Storage")
    print("="*50)
    
    images = get_oci_images()
    display_images(images)
    
    if images:
        print("\n💡 Opciones:")
        print("  - Para descargar una imagen: python view_images.py download <número>")
        print("  - Ejemplo: python view_images.py download 0")
        
        # Manejo de argumentos para descargar
        if len(sys.argv) > 1:
            if sys.argv[1].lower() == 'download' and len(sys.argv) > 2:
                try:
                    idx = int(sys.argv[2])
                    download_image(images, idx)
                except ValueError:
                    print(f"❌ Índice inválido: {sys.argv[2]}")


if __name__ == "__main__":
    main()
