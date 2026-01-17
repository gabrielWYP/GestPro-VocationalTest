# Test de Orientación Vocacional

Una aplicación web moderna para ayudar a los usuarios a descubrir su carrera ideal a través de un test de orientación vocacional.

## Características

- ✨ **Test Interactivo**: 8 preguntas diseñadas para analizar intereses y habilidades
- 📚 **8 Carreras Profesionales**: Explora diferentes opciones de estudio
- 📊 **Resultados Personalizados**: Recomendación basada en las respuestas
- 👨‍💼 **Asesoría Profesional**: Sistema de agendamiento de asesorías
- 📱 **Diseño Responsivo**: Funciona en dispositivos móviles y desktop
- 💾 **Base de Datos**: Almacenamiento de resultados y citas

## Carreras Disponibles

1. **Ingeniería Informática** - Desarrollo de software, programación, ciberseguridad
2. **Medicina** - Diagnóstico y tratamiento, cirugía
3. **Administración de Empresas** - Gestión empresarial, emprendimiento
4. **Psicología** - Comportamiento humano, salud mental
5. **Ingeniería Civil** - Diseño de infraestructuras
6. **Artes y Diseño** - Diseño gráfico, artes visuales
7. **Derecho** - Sistema legal, litigios
8. **Educación** - Docencia, formación

## Requisitos Previos

- Docker
- Docker Compose (opcional)

O si ejecutas localmente:
- Python 3.8+
- pip

## Instalación y Ejecución

### Opción 1: Con Docker Compose (Recomendado)

```bash
cd vocational_test
docker-compose up
```

La aplicación estará disponible en `http://localhost:80`

### Opción 2: Con Docker

```bash
cd vocational_test
docker build -t vocational-test .
docker run -p 80:80 vocational-test
```

### Opción 3: Ejecución Local

```bash
cd vocational_test
pip install -r requirements.txt
python app.py
```

Accede a `http://localhost:80`

## Estructura del Proyecto

```
vocational_test/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Configuración Docker
├── docker-compose.yml    # Configuración Docker Compose
├── templates/            # Plantillas HTML
│   ├── index.html       # Página de inicio
│   ├── careers.html     # Lista de carreras
│   ├── test.html        # Página del test
│   └── advisory.html    # Página de asesoría
├── static/              # Archivos estáticos
│   └── css/
│       └── style.css    # Estilos CSS
└── data/                # Datos y base de datos
    └── vocational_test.db
```

## Características Principales

### Test de Orientación
- 8 preguntas progresivas
- Interfaz intuitiva con barra de progreso
- Cálculo automático de puntuaciones
- Resultado recomendado basado en respuestas

### Gestión de Asesorías
- Calendario con fechas disponibles
- Sistema de reserva de horarios
- Prevención de doble booking
- Notificación de confirmación

### Base de Datos
- Almacenamiento de resultados de tests
- Registro de asesorías agendadas
- Seguimiento de usuarios

## Puertos

- **80**: Puerto HTTP principal de la aplicación

## Notas de Seguridad

Para producción:
- Cambiar `debug=False` en app.py (ya está configurado)
- Implementar autenticación
- Usar HTTPS
- Agregar validación de emails
- Implementar rate limiting

## Desarrollo

Para hacer cambios y recompilar:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## Licencia

Este proyecto es de código abierto. Siéntete libre de modificarlo según tus necesidades.

## Contacto

Para soporte o sugerencias, contacta al equipo de orientación vocacional.
