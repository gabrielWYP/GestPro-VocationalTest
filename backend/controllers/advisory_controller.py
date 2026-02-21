"""
Controlador para asesorías
Endpoints para gestionar asesores, horarios y reservas de asesoría
"""
import logging
from flask import request, jsonify, session
from services.advisory_service import AdvisoryService
from utils.validators import validate_date, validate_time
from utils.errors import DatabaseError

logger = logging.getLogger(__name__)


class AdvisoryController:
    """Controlador para operaciones de asesorías"""

    # ─── Asesores ────────────────────────────────────────────────

    @staticmethod
    def get_advisors():
        """
        GET /api/advisors
        Obtiene la lista de asesores con su carrera asociada
        """
        try:
            advisors = AdvisoryService.get_advisors()
            return jsonify({
                'success': True,
                'advisors': advisors
            })
        except DatabaseError as e:
            logger.error(f"Error obteniendo asesores: {e}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo asesores'
            }), 500

    # ─── Slots reservados ────────────────────────────────────────

    @staticmethod
    def get_booked_slots():
        """
        GET /api/booked-slots?advisor_id=X
        Obtiene horarios ya reservados (opcionalmente por asesor)
        """
        try:
            advisor_id = request.args.get('advisor_id', type=int)
            slots = AdvisoryService.get_booked_slots(advisor_id)
            return jsonify({
                'success': True,
                'booked_slots': slots
            })
        except DatabaseError as e:
            logger.error(f"Error obteniendo slots: {e}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo asesorías'
            }), 500

    # ─── Horarios disponibles ────────────────────────────────────

    @staticmethod
    def get_available_times():
        """
        GET /api/available-times?advisor_id=X&date=YYYY-MM-DD
        Obtiene horarios disponibles para un asesor en una fecha
        """
        try:
            advisor_id = request.args.get('advisor_id', type=int)
            date = request.args.get('date', '')

            if not advisor_id:
                return jsonify({
                    'success': False,
                    'message': 'Se requiere advisor_id'
                }), 400

            if not date or not validate_date(date):
                return jsonify({
                    'success': False,
                    'message': 'Fecha inválida (formato: YYYY-MM-DD)'
                }), 400

            available_times = AdvisoryService.get_available_times(advisor_id, date)

            return jsonify({
                'success': True,
                'available_times': available_times
            })
        except DatabaseError as e:
            logger.error(f"Error obteniendo horarios: {e}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo horarios'
            }), 500

    # ─── Reservar asesoría ───────────────────────────────────────

    @staticmethod
    def book_advisory():
        """
        POST /api/advisory-submit
        Reserva una asesoría. Requiere sesión activa.
        Body: { advisor_id, date, time }
        """
        try:
            # Verificar que el usuario esté logueado
            if 'usuario' not in session:
                return jsonify({
                    'success': False,
                    'message': 'Debes iniciar sesión para agendar una asesoría'
                }), 401

            user = session['usuario']
            user_id = user['id']

            data = request.json
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se recibieron datos'
                }), 400

            advisor_id = data.get('advisor_id')
            date = data.get('date', '').strip()
            time = data.get('time', '').strip()

            if not all([advisor_id, date, time]):
                return jsonify({
                    'success': False,
                    'message': 'Faltan datos requeridos (advisor_id, date, time)'
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

            # Verificar que el asesor exista
            advisor = AdvisoryService.get_advisor_by_id(int(advisor_id))
            if not advisor:
                return jsonify({
                    'success': False,
                    'message': 'Asesor no encontrado'
                }), 404

            # Reservar
            result = AdvisoryService.book_advisory(
                advisor_id=int(advisor_id),
                user_id=user_id,
                date_str=date,
                time_str=time
            )

            return jsonify({
                'success': True,
                'message': f'Asesoría agendada para {date} a las {time} con {advisor["nombre"]} {advisor["apellido"]}',
                'booking': result
            })

        except DatabaseError as e:
            error_msg = str(e)
            status_code = 409 if 'ya está reservado' in error_msg or 'ya tienes' in error_msg.lower() else 500
            return jsonify({
                'success': False,
                'message': error_msg
            }), status_code
        except Exception as e:
            logger.error(f"Error en book_advisory: {e}")
            return jsonify({
                'success': False,
                'message': 'Error guardando asesoría'
            }), 500

    # ─── Mis asesorías ──────────────────────────────────────────

    @staticmethod
    def get_my_bookings():
        """
        GET /api/advisory/my-bookings
        Obtiene las asesorías del usuario logueado
        """
        try:
            if 'usuario' not in session:
                return jsonify({
                    'success': False,
                    'message': 'Debes iniciar sesión'
                }), 401

            user_id = session['usuario']['id']
            bookings = AdvisoryService.get_user_bookings(user_id)

            return jsonify({
                'success': True,
                'bookings': bookings
            })
        except DatabaseError as e:
            logger.error(f"Error obteniendo mis asesorías: {e}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo tus asesorías'
            }), 500

    # ─── Cancelar asesoría ───────────────────────────────────────

    @staticmethod
    def cancel_booking():
        """
        DELETE /api/advisory/<booking_id>
        Cancela una asesoría del usuario logueado
        """
        try:
            if 'usuario' not in session:
                return jsonify({
                    'success': False,
                    'message': 'Debes iniciar sesión'
                }), 401

            booking_id = request.view_args.get('booking_id')
            if not booking_id:
                return jsonify({
                    'success': False,
                    'message': 'ID de asesoría requerido'
                }), 400

            user_id = session['usuario']['id']
            AdvisoryService.cancel_booking(int(booking_id), user_id)

            return jsonify({
                'success': True,
                'message': 'Asesoría cancelada exitosamente'
            })
        except DatabaseError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Error cancelando asesoría: {e}")
            return jsonify({
                'success': False,
                'message': 'Error cancelando asesoría'
            }), 500
