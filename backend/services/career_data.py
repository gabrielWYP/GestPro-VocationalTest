"""
Datos estáticos: Carreras y Preguntas del test
"""

#Cambio para pushear
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
