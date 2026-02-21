"""
Controlador de Upload
Maneja las peticiones HTTP de subida de archivos a OCI
"""
import logging
from flask import request, jsonify
from services.upload_service import UploadService
from utils.errors import ValidationError

logger = logging.getLogger(__name__)


class UploadController:
    """Controlador para subida de archivos"""
    
    @staticmethod
    def upload_image():
        """
        Endpoint POST /upload/image
        Sube una imagen a Oracle Cloud Infrastructure
        
        Multipart/form-data:
        - file: archivo de imagen (jpg, png, gif, webp, svg)
        
        Returns:
            JSON con información del archivo subido
        """
        try:
            # Verificar que hay archivo en la request
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'No se envió ningún archivo'
                }), 400
            
            file = request.files['file']
            
            # Verificar que el archivo tiene nombre
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'Archivo sin nombre'
                }), 400
            
            # Leer el contenido del archivo
            file_content = file.read()
            file_size = len(file_content)
            
            # Validar imagen
            try:
                UploadService.validate_image(file.filename, file_size)
            except ValidationError as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 400
            
            # Obtener el content type del archivo
            content_type = file.content_type
            
            # Subir archivo a OCI
            result = UploadService.upload_to_oci(
                file_content=file_content,
                filename=file.filename,
                content_type=content_type
            )
            
            logger.info(f"✓ Imagen subida: {result['filename']}")
            
            return jsonify(result), 201
            
        except ValidationError as e:
            logger.warning(f"Error de validación en upload: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except Exception as e:
            logger.error(f"Error en upload: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error al subir el archivo'
            }), 500
    
    @staticmethod
    def upload_multiple_images():
        """
        Endpoint POST /upload/images
        Sube múltiples imágenes a Oracle Cloud Infrastructure
        
        Multipart/form-data:
        - files[]: array de archivos de imagen
        
        Returns:
            JSON con información de todos los archivos subidos
        """
        try:
            # Verificar que hay archivos en la request
            if 'files[]' not in request.files and 'files' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron archivos'
                }), 400
            
            # Obtener los archivos (intenta ambos nombres de campo)
            files = request.files.getlist('files[]') or request.files.getlist('files')
            
            if not files or len(files) == 0:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron archivos'
                }), 400
            
            # Limitar número de archivos
            MAX_FILES = 10
            if len(files) > MAX_FILES:
                return jsonify({
                    'success': False,
                    'message': f'Máximo {MAX_FILES} archivos por request'
                }), 400
            
            uploaded_files = []
            errors = []
            
            # Procesar cada archivo
            for idx, file in enumerate(files):
                try:
                    if file.filename == '':
                        errors.append({
                            'index': idx,
                            'error': 'Archivo sin nombre'
                        })
                        continue
                    
                    # Leer contenido
                    file_content = file.read()
                    file_size = len(file_content)
                    
                    # Validar
                    UploadService.validate_image(file.filename, file_size)
                    
                    # Subir
                    result = UploadService.upload_to_oci(
                        file_content=file_content,
                        filename=file.filename,
                        content_type=file.content_type
                    )
                    
                    uploaded_files.append(result)
                    logger.info(f"✓ Imagen {idx+1}/{len(files)} subida: {result['filename']}")
                    
                except ValidationError as e:
                    errors.append({
                        'index': idx,
                        'filename': file.filename,
                        'error': str(e)
                    })
                except Exception as e:
                    errors.append({
                        'index': idx,
                        'filename': file.filename,
                        'error': f'Error al subir: {str(e)}'
                    })
            
            # Preparar respuesta
            response = {
                'success': len(uploaded_files) > 0,
                'uploaded': len(uploaded_files),
                'failed': len(errors),
                'files': uploaded_files
            }
            
            if errors:
                response['errors'] = errors
            
            status_code = 201 if len(uploaded_files) > 0 else 400
            
            return jsonify(response), status_code
            
        except Exception as e:
            logger.error(f"Error en upload múltiple: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error al procesar los archivos'
            }), 500
