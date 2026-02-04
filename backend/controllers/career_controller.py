"""
Controlador para carreras
"""
import logging
from flask import jsonify
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
        """
        try:
            careers = CareerService.get_careers_list()
            return jsonify({
                'success': True,
                'careers': careers
            })
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
        """
        try:
            career = CareerService.get_career_detail(career_id)
            
            if not career:
                return jsonify({
                    'success': False,
                    'message': 'Carrera no encontrada'
                }), 404
            
            return jsonify({
                'success': True,
                'career': career
            })
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
        """
        try:
            careers = CareerService.get_all_careers()
            return jsonify({
                'success': True,
                'careers': careers
            })
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
        """
        try:
            careers = CareerService.get_all_careers_full()
            return jsonify({
                'success': True,
                'careers': careers
            })
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
        """
        try:
            career = CareerService.get_career_by_id(career_id)
            
            if not career:
                return jsonify({
                    'success': False,
                    'message': 'Carrera no encontrada'
                }), 404
            
            return jsonify({
                'success': True,
                'career': career
            })
        except Exception as e:
            logger.error(f"Error obteniendo carrera: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo carrera'
            }), 500
