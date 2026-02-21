"""
Controlador para carreras
"""
import logging
from flask import jsonify, make_response
from services.career_service import CareerService
from utils.errors import NotFoundError


logger = logging.getLogger(__name__)


class CareerController:
    """Controlador para operaciones de carreras"""
    
    @staticmethod
    def get_careers_list():
        """
        Endpoint GET /api/careers/list
        Obtiene lista básica de carreras (id, nombre, icono, descripción)
        Para la página de listado - más liviano
        Cache: 1 hora en navegador
        """
        try:
            careers = CareerService.get_careers_list()
            
            response = make_response(jsonify({
                'success': True,
                'careers': careers
            }))
            
            response.headers['Cache-Control'] = 'public, max-age=3600'
            return response
        except Exception as e:
            logger.error(f"Error obteniendo lista de carreras: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo carreras'
            }), 500
    
    @staticmethod
    def get_career_detail(career_id: int):
        """
        Endpoint GET /api/careers/<id>/detail
        Obtiene detalle completo de una carrera (skills, jobs, etc.)
        Cache: 6 horas (menos frecuencia de cambio que el listado)
        """
        try:
            career = CareerService.get_career_detail(career_id)
            
            if not career:
                return jsonify({
                    'success': False,
                    'message': 'Carrera no encontrada'
                }), 404
            
            response = make_response(jsonify({
                'success': True,
                'career': career
            }))
            
            response.headers['Cache-Control'] = 'public, max-age=21600'  # 6 horas
            return response
        except Exception as e:
            logger.error(f"Error obteniendo detalle de carrera: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo carrera'
            }), 500
    
    @staticmethod
    def get_all_careers():
        """
        Endpoint GET /api/careers
        Obtiene todas las carreras
        Cache: 1 hora en navegador
        """
        try:
            careers = CareerService.get_all_careers()
            
            response = make_response(jsonify({
                'success': True,
                'careers': careers
            }))
            
            response.headers['Cache-Control'] = 'public, max-age=3600'
            return response
        except Exception as e:
            logger.error(f"Error obteniendo carreras: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo carreras'
            }), 500
    
    @staticmethod
    def get_all_careers_full():
        """
        Endpoint GET /api/careers/all
        Obtiene TODAS las carreras con TODOS sus datos (skills + jobs)
        Para cachear en frontend y evitar múltiples llamadas
        
        Cache: 1 hora en navegador + 24 horas en CDN (si existe)
        """
        try:
            careers = CareerService.get_all_careers_full()
            
            response = make_response(jsonify({
                'success': True,
                'careers': careers
            }))
            
            # Headers de caché HTTP para navegador y CDN
            response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hora en navegador
            response.headers['ETag'] = f'"{hash(str(careers))}"'  # Para validación de caché
            response.headers['Expires'] = 'Thu, 01 Dec 2099 16:00:00 GMT'  # Fallback
            
            logger.info("✓ Carreras completas servidas (cacheado 1 hora en navegador)")
            return response
        except Exception as e:
            logger.error(f"Error obteniendo carreras completas: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo carreras'
            }), 500
    
    @staticmethod
    def get_career(career_id: int):
        """
        Endpoint GET /api/careers/<id>
        Obtiene una carrera específica
        Cache: 6 horas
        """
        try:
            career = CareerService.get_career_by_id(career_id)
            
            if not career:
                return jsonify({
                    'success': False,
                    'message': 'Carrera no encontrada'
                }), 404
            
            response = make_response(jsonify({
                'success': True,
                'career': career
            }))
            
            response.headers['Cache-Control'] = 'public, max-age=21600'  # 6 horas
            return response
        except Exception as e:
            logger.error(f"Error obteniendo carrera: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo carrera'
            }), 500    
    @staticmethod
    def clear_cache():
        """
        Endpoint POST /api/careers/clear-cache
        Limpia el cache del servidor para recargar datos de la BD
        """
        try:
            CareerService.clear_cache()
            return jsonify({
                'success': True,
                'message': 'Cache limpiado exitosamente'
            })
        except Exception as e:
            logger.error(f"Error limpiando cache: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error limpiando cache'
            }), 500