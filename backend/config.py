"""
Configuración centralizada de la aplicación
"""
import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).resolve().parent

# Flask config
DEBUG = os.environ.get('FLASK_ENV') != 'production'
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-not-for-production')

# Database
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'vocational_test.db')

# Oracle Autonomous DB
ORACLE_USER = os.environ.get('ORACLE_USER', 'ADMIN')
ORACLE_PASSWORD = os.environ.get('ORACLE_PASSWORD', '')
ORACLE_CONNECTION_STRING = os.environ.get('ORACLE_CONNECTION_STRING', '')

# Carrera default schema en Oracle
ORACLE_SCHEMA = 'ALEJO'

# App settings
ADVISORY_START_HOUR = 9
ADVISORY_END_HOUR = 17
ADVISORY_INTERVAL_MINUTES = 30
