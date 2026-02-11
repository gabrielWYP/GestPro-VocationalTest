# Test de Orientación Vocacional

Una aplicación web enterprise para orientación vocacional que ayuda a usuarios a descubrir su carrera ideal mediante el test RIASEC, predicción de afinidad con profesiones y sistema de asesoría profesional integrado.

## ✨ Características Principales

### 🔐 Autenticación y Sesiones
- Registro de nuevos usuarios con validación de datos
- Login seguro con sesiones persistentes
- Control de acceso mediante autenticación de sesión
- Logout con limpieza de sesión
- Verificación de estado de sesión en tiempo real

### 📋 Test de Orientación Vocacional (RIASEC)
- Test basado en el modelo **RIASEC** (Realista, Investigador, Artístico, Social, Empresario, Convencional)
- Múltiples preguntas (afirmaciones) para evaluación integral
- Obtención progresiva de puntuaciones en las 6 dimensiones
- Sistema de guardado de respuestas en tiempo real
- Reset de test para permitir múltiples intentos
- Validación de completitud antes de envío
- Visualización del estado/progreso del test

### 🎯 Predicción Inteligente de Carreras
- Cálculo automático del perfil RIASEC del usuario
- Motor de predicción que sugiere carreras afines basado en:
  - Similitud del perfil del usuario con requirements de cada carrera
  - Coincidencia en las 6 dimensiones RIASEC
  - Ranking de ocupaciones recomendadas
- Retorna carrera más afín con puntuación de similitud
- Lista completa de carreras sugeridas ordenadas por relevancia
- Exposición del perfil RIASEC del usuario

### 📚 Gestión de Carreras Profesionales
- Base de datos de **8 carreras profesionales** con información detallada:
  1. Ingeniería Informática
  2. Medicina
  3. Administración de Empresas
  4. Psicología
  5. Ingeniería Civil
  6. Artes y Diseño
  7. Derecho
  8. Educación
- Perfiles RIASEC por carrera para matching
- API para consulta de carreras disponibles

### 👨‍💼 Sistema de Asesoría Profesional
- Agendamiento de asesorías con profesionales
- Consulta de horarios disponibles
- Prevención de conflictos de horarios (double booking)
- Confirmación de reservas
- Integración con calendar backend

### 📊 Análisis y Datos
- Almacenamiento de resultados de tests por usuario
- Historial de asesorías agendadas
- Seguimiento de progreso del usuario
- Base de datos persistente para auditoría

### 📱 Interfaz de Usuario
- Frontend responsivo (Desktop y Mobile)
- Plantillas HTML modernas
- Estilos CSS profesionales
- Experiencia interactiva e intuitiva

## 🏗️ Arquitectura Técnica

### Stack Tecnológico
- **Backend**: Flask (Python 3.10)
- **Base de Datos**: SQLite (desarrollo) / Oracle Autonomous DB (producción)
- **Server**: Gunicorn (4 workers, 2 threads)
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Deployment**: Docker + Docker Compose + Nginx (Reverse Proxy)

### Estructura del Proyecto

```
vocational_test_dev/
├── backend/
│   ├── app.py                         # Punto de entrada Flask
│   ├── config.py                      # Configuración centralizada
│   ├── requirements.txt               # Dependencias Python
│   │
│   ├── controllers/                   # Lógica de request/response HTTP
│   │   ├── auth_controller.py        # Registro, login, sesiones
│   │   ├── test_controller.py        # Test RIASEC
│   │   ├── predictions_controller.py # Predicción de carreras
│   │   ├── advisory_controller.py    # Asesorías
│   │   └── career_controller.py      # Gestión de carreras
│   │
│   ├── services/                      # Lógica de negocio
│   │   ├── auth_service.py           # Autenticación
│   │   ├── test_service.py           # Procesamiento del test
│   │   ├── predictions_service.py    # Motor de predicción RIASEC
│   │   ├── advisory_service.py       # Gestión de asesorías
│   │   ├── career_service.py         # Datos de carreras
│   │   └── model_service.py          # Modelos ML/matching
│   │
│   ├── routes/                        # Enrutamiento y blueprints
│   │   ├── api_routes.py             # Endpoints JSON (/api/*)
│   │   ├── health_routes.py          # Health checks
│   │   └── page_routes.py            # Páginas HTML
│   │
│   ├── database/
│   │   ├── db_config.py              # Configuración de conexiones
│   │   └── migrations/               # Migraciones de BD
│   │
│   ├── models/                        # Modelos de datos ORM
│   │
│   └── utils/                         # Utilidades
│       ├── errors.py                 # Clases de error personalizadas
│       └── validators.py             # Validadores de datos
│
├── frontend/
│   ├── templates/                     # Plantillas HTML Jinja2
│   │   ├── index.html                # Página de bienvenida
│   │   ├── login.html                # Formulario de login
│   │   ├── register.html             # Formulario de registro
│   │   ├── test.html                 # Interfaz del test RIASEC
│   │   ├── test-intro.html           # Introducción al test
│   │   ├── predicciones.html         # Resultados y predicciones
│   │   ├── careers.html              # Catálogo de carreras
│   │   ├── career-detail.html        # Detalle de carrera
│   │   └── advisory.html             # Sistema de asesorías
│   │
│   └── static/                        # Archivos estáticos
│       ├── css/                       # Estilos
│       ├── js/                        # Scripts del cliente
│       └── images/                    # Recursos visuales
│
├── scripts/
│   ├── install.sh                    # Script de instalación
│   └── manage.sh                     # Script de gestión
│
├── Dockerfile                         # Imagen Docker multi-stage
├── docker-compose.yml                # Orquestación local
├── TECHNICAL.md                      # Documentación técnica
├── BACKEND_STRUCTURE.md              # Detalle de estructura
└── requirements.txt                  # Dependencias (local)
```

