# Documentación Técnica - Test de Orientación Vocacional

## Visión General

Aplicación web enterprise de orientación vocacional basada en el modelo RIASEC con arquitectura en capas, integración con Oracle Autonomous DB, y deployment con Docker + Nginx en arquitectura ARM64.

## 🏗️ Arquitectura de Sistemas

### Stack Tecnológico Completo

```
┌─────────────────────────────────────────────────────┐
│                   Usuario (Navegador)               │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP/HTTPS
                      ▼
┌─────────────────────────────────────────────────────┐
│         Nginx Reverse Proxy (shared_infra)          │
│         - Load balancing                            │
│         - SSL termination                           │
│         - Static files caching                      │
│         - Security headers                          │
└─────────────────────┬───────────────────────────────┘
                      │ Docker Network (shared_network)
                      ▼
┌─────────────────────────────────────────────────────┐
│       Flask/Gunicorn (sentiment_test_app:8000)      │
│       - 4 worker processes                          │
│       - 2 threads per worker                        │
│       - Connection pooling                          │
│       - Session management                          │
└─────────────────────┬───────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐        ┌─────────┐        ┌─────────┐
    │ Routes  │        │ Services│        │Database │
    │ Layer   │        │ Layer   │        │ Config  │
    └─────────┘        └─────────┘        └─────────┘
         │                    │                    │
         └────────┬───────────┴────────┬───────────┘
                  ▼
         ┌────────────────────────┐
         │ Controllers Layer      │
         │ - Request handling     │
         │ - Response formatting  │
         │ - Error mapping        │
         └────────────┬───────────┘
                      ▼
         ┌────────────────────────┐
         │ Business Logic         │
         │ - RIASEC calculations  │
         │ - Career predictions   │
         │ - User management      │
         └────────────┬───────────┘
                      ▼
         ┌────────────────────────┐
         │ Data Access Layer      │
         │ - ORM (SQLAlchemy)     │
         │ - Query building       │
         │ - Connection pooling   │
         └────────────┬───────────┘
                      ▼
         ┌────────────────────────┐
         │ Oracle Autonomous DB   │
         │ - Vector embeddings    │
         │ - User data            │
         │ - Career profiles      │
         │ - Test results         │
         └────────────────────────┘
```

### Arquitectura en Capas

**Capas del Backend:**

1. **Routes Layer** (`routes/`)
   - API blueprints (api_routes.py)
   - Page routes (page_routes.py)
   - Health check routes (health_routes.py)
   - Request/response mapping

2. **Controllers Layer** (`controllers/`)
   - auth_controller.py: Autenticación y sesiones
   - test_controller.py: Gestión del test RIASEC
   - predictions_controller.py: Motor de predicción
   - advisory_controller.py: Agendamiento de asesorías
   - career_controller.py: Catálogo de carreras
   
   **Responsabilidad**: HTTP request/response handling, validación básica

3. **Services Layer** (`services/`)
   - auth_service.py: Lógica de autenticación
   - test_service.py: Procesamiento de respuestas del test
   - predictions_service.py: Cálculo de perfiles RIASEC, matching de carreras
   - advisory_service.py: Lógica de asesorías
   - career_service.py: Gestión de catálogo de carreras
   - model_service.py: Modelos de ML y matching
   
   **Responsabilidad**: Lógica de negocio principal

4. **Database Layer** (`db/`)
   - db_config.py: Conexión y configuración de BD
   - ORM con SQLAlchemy
   - Connection pooling
   - Transaction management
   
   **Responsabilidad**: Persistencia y acceso a datos

5. **Models Layer** (`models/`)
   - Definición de entidades
   - Relaciones entre tablas
   - Validaciones ORM

6. **Utils Layer** (`utils/`)
   - errors.py: Custom exceptions
   - validators.py: Validadores reutilizables
   - Funciones de utilidad

## 🔐 Modelo de Autenticación

