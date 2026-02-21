"""
Rutas de páginas HTML
Rendering de templates con Jinja2
"""
from flask import Blueprint, render_template
from services.test_service import TestService
from services.career_service import CareerService

page_bp = Blueprint('pages', __name__)


@page_bp.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@page_bp.route('/careers')
def careers():
    """Página de carreras"""
    return render_template('careers.html')


@page_bp.route('/career-detail')
def career_detail():
    """Página de detalle de carrera"""
    return render_template('career-detail.html')


@page_bp.route('/login')
def login():
    """Página de login"""
    return render_template('login.html')


@page_bp.route('/register')
def register():
    """Página de registro"""
    return render_template('register.html')


@page_bp.route('/test/intro')
def test_intro():
    """Página de introducción al test (requiere estar logueado)"""
    return render_template('test-intro.html')


@page_bp.route('/test/responder')
def test_responder():
    """Página del test vocacional (requiere estar logueado)"""
    questions = TestService.get_questions()
    total = len(questions)
    return render_template('test.html', questions=questions, total=total)


@page_bp.route('/test')
def test():
    """Página del test vocacional - redirige a intro"""
    return test_intro()


@page_bp.route('/advisory')
def advisory():
    """Página de asesorías"""
    return render_template('advisory.html')


@page_bp.route('/predicciones')
def predicciones():
    """Página de predicción de carreras (requiere respuestas completadas)"""
    return render_template('predicciones.html')


@page_bp.route('/upload')
def upload():
    """Página de prueba para subir imágenes a OCI"""
    return render_template('upload.html')


@page_bp.route('/riasec')
def riasec():
    """Página del test RIASEC"""
    return render_template('riasec.html')
