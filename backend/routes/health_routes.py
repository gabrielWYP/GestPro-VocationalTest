"""
Rutas de salud y status
"""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'vocational-test-api'
    }), 200


@health_bp.route('/ready')
def readiness_check():
    """Readiness check endpoint"""
    return jsonify({
        'ready': True,
        'service': 'vocational-test-api'
    }), 200
