"""
Lógica de negocio para carreras
"""
from functools import lru_cache
from urllib.parse import quote
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA

class CareerService:
    """Servicio para gestionar carreras"""
    
    @staticmethod
    def _build_image_url(image_path: str) -> str:
        """
        Construye URL del proxy para servir imágenes
        El proxy maneja URL encoding automáticamente
        Ej: 'ikigais_images/Administración de Empresas.svg' → '/api/image/proxy?path=ikigais_images/Administración%20de%20Empresas.svg'
        """
        encoded_path = quote(image_path, safe='/')
        return f"/api/image/proxy?path={encoded_path}"
    @staticmethod
    def clear_cache():
        """Limpiar todo el cache de este servicio"""
        CareerService.get_careers_list.cache_clear()
        CareerService.get_career_detail.cache_clear()
        CareerService.get_all_careers.cache_clear()
        CareerService.get_all_careers_full.cache_clear()
        CareerService.get_career_by_id.cache_clear()
        print("Cache del servicio de carreras limpiado")
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_careers_list() -> tuple:
        """
        Obtener lista básica de carreras (solo id, nombre, icono, descripción)
        Para la página de listado de carreras - más liviano
        Cacheado: máximo 128 resultados en memoria
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"SELECT ID, CARRERA, DESCRIPCION, AFINIDAD, URL FROM {ORACLE_SCHEMA}.CARRERAS_NUEVO ORDER BY CARRERA"
                    )
                    rows = cursor.fetchall()
                    
                    result = tuple({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'afinidad': row[3],
                        'url': CareerService._build_image_url(row[4])
                    } for row in rows)
                    return result
        except Exception as e:
            print(f"Error obteniendo lista de carreras: {e}")
            return ()
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_career_detail(career_id: int) -> dict:
        """
        Obtener detalle completo de una carrera (con skills, jobs, etc.)
        Para la página de detalle de carrera
        Cacheado: máximo 128 consultas diferentes en memoria
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Obtener datos básicos de la carrera
                    cursor.execute(
                        f"SELECT ID, CARRERA, DESCRIPCION, AFINIDAD, URL FROM {ORACLE_SCHEMA}.CARRERAS_NUEVO WHERE ID = :1",
                        (career_id,)
                    )
                    row = cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    # Obtener skills de esta carrera
                    cursor.execute(
                        f"""SELECT S.NOMBRE FROM {ORACLE_SCHEMA}.SKILLS S
                           INNER JOIN {ORACLE_SCHEMA}.CARRERAS_SKILLS CS ON S.ID = CS.FK_SKILLS
                           WHERE CS.FK_CARRERA = :1
                           ORDER BY S.NOMBRE""",
                        (career_id,)
                    )
                    skills = [skill[0] for skill in cursor.fetchall()]
                    
                    # Obtener tareas/jobs de esta carrera
                    cursor.execute(
                        f"""SELECT T.NOMBRE FROM {ORACLE_SCHEMA}.TAREAS T
                           INNER JOIN {ORACLE_SCHEMA}.CARRERA_TAREAS CT ON T.ID = CT.FK_TAREA
                           WHERE CT.FK_CARRERA = :1
                           ORDER BY T.NOMBRE""",
                        (career_id,)
                    )
                    jobs = [job[0] for job in cursor.fetchall()]
                    
                    return {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'afinidad': row[3],
                        'url': CareerService._build_image_url(row[4]),
                        'skills': skills,
                        'jobs': jobs
                    }
        except Exception as e:
            print(f"Error obteniendo detalle de carrera {career_id}: {e}")
            return None
    
    @staticmethod
    @lru_cache(maxsize=1)
    def get_all_careers() -> tuple:
        """Obtener todas las carreras con sus skills desde la BD
        Cacheado: solo se guarda 1 resultado ya que no toma parámetros
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Obtener carreras
                    cursor.execute(f"SELECT ID, CARRERA, DESCRIPCION, AFINIDAD, URL FROM {ORACLE_SCHEMA}.CARRERAS_NUEVO")
                    rows = cursor.fetchall()
                    
                    careers = []
                    for row in rows:
                        career_id = row[0]
                        
                        # Obtener skills de esta carrera
                        cursor.execute(
                            f"""SELECT S.NOMBRE FROM {ORACLE_SCHEMA}.SKILLS S
                               LEFT JOIN {ORACLE_SCHEMA}.CARRERAS_SKILLS CS ON S.ID = CS.FK_SKILLS
                               WHERE CS.FK_CARRERA = :1 OR CS.FK_CARRERA IS NULL
                               ORDER BY S.NOMBRE""",
                            (career_id,)
                        )
                        skills_rows = cursor.fetchall()
                        skills = [skill[0] for skill in skills_rows if skill[0]]
                        
                        careers.append({
                            'id': career_id,
                            'name': row[1],
                            'description': row[2],
                            'afinidad': row[3],
                            'url': CareerService._build_image_url(row[4]),
                            'skills': skills
                        })
                    
                    return tuple(careers)
        except Exception as e:
            print(f"Error obteniendo carreras: {e}")
            return ()
    
    @staticmethod
    @lru_cache(maxsize=1)
    def get_all_careers_full() -> tuple:
        """Obtener todas las carreras con TODOS sus datos (skills + jobs)
        Para cargar en cache del frontend y evitar múltiples llamadas
        Cacheado: solo se guarda 1 resultado ya que no toma parámetros
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Obtener todas las carreras
                    cursor.execute(f"SELECT ID, CARRERA, DESCRIPCION, AFINIDAD, URL FROM {ORACLE_SCHEMA}.CARRERAS_NUEVO ORDER BY CARRERA")
                    rows = cursor.fetchall()
                    
                    careers = []
                    for row in rows:
                        career_id = row[0]
                        
                        # Obtener skills de esta carrera
                        try:
                            cursor.execute(
                                f"""SELECT S.NOMBRE FROM {ORACLE_SCHEMA}.SKILLS S
                                   INNER JOIN {ORACLE_SCHEMA}.CARRERAS_SKILLS CS ON S.ID = CS.FK_SKILLS
                                   WHERE CS.FK_CARRERA = :1
                                   ORDER BY S.NOMBRE""",
                                (career_id,)
                            )
                            skills = [skill[0] for skill in cursor.fetchall()]
                        except:
                            skills = []
                        
                        # Obtener tareas/jobs de esta carrera
                        cursor.execute(
                            f"""SELECT T.NOMBRE FROM {ORACLE_SCHEMA}.TAREAS T
                               INNER JOIN {ORACLE_SCHEMA}.CARRERA_TAREAS CT ON T.ID = CT.FK_TAREA
                               WHERE CT.FK_CARRERA = :1
                               ORDER BY T.NOMBRE""",
                            (career_id,)
                        )
                        jobs = [job[0] for job in cursor.fetchall()]
                        
                        careers.append({
                            'id': career_id,
                            'name': row[1],
                            'description': row[2],
                            'afinidad': row[3],
                            'url': CareerService._build_image_url(row[4]),
                            'skills': skills,
                            'jobs': jobs
                        })
                    
                    # Log del payload para debug
                    print(f"\n✓ Carreras completas cargadas desde BD ({len(careers)} carreras):")
                    for career in careers:
                        print(f"  - ID: {career['id']}, Nombre: {career['name']}, URL: {career['url']}, Skills: {len(career['skills'])}, Jobs: {len(career['jobs'])}")
                    
                    return tuple(careers)
        except Exception as e:
            print(f"Error obteniendo carreras completas: {e}")
            return ()
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_career_by_id(career_id: int) -> dict:
        """
        Obtener una carrera por ID con sus skills desde la BD
        
        Args:
            career_id: ID de la carrera
            
        Returns:
            Dict con datos de la carrera y lista de skills
            
        Nota: Cacheado hasta 128 carreras diferentes
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Obtener carrera
                    cursor.execute(
                        f"SELECT ID, CARRERA, DESCRIPCION FROM {ORACLE_SCHEMA}.CARRERAS_NUEVO WHERE ID = :1",
                        (career_id,)
                    )
                    row = cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    # Obtener skills de esta carrera
                    cursor.execute(
                        f"""SELECT S.NOMBRE FROM {ORACLE_SCHEMA}.SKILLS S
                           INNER JOIN {ORACLE_SCHEMA}.CARRERAS_SKILLS CS ON S.ID = CS.FK_SKILLS
                           WHERE CS.FK_CARRERA = :1
                           ORDER BY S.NOMBRE""",
                        (career_id,)
                    )
                    skills_rows = cursor.fetchall()
                    skills = [skill[0] for skill in skills_rows]
                    
                    return {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'skills': skills
                    }
        except Exception as e:
            print(f"Error obteniendo carrera {career_id}: {e}")
            return None


if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBA: CareerService")
    print("=" * 70)
    
    print("\n✓ Obteniendo todas las carreras:")
    all_careers = CareerService.get_all_careers()
    for career in all_careers:
        print(f"  - {career}")
    
    print("\n✓ Obteniendo carrera por ID (1):")
    career = CareerService.get_career_by_id(1)
    print(f"  {career}")
    
    print("\n" + "=" * 70)
