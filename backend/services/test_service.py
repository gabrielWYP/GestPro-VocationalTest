"""
Lógica de negocio para el test vocacional
"""
import json
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA
from utils.errors import DatabaseError
from .career_data import CAREERS, QUESTIONS


class TestService:
    """Servicio para gestionar el test vocacional"""
    
    @staticmethod
    def get_questions():
        """Obtener todas las preguntas del test"""
        return QUESTIONS
    
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
