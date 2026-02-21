"""
Lógica de negocio para carreras
"""
from functools import lru_cache
from pathlib import Path
import unicodedata
import logging
import time
from urllib.parse import quote
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA

logger = logging.getLogger(__name__)

class CareerService:
    """Servicio para gestionar carreras"""

    @staticmethod
    @lru_cache(maxsize=1)
    def _local_images_index() -> dict:
        """Indexa imágenes locales por nombre normalizado.
        Soporta DOS rutas:
        1. /app/static/images (en Docker)
        2. vocational_test_dev/frontend/static/images (en desarrollo local)
        """
        current_file = Path(__file__).resolve()
        
        # Intentar ruta Docker primero (/app/static/images)
        images_dir = current_file.parents[1] / 'static' / 'images'
        if not images_dir.exists():
            # Fallback a ruta de desarrollo local
            images_dir = current_file.parents[2] / 'frontend' / 'static' / 'images'
        
        if not images_dir.exists():
            logger.warning(f"Directorio de imágenes no existe en: {images_dir}")
            return {}

        index = {}
        for image_path in images_dir.glob('*.svg'):
            normalized_name = CareerService._normalize_text(image_path.stem)
            if normalized_name:
                index[normalized_name] = image_path.name
        
        logger.info(f"✓ Índice de imágenes locales cargado: {len(index)} imágenes encontradas en {images_dir}")
        for norm_name, filename in list(index.items())[:3]:  # Log primeras 3
            logger.debug(f"  - {norm_name} → {filename}")

        return index

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normaliza texto para comparación flexible (acentos, mayúsculas, espacios)."""
        if not text:
            return ''

        text = unicodedata.normalize('NFKD', text)
        text = ''.join(ch for ch in text if not unicodedata.combining(ch))
        return ' '.join(text.casefold().strip().split())

    @staticmethod
    def _build_local_image_url(career_name: str) -> str:
        """Construye URL local de imagen basada en el nombre de la carrera."""
        normalized_career_name = CareerService._normalize_text(career_name)
        if not normalized_career_name:
            return ''

        image_filename = CareerService._local_images_index().get(normalized_career_name)
        if not image_filename:
            return ''

        url = f"/static/images/{quote(image_filename)}"
        return url
    
    @staticmethod
    def _build_image_url(career_name: str, image_path: str) -> str:
        """
        Prioriza imágenes locales asociadas al nombre de carrera.
        Si no existe imagen local, usa proxy remoto como fallback.
        Estrategia: UNA sola fuente por carrera (local O proxy, nunca ambas)
        """
        # Intenta cargar local primero
        local_url = CareerService._build_local_image_url(career_name)
        if local_url:
            logger.debug(f"📦 CARGA LOCAL: '{career_name}' → {local_url}")
            return local_url

        # Si no hay local, usa proxy como fallback
        if not image_path:
            logger.warning(f"⚠️  Sin imagen para '{career_name}' (ni local ni fallback)")
            return ""

        normalized_path = image_path.strip()
        if normalized_path.startswith('ikigais_images/'):
            normalized_path = normalized_path.split('/', 1)[1]

        encoded_path = quote(normalized_path, safe='/')
        proxy_url = f"/api/image/proxy?path={encoded_path}"
        logger.debug(f"🌐 FALLBACK PROXY: '{career_name}' → {proxy_url}")
        return proxy_url
    @staticmethod
    def clear_cache():
        """Limpiar todo el cache de este servicio"""
        CareerService._local_images_index.cache_clear()
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
                        'url': CareerService._build_image_url(row[1], row[4])
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
                        'url': CareerService._build_image_url(row[1], row[4]),
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
        OPTIMIZADO: 2 queries en lugar de 60+
        Cacheado: solo se guarda 1 resultado ya que no toma parámetros
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Query 1: Obtener todas las carreras
                    cursor.execute(f"SELECT ID, CARRERA, DESCRIPCION, AFINIDAD, URL FROM {ORACLE_SCHEMA}.CARRERAS_NUEVO ORDER BY CARRERA")
                    career_rows = cursor.fetchall()
                    
                    # Query 2: Obtener TODOS los skills mapeados por carrera
                    cursor.execute(f"""
                        SELECT CS.FK_CARRERA, S.NOMBRE 
                        FROM {ORACLE_SCHEMA}.CARRERAS_SKILLS CS
                        INNER JOIN {ORACLE_SCHEMA}.SKILLS S ON S.ID = CS.FK_SKILLS
                        ORDER BY CS.FK_CARRERA, S.NOMBRE
                    """)
                    skills_rows = cursor.fetchall()
                    
                    # Mapear skills por carrera_id
                    skills_by_career = {}
                    for career_id, skill_name in skills_rows:
                        if career_id not in skills_by_career:
                            skills_by_career[career_id] = []
                        skills_by_career[career_id].append(skill_name)
                    
                    # Armar resultado
                    careers = []
                    for row in career_rows:
                        career_id = row[0]
                        careers.append({
                            'id': career_id,
                            'name': row[1],
                            'description': row[2],
                            'afinidad': row[3],
                            'url': CareerService._build_image_url(row[1], row[4]),
                            'skills': skills_by_career.get(career_id, [])
                        })
                    
                    return tuple(careers)
        except Exception as e:
            logger.error(f"Error obteniendo carreras: {e}")
            return ()
    
    @staticmethod
    @lru_cache(maxsize=1)
    def get_all_careers_full() -> tuple:
        """Obtener todas las carreras con TODOS sus datos (skills + jobs)
        Para cargar en cache del frontend y evitar múltiples llamadas
        OPTIMIZADO: 3 queries instead of 120+ (antes hacía 2 queries por carrera)
        Cacheado: solo se guarda 1 resultado ya que no toma parámetros
        """
        t_start = time.time()
        
        try:
            with OracleConnection() as conn:
                # Query 1: Obtener TODAS las carreras
                t_q1 = time.time()
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT ID, CARRERA, DESCRIPCION, AFINIDAD, URL FROM {ORACLE_SCHEMA}.CARRERAS_NUEVO ORDER BY CARRERA")
                    career_rows = cursor.fetchall()
                t_q1_elapsed = time.time() - t_q1
                logger.info(f"⏱️ Query 1 (carreras): {t_q1_elapsed:.3f}s ({len(career_rows)} filas)")
                
                # Query 2: Obtener TODOS los skills con sus carreras (un JOIN)
                t_q2 = time.time()
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT CS.FK_CARRERA, S.NOMBRE 
                        FROM {ORACLE_SCHEMA}.CARRERAS_SKILLS CS
                        INNER JOIN {ORACLE_SCHEMA}.SKILLS S ON S.ID = CS.FK_SKILLS
                        ORDER BY CS.FK_CARRERA, S.NOMBRE
                    """)
                    skills_rows = cursor.fetchall()
                t_q2_elapsed = time.time() - t_q2
                logger.info(f"⏱️ Query 2 (skills): {t_q2_elapsed:.3f}s ({len(skills_rows)} filas)")
                
                # Query 3: Obtener TODOS los jobs con sus carreras (un JOIN)
                t_q3 = time.time()
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT CT.FK_CARRERA, T.NOMBRE 
                        FROM {ORACLE_SCHEMA}.CARRERA_TAREAS CT
                        INNER JOIN {ORACLE_SCHEMA}.TAREAS T ON T.ID = CT.FK_TAREA
                        ORDER BY CT.FK_CARRERA, T.NOMBRE
                    """)
                    jobs_rows = cursor.fetchall()
                t_q3_elapsed = time.time() - t_q3
                logger.info(f"⏱️ Query 3 (jobs): {t_q3_elapsed:.3f}s ({len(jobs_rows)} filas)")
                
            # Mapear skills por carrera_id para acceso O(1)
            t_map = time.time()
            skills_by_career = {}
            for career_id, skill_name in skills_rows:
                if career_id not in skills_by_career:
                    skills_by_career[career_id] = []
                skills_by_career[career_id].append(skill_name)
            
            # Mapear jobs por carrera_id para acceso O(1)
            jobs_by_career = {}
            for career_id, job_name in jobs_rows:
                if career_id not in jobs_by_career:
                    jobs_by_career[career_id] = []
                jobs_by_career[career_id].append(job_name)
            t_map_elapsed = time.time() - t_map
            logger.info(f"⏱️ Mapping (skills+jobs): {t_map_elapsed:.3f}s")
            
            # Armar resultado final
            t_build = time.time()
            careers = []
            for row in career_rows:
                career_id = row[0]
                careers.append({
                    'id': career_id,
                    'name': row[1],
                    'description': row[2],
                    'afinidad': row[3],
                    'url': CareerService._build_image_url(row[1], row[4]),
                    'skills': skills_by_career.get(career_id, []),
                    'jobs': jobs_by_career.get(career_id, [])
                })
            t_build_elapsed = time.time() - t_build
            logger.info(f"⏱️ Build carreras+URLs: {t_build_elapsed:.3f}s ({len(careers)} carreras)")
            
            t_total = time.time() - t_start
            logger.info(f"✓ Total: {t_total:.3f}s (Q1:{t_q1_elapsed:.3f}s Q2:{t_q2_elapsed:.3f}s Q3:{t_q3_elapsed:.3f}s Map:{t_map_elapsed:.3f}s Build:{t_build_elapsed:.3f}s)")
            
            return tuple(careers)
        except Exception as e:
            logger.error(f"Error obteniendo carreras completas: {e}")
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