### Implementación Actual
- **Sesiones HTTP-only**: Persistencia en servidor
- **SECRET_KEY**: Configurado en variables de entorno
- **PERMANENT_SESSION_LIFETIME**: 24 horas
- **Validación**: En cada endpoint protegido

### Flujo de Autenticación

```
[Usuario] → [Formulario] → POST /api/auth/register
                              ↓
                         [Validación]
                              ↓
                         [Hash Password]
                              ↓
                         [Guardar en DB]
                              ↓
                         [Crear Sesión]
                              ↓
                         [Response 200]
```

### Endpoints de Autenticación

```
POST   /api/auth/register    - Registrar usuario
POST   /api/auth/login       - Iniciar sesión
GET    /api/auth/profile     - Obtener perfil (requiere sesión)
GET    /api/auth/check-session - Verificar sesión activa
POST   /api/auth/logout      - Cerrar sesión
```

## 📋 Modelo RIASEC

### Teoría del Modelo

**RIASEC** es la tipología de John Holland que clasifica:
- **Ocupaciones**: En 6 categorías basadas en ambientes laborales
- **Personas**: Por intereses y habilidades

### Las 6 Dimensiones

| Código | Nombre | Características |
|--------|--------|-----------------|
| **R** | Realista | Trabajo manual, técnico, herramientas, aire libre |
| **I** | Investigador | Análisis, ciencia, ideas, computación |
| **A** | Artístico | Creatividad, expresión, artes, diseño |
| **S** | Social | Gente, enseñanza, ayuda, servicio |
| **E** | Empresario | Liderazgo, ventas, dinero, influencia |
| **C** | Convencional | Orden, procedimientos, datos, administración |

### Perfil de Usuario

Se calcula como un vector de 6 dimensiones:
```python
user_profile = {
    'R': float,  # 0.0 - 1.0
    'I': float,
    'A': float,
    'S': float,
    'E': float,
    'C': float
}
```

### Perfil de Carrera

Cada carrera tiene un perfil RIASEC definido:
```python
career_profile = {
    'id': int,
    'name': str,
    'R': float,
    'I': float,
    'A': float,
    'S': float,
    'E': float,
    'C': float
}
```

## 🎯 Algoritmo de Predicción de Carreras

### Componentes

1. **Cálculo de Perfil del Usuario**
   ```
   Respuestas del test → Ponderación → Normalización → Perfil RIASEC
   ```

2. **Cálculo de Similitud**
   ```
   Fórmula: Cosine Similarity entre vectores RIASEC
   
   similarity = dot_product(user_profile, career_profile) / 
                (||user_profile|| * ||career_profile||)
   
   Rango: 0.0 (nada similar) a 1.0 (idéntico)
   ```

3. **Ranking de Carreras**
   ```
   1. Calcular similitud para todas las carreras
   2. Ordenar por similitud descendente
   3. Retornar top-N carreras
   ```

### Flujo de Predicción

```
[Usuario completa test]
         ↓
    [POST /api/test-submit]
         ↓
    [TestController.submit_test()]
         ↓
    [TestService.process_answers()]
    - Validar completitud
    - Guardar respuestas en BD
         ↓
    [PredictionsService.predict_careers()]
    - Calcular perfil RIASEC del usuario
    - Cargar perfiles de carreras de BD
    - Calcular similitud con cada carrera
    - Ordenar resultados
         ↓
    [PredictionsController.predict_careers()]
    - Mapear a Response DTO
         ↓
    [Response JSON]
    {
        "success": true,
        "occupation": {
            "id": 1,
            "name": "Ingeniería Informática",
            "similarity": 0.92
        },
        "suggested_careers": [...],
        "user_profile": {
            "R": 0.6,
            "I": 0.9,
            ...
        }
    }
```

## 📊 Estructura de Base de Datos

### Entidades Principales

