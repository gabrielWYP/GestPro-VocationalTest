"""
Controlador para el test vocacional
Procesa requests, valida datos y llama servicios
"""
import logging
from flask import request, jsonify
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
