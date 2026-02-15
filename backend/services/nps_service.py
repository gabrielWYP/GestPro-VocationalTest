"""
Servicio NPS (Net Promoter Score)
Gestiona el seguimiento de tiempo acumulado y respuestas NPS de usuarios
que han completado el test vocacional.
"""

import logging
from datetime import datetime
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA
from utils.errors import DatabaseError

logger = logging.getLogger(__name__)


class NpsService:
    """Servicio para gestionar encuestas NPS"""

    @staticmethod
    def get_nps_status(usuario_id: int) -> dict:
        """
        Obtiene el estado NPS de un usuario.
        Retorna si ya respondió, tiempo acumulado y respuestas previas.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            dict con estado NPS o None si no existe registro
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    query = f"""
                    SELECT TIEMPO_ACUMULADO, ULTIMA_FECHA_VISTO,
                           RESPUESTA_PAGINA, RESPUESTA_TEST,
                           ESTADO, FECHA_RESPUESTA
                    FROM {ORACLE_SCHEMA}.USUARIO_NPS
                    WHERE USUARIO_ID = :usuario_id
                    """
                    cursor.execute(query, {'usuario_id': usuario_id})
                    row = cursor.fetchone()

                    if row:
                        return {
                            'exists': True,
                            'tiempo_acumulado': float(row[0]) if row[0] else 0,
                            'ultima_fecha_visto': row[1].isoformat() if row[1] else None,
                            'respuesta_pagina': int(row[2]) if row[2] is not None else None,
                            'respuesta_test': int(row[3]) if row[3] is not None else None,
                            'estado': int(row[4]) if row[4] is not None else 0,
                            'fecha_respuesta': row[5].isoformat() if row[5] else None
                        }
                    else:
                        return {
                            'exists': False,
                            'tiempo_acumulado': 0,
                            'ultima_fecha_visto': None,
                            'respuesta_pagina': None,
                            'respuesta_test': None,
                            'estado': 0,
                            'fecha_respuesta': None
                        }

        except Exception as e:
            logger.error(f"Error obteniendo estado NPS para usuario {usuario_id}: {str(e)}")
            raise DatabaseError(f"Error obteniendo estado NPS: {str(e)}")

    @staticmethod
    def init_nps_record(usuario_id: int) -> bool:
        """
        Crea el registro NPS para un usuario si no existe.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            True si se creó o ya existía
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Verificar si ya existe
                    cursor.execute(
                        f"SELECT 1 FROM {ORACLE_SCHEMA}.USUARIO_NPS WHERE USUARIO_ID = :usuario_id",
                        {'usuario_id': usuario_id}
                    )
                    if cursor.fetchone():
                        return True

                    # Crear registro inicial
                    insert_sql = f"""
                    INSERT INTO {ORACLE_SCHEMA}.USUARIO_NPS 
                        (USUARIO_ID, TIEMPO_ACUMULADO, ULTIMA_FECHA_VISTO, ESTADO, FECHA_CREACION)
                    VALUES 
                        (:usuario_id, 0, CURRENT_TIMESTAMP, 0, CURRENT_TIMESTAMP)
                    """
                    cursor.execute(insert_sql, {'usuario_id': usuario_id})
                    conn.commit()

                    logger.info(f"Registro NPS creado para usuario {usuario_id}")
                    return True

        except Exception as e:
            logger.error(f"Error creando registro NPS para usuario {usuario_id}: {str(e)}")
            raise DatabaseError(f"Error creando registro NPS: {str(e)}")

    @staticmethod
    def update_accumulated_time(usuario_id: int, seconds: float) -> dict:
        """
        Actualiza el tiempo acumulado del usuario en la página.
        
        Args:
            usuario_id: ID del usuario
            seconds: Segundos a agregar al tiempo acumulado
            
        Returns:
            dict con el nuevo tiempo acumulado y si debe mostrar NPS
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Primero asegurar que existe el registro
                    cursor.execute(
                        f"SELECT TIEMPO_ACUMULADO, ESTADO FROM {ORACLE_SCHEMA}.USUARIO_NPS WHERE USUARIO_ID = :usuario_id",
                        {'usuario_id': usuario_id}
                    )
                    row = cursor.fetchone()

                    if not row:
                        # Crear registro si no existe
                        NpsService.init_nps_record(usuario_id)
                        tiempo_actual = 0
                        estado = 0
                    else:
                        tiempo_actual = float(row[0]) if row[0] else 0
                        estado = int(row[1]) if row[1] is not None else 0

                    # Si ya completó ambas encuestas (estado=2), no actualizar más
                    if estado >= 2:
                        return {
                            'tiempo_acumulado': tiempo_actual,
                            'show_nps': False,
                            'estado': estado
                        }

                    nuevo_tiempo = tiempo_actual + seconds

                    # Actualizar tiempo acumulado
                    update_sql = f"""
                    UPDATE {ORACLE_SCHEMA}.USUARIO_NPS
                    SET TIEMPO_ACUMULADO = :nuevo_tiempo,
                        ULTIMA_FECHA_VISTO = CURRENT_TIMESTAMP
                    WHERE USUARIO_ID = :usuario_id
                    """
                    cursor.execute(update_sql, {
                        'nuevo_tiempo': nuevo_tiempo,
                        'usuario_id': usuario_id
                    })
                    conn.commit()

                    # Determinar si mostrar NPS (cada 5 minutos = 300 segundos)
                    # Se muestra si el tiempo acumulado supera un múltiplo de 300
                    # y el usuario no ha completado ambas encuestas
                    show_nps = False
                    if estado < 2 and nuevo_tiempo >= 300:
                        # Verificar si cruzó un umbral de 5 minutos
                        prev_intervals = int(tiempo_actual // 300)
                        new_intervals = int(nuevo_tiempo // 300)
                        if new_intervals > prev_intervals:
                            show_nps = True

                    return {
                        'tiempo_acumulado': nuevo_tiempo,
                        'show_nps': show_nps,
                        'estado': estado
                    }

        except Exception as e:
            logger.error(f"Error actualizando tiempo NPS para usuario {usuario_id}: {str(e)}")
            raise DatabaseError(f"Error actualizando tiempo NPS: {str(e)}")

    @staticmethod
    def save_nps_response(usuario_id: int, tipo: str, puntuacion: int) -> dict:
        """
        Guarda la respuesta NPS del usuario.
        tipo puede ser 'pagina' o 'test'.
        
        Args:
            usuario_id: ID del usuario
            tipo: 'pagina' o 'test'
            puntuacion: Puntuación NPS (0-10)
            
        Returns:
            dict con resultado de guardado
        """
        try:
            if tipo not in ('pagina', 'test'):
                return {'success': False, 'message': 'Tipo NPS inválido'}

            if not isinstance(puntuacion, int) or puntuacion < 0 or puntuacion > 10:
                return {'success': False, 'message': 'Puntuación debe ser entre 0 y 10'}

            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Obtener estado actual
                    cursor.execute(
                        f"""SELECT RESPUESTA_PAGINA, RESPUESTA_TEST, ESTADO 
                        FROM {ORACLE_SCHEMA}.USUARIO_NPS 
                        WHERE USUARIO_ID = :usuario_id""",
                        {'usuario_id': usuario_id}
                    )
                    row = cursor.fetchone()

                    if not row:
                        # Crear registro si no existe
                        NpsService.init_nps_record(usuario_id)
                        resp_pagina = None
                        resp_test = None
                        estado = 0
                    else:
                        resp_pagina = row[0]
                        resp_test = row[1]
                        estado = int(row[2]) if row[2] is not None else 0

                    # Determinar qué campo actualizar
                    if tipo == 'pagina':
                        if resp_pagina is not None:
                            return {'success': False, 'message': 'Ya respondiste la encuesta de la página'}
                        campo = 'RESPUESTA_PAGINA'
                    else:
                        if resp_test is not None:
                            return {'success': False, 'message': 'Ya respondiste la encuesta del test'}
                        campo = 'RESPUESTA_TEST'

                    # Calcular nuevo estado
                    nuevo_estado = estado + 1

                    # Actualizar respuesta
                    update_sql = f"""
                    UPDATE {ORACLE_SCHEMA}.USUARIO_NPS
                    SET {campo} = :puntuacion,
                        ESTADO = :nuevo_estado,
                        FECHA_RESPUESTA = CURRENT_TIMESTAMP
                    WHERE USUARIO_ID = :usuario_id
                    """
                    cursor.execute(update_sql, {
                        'puntuacion': puntuacion,
                        'nuevo_estado': nuevo_estado,
                        'usuario_id': usuario_id
                    })
                    conn.commit()

                    logger.info(f"NPS guardado: usuario={usuario_id}, tipo={tipo}, puntuacion={puntuacion}, estado={nuevo_estado}")

                    return {
                        'success': True,
                        'message': 'Respuesta NPS guardada exitosamente',
                        'estado': nuevo_estado,
                        'completed': nuevo_estado >= 2
                    }

        except Exception as e:
            logger.error(f"Error guardando NPS para usuario {usuario_id}: {str(e)}")
            raise DatabaseError(f"Error guardando respuesta NPS: {str(e)}")

    @staticmethod
    def check_user_eligible(usuario_id: int) -> dict:
        """
        Verifica si un usuario es elegible para NPS:
        - Debe haber completado el test (42 respuestas)
        - No debe haber completado ambas encuestas NPS (estado < 2)
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            dict con elegibilidad y detalles
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Verificar si completó el test (42 respuestas)
                    cursor.execute(
                        f"""SELECT COUNT(*) FROM {ORACLE_SCHEMA}.USUARIO_AFIRMACION_RPTA 
                        WHERE USUARIO_ID = :usuario_id""",
                        {'usuario_id': usuario_id}
                    )
                    count_row = cursor.fetchone()
                    test_completed = count_row[0] >= 42 if count_row else False

                    if not test_completed:
                        return {
                            'eligible': False,
                            'reason': 'test_not_completed',
                            'test_answers': count_row[0] if count_row else 0
                        }

                    # Verificar estado NPS
                    cursor.execute(
                        f"""SELECT TIEMPO_ACUMULADO, RESPUESTA_PAGINA, RESPUESTA_TEST, ESTADO
                        FROM {ORACLE_SCHEMA}.USUARIO_NPS 
                        WHERE USUARIO_ID = :usuario_id""",
                        {'usuario_id': usuario_id}
                    )
                    nps_row = cursor.fetchone()

                    if not nps_row:
                        # Es elegible, crear registro NPS
                        NpsService.init_nps_record(usuario_id)
                        return {
                            'eligible': True,
                            'tiempo_acumulado': 0,
                            'estado': 0,
                            'pending_pagina': True,
                            'pending_test': True
                        }

                    estado = int(nps_row[3]) if nps_row[3] is not None else 0

                    if estado >= 2:
                        return {
                            'eligible': False,
                            'reason': 'nps_completed',
                            'estado': estado
                        }

                    return {
                        'eligible': True,
                        'tiempo_acumulado': float(nps_row[0]) if nps_row[0] else 0,
                        'estado': estado,
                        'pending_pagina': nps_row[1] is None,
                        'pending_test': nps_row[2] is None
                    }

        except Exception as e:
            logger.error(f"Error verificando elegibilidad NPS para usuario {usuario_id}: {str(e)}")
            raise DatabaseError(f"Error verificando elegibilidad NPS: {str(e)}")
