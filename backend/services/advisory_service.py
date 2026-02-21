"""
Lógica de negocio para gestión de asesorías
Usa las tablas: ASESORES, ASESORIA_USUARIO, USUARIO, CARRERAS_NUEVO
"""
import logging
from datetime import datetime
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA, ADVISORY_START_HOUR, ADVISORY_END_HOUR, ADVISORY_INTERVAL_MINUTES
from utils.errors import DatabaseError

logger = logging.getLogger(__name__)


class AdvisoryService:
    """Servicio para gestionar asesorías"""

    # ─── Asesores ────────────────────────────────────────────────

    @staticmethod
    def get_advisors() -> list:
        """
        Obtener todos los asesores con información de su carrera.
        JOIN ASESORES ↔ CARRERAS_NUEVO
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""SELECT a.ID, a.NOMBRE, a.APELLIDO,
                                   c.ID AS CARRERA_ID, c.CARRERA AS CARRERA_NOMBRE
                            FROM {ORACLE_SCHEMA}.ASESORES a
                            LEFT JOIN {ORACLE_SCHEMA}.CARRERAS_NUEVO c
                              ON a.FK_CARRERA = c.ID
                            ORDER BY a.NOMBRE"""
                    )
                    rows = cursor.fetchall()
                    return [
                        {
                            'id': row[0],
                            'nombre': row[1],
                            'apellido': row[2],
                            'carrera_id': row[3],
                            'carrera_nombre': row[4] or 'General'
                        }
                        for row in rows
                    ]
        except Exception as e:
            logger.error(f"Error obteniendo asesores: {e}")
            raise DatabaseError(f"Error obteniendo asesores: {e}")

    @staticmethod
    def get_advisor_by_id(advisor_id: int) -> dict:
        """Obtener un asesor por su ID"""
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""SELECT a.ID, a.NOMBRE, a.APELLIDO,
                                   c.ID AS CARRERA_ID, c.CARRERA AS CARRERA_NOMBRE
                            FROM {ORACLE_SCHEMA}.ASESORES a
                            LEFT JOIN {ORACLE_SCHEMA}.CARRERAS_NUEVO c
                              ON a.FK_CARRERA = c.ID
                            WHERE a.ID = :advisor_id""",
                        {'advisor_id': advisor_id}
                    )
                    row = cursor.fetchone()
                    if not row:
                        return None
                    return {
                        'id': row[0],
                        'nombre': row[1],
                        'apellido': row[2],
                        'carrera_id': row[3],
                        'carrera_nombre': row[4] or 'General'
                    }
        except Exception as e:
            logger.error(f"Error obteniendo asesor {advisor_id}: {e}")
            raise DatabaseError(f"Error obteniendo asesor: {e}")

    # ─── Horarios disponibles ────────────────────────────────────

    @staticmethod
    def get_booked_slots(advisor_id: int = None) -> list:
        """
        Obtener horarios ya reservados (desde hoy en adelante).
        Opcionalmente filtrados por asesor.
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    if advisor_id:
                        cursor.execute(
                            f"""SELECT TO_CHAR(DIA, 'YYYY-MM-DD'), HORA
                                FROM {ORACLE_SCHEMA}.ASESORIA_USUARIO
                                WHERE FK_ASESOR = :advisor_id
                                  AND DIA >= TRUNC(SYSDATE)
                                ORDER BY DIA, HORA""",
                            {'advisor_id': advisor_id}
                        )
                    else:
                        cursor.execute(
                            f"""SELECT TO_CHAR(DIA, 'YYYY-MM-DD'), HORA
                                FROM {ORACLE_SCHEMA}.ASESORIA_USUARIO
                                WHERE DIA >= TRUNC(SYSDATE)
                                ORDER BY DIA, HORA"""
                        )
                    return [
                        f"{row[0]} {row[1]}" for row in cursor.fetchall()
                    ]
        except Exception as e:
            logger.error(f"Error obteniendo slots reservados: {e}")
            raise DatabaseError(f"Error obteniendo asesorías: {e}")

    @staticmethod
    def get_available_times(advisor_id: int, date_str: str) -> list:
        """
        Obtener horarios disponibles para un asesor en una fecha específica.
        Genera slots de ADVISORY_START_HOUR a ADVISORY_END_HOUR cada
        ADVISORY_INTERVAL_MINUTES y excluye los ya reservados.
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""SELECT HORA
                            FROM {ORACLE_SCHEMA}.ASESORIA_USUARIO
                            WHERE FK_ASESOR = :advisor_id
                              AND TO_CHAR(DIA, 'YYYY-MM-DD') = :fecha""",
                        {'advisor_id': advisor_id, 'fecha': date_str}
                    )
                    booked_times = [str(row[0]).strip() for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo horarios: {e}")
            raise DatabaseError(f"Error obteniendo horarios: {e}")

        # Generar todos los slots y excluir los ya ocupados
        available = []
        hour = ADVISORY_START_HOUR
        minute = 0

        while hour < ADVISORY_END_HOUR:
            time_str = f"{hour:02d}:{minute:02d}"
            if time_str not in booked_times:
                available.append(time_str)
            minute += ADVISORY_INTERVAL_MINUTES
            if minute >= 60:
                minute = 0
                hour += 1

        return available

    # ─── Reservar asesoría ───────────────────────────────────────

    @staticmethod
    def book_advisory(advisor_id: int, user_id: int, date_str: str, time_str: str) -> dict:
        """
        Reservar una asesoría.
        Inserta en ASESORIA_USUARIO (FK_ASESOR, FK_USUARIO, DIA, HORA, LINK).
        Genera un link de reunión automáticamente.

        Returns:
            dict con info de la asesoría creada
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Verificar que no exista ya una reserva en ese horario para el asesor
                    cursor.execute(
                        f"""SELECT COUNT(*)
                            FROM {ORACLE_SCHEMA}.ASESORIA_USUARIO
                            WHERE FK_ASESOR = :advisor_id
                              AND TO_CHAR(DIA, 'YYYY-MM-DD') = :fecha
                              AND HORA = :hora""",
                        {'advisor_id': advisor_id, 'fecha': date_str, 'hora': time_str}
                    )
                    count = cursor.fetchone()[0]
                    if count > 0:
                        raise DatabaseError("Este horario ya está reservado para este asesor")

                    # Verificar que el usuario no tenga otra asesoría en la misma fecha y hora
                    cursor.execute(
                        f"""SELECT COUNT(*)
                            FROM {ORACLE_SCHEMA}.ASESORIA_USUARIO
                            WHERE FK_USUARIO = :user_id
                              AND TO_CHAR(DIA, 'YYYY-MM-DD') = :fecha
                              AND HORA = :hora""",
                        {'user_id': user_id, 'fecha': date_str, 'hora': time_str}
                    )
                    count = cursor.fetchone()[0]
                    if count > 0:
                        raise DatabaseError("Ya tienes una asesoría agendada en ese horario")

                    # Link fijo de Zoom para asesorías
                    link = "https://ulima-edu-pe.zoom.us/j/6595549038?pwd=bUY0ZkdSOXk5UHU5UVBRV1JuM2VyUT09"

                    # Insertar la asesoría
                    cursor.execute(
                        f"""INSERT INTO {ORACLE_SCHEMA}.ASESORIA_USUARIO
                            (FK_ASESOR, FK_USUARIO, DIA, HORA, LINK)
                            VALUES (:advisor_id, :user_id, TO_DATE(:fecha, 'YYYY-MM-DD'), :hora, :link)""",
                        {
                            'advisor_id': advisor_id,
                            'user_id': user_id,
                            'fecha': date_str,
                            'hora': time_str,
                            'link': link
                        }
                    )
                    conn.commit()

            logger.info(f"Asesoría reservada: asesor={advisor_id}, usuario={user_id}, {date_str} {time_str}")
            return {
                'date': date_str,
                'time': time_str,
                'link': link
            }

        except DatabaseError:
            raise
        except Exception as e:
            error_msg = str(e).upper()
            if 'UNIQUE' in error_msg or 'CONSTRAINT' in error_msg:
                raise DatabaseError("Este horario ya está reservado")
            logger.error(f"Error guardando asesoría: {e}")
            raise DatabaseError(f"Error guardando asesoría: {e}")

    # ─── Mis asesorías ──────────────────────────────────────────

    @staticmethod
    def get_user_bookings(user_id: int) -> list:
        """
        Obtener todas las asesorías de un usuario (futuras).
        JOIN con ASESORES y CARRERAS_NUEVO para info completa.
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""SELECT au.ID,
                                   TO_CHAR(au.DIA, 'YYYY-MM-DD') AS DIA,
                                   au.HORA,
                                   au.LINK,
                                   a.NOMBRE AS ASESOR_NOMBRE,
                                   a.APELLIDO AS ASESOR_APELLIDO,
                                   c.CARRERA AS CARRERA_NOMBRE
                            FROM {ORACLE_SCHEMA}.ASESORIA_USUARIO au
                            JOIN {ORACLE_SCHEMA}.ASESORES a ON au.FK_ASESOR = a.ID
                            LEFT JOIN {ORACLE_SCHEMA}.CARRERAS_NUEVO c ON a.FK_CARRERA = c.ID
                            WHERE au.FK_USUARIO = :user_id
                              AND au.DIA >= TRUNC(SYSDATE)
                            ORDER BY au.DIA, au.HORA""",
                        {'user_id': user_id}
                    )
                    rows = cursor.fetchall()
                    return [
                        {
                            'id': row[0],
                            'dia': row[1],
                            'hora': row[2],
                            'link': row[3],
                            'asesor_nombre': row[4],
                            'asesor_apellido': row[5],
                            'carrera_nombre': row[6] or 'General'
                        }
                        for row in rows
                    ]
        except Exception as e:
            logger.error(f"Error obteniendo asesorías del usuario {user_id}: {e}")
            raise DatabaseError(f"Error obteniendo tus asesorías: {e}")

    # ─── Cancelar asesoría ───────────────────────────────────────

    @staticmethod
    def cancel_booking(booking_id: int, user_id: int) -> bool:
        """
        Cancelar (eliminar) una asesoría del usuario.
        Solo permite cancelar asesorías propias.
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""DELETE FROM {ORACLE_SCHEMA}.ASESORIA_USUARIO
                            WHERE ID = :booking_id AND FK_USUARIO = :user_id""",
                        {'booking_id': booking_id, 'user_id': user_id}
                    )
                    deleted = cursor.rowcount
                    conn.commit()

                    if deleted == 0:
                        raise DatabaseError("Asesoría no encontrada o no tienes permisos")
                    return True
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error cancelando asesoría {booking_id}: {e}")
            raise DatabaseError(f"Error cancelando asesoría: {e}")
