"""
Lógica de negocio para gestión de asesorías
"""
from datetime import datetime, timedelta
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA, ADVISORY_START_HOUR, ADVISORY_END_HOUR, ADVISORY_INTERVAL_MINUTES
from utils.errors import DatabaseError


class AdvisoryService:
    """Servicio para gestionar asesorías"""
    
    @staticmethod
    def get_booked_slots(date_from: str = None) -> list:
        """
        Obtener horarios ya reservados
        
        Args:
            date_from: Fecha desde la cual obtener (formato YYYY-MM-DD)
            
        Returns:
            Lista de strings "YYYY-MM-DD HH:MM"
        """
        try:
            with OracleConnection() as conn:
                cursor = conn.cursor()
                
                if not date_from:
                    date_from = datetime.now().strftime('%Y-%m-%d')
                
                cursor.execute(
                    f'SELECT date, time FROM {ORACLE_SCHEMA}.advisories '
                    'WHERE date >= TRUNC(SYSDATE) ORDER BY date, time'
                )
                
                booked_slots = [f"{str(row[0])} {str(row[1])}" for row in cursor.fetchall()]
                cursor.close()
            
            return booked_slots
        except Exception as e:
            raise DatabaseError(f"Error obteniendo asesorías: {str(e)}")
    
    @staticmethod
    def get_available_times(date_str: str) -> list:
        """
        Obtener horarios disponibles para una fecha
        
        Args:
            date_str: Fecha en formato YYYY-MM-DD
            
        Returns:
            Lista de strings en formato "HH:MM"
        """
        try:
            with OracleConnection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    f'SELECT time FROM {ORACLE_SCHEMA}.advisories WHERE date = :1',
                    (date_str,)
                )
                
                booked_times = [str(row[0]) for row in cursor.fetchall()]
                cursor.close()
        except Exception as e:
            raise DatabaseError(f"Error obteniendo horarios: {str(e)}")
        
        # Generar todos los horarios disponibles
        all_times = []
        hour = ADVISORY_START_HOUR
        minute = 0
        
        while hour < ADVISORY_END_HOUR:
            time_str = f"{hour:02d}:{minute:02d}"
            if time_str not in booked_times:
                all_times.append(time_str)
            
            minute += ADVISORY_INTERVAL_MINUTES
            if minute == 60:
                minute = 0
                hour += 1
        
        return all_times
    
    @staticmethod
    def book_advisory(name: str, email: str, date: str, time: str) -> bool:
        """
        Reservar una asesoría
        
        Args:
            name: Nombre del usuario
            email: Email del usuario
            date: Fecha en formato YYYY-MM-DD
            time: Hora en formato HH:MM
            
        Returns:
            True si se reservó exitosamente
            
        Raises:
            DatabaseError: Si falla la BD
        """
        try:
            with OracleConnection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    f'INSERT INTO {ORACLE_SCHEMA}.advisories (name, email, date, time) '
                    'VALUES (:1, :2, :3, :4)',
                    (name, email, date, time)
                )
                
                conn.commit()
                cursor.close()
            
            return True
        except Exception as e:
            error_msg = str(e).upper()
            if 'UNIQUE' in error_msg or 'CONSTRAINT' in error_msg:
                raise DatabaseError(f"Este horario ya está reservado")
            raise DatabaseError(f"Error guardando asesoría: {str(e)}")
