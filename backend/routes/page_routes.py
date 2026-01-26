"""
Rutas de páginas HTML
Rendering de templates con Jinja2
"""
from flask import Blueprint, render_template
from services.test_service import TestService
from services.career_service import CareerService
from services.advisory_service import AdvisoryService
import json

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


@page_bp.route('/test')
def test():
    """Página del test vocacional"""
    questions = TestService.get_questions()
    total = len(questions)
    return render_template('test.html', questions=questions, total=total)


@page_bp.route('/advisory')
def advisory():
    """Página de asesorías"""
    try:
        booked_slots = AdvisoryService.get_booked_slots()
    except Exception:
        booked_slots = []
    
    return render_template('advisory.html', booked_slots=json.dumps(booked_slots))
