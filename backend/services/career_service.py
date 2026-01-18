"""
Lógica de negocio para carreras
"""
from db.db_config import OracleConnection
from config import ORACLE_SCHEMA

class CareerService:
    """Servicio para gestionar carreras"""
    
    @staticmethod
    def get_all_careers() -> list:
        """Obtener todas las carreras con sus skills desde la BD"""
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Obtener carreras
                    cursor.execute(f"SELECT ID, NOMBRE_CARRERA, CARRERA_DESC, CARRERA_ICONO FROM {ORACLE_SCHEMA}.CARRERAS")
                    rows = cursor.fetchall()
                    
                    careers = []
                    for row in rows:
                        career_id = row[0]
                        
                        # Obtener skills de esta carrera
                        cursor.execute(
                            f"""SELECT S.NOMBRE FROM {ORACLE_SCHEMA}.SKILLS S
                               INNER JOIN {ORACLE_SCHEMA}.CARRERAS_SKILLS CS ON S.ID = CS.FK_SKILLS
                               WHERE CS.FK_CARRERA = :1
                               ORDER BY S.NOMBRE""",
                            (career_id,)
                        )
                        skills_rows = cursor.fetchall()
                        skills = [skill[0] for skill in skills_rows]
                        
                        careers.append({
                            'id': career_id,
                            'name': row[1],
                            'description': row[2],
                            'skills': skills,
                            'icon': row[3]
                        })
                    
                    return careers
        except Exception as e:
            print(f"Error obteniendo carreras: {e}")
            return []
    
    @staticmethod
    def get_career_by_id(career_id: int) -> dict:
        """
        Obtener una carrera por ID con sus skills desde la BD
        
        Args:
            career_id: ID de la carrera
            
        Returns:
            Dict con datos de la carrera y lista de skills
        """
        try:
            with OracleConnection() as conn:
                with conn.cursor() as cursor:
                    # Obtener carrera
                    cursor.execute(
                        f"SELECT ID, NOMBRE_CARRERA, CARRERA_DESC FROM {ORACLE_SCHEMA}.CARRERAS WHERE ID = :1",
                        (career_id,)
                    )
                    row = cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    # Obtener skills de esta carrera
                    cursor.execute(
                        f"""SELECT S.NOMBRE FROM {ORACLE_SCHEMA}.SKILLS S
                           INNER JOIN {ORACLE_SCHEMA}.CARRERAS_SKILLS CS ON S.ID = CS.FK_SKILLS
                           WHERE CS.FK_CARRERA = :1
                           ORDER BY S.NOMBRE""",
                        (career_id,)
                    )
                    skills_rows = cursor.fetchall()
                    skills = [skill[0] for skill in skills_rows]
                    
                    return {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'skills': skills
                    }
        except Exception as e:
            print(f"Error obteniendo carrera {career_id}: {e}")
            return None


if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBA: CareerService")
    print("=" * 70)
    
    print("\n✓ Obteniendo todas las carreras:")
    all_careers = CareerService.get_all_careers()
    for career in all_careers:
        print(f"  - {career}")
    
    print("\n✓ Obteniendo carrera por ID (1):")
    career = CareerService.get_career_by_id(1)
    print(f"  {career}")
    
    print("\n" + "=" * 70)
