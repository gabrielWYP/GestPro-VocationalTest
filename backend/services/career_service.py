"""
Lógica de negocio para carreras
"""
from .career_data import CAREERS
from db.db_config import OracleConnection


class CareerService:
    """Servicio para gestionar carreras"""
    
    @staticmethod
    def get_all_careers() -> list:
        with OracleConnection() as conn:
            """Obtener todas las carreras"""
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM CARRERAS")
            careers = cursor.fetchall()
            cursor.close()
        
        return careers
    
    @staticmethod
    def get_career_by_id(career_id: int) -> dict:
        """
        Obtener una carrera por ID
        
        Args:
            career_id: ID de la carrera
            
        Returns:
            Dict con datos de la carrera
        """
        with OracleConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM CARRERAS WHERE ID = :id", id=career_id)
            career = cursor.fetchone()
            cursor.close()
        return career
