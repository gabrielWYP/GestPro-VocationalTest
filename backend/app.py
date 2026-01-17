from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime, timedelta
from db.db_config import get_oracle_connection

app = Flask(__name__)

# Inicialización de base de datos no es necesaria con Oracle Autonomous DB
# Las tablas deben estar creadas en la BD externa

# Definir carreras disponibles
CAREERS = [
    {
        "id": 1,
        "name": "Ingeniería Informática",
        "description": "Desarrollo de software, programación, ciberseguridad, redes.",
        "skills": ["Lógica matemática", "Creatividad tecnológica", "Resolución de problemas"],
        "icon": "💻"
    },
    {
        "id": 2,
        "name": "Medicina",
        "description": "Diagnóstico y tratamiento de enfermedades, cirugía, medicina general.",
        "skills": ["Empatía", "Precisión", "Capacidad analítica"],
        "icon": "🏥"
    },
    {
        "id": 3,
        "name": "Administración de Empresas",
        "description": "Gestión empresarial, recursos humanos, finanzas, emprendimiento.",
        "skills": ["Liderazgo", "Pensamiento estratégico", "Comunicación"],
        "icon": "📊"
    },
    {
        "id": 4,
        "name": "Psicología",
        "description": "Comportamiento humano, salud mental, orientación psicológica.",
        "skills": ["Empatía", "Escucha activa", "Análisis conductual"],
        "icon": "🧠"
    },
    {
        "id": 5,
        "name": "Ingeniería Civil",
        "description": "Diseño y construcción de infraestructuras, proyectos civiles.",
        "skills": ["Visión espacial", "Matemáticas", "Planificación"],
        "icon": "🏗️"
    },
    {
        "id": 6,
        "name": "Artes y Diseño",
        "description": "Diseño gráfico, artes visuales, creatividad artística, multimedia.",
        "skills": ["Creatividad", "Sensibilidad estética", "Expresión artística"],
        "icon": "🎨"
    },
    {
        "id": 7,
        "name": "Derecho",
        "description": "Sistema legal, litigios, asesoría legal, derechos humanos.",
        "skills": ["Análisis crítico", "Argumentación", "Justicia"],
        "icon": "⚖️"
    },
    {
        "id": 8,
        "name": "Educación",
        "description": "Docencia, pedagogía, formación de recursos humanos.",
        "skills": ["Paciencia", "Comunicación clara", "Pasión por enseñar"],
        "icon": "📚"
    }
]

