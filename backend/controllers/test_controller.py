"""
Controlador para el test vocacional
Procesa requests, valida datos y llama servicios
"""
import logging
from flask import request, jsonify, session
from services.test_service import TestService
from services.career_data import CAREERS
from utils.validators import validate_email, validate_name
from utils.errors import ValidationError, DatabaseError


logger = logging.getLogger(__name__)


class TestController:
    """Controlador para operaciones del test"""
    
    @staticmethod
    def submit_test():
        """
        Endpoint POST /api/test-submit
        Procesa respuestas del test y retorna carrera recomendada
        """
        try:
            data = request.json
            
            # Validar datos
            name = data.get('name', '').strip() or 'Anónimo'
            email = data.get('email', '').strip()
            answers = data.get('answers', [])
            
            if not answers:
                return jsonify({
                    'success': False,
                    'message': 'El test debe tener respuestas'
                }), 400
            
            if email and not validate_email(email):
                return jsonify({
                    'success': False,
                    'message': 'Email inválido'
                }), 400
            
            # Calcular puntuación
            career_scores = TestService.calculate_scores(answers)
            best_career = TestService.get_best_career(career_scores)
            
            # Guardar en BD
            try:
                TestService.save_test_result(name, email, best_career['name'], career_scores)
            except DatabaseError as e:
                logger.error(f"Error guardando test: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Error al guardar resultado'
                }), 500
            
            return jsonify({
                'success': True,
                'career': best_career,
                'scores': career_scores
            })
        
        except Exception as e:
            logger.error(f"Error en submit_test: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error procesando test'
            }), 500
            
    @staticmethod
    def get_afirmaciones_controller():
        """
        Endpoint GET /api/test-questions
        Retorna las afirmaciones del test
        """
        try:
            questions = TestService.get_afirmaciones()
            
            return jsonify({
                'success': True,
                'questions': questions
            })
        
        except Exception as e:
            logger.error(f"Error en get_afirmaciones_controller: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo preguntas'
            }), 500

    @staticmethod
    def get_test_status():
        """
        Endpoint GET /api/test-status
        Obtiene el estado del test del usuario logueado
        """
        try:
            if 'usuario' not in session:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no autenticado'
                }), 401
            
            usuario_id = session['usuario'].get('id')
            if not usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'Error: ID de usuario no disponible'
                }), 400
            
            status = TestService.get_test_status(usuario_id)
            
            return jsonify({
                'success': True,
                'status': status
            }), 200
        
        except Exception as e:
            logger.error(f"Error en get_test_status: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error obteniendo estado del test'
            }), 500

    @staticmethod
    def reset_test():
        """
        Endpoint POST /api/reset-test
        Borra TODAS las respuestas del usuario
        """
        try:
            if 'usuario' not in session:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no autenticado'
                }), 401
            
            usuario_id = session['usuario'].get('id')
            if not usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'Error: ID de usuario no disponible'
                }), 400
            
            # Borrar todas las respuestas
            TestService.reset_user_answers(usuario_id)
            
            logger.info(f"Test reseteado para usuario {usuario_id}")
            
            return jsonify({
                'success': True,
                'message': 'Test reseteado exitosamente'
            }), 200
        
        except Exception as e:
            logger.error(f"Error en reset_test: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error al resetear el test'
            }), 500

    @staticmethod
    def save_answers():
        """
        Endpoint POST /api/save-answers
        Guarda respuestas parciales del test (autoguardado por página)
        
        Body:
        {
            "answers": [
                {"afirmacion_id": 1, "riasec_id": 5},
                {"afirmacion_id": 2, "riasec_id": 4},
                ...
            ]
        }
        """
        try:
            # Verificar que el usuario esté logueado
            if 'usuario' not in session:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no autenticado'
                }), 401
            
            usuario_id = session['usuario'].get('id')
            if not usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'Error: ID de usuario no disponible'
                }), 400
            
            data = request.json
            answers = data.get('answers', [])
            
            if not answers:
                return jsonify({
                    'success': False,
                    'message': 'No hay respuestas para guardar'
                }), 400
            
            # Validar estructura de respuestas
            for answer in answers:
                if 'afirmacion_id' not in answer or 'riasec_id' not in answer:
                    return jsonify({
                        'success': False,
                        'message': 'Estructura inválida: se requieren afirmacion_id y riasec_id'
                    }), 400
                
                # Validar que riasec_id sea entre 1 y 5
                if not isinstance(answer['riasec_id'], int) or answer['riasec_id'] < 1 or answer['riasec_id'] > 5:
                    return jsonify({
                        'success': False,
                        'message': 'El puntaje RIASEC debe estar entre 1 y 5'
                    }), 400
            
            # Guardar respuestas
            try:
                TestService.save_answers_batch(usuario_id, answers)
                
                return jsonify({
                    'success': True,
                    'message': f'{len(answers)} respuesta(s) guardada(s) exitosamente'
                }), 200
                
            except DatabaseError as e:
                logger.error(f"Error guardando respuestas: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Error al guardar respuestas'
                }), 500
        
        except Exception as e:
            logger.error(f"Error en save_answers: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error procesando solicitud'
            }), 500
