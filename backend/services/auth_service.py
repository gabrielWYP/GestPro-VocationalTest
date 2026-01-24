"""
Servicio de Autenticación de Usuarios
Gestiona registro y login de usuarios con contraseñas hasheadas
"""

import hashlib
import logging
from datetime import datetime
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA

logger = logging.getLogger(__name__)


class AuthService:
    """Servicio de autenticación de usuarios"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashea una contraseña usando SHA-256
        Args:
            password: Contraseña en texto plano
        Returns:
            Contraseña hasheada en hexadecimal
        """
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def register_user(nombre: str, apellido: str, correo: str, password: str) -> dict:
        """
        Registra un nuevo usuario en la base de datos
        Args:
            nombre: Nombre del usuario
            apellido: Apellido del usuario
            correo: Email del usuario (debe ser único)
            password: Contraseña en texto plano
        Returns:
            dict con el resultado {'success': bool, 'message': str, 'user_id': int/None}
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Verificar si el usuario ya existe
                    cursor.execute(
                        f"SELECT CORREO FROM {ORACLE_SCHEMA}.USUARIO WHERE CORREO = :correo",
                        {'correo': correo}
                    )
                    if cursor.fetchone():
                        return {
                            'success': False,
                            'message': 'El correo ya está registrado',
                            'user_id': None
                        }

                    # Hashear contraseña
                    password_hash = AuthService.hash_password(password)

                    # Insertar nuevo usuario
                    cursor.execute(
                        f"""INSERT INTO {ORACLE_SCHEMA}.USUARIO (NOMBRE, APELLIDO, CORREO, PASSWORD) 
                           VALUES (:nombre, :apellido, :correo, :password)""",
                        {
                            'nombre': nombre,
                            'apellido': apellido,
                            'correo': correo,
                            'password': password_hash
                        }
                    )
                    conn.commit()

            logger.info(f"Usuario registrado: {correo}")
            return {
                'success': True,
                'message': 'Usuario registrado exitosamente',
                'user_id': None
            }

        except Exception as e:
            logger.error(f"Error al registrar usuario: {str(e)}")
            return {
                'success': False,
                'message': f'Error al registrar: {str(e)}',
                'user_id': None
            }

    @staticmethod
    def login_user(correo: str, password: str) -> dict:
        """
        Valida las credenciales del usuario
        Args:
            correo: Email del usuario
            password: Contraseña en texto plano
        Returns:
            dict con el resultado {'success': bool, 'message': str, 'user': dict/None}
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Buscar usuario por correo
                    cursor.execute(
                        f"""SELECT NOMBRE, APELLIDO, CORREO, PASSWORD 
                           FROM {ORACLE_SCHEMA}.USUARIO WHERE CORREO = :correo""",
                        {'correo': correo}
                    )
                    result = cursor.fetchone()

                    if not result:
                        return {
                            'success': False,
                            'message': 'Correo o contraseña incorrectos',
                            'user': None
                        }

                    nombre, apellido, correo_db, password_hash = result

                    # Verificar contraseña
                    password_input_hash = AuthService.hash_password(password)
                    if password_input_hash != password_hash:
                        return {
                            'success': False,
                            'message': 'Correo o contraseña incorrectos',
                            'user': None
                        }

            logger.info(f"Usuario logueado: {correo}")
            return {
                'success': True,
                'message': 'Login exitoso',
                'user': {
                    'nombre': nombre,
                    'apellido': apellido,
                    'correo': correo_db
                }
            }

        except Exception as e:
            logger.error(f"Error al hacer login: {str(e)}")
            return {
                'success': False,
                'message': f'Error al hacer login: {str(e)}',
                'user': None
            }

    @staticmethod
    def get_user_by_email(correo: str) -> dict:
        """
        Obtiene información de un usuario por su correo
        Args:
            correo: Email del usuario
        Returns:
            dict con datos del usuario o None si no existe
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""SELECT NOMBRE, APELLIDO, CORREO, PASSWORD 
                           FROM {ORACLE_SCHEMA}.USUARIO WHERE CORREO = :correo""",
                        {'correo': correo}
                    )
                    result = cursor.fetchone()

                    if not result:
                        return None

                    nombre, apellido, correo_db, password_hash = result
                    return {
                        'NOMBRE': nombre,
                        'APELLIDO': apellido,
                        'CORREO': correo_db,
                        'PASSWORD': password_hash
                    }

        except Exception as e:
            logger.error(f"Error al obtener usuario: {str(e)}")
            return None
