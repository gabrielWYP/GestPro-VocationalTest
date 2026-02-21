"""
Servicio para subir archivos a Oracle Cloud Infrastructure (OCI)
Usa URL pre-autenticada para subir imágenes al bucket
"""
import logging
import os
import uuid
import mimetypes
from datetime import datetime
import requests
from config import OCI_PREAUTH_URL
from utils.errors import ValidationError

logger = logging.getLogger(__name__)


class UploadService:
    """Servicio para manejar subida de archivos a OCI"""
    
    # Extensiones de imagen permitidas
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
    
    # Tamaño máximo de archivo: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @staticmethod
    def validate_image(filename, file_size):
        """
        Valida que el archivo sea una imagen válida
        
        Args:
            filename (str): Nombre del archivo
            file_size (int): Tamaño del archivo en bytes
            
        Raises:
            ValidationError: Si el archivo no es válido
        """
        if not filename:
            raise ValidationError("Nombre de archivo vacío")
        
        # Validar extensión
        ext = os.path.splitext(filename.lower())[1]
        if ext not in UploadService.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Extensión no permitida. Solo se permiten: {', '.join(UploadService.ALLOWED_EXTENSIONS)}"
            )
        
        # Validar tamaño
        if file_size > UploadService.MAX_FILE_SIZE:
            max_mb = UploadService.MAX_FILE_SIZE / (1024 * 1024)
            raise ValidationError(f"Archivo muy grande. Tamaño máximo: {max_mb}MB")
        
        return True
    
    @staticmethod
    def generate_unique_filename(original_filename):
        """
        Genera un nombre único para el archivo
        
        Args:
            original_filename (str): Nombre original del archivo
            
        Returns:
            str: Nombre único con timestamp y UUID
        """
        ext = os.path.splitext(original_filename.lower())[1]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}{ext}"
    
    @staticmethod
    def upload_to_oci(file_content, filename, content_type=None):
        """
        Sube un archivo a OCI usando URL pre-autenticada
        
        Args:
            file_content (bytes): Contenido del archivo
            filename (str): Nombre del archivo
            content_type (str, optional): Tipo MIME del archivo
            
        Returns:
            dict: Información sobre el archivo subido
            
        Raises:
            ValidationError: Si hay error en la validación
            Exception: Si hay error en la subida
        """
        try:
            # Validar que existe la URL de OCI
            if not OCI_PREAUTH_URL:
                raise ValidationError("URL de OCI no configurada en variables de entorno")
            
            # Generar nombre único
            unique_filename = UploadService.generate_unique_filename(filename)
            
            # Determinar content type si no se proporciona
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'
            
            # Construir URL completa
            upload_url = f"{OCI_PREAUTH_URL}{unique_filename}"
            
            # Headers para la petición
            headers = {
                'Content-Type': content_type
            }
            
            logger.info(f"Subiendo archivo: {unique_filename} ({len(file_content)} bytes)")
            
            # Hacer PUT request para subir el archivo
            response = requests.put(
                upload_url,
                data=file_content,
                headers=headers,
                timeout=30
            )
            
            # Verificar respuesta
            if response.status_code in [200, 201]:
                logger.info(f"✓ Archivo subido exitosamente: {unique_filename}")
                
                # URL pública del archivo (sin query params de auth)
                public_url = upload_url.split('?')[0] if '?' in upload_url else upload_url
                
                return {
                    'success': True,
                    'filename': unique_filename,
                    'original_filename': filename,
                    'url': public_url,
                    'size': len(file_content),
                    'content_type': content_type,
                    'uploaded_at': datetime.now().isoformat()
                }
            else:
                logger.error(f"Error subiendo archivo. Status: {response.status_code}, Response: {response.text}")
                raise Exception(f"Error al subir archivo: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión al subir archivo: {str(e)}")
            raise Exception(f"Error de conexión: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado al subir archivo: {str(e)}")
            raise
    
    @staticmethod
    def delete_from_oci(filename):
        """
        Elimina un archivo de OCI (requeriría autenticación adicional)
        
        Nota: Las URLs pre-autenticadas normalmente solo permiten PUT/GET,
        no DELETE. Esta función requeriría configuración adicional con
        credenciales de OCI.
        
        Args:
            filename (str): Nombre del archivo a eliminar
            
        Returns:
            dict: Resultado de la operación
        """
        logger.warning("La eliminación de archivos requiere autenticación adicional de OCI")
        raise NotImplementedError(
            "La eliminación requiere configurar credenciales de OCI completas"
        )
