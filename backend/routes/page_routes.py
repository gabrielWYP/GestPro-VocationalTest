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
    careers_data = CareerService.get_all_careers()
    return render_template('careers.html', careers=careers_data)


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
