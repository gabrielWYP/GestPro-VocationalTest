"""
Vocational Test API
Aplicación principal - Punto de entrada

Estructura:
- app.py: Inicialización minimal
- config.py: Configuración centralizada
- routes/: Enrutamiento y blueprints
- controllers/: Lógica de request/response
- services/: Lógica de negocio
- db/: Configuración de BD
- utils/: Utilidades y helpers
"""
import logging
import os
import sys
from flask import Flask
from whitenoise import WhiteNoise
from config import DEBUG
from routes import register_blueprints

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#Ci/cd

# Determinar modo de ejecución
APP_MODE = os.getenv('APP_MODE', 'PRODUCTION').upper()
IS_DEVELOPMENT = APP_MODE == 'DEVELOPMENT'

# Crear instancia de Flask
# Especificar rutas correctas para templates y static files
app_dir = os.path.dirname(os.path.abspath(__file__))

# En Docker: app.py está en /app, templates en /app/templates
# En desarrollo: app.py está en backend/, templates en ../frontend/templates
if os.path.exists(os.path.join(app_dir, 'templates')):
    # Docker: templates como sibling de app.py
    template_dir = os.path.join(app_dir, 'templates')
    static_dir = os.path.join(app_dir, 'static')
else:
    # Desarrollo: templates en carpeta frontend hermana
    parent_dir = os.path.dirname(app_dir)
    template_dir = os.path.join(parent_dir, 'frontend', 'templates')
    static_dir = os.path.join(parent_dir, 'frontend', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['DEBUG'] = DEBUG or IS_DEVELOPMENT
# Configurar secret key para sesiones
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas

# Agregar WhiteNoise para servir archivos estáticos en producción
if not IS_DEVELOPMENT:
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=static_dir, index_file=False)

# Registrar blueprints (rutas)
register_blueprints(app)

# Handlers para errores
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint no encontrado'}, 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno: {str(error)}")
    return {'error': 'Error interno del servidor'}, 500


if __name__ == '__main__':
    logger.info(f"🚀 Iniciando Vocational Test API en modo {APP_MODE}")
    
    if IS_DEVELOPMENT:
        # Configuración para DEVELOPMENT - Hot reload activo
        logger.info("⚙️  Modo DEVELOPMENT - Hot reload activado")
        app.run(
            host='localhost',
            port=5000,
            debug=True,
            use_reloader=True
        )
    else:
        # Configuración para PRODUCTION
        logger.info("⚙️  Modo PRODUCTION - Debug desactivado")
        app.run(
            host='0.0.0.0',
            port=8000,
            debug=False,
            use_reloader=False
        )
        
#ci/cd