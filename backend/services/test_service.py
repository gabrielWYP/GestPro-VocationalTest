"""
Lógica de negocio para el test vocacional
"""
import json
import logging
from datetime import datetime
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA
from utils.errors import DatabaseError
from .career_data import CAREERS, QUESTIONS

logger = logging.getLogger(__name__)


class TestService:
    """Servicio para gestionar el test vocacional"""
    
    @staticmethod
    def get_questions():
        """Obtener todas las preguntas del test"""
        return QUESTIONS
    
    
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
    def calculate_scores(answers: list) -> dict:
        """
        Calcular puntuación por carrera según respuestas
        
        Args:
            answers: Lista de textos de opciones seleccionadas
            
        Returns:
            Dict con ID de carrera y puntuación
        """
        career_scores = {career['id']: 0 for career in CAREERS}
        
        for answer_text in answers:
            for question in QUESTIONS:
                for option in question['options']:
                    if option['text'] == answer_text:
                        for career_id in option['careers']:
                            career_scores[career_id] += 1
        
        return career_scores
    
    @staticmethod
    def get_best_career(career_scores: dict) -> dict:
        """
        Obtener la carrera con mejor puntuación
        
        Args:
            career_scores: Dict con puntuaciones por carrera
            
        Returns:
            Dict con datos de la carrera ganadora
        """
        best_career_id = max(career_scores, key=career_scores.get)
        return next(c for c in CAREERS if c['id'] == best_career_id)
    
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
