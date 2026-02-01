"""
Lógica de negocio para el modelo de predicción
"""
import json
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA
from utils.errors import DatabaseError
from .career_data import CAREERS, QUESTIONS


class ModelService:
    """Servicio para gestionar el modelo de predicción"""
    
    @staticmethod
    def get_model_info() -> dict:
        """
        Obtener información del modelo de predicción almacenado en la base de datos
        
        Returns:
            Dict con información del modelo
        Raises:
            DatabaseError: Si hay un error al acceder a la base de datos
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"SELECT MODEL_NAME, VERSION, METADATA FROM {ORACLE_SCHEMA}.PREDICTION_MODELS ORDER BY CREATED_AT DESC FETCH FIRST 1 ROWS ONLY"
                    )
                    row = cursor.fetchone()
                    
                    if not row:
                        raise DatabaseError("No se encontró ningún modelo de predicción.")
                    
                    model_info = {
                        'model_name': row[0],
                        'version': row[1],
                        'metadata': json.loads(row[2]) if row[2] else {}
                    }
                    return model_info
        except Exception as e:
            raise DatabaseError(f"Error al obtener información del modelo: {e}")