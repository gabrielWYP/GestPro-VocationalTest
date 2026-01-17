"""
Configuración y utilidades para conexión a Oracle Autonomous Database
Soporta thin mode sin instalación de cliente Oracle
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import oracledb

# Cargar variables de entorno desde .env en la raíz del proyecto
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

# Configuración de conexión Oracle Autonomous DB
ORACLE_CONFIG = {
    'user': os.environ.get('ORACLE_USER', ''),
    'password': os.environ.get('ORACLE_PASSWORD', ''),
    'connection_string': os.environ.get('ORACLE_CONNECTION_STRING', ''),
}


def get_oracle_connection():
    """
    Crea una conexión a Oracle Autonomous Database en thin mode
    
    Returns:
        oracledb.Connection: Conexión a la base de datos Oracle
        
    Raises:
        Exception: Si falla la conexión
    """
    if not ORACLE_CONFIG['connection_string']:
        raise ValueError("ORACLE_CONNECTION_STRING no está configurada")
    
    try:
        # Usar thin mode (no requiere cliente Oracle instalado)
        oracledb.init_oracle_client()
    except Exception as e:
        print(f"Nota: init_oracle_client no fue necesario: {e}")
    
    connection = oracledb.connect(
        user=ORACLE_CONFIG['user'],
        password=ORACLE_CONFIG['password'],
        dsn=ORACLE_CONFIG['connection_string']
    )
    
    return connection


def test_connection():
    """
    Prueba la conexión a Oracle Autonomous Database y describe una tabla del esquema ALEJO
    """
    try:
        print("=" * 70)
        print("PRUEBA DE CONEXIÓN A ORACLE AUTONOMOUS DATABASE")
        print("=" * 70)
        print(f"\nIntentando conectar con:")
        print(f"  Usuario: {ORACLE_CONFIG['user']}")
        print(f"  Connection String: {ORACLE_CONFIG['connection_string']}")
        print()
        
        # Conectar
        conn = get_oracle_connection()
        print("✅ CONEXIÓN EXITOSA\n")
        
        # Obtener información de la sesión
        cursor = conn.cursor()
        cursor.execute("SELECT USER FROM DUAL")
        current_user = cursor.fetchone()[0]
        print(f"Usuario actual: {current_user}")
        
        # Listar tablas en el esquema ALEJO (migrations)
        print("\n" + "=" * 70)
        print("TABLAS EN ESQUEMA ALEJO (MIGRATIONS)")
        print("=" * 70 + "\n")
        
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM ALL_TABLES 
            WHERE OWNER = 'ALEJO'
            ORDER BY TABLE_NAME
        """)
        
        tables = cursor.fetchall()
        if tables:
            print(f"Se encontraron {len(tables)} tabla(s):\n")
            for idx, (table_name,) in enumerate(tables, 1):
                print(f"  {idx}. {table_name}")
        else:
            print("No hay tablas en el esquema ALEJO")
            cursor.close()
            conn.close()
            return
        
        # Hacer DESC de la primera tabla encontrada
        first_table = tables[0][0]
        print(f"\n" + "=" * 70)
        print(f"DESCRIPCIÓN DE TABLA: ALEJO.{first_table}")
        print("=" * 70 + "\n")
        
        cursor.execute(f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                DATA_LENGTH,
                DATA_PRECISION,
                DATA_SCALE,
                NULLABLE
            FROM ALL_TAB_COLUMNS
            WHERE TABLE_NAME = '{first_table}' 
            AND OWNER = 'ALEJO'
            ORDER BY COLUMN_ID
        """)
        
        columns = cursor.fetchall()
        print(f"{'COLUMNA':<30} {'TIPO':<20} {'LONG':<8} {'PREC':<6} {'ESCA':<6} {'NULL':<5}")
        print("-" * 75)
        
        for col_name, data_type, data_len, precision, scale, nullable in columns:
            nullable_str = "Y" if nullable == "Y" else "N"
            length_str = str(data_len) if data_len else "-"
            prec_str = str(precision) if precision else "-"
            scale_str = str(scale) if scale else "-"
            
            print(f"{col_name:<30} {data_type:<20} {length_str:<8} {prec_str:<6} {scale_str:<6} {nullable_str:<5}")
        
        # Contar registros
        print(f"\n{'REGISTROS EN LA TABLA':<30} ", end="")
        cursor.execute(f"SELECT COUNT(*) FROM ALEJO.{first_table}")
        row_count = cursor.fetchone()[0]
        print(f"{row_count}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA CONEXIÓN:")
        print(f"   {type(e).__name__}: {str(e)}\n")
        raise


if __name__ == '__main__':
    test_connection()