# Preguntas del test
QUESTIONS = [
    {
        "id": 1,
        "question": "¿Qué te atrae más?",
        "options": [
            {"text": "Resolver problemas técnicos y crear soluciones", "careers": [1]},
            {"text": "Ayudar a otros a mejorar su salud", "careers": [2]},
            {"text": "Dirigir y administrar negocios", "careers": [3]},
            {"text": "Entender el comportamiento humano", "careers": [4]}
        ]
    },
    {
        "id": 2,
        "question": "¿Cuál es tu mayor fortaleza?",
        "options": [
            {"text": "Capacidad analítica y lógica", "careers": [1, 7]},
            {"text": "Empatía y sensibilidad", "careers": [2, 4, 8]},
            {"text": "Liderazgo y organización", "careers": [3, 7]},
            {"text": "Creatividad e innovación", "careers": [6, 1]}
        ]
    },
    {
        "id": 3,
        "question": "¿Cómo prefieres trabajar?",
        "options": [
            {"text": "En equipo colaborando con otros", "careers": [3, 4, 8]},
            {"text": "De forma independiente en proyectos específicos", "careers": [1, 6]},
            {"text": "Con responsabilidad directa sobre personas", "careers": [2, 4, 8]},
            {"text": "Trabajando con infraestructuras y sistemas", "careers": [5, 1]}
        ]
    },
    {
        "id": 4,
        "question": "¿Qué tipo de actividades te motivan?",
        "options": [
            {"text": "Actividades que requieran precisión y atención", "careers": [2, 5]},
            {"text": "Proyectos que tengan impacto social", "careers": [4, 8, 7]},
            {"text": "Tareas que demanden pensamiento creativo", "careers": [6, 1]},
            {"text": "Desafíos que requieran estrategia y análisis", "careers": [3, 7]}
        ]
    },
    {
        "id": 5,
        "question": "¿Qué asignatura te apasionaba en la escuela?",
        "options": [
            {"text": "Matemáticas y ciencias", "careers": [1, 2, 5]},
            {"text": "Humanidades e idiomas", "careers": [7, 8, 4]},
            {"text": "Artes y educación física", "careers": [6]},
            {"text": "Todas me interesaban por igual", "careers": [3, 4]}
        ]
    },
    {
        "id": 6,
        "question": "¿Cómo manejas los conflictos?",
        "options": [
            {"text": "Buscando soluciones lógicas y objetivas", "careers": [1, 7]},
            {"text": "Considerando los sentimientos de todos", "careers": [4, 8]},
            {"text": "Mediando y buscando consenso", "careers": [3, 4]},
            {"text": "Aplicando reglas y procedimientos", "careers": [5, 7]}
        ]
    },
    {
        "id": 7,
        "question": "¿Qué tipo de salario/beneficio es más importante para ti?",
        "options": [
            {"text": "Estabilidad y buenos beneficios", "careers": [2, 8]},
            {"text": "Potencial de crecimiento económico", "careers": [3, 1]},
            {"text": "Flexibilidad y libertad de horarios", "careers": [6, 1]},
            {"text": "Satisfacción personal y propósito", "careers": [4, 7, 8]}
        ]
    },
    {
        "id": 8,
        "question": "¿Cuál es tu objetivo profesional principal?",
        "options": [
            {"text": "Innovar y crear nuevas tecnologías", "careers": [1, 6]},
            {"text": "Ayudar directamente a las personas", "careers": [2, 4, 8]},
            {"text": "Tener éxito empresarial", "careers": [3, 1]},
            {"text": "Defender la justicia y los derechos", "careers": [7, 4]}
        ]
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/careers')
def careers():
    return render_template('careers.html', careers=CAREERS)

@app.route('/test')
def test():
    return render_template('test.html', questions=QUESTIONS, total=len(QUESTIONS))

@app.route('/api/test-submit', methods=['POST'])
def submit_test():
    data = request.json
    answers = data.get('answers', [])
    name = data.get('name', 'Anónimo')
    email = data.get('email', '')
    
    # Calcular puntuación por carrera
    career_scores = {career['id']: 0 for career in CAREERS}
    
    for answer_id in answers:
        for question in QUESTIONS:
            for option in question['options']:
                if option['text'] == answer_id:
                    for career_id in option['careers']:
                        career_scores[career_id] += 1
    
    # Encontrar carrera con mayor puntuación
    best_career_id = max(career_scores, key=career_scores.get)
    best_career = next(c for c in CAREERS if c['id'] == best_career_id)
    
    # Guardar resultado en BD Oracle
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO ALEJO.test_results (name, email, result_career, scores) VALUES (:1, :2, :3, :4)',
            (name, email, best_career['name'], json.dumps(career_scores))
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        app.logger.error(f"Error guardando resultado de test: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al guardar resultado'}), 500
    
    return jsonify({
        'success': True,
        'career': best_career,
        'scores': career_scores
    })

@app.route('/advisory')
def advisory():
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT date, time FROM ALEJO.advisories WHERE date >= TRUNC(SYSDATE) ORDER BY date, time'
        )
        booked_slots = [f"{row[0]} {row[1]}" for row in cursor.fetchall()]
        cursor.close()
        conn.close()
    except Exception as e:
        app.logger.error(f"Error obteniendo asesorías: {str(e)}")
        booked_slots = []
    
    return render_template('advisory.html', booked_slots=json.dumps(booked_slots))

@app.route('/api/advisory-submit', methods=['POST'])
def submit_advisory():
    data = request.json
    name = data.get('name', '')
    email = data.get('email', '')
    date = data.get('date', '')
    time = data.get('time', '')
    
    if not all([name, email, date, time]):
        return jsonify({'success': False, 'message': 'Faltan datos'}), 400
    
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO ALEJO.advisories (name, email, date, time) VALUES (:1, :2, :3, :4)',
            (name, email, date, time)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Asesoría agendada para {date} a las {time}'
        })
    except Exception as e:
        if 'UNIQUE' in str(e) or 'constraint' in str(e).lower():
            return jsonify({'success': False, 'message': 'Este horario ya está reservado'}), 400
        app.logger.error(f"Error guardando asesoría: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al guardar asesoría'}), 500

@app.route('/api/available-times')
def available_times():
    date = request.args.get('date', '')
    
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT time FROM ALEJO.advisories WHERE date = :1', (date,))
        booked_times = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
    except Exception as e:
        app.logger.error(f"Error obteniendo horarios: {str(e)}")
        booked_times = []
    
    # Horarios disponibles: 09:00 a 17:00 con intervalos de 30 minutos
    all_times = []
    hour = 9
    minute = 0
    while hour < 17:
        time_str = f"{hour:02d}:{minute:02d}"
        if time_str not in booked_times:
            all_times.append(time_str)
        minute += 30
        if minute == 60:
            minute = 0
            hour += 1
    
    return jsonify({'available_times': all_times})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