## 🚀 Instalación y Ejecución

### Opción 1: Con Docker Compose (Recomendado - Desarrollo Local)

```bash
cd vocational_test_dev
docker-compose up
```

La aplicación estará disponible en `http://localhost`

### Opción 2: Con Docker (Producción)

```bash
cd vocational_test_dev
docker build -t vocational-test .
docker run -p 8000:8000 vocational-test
```

### Opción 3: Ejecución Local

```bash
cd vocational_test_dev
pip install -r backend/requirements.txt
cd backend
python app.py
```

Accede a:
- `http://localhost:5000` (modo desarrollo con hot-reload)
- `http://localhost:8000` (modo producción)

## 📊 Endpoints API

### Autenticación
- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/check-session` - Verificar sesión activa
- `GET /api/auth/profile` - Obtener perfil de usuario
- `POST /api/auth/logout` - Cerrar sesión

### Test RIASEC
- `GET /api/test-questions` - Obtener preguntas del test
- `POST /api/test-submit` - Enviar respuestas del test
- `GET /api/test-status` - Obtener estado actual del test
- `POST /api/save-answers` - Guardar respuestas parcialmente
- `POST /api/reset-test` - Reiniciar el test

### Predicciones
- `POST /api/predict-careers` - Predecir carreras afines basado en perfil RIASEC

### Asesorías
- `GET /api/available-times` - Obtener horarios disponibles
- `POST /api/advisory-submit` - Agendar asesoría

### Carreras
- Endpoints para explorar información de carreras disponibles

## 🔒 Seguridad

- ✅ Autenticación basada en sesiones HTTP-only
- ✅ Validación de entrada en todos los endpoints
- ✅ Control de acceso mediante autenticación
- ✅ Dockerfile con usuario no-root
- ✅ Environment variables para secretos (no hardcodeados)
- ✅ CORS configurado para desarrollo
- ✅ Secret key para sesiones

## ⚙️ Configuración

### Variables de Entorno Requeridas (Producción)
```env
FLASK_ENV=production
ORACLE_USER=<usuario_autonomousdb>
ORACLE_PASSWORD=<contraseña>
ORACLE_CONNECTION_STRING=<connection_string>
SECRET_KEY=<clave_secreta_sesiones>
APP_MODE=PRODUCTION
```

### En desarrollo
El proyecto usa `.env` local con valores de ejemplo

## 📦 Requisitos

### Con Docker
- Docker
- Docker Compose (opcional)

### Local
- Python 3.10+
- pip
- SQLite3

## 🔄 CI/CD

El proyecto incluye GitHub Actions workflow en `.github/workflows/deploy.yml`:
- ✅ Despliegue automático en push a rama `main`
- ✅ Build de imagen Docker multi-stage
- ✅ Deploy en VM privada con nginx reverse proxy
- ✅ Rollback automático si falla validación
- ✅ Mantenimiento de múltiples servicios en mismo puerto 80
- ✅ Respaldo de imágenes anteriores

## 📝 Documentación Adicional

- [TECHNICAL.md](TECHNICAL.md) - Especificaciones técnicas detalladas
- [BACKEND_STRUCTURE.md](BACKEND_STRUCTURE.md) - Estructura del backend
- Tests: Ver carpeta `/tests`

## 🛠️ Desarrollo Local

```bash
# Activar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o en Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Ejecutar en modo desarrollo
cd backend
python app.py

# Abre http://localhost:5000 en tu navegador
# Los cambios se reflejan automáticamente (hot-reload)
```

## 📚 Modelo RIASEC

**RIASEC** es una clasificación desarrollada por John Holland que tipifica ocupaciones en 6 categorías:

- **R (Realista)**: Trabajo manual, técnico, al aire libre
- **I (Investigador)**: Análisis, investigación científica
- **A (Artístico)**: Creatividad, expresión, artes
- **S (Social)**: Interacción con personas, ayuda, enseñanza
- **E (Empresario)**: Liderazgo, emprendimiento, ventas
- **C (Convencional)**: Orden, procedimientos, administración

El sistema calcula un perfil del usuario en estas 6 dimensiones y lo compara con los perfiles de cada carrera para encontrar el mejor matching.

## 🎯 Algoritmo de Predicción

1. Se calcula el perfil RIASEC del usuario basado en respuestas al test
2. Se compara con los perfiles RIASEC de cada carrera disponible
3. Se calcula una puntuación de similitud (0-1) para cada carrera
4. Las carreras se ordenan por similitud (mayor a menor)
5. Se retorna la carrera más afín y las sugerencias ordenadas

## 📄 Licencia

Proyecto educativo - Derechos reservados
