"""
Rutas de API (JSON endpoints)
"""
from flask import Blueprint
from controllers.test_controller import TestController
from controllers.advisory_controller import AdvisoryController
from controllers.career_controller import CareerController
from controllers.auth_controller import AuthController
from controllers.predictions_controller import PredictionsController

api_bp = Blueprint('api', __name__, url_prefix='/api')


# Auth endpoints
api_bp.add_url_rule('/auth/register', 'register', 
                    AuthController.register, methods=['POST'])
api_bp.add_url_rule('/auth/login', 'login',
                    AuthController.login, methods=['POST'])
api_bp.add_url_rule('/auth/profile', 'get_profile',
                    AuthController.get_profile, methods=['GET'])
api_bp.add_url_rule('/auth/check-session', 'check_session',
                    AuthController.check_session, methods=['GET'])
api_bp.add_url_rule('/auth/logout', 'logout',
                    AuthController.logout, methods=['POST'])

# Test endpoints
api_bp.add_url_rule('/test-submit', 'submit_test', 
                    TestController.submit_test, methods=['POST'])

api_bp.add_url_rule('/test-questions', 'get_test_questions',
                    TestController.get_afirmaciones_controller, methods=['GET'])

api_bp.add_url_rule('/test-status', 'get_test_status',
                    TestController.get_test_status, methods=['GET'])

api_bp.add_url_rule('/reset-test', 'reset_test',
                    TestController.reset_test, methods=['POST'])

api_bp.add_url_rule('/save-answers', 'save_answers',
                    TestController.save_answers, methods=['POST'])

# Predictions endpoints
api_bp.add_url_rule('/predict-careers', 'predict_careers',
                    PredictionsController.predict_careers, methods=['POST'])

# Advisory endpoints
api_bp.add_url_rule('/advisory-submit', 'book_advisory',
                    AdvisoryController.book_advisory, methods=['POST'])
api_bp.add_url_rule('/available-times', 'get_available_times',
                    AdvisoryController.get_available_times, methods=['GET'])
api_bp.add_url_rule('/booked-slots', 'get_booked_slots',
                    AdvisoryController.get_booked_slots, methods=['GET'])

# Career endpoints
api_bp.add_url_rule('/careers/list', 'get_careers_list',
                    CareerController.get_careers_list, methods=['GET'])
api_bp.add_url_rule('/careers/all', 'get_all_careers_full',
                    CareerController.get_all_careers_full, methods=['GET'])
api_bp.add_url_rule('/careers/<int:career_id>/detail', 'get_career_detail',
                    CareerController.get_career_detail, methods=['GET'])
api_bp.add_url_rule('/careers', 'get_all_careers',
                    CareerController.get_all_careers, methods=['GET'])
api_bp.add_url_rule('/careers/<int:career_id>', 'get_career',
                    CareerController.get_career, methods=['GET'])
