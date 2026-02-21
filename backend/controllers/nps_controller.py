"""
Controlador NPS (Net Promoter Score)
Maneja las peticiones HTTP para el sistema de encuestas NPS
"""

import logging
from flask import request, jsonify, session
from services.nps_service import NpsService

logger = logging.getLogger(__name__)


class NpsController:
    """Controlador para operaciones NPS"""

    @staticmethod
    def check_eligibility():
        """
        Endpoint GET /api/nps/check
        Verifica si el usuario logueado es elegible para NPS.
        Retorna elegibilidad, tiempo acumulado y qué encuestas faltan.
        """
        try:
            if 'usuario' not in session:
                return jsonify({
                    'success': True,
                    'eligible': False,
                    'reason': 'not_authenticated'
                }), 200

            usuario_id = session['usuario'].get('id')
            if not usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'Error: ID de usuario no disponible'
                }), 400

            result = NpsService.check_user_eligible(usuario_id)

            return jsonify({
                'success': True,
                **result
            }), 200

        except Exception as e:
            logger.error(f"Error en check_eligibility NPS: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error verificando elegibilidad NPS: {str(e)}'
            }), 500

    @staticmethod
    def update_time():
        """
        Endpoint POST /api/nps/update-time
        Actualiza el tiempo acumulado del usuario en la página.
        Body: { "seconds": 30 }
        """
        try:
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

            data = request.get_json()
            seconds = data.get('seconds', 0)

            if not isinstance(seconds, (int, float)) or seconds < 0:
                return jsonify({
                    'success': False,
                    'message': 'Segundos debe ser un número positivo'
                }), 400

            result = NpsService.update_accumulated_time(usuario_id, seconds)

            return jsonify({
                'success': True,
                **result
            }), 200

        except Exception as e:
            logger.error(f"Error en update_time NPS: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error actualizando tiempo NPS: {str(e)}'
            }), 500

    @staticmethod
    def submit_response():
        """
        Endpoint POST /api/nps/submit
        Guarda la respuesta NPS del usuario.
        Body: { "tipo": "pagina"|"test", "puntuacion": 0-10 }
        """
        try:
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

            data = request.get_json()
            tipo = data.get('tipo')
            puntuacion = data.get('puntuacion')

            if not tipo or tipo not in ('pagina', 'test'):
                return jsonify({
                    'success': False,
                    'message': 'Tipo debe ser "pagina" o "test"'
                }), 400

            if puntuacion is None or not isinstance(puntuacion, int) or puntuacion < 0 or puntuacion > 10:
                return jsonify({
                    'success': False,
                    'message': 'Puntuación debe ser un número entero entre 0 y 10'
                }), 400

            result = NpsService.save_nps_response(usuario_id, tipo, puntuacion)

            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 400

        except Exception as e:
            logger.error(f"Error en submit_response NPS: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error guardando respuesta NPS: {str(e)}'
            }), 500

    @staticmethod
    def get_status():
        """
        Endpoint GET /api/nps/status
        Obtiene el estado NPS completo del usuario logueado.
        """
        try:
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

            status = NpsService.get_nps_status(usuario_id)

            return jsonify({
                'success': True,
                'nps': status
            }), 200

        except Exception as e:
            logger.error(f"Error en get_status NPS: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error obteniendo estado NPS: {str(e)}'
            }), 500
