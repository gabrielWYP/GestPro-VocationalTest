"""
Servicio de predicción de carreras basado en RIASEC y cosine similarity
Obtiene datos de USUARIO_AFIRMACION_RPTA y calcula similitud con MODELO_CONVERSIONES
"""
import numpy as np
import logging
import ast
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA
from utils.errors import DatabaseError

logger = logging.getLogger(__name__)


class PredictionsService:
    """Servicio para predecir carreras basado en respuestas del usuario"""
    
    @staticmethod
    def get_user_riasec_profile(usuario_id: int) -> dict:
        """
        Obtiene el perfil RIASEC del usuario desde sus respuestas guardadas
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            dict con las puntuaciones por categoría RIASEC
            {
                'R': 4.5,
                'I': 3.2,
                'A': 2.8,
                ...
            }
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Query que trae respuestas con categoría RIASEC
                    query = f"""
                    SELECT 
                        cr.CATEGORY_NAME,
                        AVG(uar.RIASEC_ID) as avg_score
                    FROM {ORACLE_SCHEMA}.USUARIO_AFIRMACION_RPTA uar
                    JOIN {ORACLE_SCHEMA}.AFIRMACIONES af ON uar.AFIRMACION_ID = af.ID
                    JOIN {ORACLE_SCHEMA}.CATEGORIAS_RIASEC cr ON af.FK_RIASEC = cr.ID
                    WHERE uar.USUARIO_ID = :usuario_id
                    GROUP BY cr.CATEGORY_NAME
                    """
                    
                    cursor.execute(query, {'usuario_id': usuario_id})
                    results = cursor.fetchall()
                    
                    if not results:
                        raise DatabaseError(f"No se encontraron respuestas para usuario {usuario_id}")
                    
                    # Mapear resultados a dict
                    riasec_profile = {}
                    for row in results:
                        category = row[0]  # CATEGORY_NAME (R, I, A, S, E, C)
                        score = float(row[1])  # Promedio de puntajes (1-5)
                        riasec_profile[category] = score
                    
                    logger.info(f"Perfil RIASEC obtenido para usuario {usuario_id}: {riasec_profile}")
                    return riasec_profile
                    
        except Exception as e:
            logger.error(f"Error obteniendo perfil RIASEC: {str(e)}")
            raise DatabaseError(f"Error obteniendo perfil RIASEC: {str(e)}")
    
    @staticmethod
    def get_occupations_model() -> list:
        """
        Obtiene todas las ocupaciones del modelo MODELO_CONVERSIONES
        
        Returns:
            list de dicts con ocupaciones y sus vectores RIASEC
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    query = f"""
                    SELECT 
                        ID,
                        OCUPACION,
                        REALISTIC,
                        INVESTIGATIVE,
                        ARTISTIC,
                        SOCIAL,
                        ENTERPRISING,
                        CONVENTIONAL,
                        CAST(POSIBLES_CARRERAS AS VARCHAR2(4000)) as POSIBLES_CARRERAS
                    FROM {ORACLE_SCHEMA}.MODELO_CONVERSIONES
                    ORDER BY ID
                    """
                    
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    occupations = []
                    for row in results:
                        # Manejar POSIBLES_CARRERAS (puede ser LOB o string con formato array)
                        carreras_data = row[8]
                        carreras_list = []
                        
                        if carreras_data is not None:
                            # Convertir a string si es LOB
                            if hasattr(carreras_data, 'read'):
                                carreras_str = carreras_data.read()
                            else:
                                carreras_str = str(carreras_data)
                            
                            # Parsear el formato de array literal: ['Carrera 1', 'Carrera 2', ...]
                            if carreras_str.strip():
                                try:
                                    # ast.literal_eval convierte el string a lista Python
                                    carreras_list = ast.literal_eval(carreras_str)
                                    # Asegurar que es una lista
                                    if not isinstance(carreras_list, list):
                                        carreras_list = [carreras_list]
                                except (ValueError, SyntaxError):
                                    # Si falla el parseo, tratar como string simple
                                    carreras_list = [carreras_str]
                        
                        occupation = {
                            'id': row[0],
                            'name': row[1],
                            'vector': np.array([
                                float(row[2]),  # REALISTIC
                                float(row[3]),  # INVESTIGATIVE
                                float(row[4]),  # ARTISTIC
                                float(row[5]),  # SOCIAL
                                float(row[6]),  # ENTERPRISING
                                float(row[7])   # CONVENTIONAL
                            ]),
                            'carreras': carreras_list
                        }
                        occupations.append(occupation)
                    
                    logger.info(f"Cargadas {len(occupations)} ocupaciones del modelo")
                    return occupations
                    
        except Exception as e:
            logger.error(f"Error cargando modelo de ocupaciones: {str(e)}")
            raise DatabaseError(f"Error cargando modelo: {str(e)}")
    
    @staticmethod
    def predict_careers(usuario_id: int) -> dict:
        """
        Predice las mejores carreras para un usuario usando cosine similarity
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            dict con ocupación predicha y carreras sugeridas
        """
        try:
            # Obtener perfil RIASEC del usuario
            profile = PredictionsService.get_user_riasec_profile(usuario_id)
            
            # Mapeo de nombres españoles a siglas RIASEC
            name_to_code = {
                'Realista': 'R',
                'Investigativo': 'I',
                'Artístico': 'A',
                'Social': 'S',
                'Emprendedor': 'E',
                'Convencional': 'C'
            }
            
            # Convertir profile a códigos RIASEC
            riasec_code_profile = {}
            for name, score in profile.items():
                code = name_to_code.get(name)
                if code:
                    riasec_code_profile[code] = score
            
            # Asegurar que tenemos todas las categorías
            riasec_order = ['R', 'I', 'A', 'S', 'E', 'C']
            if len(riasec_code_profile) != 6:
                logger.warning(f"Perfil incompleto para usuario {usuario_id}: {riasec_code_profile}")
            
            # Construir vector del usuario (escala 1-5 -> normalizar a 1-7 para MODELO_CONVERSIONES)
            # Conversión correcta: (valor - 1) * 1.5 + 1 = valor * 1.5 - 0.5
            # Si valor=1: 1*1.5-0.5=1 ✓
            # Si valor=3: 3*1.5-0.5=4 ✓
            # Si valor=5: 5*1.5-0.5=7 ✓
            user_vector = np.array([
                riasec_code_profile.get(cat, 3) * 1.5 - 0.5  # Escalar de 1-5 a 1-7
                for cat in riasec_order
            ])
            
            logger.info(f"Vector usuario: {user_vector}")
            
            # Obtener modelo de ocupaciones
            occupations = PredictionsService.get_occupations_model()
            
            # Preparar matriz de vectores de ocupaciones
            occupation_vectors = np.array([occ['vector'] for occ in occupations])
            
            # Calcular cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(
                user_vector.reshape(1, -1),
                occupation_vectors
            )[0]
            
            # Encontrar el top 5 de ocupaciones
            top_5_indices = np.argsort(similarities)[-5:][::-1]  # Top 5 en orden descendente
            
            top_occupations = []
            for idx in top_5_indices:
                occ = occupations[idx]
                top_occupations.append({
                    'id': occ['id'],
                    'name': occ['name'],
                    'similarity': float(similarities[idx]),
                    'carreras': occ['carreras']
                })
            
            # La mejor ocupación es la primera del top 5
            best_occupation = top_occupations[0]
            
            # Crear perfil escalado a 1-7 para mostrar en frontend
            riasec_profile_scaled = {
                cat: float((riasec_code_profile.get(cat, 3) * 1.5 - 0.5))
                for cat in riasec_order
            }
            
            logger.info(f"Top 5 ocupaciones predichas:")
            for i, occ in enumerate(top_occupations, 1):
                logger.info(f"  {i}. {occ['name']} ({occ['similarity']:.4f})")
            
            return {
                'success': True,
                'occupation': {
                    'id': best_occupation['id'],
                    'name': best_occupation['name'],
                    'similarity': best_occupation['similarity']
                },
                'suggested_careers': best_occupation['carreras'],
                'top_occupations': top_occupations,
                'user_profile': riasec_code_profile,
                'user_profile_scaled': riasec_profile_scaled
            }
            
        except DatabaseError as e:
            logger.error(f"Error en predicción: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
