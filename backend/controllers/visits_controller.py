"""
Controlador para gestionar visitas de usuarios anónimos
"""
from flask import request, jsonify
from services.visits_service import VisitsService
import logging

logger = logging.getLogger(__name__)


class VisitsController:
    """Controlador para registrar y obtener estadísticas de visitas"""
    
    @staticmethod
    def register_visit():
        """
        Endpoint para registrar una visita
        Espera: visitor_id, page, user_agent, ip_address, device_type
        """
        try:
            data = request.get_json()
            
            visitor_id = data.get('visitor_id')
            page = data.get('page', '/')
            user_agent = data.get('user_agent')
            ip_address = data.get('ip_address')
            device_type = data.get('device_type')
            
            if not visitor_id:
                return jsonify({
                    'success': False,
                    'message': 'visitor_id es requerido'
                }), 400
            
            # Registrar la visita
            result = VisitsService.register_visit(
                visitor_id=visitor_id,
                page=page,
                user_agent=user_agent,
                ip_address=ip_address,
                device_type=device_type
            )
            
            return jsonify(result), 200 if result['success'] else 400
            
        except Exception as e:
            logger.error(f"Error en register_visit: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error registrando visita: {str(e)}'
            }), 500
    
    @staticmethod
    def get_visitor_info():
        """
        Endpoint para obtener información de un visitante
        Query param: visitor_id
        """
        try:
            visitor_id = request.args.get('visitor_id')
            
            if not visitor_id:
                return jsonify({
                    'success': False,
                    'message': 'visitor_id es requerido'
                }), 400
            
            visitor_info = VisitsService.get_visitor_info(visitor_id)
            
            return jsonify({
                'success': visitor_info is not None,
                'data': visitor_info
            }), 200
            
        except Exception as e:
            logger.error(f"Error en get_visitor_info: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error obteniendo info: {str(e)}'
            }), 500
    
    @staticmethod
    def get_statistics():
        """
        Endpoint para obtener estadísticas generales de visitas
        (Puede requerir autenticación admin en el futuro)
        """
        try:
            stats = VisitsService.get_visit_statistics()
            
            return jsonify({
                'success': True,
                'statistics': stats
            }), 200
            
        except Exception as e:
            logger.error(f"Error en get_statistics: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error obteniendo estadísticas: {str(e)}'
            }), 500
