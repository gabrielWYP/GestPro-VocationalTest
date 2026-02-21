"""
Lógica de negocio para el test vocacional
"""
import json
import logging
from datetime import datetime
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA
from utils.errors import DatabaseError

logger = logging.getLogger(__name__)


class TestService:
    """Servicio para gestionar el test vocacional"""
    
    @staticmethod
    def get_afirmaciones():
        with OracleConnection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT ID, AFIRMACION_DSC FROM {ORACLE_SCHEMA}.AFIRMACIONES ORDER BY ID"
                )
                rows = cursor.fetchall()
                result = tuple({
                    'id': row[0],
                    'text': row[1]
                } for row in rows)
                return result
    
    @staticmethod
    def save_test_result(name: str, email: str, career_name: str, scores: dict) -> bool:
        """
        Guardar resultado del test en BD Oracle
        
        Args:
            name: Nombre del usuario
            email: Email del usuario
            career_name: Nombre de la carrera recomendada
            scores: Dict con puntuaciones por carrera
            
        Returns:
            True si se guardó exitosamente
            
        Raises:
            DatabaseError: Si falla la BD
        """
        try:
            with OracleConnection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    f'INSERT INTO {ORACLE_SCHEMA}.test_results (name, email, result_career, scores) '
                    'VALUES (:1, :2, :3, :4)',
                    (name, email, career_name, json.dumps(scores))
                )
                
                conn.commit()
                cursor.close()
            
            return True
        except Exception as e:
            raise DatabaseError(f"Error guardando resultado de test: {str(e)}")

    @staticmethod
    def save_answer(usuario_id: int, afirmacion_id: int, riasec_id: int) -> bool:
        """
        Guarda o actualiza la respuesta de un usuario a una afirmación
        Usa MERGE para hacer INSERT/UPDATE automáticamente
        
        Args:
            usuario_id: ID del usuario
            afirmacion_id: ID de la afirmación/pregunta
            riasec_id: ID del puntaje RIASEC (1-5)
            
        Returns:
            True si se guardó exitosamente
            
        Raises:
            DatabaseError: Si falla la BD
        """
        try:
            with OracleConnection() as conn:
                cursor = conn.cursor()
                
                # Usar MERGE para hacer INSERT o UPDATE según corresponda
                merge_sql = f"""
                MERGE INTO {ORACLE_SCHEMA}.USUARIO_AFIRMACION_RPTA t
                USING (SELECT :usuario_id as usuario_id, 
                              :afirmacion_id as afirmacion_id,
                              :riasec_id as riasec_id
                       FROM dual) s
                ON (t.usuario_id = s.usuario_id AND t.afirmacion_id = s.afirmacion_id)
                WHEN MATCHED THEN
                    UPDATE SET t.riasec_id = s.riasec_id,
                               t.estampa = CURRENT_TIMESTAMP
                WHEN NOT MATCHED THEN
                    INSERT (usuario_id, afirmacion_id, riasec_id, estampa)
                    VALUES (s.usuario_id, s.afirmacion_id, s.riasec_id, CURRENT_TIMESTAMP)
                """
                
                cursor.execute(merge_sql, {
                    'usuario_id': usuario_id,
                    'afirmacion_id': afirmacion_id,
                    'riasec_id': riasec_id
                })
                
                conn.commit()
                cursor.close()
                
                logger.info(f"Respuesta guardada: usuario={usuario_id}, afirmacion={afirmacion_id}, riasec={riasec_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error guardando respuesta: {str(e)}")
            raise DatabaseError(f"Error guardando respuesta: {str(e)}")
    
    @staticmethod
    def save_answers_batch(usuario_id: int, answers: list) -> bool:
        """
        Guarda múltiples respuestas en una transacción
        
        Args:
            usuario_id: ID del usuario
            answers: Lista de dicts con 'afirmacion_id' y 'riasec_id'
                    Ej: [{'afirmacion_id': 1, 'riasec_id': 5}, ...]
            
        Returns:
            True si se guardaron exitosamente
            
        Raises:
            DatabaseError: Si falla la BD
        """
        try:
            with OracleConnection() as conn:
                cursor = conn.cursor()
                
                for answer in answers:
                    merge_sql = f"""
                    MERGE INTO {ORACLE_SCHEMA}.USUARIO_AFIRMACION_RPTA t
                    USING (SELECT :usuario_id as usuario_id, 
                                  :afirmacion_id as afirmacion_id,
                                  :riasec_id as riasec_id
                           FROM dual) s
                    ON (t.usuario_id = s.usuario_id AND t.afirmacion_id = s.afirmacion_id)
                    WHEN MATCHED THEN
                        UPDATE SET t.riasec_id = s.riasec_id,
                                   t.estampa = CURRENT_TIMESTAMP
                    WHEN NOT MATCHED THEN
                        INSERT (usuario_id, afirmacion_id, riasec_id, estampa)
                        VALUES (s.usuario_id, s.afirmacion_id, s.riasec_id, CURRENT_TIMESTAMP)
                    """
                    
                    cursor.execute(merge_sql, {
                        'usuario_id': usuario_id,
                        'afirmacion_id': answer['afirmacion_id'],
                        'riasec_id': answer['riasec_id']
                    })
                
                conn.commit()
                cursor.close()
                
                logger.info(f"Lote de {len(answers)} respuestas guardadas para usuario={usuario_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error guardando lote de respuestas: {str(e)}")
            raise DatabaseError(f"Error guardando respuestas: {str(e)}")    
    @staticmethod
    def get_test_status(usuario_id: int) -> dict:
        """
        Obtiene el estado del test para un usuario
        
        Returns:
            dict con:
            - total_questions: 42
            - answered_questions: cantidad de respuestas en BD
            - status: "0" (sin empezar), "incomplete" (parcial) o "complete" (todas 42)
            - answers: dict con respuestas {question_id: riasec_id}
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Contar respuestas del usuario
                    query = f"""
                    SELECT 
                        uar.AFIRMACION_ID,
                        uar.RIASEC_ID
                    FROM {ORACLE_SCHEMA}.USUARIO_AFIRMACION_RPTA uar
                    WHERE uar.USUARIO_ID = :usuario_id
                    ORDER BY uar.AFIRMACION_ID
                    """
                    
                    cursor.execute(query, {'usuario_id': usuario_id})
                    results = cursor.fetchall()
                    
                    total_questions = 42
                    answered = len(results)
                    
                    # Mapear respuestas
                    answers = {}
                    for row in results:
                        answers[str(row[0])] = int(row[1])
                    
                    # Determinar estado
                    if answered == 0:
                        status = "0"
                    elif answered == total_questions:
                        status = "complete"
                    else:
                        status = "incomplete"
                    
                    logger.info(f"Estado del test para usuario {usuario_id}: {status} ({answered}/{total_questions})")
                    
                    return {
                        'total_questions': total_questions,
                        'answered_questions': answered,
                        'status': status,
                        'answers': answers
                    }
                    
        except Exception as e:
            logger.error(f"Error obteniendo estado del test: {str(e)}")
            raise DatabaseError(f"Error obteniendo estado del test: {str(e)}")
    
    @staticmethod
    def reset_user_answers(usuario_id: int) -> bool:
        """
        Borra TODAS las respuestas guardadas de un usuario
        Se usa cuando el usuario quiere resetear su test
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            bool indicando si fue exitoso
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    delete_query = f"""
                    DELETE FROM {ORACLE_SCHEMA}.USUARIO_AFIRMACION_RPTA
                    WHERE USUARIO_ID = :usuario_id
                    """
                    
                    cursor.execute(delete_query, {'usuario_id': usuario_id})
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    logger.info(f"Se eliminaron {deleted_count} respuestas del usuario {usuario_id}")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Error borrando respuestas del usuario {usuario_id}: {str(e)}")
            raise DatabaseError(f"Error al resetear test: {str(e)}")
