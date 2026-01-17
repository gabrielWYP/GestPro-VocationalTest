# Documentación Técnica - Test de Orientación Vocacional

## Resumen de Implementación

Se ha creado una aplicación web completa de test de orientación vocacional con las siguientes características:

## Arquitectura

```
Frontend (HTML/CSS/JavaScript)
         ↓
    Flask Backend (Python)
         ↓
    SQLite Database
```

## Componentes Principales

### 1. Backend (app.py)
- **Framework**: Flask 2.3.3
- **Base de Datos**: SQLite3
- **Puerto**: 80

#### Rutas API Implementadas:
- `GET /` - Página de inicio
- `GET /careers` - Lista de carreras
- `GET /test` - Test interactivo
- `GET /advisory` - Sistema de asesoría
- `POST /api/test-submit` - Procesar respuestas del test
- `POST /api/advisory-submit` - Agendar asesoría
- `GET /api/available-times` - Obtener horarios disponibles

#### Base de Datos:
- **Tabla advisories**: Almacena citas agendadas
  - id, name, email, date, time, created_at
- **Tabla test_results**: Almacena resultados del test
  - id, name, email, result_career, scores, created_at

### 2. Frontend

#### Páginas HTML:
1. **index.html** - Página de inicio con información general
2. **careers.html** - Catálogo de 8 carreras profesionales
3. **test.html** - Test interactivo con 8 preguntas
4. **advisory.html** - Sistema de agendamiento de asesorías

#### Estilos (style.css):
- Diseño responsivo
- Gradientes modernos (Indigo-Púrpura)
- Animaciones suaves
- Interfaz amigable para móviles

### 3. Docker

#### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 80
CMD ["python", "app.py"]
```

#### Características:
- Base ligera (slim) para menor tamaño
- Caché de pip optimizado
- Puerto 80 expuesto
- Compatible con Docker Compose

## Preguntas del Test (8 preguntas)

1. ¿Qué te atrae más? (Orientación general)
2. ¿Cuál es tu mayor fortaleza? (Habilidades)
3. ¿Cómo prefieres trabajar? (Ambiente laboral)
4. ¿Qué tipo de actividades te motivan? (Motivación)
5. ¿Qué asignatura te apasionaba? (Intereses académicos)
6. ¿Cómo manejas los conflictos? (Resolución de problemas)
7. ¿Qué tipo de salario es importante? (Prioridades)
8. ¿Cuál es tu objetivo profesional? (Metas)

## Carreras Disponibles (8 opciones)

1. 💻 **Ingeniería Informática**
2. 🏥 **Medicina**
3. 📊 **Administración de Empresas**
4. 🧠 **Psicología**
5. 🏗️ **Ingeniería Civil**
6. 🎨 **Artes y Diseño**
7. ⚖️ **Derecho**
8. 📚 **Educación**

## Algoritmo de Recomendación

El sistema utiliza un algoritmo de puntuación ponderada:

1. **Captura de respuestas**: Se registra la opción seleccionada por el usuario
2. **Mapeo de carreras**: Cada opción está mapeada a 1-4 carreras relacionadas
3. **Conteo de puntos**: Se incrementa la puntuación de cada carrera según las respuestas
4. **Carrera recomendada**: Se devuelve la carrera con mayor puntuación

```python
# Pseudo-código
scores = {career: 0 for career in all_careers}
for answer in user_answers:
    for career in answer.related_careers:
        scores[career] += 1
best_career = max(scores, key=scores.get)
```

## Instalación y Ejecución

### Requisitos Previos
- Docker instalado
- Puerto 80 disponible

### Pasos

1. **Construcción**:
   ```bash
   cd /mnt/tesis_data/codigo/vocational_test
   docker build -t vocational-test:latest .
   ```

2. **Ejecución**:
   ```bash
   docker run -d -p 80:80 --name vocational-test-container vocational-test:latest
   ```

3. **Acceso**:
   ```
   http://localhost
   ```

### Con Docker Compose

```bash
cd /mnt/tesis_data/codigo/vocational_test
docker-compose up -d
```

## Scripts de Administración

### manage.sh
Gestión de la aplicación:
```bash
./manage.sh start    # Iniciar
./manage.sh stop     # Detener
./manage.sh restart  # Reiniciar
./manage.sh logs     # Ver logs
./manage.sh build    # Construir imagen
./manage.sh rebuild  # Reconstruir todo
./manage.sh status   # Ver estado
```

### install.sh
Instalación rápida:
```bash
./install.sh
```

## Características de Seguridad

- ✓ Validación de entrada en formularios
- ✓ SQLite con prepared statements (protección contra SQL injection)
- ✓ Debug desactivado en producción
- ✓ CORS implícitamente restrictivo

## Mejoras Futuras Recomendadas

1. **Autenticación**
   - Implementar usuario/contraseña
   - JWT tokens
   - OAuth2

2. **Notificaciones**
   - Envío de emails para confirmaciones
   - Recordatorios de asesorías
   - Notificaciones push

3. **Análisis**
   - Dashboard de estadísticas
   - Análisis de tendencias
   - Reportes de resultados

4. **Funcionalidades**
   - Test más extensos
   - Comparación entre carreras
   - Testimonios de egresados
   - Vínculos con universidades

5. **Infraestructura**
   - Migrar a PostgreSQL
   - Implementar caché con Redis
   - Load balancing
   - CI/CD pipeline

## Rendimiento

- Tiempo de carga: < 2 segundos
- Tamaño de imagen Docker: ~160 MB
- Memoria requerida: 128-256 MB
- CPU: Mínimo (Aplicación ligera)

## Estructura de Archivos

```
vocational_test/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Configuración Docker
├── docker-compose.yml    # Composición Docker
├── .dockerignore         # Archivos ignorados por Docker
├── manage.sh            # Script de administración
├── install.sh           # Script de instalación
├── README.md            # Documentación
├── TECHNICAL.md         # Este archivo
├── templates/           # Plantillas HTML
│   ├── index.html
│   ├── careers.html
│   ├── test.html
│   └── advisory.html
├── static/
│   └── css/
│       └── style.css
└── data/
    └── vocational_test.db
```

## Endpoints de la API

### GET /
Página de inicio

### GET /careers
Lista de carreras con descripciones

### GET /test
Interfaz del test de orientación

### GET /advisory
Sistema de agendamiento de asesorías

### POST /api/test-submit
**Body**:
```json
{
  "name": "string",
  "email": "string",
  "answers": ["option1", "option2", ...]
}
```

**Response**:
```json
{
  "success": true,
  "career": {
    "id": 1,
    "name": "Ingeniería Informática",
    "description": "...",
    "skills": [...]
  },
  "scores": {
    "1": 4,
    "2": 2,
    ...
  }
}
```

### POST /api/advisory-submit
**Body**:
```json
{
  "name": "string",
  "email": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:MM"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Asesoría agendada para YYYY-MM-DD a las HH:MM"
}
```

### GET /api/available-times
**Query Parameters**:
- `date` (YYYY-MM-DD)

**Response**:
```json
{
  "available_times": ["09:00", "09:30", "10:00", ...]
}
```

## Consideraciones de Producción

1. **HTTPS**: Usar reverse proxy con Nginx
2. **Autenticación**: Implementar OAuth2 o JWT
3. **Base de Datos**: Migrar a PostgreSQL
4. **Caché**: Usar Redis para sesiones
5. **Logs**: Configurar ELK Stack
6. **Monitoreo**: Prometheus + Grafana
7. **Backup**: Automatizar copias de base de datos

## Licencia

Este proyecto es software de código abierto.

---

Generado: Enero 2024
Versión: 1.0
