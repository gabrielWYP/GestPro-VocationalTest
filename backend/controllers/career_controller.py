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
