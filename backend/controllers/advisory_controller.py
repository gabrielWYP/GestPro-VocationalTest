"""
Controlador para asesorías
"""
import logging
from flask import request, jsonify
from services.advisory_service import AdvisoryService
from utils.validators import validate_email, validate_name, validate_date, validate_time
from utils.errors import DatabaseError


logger = logging.getLogger(__name__)


class AdvisoryController:
    """Controlador para operaciones de asesorías"""
    
    @staticmethod
    def get_booked_slots():
        """
        Endpoint GET /api/booked-slots
        Obtiene horarios ya reservados
        """
        try:
            slots = AdvisoryService.get_booked_slots()
            return jsonify({
                'success': True,
                'booked_slots': slots
            })
        except DatabaseError as e:
            logger.error(f"Error obteniendo slots: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo asesorías'
            }), 500
    
    @staticmethod
    def get_available_times():
        """
        Endpoint GET /api/available-times?date=YYYY-MM-DD
        Obtiene horarios disponibles para una fecha
        """
        try:
            date = request.args.get('date', '')
            
            if not date or not validate_date(date):
                return jsonify({
                    'success': False,
                    'message': 'Fecha inválida (formato: YYYY-MM-DD)'
                }), 400
            
            available_times = AdvisoryService.get_available_times(date)
            
            return jsonify({
                'success': True,
                'available_times': available_times
            })
        except DatabaseError as e:
            logger.error(f"Error obteniendo horarios: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo horarios'
            }), 500
    
    @staticmethod
    def book_advisory():
        """
        Endpoint POST /api/advisory-submit
        Reserva una asesoría
        """
        try:
            data = request.json
            
            # Validar datos
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            date = data.get('date', '').strip()
            time = data.get('time', '').strip()
            
            if not all([name, email, date, time]):
                return jsonify({
                    'success': False,
                    'message': 'Faltan datos requeridos'
                }), 400
            
            if not validate_name(name):
                return jsonify({
                    'success': False,
                    'message': 'Nombre inválido'
                }), 400
            
            if not validate_email(email):
                return jsonify({
                    'success': False,
                    'message': 'Email inválido'
                }), 400
            
            if not validate_date(date):
                return jsonify({
                    'success': False,
                    'message': 'Fecha inválida (formato: YYYY-MM-DD)'
                }), 400
            
            if not validate_time(time):
                return jsonify({
                    'success': False,
                    'message': 'Hora inválida (formato: HH:MM)'
                }), 400
            
            # Guardar en BD
            try:
                AdvisoryService.book_advisory(name, email, date, time)
            except DatabaseError as e:
                error_msg = str(e)
                status_code = 409 if 'ya está reservado' in error_msg else 500
                return jsonify({
                    'success': False,
                    'message': error_msg
                }), status_code
            
            return jsonify({
                'success': True,
                'message': f'Asesoría agendada para {date} a las {time}'
            })
        
        except Exception as e:
            logger.error(f"Error en book_advisory: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error guardando asesoría'
            }), 500
