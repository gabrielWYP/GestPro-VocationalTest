"""
Archivo __init__.py para el paquete routes
"""
from flask import Flask
from .page_routes import page_bp
from .api_routes import api_bp
from .health_routes import health_bp


def register_blueprints(app: Flask):
    """Registrar todos los blueprints en la app"""
    app.register_blueprint(page_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(health_bp)
