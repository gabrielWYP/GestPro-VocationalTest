"""
Lógica de negocio para carreras
"""
from .career_data import CAREERS
from db.db_config import OracleConnection


class CareerService:
    """Servicio para gestionar carreras"""
    
    @staticmethod
    def get_all_careers() -> list:
        """Obtener todas las carreras"""
        return CAREERS
    
    @staticmethod
    def get_career_by_id(career_id: int) -> dict:
        """
        Obtener una carrera por ID
        
        Args:
            career_id: ID de la carrera
            
        Returns:
            Dict con datos de la carrera
        """
        career = next((c for c in CAREERS if c['id'] == career_id), None)
        return career
