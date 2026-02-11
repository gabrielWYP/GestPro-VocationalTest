"""
Servicio para registrar y gestionar visitas de usuarios no autenticados
Almacena datos de visitantes basado en visitor_id (cookie UUID)
"""
import logging
from datetime import datetime
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA

logger = logging.getLogger(__name__)


class VisitsService:
    """Servicio para rastrear visitas de usuarios anónimos"""
    
    @staticmethod
    def register_visit(visitor_id: str, page: str, user_agent: str = None, ip_address: str = None, device_type: str = None) -> dict:
        """
        Registra o actualiza una visita en la base de datos
        
        Args:
            visitor_id: UUID único del visitante (desde cookie)
            page: Página visitada (ej: '/', '/careers', '/test')
            user_agent: String del navegador/dispositivo
            ip_address: Dirección IP del visitante
            device_type: Tipo de dispositivo (mobile, tablet, desktop)
            
        Returns:
            dict con {success: bool, message: str, visitor_data: dict}
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Primero, verificar si el visitante ya existe
                    check_query = f"""
                    SELECT CANTIDAD_VISITAS, ULTIMA_VISITA 
                    FROM {ORACLE_SCHEMA}.VISITAS
                    WHERE VISITOR_ID = :visitor_id
                    """
                    
                    cursor.execute(check_query, {'visitor_id': visitor_id})
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Actualizar visita existente
                        cantidad_visitas = existing[0] + 1
                        
                        update_query = f"""
                        UPDATE {ORACLE_SCHEMA}.VISITAS
                        SET ULTIMA_VISITA = SYSDATE,
                            CANTIDAD_VISITAS = :cantidad_visitas,
                            PAGINA = :pagina,
                            USER_AGENT = :user_agent,
                            IP_ADDRESS = :ip_address,
                            DEVICE_TYPE = :device_type
                        WHERE VISITOR_ID = :visitor_id
                        """
                        
                        cursor.execute(update_query, {
                            'visitor_id': visitor_id,
                            'cantidad_visitas': cantidad_visitas,
                            'pagina': page,
                            'user_agent': user_agent,
                            'ip_address': ip_address,
                            'device_type': device_type
                        })
                        
                        conn.commit()
                        logger.info(f"✓ Visita actualizada para visitor_id: {visitor_id} (Visita #{cantidad_visitas})")
                        
                        return {
                            'success': True,
                            'message': 'Visita actualizada',
                            'visitor_data': {
                                'visitor_id': visitor_id,
                                'cantidad_visitas': cantidad_visitas,
                                'page': page
                            }
                        }
                    else:
                        # Crear nueva visita
                        insert_query = f"""
                        INSERT INTO {ORACLE_SCHEMA}.VISITAS 
                        (VISITOR_ID, PAGINA, USER_AGENT, IP_ADDRESS, DEVICE_TYPE, PRIMERA_VISITA, ULTIMA_VISITA, CANTIDAD_VISITAS)
                        VALUES (:visitor_id, :pagina, :user_agent, :ip_address, :device_type, SYSDATE, SYSDATE, 1)
                        """
                        
                        cursor.execute(insert_query, {
                            'visitor_id': visitor_id,
                            'pagina': page,
                            'user_agent': user_agent,
                            'ip_address': ip_address,
                            'device_type': device_type
                        })
                        
                        conn.commit()
                        logger.info(f"✓ Nueva visita registrada para visitor_id: {visitor_id}")
                        
                        return {
                            'success': True,
                            'message': 'Visita registrada',
                            'visitor_data': {
                                'visitor_id': visitor_id,
                                'cantidad_visitas': 1,
                                'page': page
                            }
                        }
                        
        except Exception as e:
            logger.error(f"Error registrando visita: {str(e)}")
            return {
                'success': False,
                'message': f'Error registrando visita: {str(e)}',
                'visitor_data': None
            }
    
    @staticmethod
    def get_visitor_info(visitor_id: str) -> dict:
        """
        Obtiene información de un visitante específico
        
        Args:
            visitor_id: UUID único del visitante
            
        Returns:
            dict con información del visitante o None
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    query = f"""
                    SELECT VISITOR_ID, PRIMEIRA_VISITA, ULTIMA_VISITA, CANTIDAD_VISITAS, PAGINA, DEVICE_TYPE
                    FROM {ORACLE_SCHEMA}.VISITAS
                    WHERE VISITOR_ID = :visitor_id
                    """
                    
                    cursor.execute(query, {'visitor_id': visitor_id})
                    result = cursor.fetchone()
                    
                    if result:
                        return {
                            'visitor_id': result[0],
                            'primera_visita': result[1],
                            'ultima_visita': result[2],
                            'cantidad_visitas': result[3],
                            'pagina': result[4],
                            'device_type': result[5]
                        }
                    return None
                    
        except Exception as e:
            logger.error(f"Error obteniendo info del visitante: {str(e)}")
            return None
    
    @staticmethod
    def get_visit_statistics() -> dict:
        """
        Obtiene estadísticas generales de visitas
        
        Returns:
            dict con estadísticas de visitas
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Total de visitantes únicos
                    cursor.execute(f"SELECT COUNT(DISTINCT VISITOR_ID) FROM {ORACLE_SCHEMA}.VISITAS")
                    total_visitors = cursor.fetchone()[0]
                    
                    # Total de visitas registradas
                    cursor.execute(f"SELECT SUM(CANTIDAD_VISITAS) FROM {ORACLE_SCHEMA}.VISITAS")
                    total_visits = cursor.fetchone()[0] or 0
                    
                    # Visitantes por dispositivo
                    cursor.execute(f"""
                    SELECT DEVICE_TYPE, COUNT(DISTINCT VISITOR_ID) as count
                    FROM {ORACLE_SCHEMA}.VISITAS
                    GROUP BY DEVICE_TYPE
                    """)
                    devices = {row[0]: row[1] for row in cursor.fetchall()}
                    
                    # Páginas más visitadas
                    cursor.execute(f"""
                    SELECT PAGINA, COUNT(DISTINCT VISITOR_ID) as visitor_count, SUM(CANTIDAD_VISITAS) as total_visits
                    FROM {ORACLE_SCHEMA}.VISITAS
                    GROUP BY PAGINA
                    ORDER BY visitor_count DESC
                    """)
                    top_pages = [
                        {'page': row[0], 'unique_visitors': row[1], 'total_visits': row[2]}
                        for row in cursor.fetchall()
                    ]
                    
                    return {
                        'total_unique_visitors': total_visitors,
                        'total_visits': total_visits,
                        'visits_per_device': devices,
                        'top_visited_pages': top_pages
                    }
                    
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {}
