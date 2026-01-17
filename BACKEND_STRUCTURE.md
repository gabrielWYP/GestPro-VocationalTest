# Estructura del Backend - Vocational Test API

## 📁 Estructura de carpetas

```
backend/
├── __init__.py                    # Paquete Python
├── app.py                         # Punto de entrada (minimal)
├── config.py                      # Configuración centralizada
├── requirements.txt
│
├── db/
│   ├── db_config.py              # Conexión Oracle Autonomous DB
│   └── migrations/               # Scripts SQL
│
├── routes/                        # Enrutamiento (blueprints)
│   ├── __init__.py
│   ├── page_routes.py            # Rutas de páginas HTML
│   ├── api_routes.py             # Rutas de API JSON
│   └── health_routes.py          # Health check, readiness
│
├── controllers/                   # Lógica de request/response
│   ├── __init__.py
│   ├── test_controller.py        # Test vocacional
│   ├── advisory_controller.py    # Asesorías
│   └── career_controller.py      # Carreras
│
├── services/                      # Lógica de negocio
│   ├── __init__.py
│   ├── career_data.py            # Datos estáticos (CAREERS, QUESTIONS)
│   ├── test_service.py           # Lógica del test
│   ├── advisory_service.py       # Lógica de asesorías
│   └── career_service.py         # Lógica de carreras
│
├── utils/                         # Utilidades
│   ├── __init__.py
│   ├── errors.py                 # Excepciones personalizadas
│   └── validators.py             # Funciones de validación
│
├── templates/                     # Templates Jinja2
│   ├── index.html
│   ├── test.html
│   ├── careers.html
│   └── advisory.html
│
└── static/                        # Archivos estáticos
    ├── css/
    │   └── style.css
    └── js/
        ├── index.js
        ├── test.js
        └── advisory.js
```

---

## 🔄 Flujo de una Request

### Ejemplo: POST /api/test-submit

```
1. Cliente → POST /api/test-submit { answers: [...], name: "Juan", email: "juan@email.com" }

2. routes/api_routes.py
   ↓
   Registra: POST /api/test-submit → TestController.submit_test()

3. controllers/test_controller.py
   ├─ Valida datos (email, nombre, respuestas)
   ├─ Llama a TestService
   └─ Formatea response

4. services/test_service.py
   ├─ Calcula puntuación: calculate_scores(answers)
   ├─ Obtiene mejor carrera: get_best_career(scores)
   └─ Persiste en BD: save_test_result(...)

5. db/db_config.py
   ├─ Abre conexión Oracle
   ├─ Ejecuta: INSERT INTO ALEJO.test_results (...)
   └─ Retorna resultado

6. Response
   ↓
   { success: true, career: {...}, scores: {...} }
```

---

## 📋 Responsabilidades por capa

### `routes/` - Enrutamiento
- Mapear URLs a funciones
- Elegir si renderizar HTML o JSON
- Registrar blueprints en app.py

```python
# page_routes.py
@page_bp.route('/test')
def test():
    questions = TestService.get_questions()
    return render_template('test.html', questions=questions)

# api_routes.py
api_bp.add_url_rule('/api/test-submit', ..., TestController.submit_test, methods=['POST'])
```

### `controllers/` - Control de Request/Response
- Validar entrada del usuario
- Llamar servicios
- Formatear respuesta
- Manejo de errores

```python
class TestController:
    @staticmethod
    def submit_test():
        # 1. Validar datos
        data = request.json
        if not validate_email(data['email']):
            return jsonify({'error': 'Email inválido'}), 400
        
        # 2. Llamar service
        TestService.calculate_scores(data['answers'])
        
        # 3. Retornar response
        return jsonify({'success': True, ...})
```

### `services/` - Lógica de Negocio
- Reglas de negocio puras
- Independiente de Framework Flask
- Fácil de testear
- Acceso a BD

```python
class TestService:
    @staticmethod
    def calculate_scores(answers: list) -> dict:
        # Lógica pura: calcular puntuación
        career_scores = {...}
        return career_scores
    
    @staticmethod
    def save_test_result(name, email, career_name, scores):
        # Acceso a BD Oracle
        conn = get_oracle_connection()
        cursor.execute(...)
```

### `db/` - Acceso a datos
- Conexiones a BD
- Queries
- Modelos

### `utils/` - Utilidades
- Validaciones reutilizables
- Excepciones personalizadas
- Funciones auxiliares

### `config.py` - Configuración
- Variables de entorno
- Configuración centralizada
- Constantes de la aplicación

### `app.py` - Punto de entrada
- Crear instancia de Flask
- Registrar blueprints
- Handlers de error
- Minimal (solo ~40 líneas)

---

## ✨ Ventajas de esta estructura

✅ **Separación de responsabilidades** - Cada capa hace una cosa bien  
✅ **Fácil de testear** - Services no dependen de Flask  
✅ **Escalable** - Agregar features es sencillo  
✅ **Mantenible** - Código limpio y organizado  
✅ **Reutilizable** - Services se usan en múltiples controllers  
✅ **Configurable** - Un solo lugar para configurar (config.py)  

---

## 🚀 Cómo agregar una nueva feature

Si quiero agregar un endpoint que envíe email después de una asesoría:

### 1. Crear service (services/email_service.py)
```python
class EmailService:
    @staticmethod
    def send_advisory_confirmation(email, date, time):
        # Lógica de envío de email
        pass
```

### 2. Agregar a controller (controllers/advisory_controller.py)
```python
def book_advisory():
    ...
    EmailService.send_advisory_confirmation(email, date, time)
```

### 3. Eso es todo. La ruta ya existe en api_routes.py

No necesitas tocar rutas, solo agregar la lógica en service y llamarla en controller.

---

## 📝 Notas importantes

- **Templates** se sirven desde `routes/page_routes.py` con Flask
- **APIs JSON** se sirven desde `routes/api_routes.py` con controllers
- **Base de datos** se accede siempre a través de services
- **Logging** centralizado en app.py
- **Errores personalizados** en utils/errors.py

---

## 🔗 Imports típicos

En un controller:
```python
from services.test_service import TestService
from utils.validators import validate_email
from utils.errors import ValidationError
```

En un service:
```python
from db.db_config import get_oracle_connection
from config import ORACLE_SCHEMA
from utils.errors import DatabaseError
```

En una ruta:
```python
from flask import Blueprint, render_template
from services.test_service import TestService
```
