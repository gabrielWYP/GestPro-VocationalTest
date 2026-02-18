"""
Controlador para predicciones de carreras
Expone endpoint /api/predict-careers
"""
import logging
from flask import request, jsonify, session
from services.predictions_service import PredictionsService
from utils.errors import DatabaseError

logger = logging.getLogger(__name__)


class PredictionsController:
    """Controlador para predicciones"""
    
    @staticmethod
    def predict_careers():
        """
        Endpoint POST /api/predict-careers
        Predice carreras para el usuario logueado basado en sus respuestas RIASEC
        
        Retorna:
        {
            'success': bool,
            'occupation': {
                'id': int,
                'name': str,
                'similarity': float
            },
            'suggested_careers': [list],
            'user_profile': {
                'R': float,
                'I': float,
                ...
            }
        }
        """
        try:
            # Verificar que el usuario esté logueado
            if 'usuario' not in session:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no autenticado'
                }), 401
            
            usuario_id = session['usuario'].get('id')
            if not usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'Error: ID de usuario no disponible'
                }), 400
            
            logger.info(f"Predicción de carreras para usuario {usuario_id}")
            
            # Realizar predicción
            result = PredictionsService.predict_careers(usuario_id)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 400
                
        except DatabaseError as e:
            logger.error(f"Error en predict_careers: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error procesando predicción'
            }), 500
        except Exception as e:
            logger.error(f"Error inesperado en predict_careers: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error inesperado'
            }), 500

    @staticmethod
    def get_occupations():
        """
        Endpoint GET /api/occupations
        Retorna todas las ocupaciones con sus posibles carreras
        desde MODELO_CONVERSIONES
        """
        try:
            occupations = PredictionsService.get_all_occupations()
            
            return jsonify({
                'success': True,
                'total': len(occupations),
                'occupations': occupations
            }), 200
            
        except Exception as e:
            logger.error(f"Error en get_occupations: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo ocupaciones'
            }), 500