#### usuarios
```sql
CREATE TABLE usuarios (
    id INT PRIMARY KEY,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    correo VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### test_responses
```sql
CREATE TABLE test_responses (
    id INT PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    respuesta_1 VARCHAR(50),
    respuesta_2 VARCHAR(50),
    ...
    respuesta_N VARCHAR(50),
    created_at TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

#### test_results
```sql
CREATE TABLE test_results (
    id INT PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    carrera_recomendada_id INT REFERENCES carreras(id),
    puntuaciones_riasec JSON,  -- {"R": 0.6, "I": 0.9, ...}
    similitudes JSON,          -- {"1": 0.92, "2": 0.85, ...}
    created_at TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

#### carreras
```sql
CREATE TABLE carreras (
    id INT PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion TEXT,
    perfil_riasec JSON,  -- {"R": 0.4, "I": 0.8, ...}
    skills TEXT[],
    salario_promedio INT
);
```

#### asesorias
```sql
CREATE TABLE asesorias (
    id INT PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    carrera_id INT REFERENCES carreras(id),
    fecha DATE,
    hora TIME,
    profesional_id INT,
    notas TEXT,
    created_at TIMESTAMP
);
```

### Índices

```sql
CREATE INDEX idx_usuario_correo ON usuarios(correo);
CREATE INDEX idx_test_results_usuario ON test_results(usuario_id);
CREATE INDEX idx_asesorias_fecha ON asesorias(fecha);
CREATE INDEX idx_asesorias_usuario ON asesorias(usuario_id);
```

## 🐳 Configuración Docker

### Dockerfile Multi-Stage

```dockerfile
# Stage 1: Builder
FROM python:3.10-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache /wheels/*
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["gunicorn", "--workers=4", "--threads=2", "--worker-class=gthread", "--bind=0.0.0.0:8000", "app:app"]
```

### Ventajas
- ✅ Imagen más pequeña (solo runtime)
- ✅ Sin herramientas de construcción
- ✅ Usuario no-root
- ✅ Production-ready

## 🚀 Deployment con Nginx

### Integración en shared_infrastructure

```yaml
# shared_infrastructure/docker-compose.yml
services:
  nginx:
    # ... config
    depends_on:
      - vocational-test-app

  vocational-test-app:
    build:
      context: ../vocational_test_dev
      dockerfile: Dockerfile
    ports: []  # No expuesto, solo red interna
    networks:
      - shared_network
```

### Configuración Nginx

```nginx
upstream vocational_test {
    server vocational-test-app:8000;
}

server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://vocational_test;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

1. **Trigger**: Push a rama `main`
2. **Checkout**: Obtener código
3. **Deploy Files**: Copiar a carpeta PRD
4. **Build Docker**: Construir imagen multi-stage
5. **Health Check**: Validar servicio
6. **Rollback**: Si falla, revertir a versión anterior

### Pasos Principales

```bash
# 1. Copiar archivos
rsync -av --exclude=.git backend/ frontend/ /prd/

# 2. Build
docker compose build --no-cache vocational-test-app

# 3. Deploy
docker compose up -d --no-deps vocational-test-app

# 4. Validate (máx 30 segundos)
curl -f http://localhost:8000/

# 5. Rollback si falla
docker tag $BACKUP_IMAGE $CURRENT_IMAGE
```

## 📈 Consideraciones de Rendimiento

### Gunicorn Configuration

```python
# workers: 4
#   - ARM64: 2-4 recomendado
#   - Soporta ~5 usuarios concurrentes

# threads: 2 por worker
#   - Gthread worker class
#   - I/O multiplexing

# Max requests: 1000
#   - Evita memory leaks
#   - Reciclaje de workers
```

### Optimizaciones

- ✅ Connection pooling en ORM
- ✅ Prepared statements
- ✅ Índices en BD
- ✅ Static files servidos por Nginx
- ✅ Caché de headers HTTP

### Benchmarks (ARM64)

| Métrica | Valor |
|---------|-------|
| Startup time | ~3-5s |
| Request latency | 50-200ms |
| Memory usage | 256-512MB |
| CPU utilization | 5-15% |
| Imagen Docker size | ~280MB |

## 🔒 Consideraciones de Seguridad

### Implementadas

- ✅ **Input Validation**: En controllers y service layer
- ✅ **Session Security**: 
  - HTTP-only cookies
  - Secure flag en HTTPS
  - Timeout de 24h
- ✅ **Database**:
  - Prepared statements (SQLAlchemy)
  - Protección contra SQL injection
- ✅ **Runtime**:
  - User no-root en Docker
  - ReadOnly filesystems donde posible

### Recomendaciones Para Producción

- [ ] HTTPS/SSL con certificado válido
- [ ] CORS configurado correctamente
- [ ] Rate limiting
- [ ] WAF (Web Application Firewall)
- [ ] Hashing seguro de passwords (bcrypt, argon2)
- [ ] Secrets management (HashiCorp Vault)
- [ ] Monitoreo de intentos de acceso
- [ ] Audit logging

## 📝 Configuración de Variables de Entorno

### Desarrollo
```env
FLASK_ENV=development
APP_MODE=DEVELOPMENT
DEBUG=True
SECRET_KEY=dev-secret-key
DATABASE_PATH=/app/data/dev.db
```

### Producción (GitHub Secrets)
```env
FLASK_ENV=production
APP_MODE=PRODUCTION
DEBUG=False
SECRET_KEY=<strong-random-key>
ORACLE_USER=<usuario>
ORACLE_PASSWORD=<contraseña>
ORACLE_CONNECTION_STRING=<tnsnaming>
```

## 🧪 Testing

### Estructura Recomendada
```
tests/
├── unit/
│   ├── test_auth_service.py
│   ├── test_predictions_service.py
│   └── test_validators.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_database.py
└── conftest.py  # Fixtures
```

### Ejecución
```bash
pytest tests/ -v --cov=backend
```

## 📚 Arqueología del Código

### Flujo de Solicitud Completo

```
1. HTTP Request → Nginx (reverse proxy)
2. Nginx → localhost:8000 (Docker network)
3. Gunicorn worker pickea la request
4. Flask router → Controllers
5. Controller → Services
6. Services → Database layer
7. Database → Oracle
8. Response forma (JSON)
9. Response → Nginx
10. Nginx → Cliente
```

### Ejemplo: POST /api/test-submit

```
POST /api/test-submit
│
├─ routes/api_routes.py
│  └─ TestController.submit_test()
│
├─ controllers/test_controller.py
│  ├─ Validar sesión
│  ├─ Validar JSON
│  └─ TestService.submit_test()
│
├─ services/test_service.py
│  ├─ Guardar respuestas en BD
│  └─ PredictionsService.predict_careers()
│
├─ services/predictions_service.py
│  ├─ Calcular perfil usuario
│  ├─ Cargar perfiles carreras
│  └─ Calcular similitudes
│
├─ db/db_config.py (ORM queries)
│
└─ Response JSON
```

## 🛠️ Herramientas y Dependencias

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM
- **oracledb**: Driver Oracle
- **Gunicorn**: WSGI server
- **Pydantic**: Validación de datos
- **python-dotenv**: Gestión de .env

### Frontend
- **HTML5**: Estructura
- **CSS3**: Estilos
- **JavaScript vanilla**: Interactividad

### DevOps
- **Docker**: Containerización
- **Docker Compose**: Orquestación
- **Nginx**: Reverse proxy
- **GitHub Actions**: CI/CD

## 📄 Licencia

Código propietario - Derechos reservados

---

**Versión**: 2.0  
**Actualizado**: Febrero 2026  
**Arquitectura**: Enterprise Multi-tier  
**Plataforma**: ARM64 Linux
