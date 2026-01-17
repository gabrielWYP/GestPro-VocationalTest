"""Test directo sin pool para aislar el problema"""
import os
from pathlib import Path
from dotenv import load_dotenv
import oracledb

# Cargar .env
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(env_path)

ORACLE_USER = os.environ.get('ORACLE_USER', 'ADMIN')
ORACLE_PASSWORD = os.environ.get('ORACLE_PASSWORD', '')
ORACLE_CONNECTION_STRING = os.environ.get('ORACLE_CONNECTION_STRING', '')

print("=" * 70)
print("TEST DIRECTO DE CONEXIÓN (SIN POOL)")
print("=" * 70)
print(f"\nCredenciales:")
print(f"  Usuario: {ORACLE_USER}")
print(f"  Connection String: {ORACLE_CONNECTION_STRING[:50]}..." if len(ORACLE_CONNECTION_STRING) > 50 else f"  Connection String: {ORACLE_CONNECTION_STRING}")
print()

try:
    print("Intentando conexión directa con oracledb.connect()...")
    conn = oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_CONNECTION_STRING
    )
    print("✅ CONEXIÓN DIRECTA EXITOSA!\n")
    
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM DUAL")
    result = cursor.fetchone()
    print(f"✅ Query ejecutada: SELECT 1 FROM DUAL → {result[0]}\n")
    
    cursor.close()
    conn.close()
    
except oracledb.Error as e:
    print(f"❌ oracledb.Error: {str(e)}\n")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}\n")
    import traceback
    traceback.print_exc()
