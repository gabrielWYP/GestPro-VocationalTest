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
from flask import Flask
from config import DEBUG
from routes import register_blueprints

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear instancia de Flask
app = Flask(__name__)
app.config['DEBUG'] = DEBUG

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
    logger.info("🚀 Iniciando Vocational Test API")
    app.run(host='0.0.0.0', port=8000, debug=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
