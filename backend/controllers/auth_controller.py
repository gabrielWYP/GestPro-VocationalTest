"""
Controlador de Autenticación
Maneja las peticiones HTTP de registro y login
"""

import logging
from flask import request, jsonify, session
from services.auth_service import AuthService

logger = logging.getLogger(__name__)


class AuthController:
    """Controlador de autenticación"""

    @staticmethod
    def register():
        """
        Endpoint POST /auth/register
        Registra un nuevo usuario
        Body:
        {
            "nombre": "Juan",
            "apellido": "Pérez",
            "correo": "juan@example.com",
            "password": "contraseña123"
        }
        """
        try:
            data = request.get_json()

            # Validar campos requeridos
            required_fields = ['nombre', 'apellido', 'correo', 'password']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'success': False,
                    'message': 'Faltan campos requeridos: nombre, apellido, correo, password'
                }), 400

            # Validar que no estén vacíos
            if not all(data[field].strip() for field in required_fields):
                return jsonify({
                    'success': False,
                    'message': 'Los campos no pueden estar vacíos'
                }), 400

            # Validar longitud mínima de contraseña
            if len(data['password']) < 6:
                return jsonify({
                    'success': False,
                    'message': 'La contraseña debe tener al menos 6 caracteres'
                }), 400

            # Registrar usuario
            result = AuthService.register_user(
                nombre=data['nombre'].strip(),
                apellido=data['apellido'].strip(),
                correo=data['correo'].strip().lower(),
                password=data['password']
            )

            if result['success']:
                return jsonify(result), 201
            else:
                return jsonify(result), 400

        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error en el servidor: {str(e)}'
            }), 500

    @staticmethod
    def login():
        """
        Endpoint POST /auth/login
        Valida credenciales del usuario
        Body:
        {
            "correo": "juan@example.com",
            "password": "contraseña123"
        }
        """
        try:
            data = request.get_json()

            # Validar campos requeridos
            if 'correo' not in data or 'password' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Faltan campos requeridos: correo, password'
                }), 400

            if not data['correo'].strip() or not data['password']:
                return jsonify({
                    'success': False,
                    'message': 'Los campos no pueden estar vacíos'
                }), 400

            # Validar login
            result = AuthService.login_user(
                correo=data['correo'].strip().lower(),
                password=data['password']
            )

            if result['success']:
                # Guardar usuario en sesión
                session.permanent = True
                session['usuario'] = {
                    'nombre': result['user']['nombre'],
                    'apellido': result['user']['apellido'],
                    'correo': result['user']['correo']
                }
                return jsonify(result), 200
            else:
                return jsonify(result), 401

        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error en el servidor: {str(e)}'
            }), 500

    @staticmethod
    def get_profile():
        """
        Endpoint GET /auth/profile/:correo
        Obtiene el perfil de un usuario
        """
        try:
            correo = request.args.get('correo')

            if not correo:
                return jsonify({
                    'success': False,
                    'message': 'Parámetro correo requerido'
                }), 400

            user = AuthService.get_user_by_email(correo.lower())

            if user:
                return jsonify({
                    'success': True,
                    'user': user
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }), 404

        except Exception as e:
            logger.error(f"Error al obtener perfil: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error en el servidor: {str(e)}'
            }), 500

    @staticmethod
    def check_session():
        """
        Endpoint GET /auth/check-session
        Verifica si hay una sesión activa
        Retorna los datos del usuario si existe sesión, sino devuelve no autenticado
        """
        try:
            if 'usuario' in session:
                return jsonify({
                    'success': True,
                    'authenticated': True,
                    'user': session['usuario']
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'authenticated': False,
                    'user': None
                }), 200

        except Exception as e:
            logger.error(f"Error al verificar sesión: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error en el servidor: {str(e)}'
            }), 500

    @staticmethod
    def logout():
        """
        Endpoint POST /auth/logout
        Cierra la sesión del usuario actual
        """
        try:
            if 'usuario' in session:
                session.pop('usuario', None)
                logger.info(f"Usuario deslogueado: {session.get('usuario', {}).get('correo')}")
            
            return jsonify({
                'success': True,
                'message': 'Sesión cerrada exitosamente'
            }), 200

        except Exception as e:
            logger.error(f"Error al cerrar sesión: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error en el servidor: {str(e)}'
            }), 500
