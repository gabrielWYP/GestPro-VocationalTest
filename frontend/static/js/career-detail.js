// Datos de carreras
const careersData = {
    'software-engineer': {
        name: 'Ingeniería de Software',
        icon: '💻',
        tagline: 'Desarrolla soluciones tecnológicas innovadoras',
        description: 'La Ingeniería de Software es una disciplina que se enfoca en el diseño, desarrollo, mantenimiento y mejora de sistemas de software. Los profesionales de esta área crean aplicaciones y programas que resuelven problemas complejos y mejoran la calidad de vida.',
        fullDescription: 'Los ingenieros de software trabajan en el análisis, diseño e implementación de soluciones informáticas. Su trabajo incluye programación, pruebas, documentación y mantenimiento de sistemas. Es una carrera con alta demanda en el mercado global y ofrece múltiples especializaciones como desarrollo web, móvil, sistemas embebidos y más.',
        skills: ['Programación', 'Análisis de Problemas', 'Pensamiento Lógico', 'Trabajo en Equipo', 'Documentación', 'Gestión de Proyectos'],
        jobs: ['Desarrollador Full Stack', 'Especialista en Ciberseguridad', 'Arquitecto de Software', 'Desarrollador de Aplicaciones Móviles', 'Ingeniero de Datos'],
        requirements: 'Bachillerato en ciencias, habilidades en matemáticas y lógica, aptitud para la programación'
    },
    'business-admin': {
        name: 'Administración de Empresas',
        icon: '📊',
        tagline: 'Lidera y gestiona organizaciones exitosas',
        description: 'La Administración de Empresas forma profesionales capaces de gestionar recursos, planificar estrategias y dirigir equipos en organizaciones. Es una carrera versátil que abre puertas en múltiples sectores.',
        fullDescription: 'Los administradores de empresas tienen conocimientos en finanzas, marketing, recursos humanos y operaciones. Trabajan para optimizar procesos, mejorar la rentabilidad y garantizar el crecimiento sostenible de las organizaciones. Pueden trabajar en cualquier tipo de empresa, desde startups hasta corporaciones multinacionales.',
        skills: ['Liderazgo', 'Análisis Financiero', 'Planificación Estratégica', 'Comunicación', 'Negociación', 'Toma de Decisiones'],
        jobs: ['Gerente General', 'Consultor Empresarial', 'Analista Financiero', 'Director de Proyectos', 'Emprendedor'],
        requirements: 'Bachillerato, aptitud numérica, capacidad de liderazgo y visión empresarial'
    },
    'medicine': {
        name: 'Medicina',
        icon: '⚕️',
        tagline: 'Dedícate a cuidar la salud de las personas',
        description: 'La Medicina es una carrera humanista orientada a la prevención, diagnóstico y tratamiento de enfermedades. Los médicos tienen la responsabilidad de mejorar la calidad de vida y bienestar de los pacientes.',
        fullDescription: 'Los médicos se forman para entender el cuerpo humano, identificar patologías y aplicar tratamientos efectivos. La carrera incluye formación teórica extensa, práctica clínica y especializaciones en diversas áreas como pediatría, cirugía, psiquiatría y más. Requiere vocación de servicio y compromiso con la ética profesional.',
        skills: ['Pensamiento Analítico', 'Empatía', 'Precisión', 'Decisión bajo Presión', 'Comunicación Interpersonal', 'Aprendizaje Continuo'],
        jobs: ['Médico General', 'Cirujano', 'Pediatra', 'Psiquiatra', 'Investigador Médico'],
        requirements: 'Bachillerato con énfasis en ciencias, excelentes calificaciones, vocación de servicio'
    },
    'psychology': {
        name: 'Psicología',
        icon: '🧠',
        tagline: 'Comprende el comportamiento humano',
        description: 'La Psicología estudia el comportamiento y los procesos mentales de las personas. Los psicólogos trabajan para entender, diagnosticar y tratar problemas de salud mental, además de contribuir al bienestar psicosocial.',
        fullDescription: 'Los psicólogos pueden especializarse en psicología clínica, organizacional, educativa, social o forense. Utilizan técnicas terapéuticas, evaluaciones psicológicas y consejería para ayudar a individuos y grupos. Trabajan en clínicas, hospitales, empresas, escuelas e instituciones gubernamentales.',
        skills: ['Empatía', 'Escucha Activa', 'Análisis de Comportamiento', 'Investigación', 'Comunicación', 'Resolución de Problemas'],
        jobs: ['Psicólogo Clínico', 'Psicólogo Organizacional', 'Orientador Educativo', 'Investigador', 'Recursos Humanos'],
        requirements: 'Bachillerato, interés en ciencias sociales, capacidad de escucha y empatía'
    },
    'engineering': {
        name: 'Ingeniería Civil',
        icon: '🏗️',
        tagline: 'Construye la infraestructura del futuro',
        description: 'La Ingeniería Civil se enfoca en el diseño, construcción y mantenimiento de infraestructuras como puentes, carreteras, edificios y sistemas de agua. Los ingenieros civiles transforman el entorno construido.',
        fullDescription: 'Los ingenieros civiles combinan conocimientos de matemáticas, física y materiales para crear estructuras seguras y eficientes. Trabajan en proyectos de infraestructura, inmobiliarios y públicos. La carrera requiere precisión técnica, responsabilidad y capacidad de gestión de proyectos complejos.',
        skills: ['Cálculo y Análisis Matemático', 'Diseño Asistido por Computadora', 'Gestión de Proyectos', 'Resolución de Problemas', 'Trabajo en Equipo', 'Conocimiento de Normativas'],
        jobs: ['Ingeniero Proyectista', 'Inspector de Obras', 'Consultor Técnico', 'Gestor de Proyectos', 'Diseñador de Infraestructuras'],
        requirements: 'Bachillerato con énfasis en matemáticas y física, aptitud espacial, precisión'
    },
    'graphic-design': {
        name: 'Diseño Gráfico',
        icon: '🎨',
        tagline: 'Comunica ideas a través del diseño visual',
        description: 'El Diseño Gráfico es la disciplina que combina arte y comunicación para crear soluciones visuales. Los diseñadores gráficos crean identidades visuales, materiales publicitarios, interfaces y experiencias digitales.',
        fullDescription: 'Los diseñadores gráficos utilizan software especializado y principios de diseño para comunicar mensajes de forma efectiva. Trabajan en agencias publicitarias, empresas, estudios de diseño independientes y en startups tecnológicas. La carrera requiere creatividad, sentido estético y capacidad de adaptación a nuevas tendencias.',
        skills: ['Creatividad', 'Dominio de Software de Diseño', 'Comunicación Visual', 'Atención al Detalle', 'Gestión del Color', 'Tipografía'],
        jobs: ['Diseñador Publicitario', 'Diseñador UX/UI', 'Ilustrador', 'Diseñador de Marca', 'Especialista en Motion Graphics'],
        requirements: 'Bachillerato, creatividad, aptitud artística, dominio de software de diseño'
    },
    'education': {
        name: 'Educación',
        icon: '📚',
        tagline: 'Forma educadores y líderes de cambio',
        description: 'La Educación forma profesionales comprometidos con el aprendizaje y desarrollo integral de estudiantes. Los educadores trabajan para mejorar la calidad de la educación en diversos contextos.',
        fullDescription: 'Los profesionales de la educación pueden ser docentes, diseñadores curriculares, capacitadores o administradores educativos. Utilizan metodologías pedagógicas innovadoras para facilitar el aprendizaje. Trabajan en instituciones educativas, organizaciones no gubernamentales, empresas y sectores públicos.',
        skills: ['Comunicación Efectiva', 'Empatía', 'Creatividad Pedagógica', 'Gestión de Grupos', 'Evaluación', 'Dominio de Contenidos'],
        jobs: ['Docente', 'Diseñador Curricular', 'Capacitador Corporativo', 'Orientador Educativo', 'Administrador de Educación'],
        requirements: 'Bachillerato, vocación docente, capacidad de comunicación, interés en pedagogía'
    },
    'marketing': {
        name: 'Marketing y Publicidad',
        icon: '📢',
        tagline: 'Conecta marcas con sus audiencias',
        description: 'El Marketing y la Publicidad estudian cómo crear estrategias para promover productos y servicios. Los profesionales de esta área trabajan para entender a los consumidores y crear campañas efectivas.',
        fullDescription: 'Los especialistas en marketing desarrollan estrategias de posicionamiento, investigan mercados, crean campañas publicitarias y manejan redes sociales. Utilizan análisis de datos para tomar decisiones informadas. Trabajan en agencias publicitarias, empresas, startups y como consultores independientes.',
        skills: ['Análisis de Datos', 'Creatividad', 'Comunicación', 'Estrategia', 'Gestión de Redes Sociales', 'Pensamiento Analítico'],
        jobs: ['Community Manager', 'Especialista SEO/SEM', 'Copywriter', 'Gerente de Marca', 'Analista de Mercado'],
        requirements: 'Bachillerato, pensamiento estratégico, creatividad, facilidad para análisis'
    }
};

// Cargar datos de la carrera
function loadCareerDetail() {
    const params = new URLSearchParams(window.location.search);
    const careerId = params.get('id');

    if (!careerId || !careersData[careerId]) {
        document.body.innerHTML = '<div style="text-align: center; padding: 4rem;"><h1>Carrera no encontrada</h1><a href="/careers">Volver a carreras</a></div>';
        return;
    }

    const career = careersData[careerId];

    // Actualizar encabezado
    document.getElementById('career-name').textContent = career.name;
    document.getElementById('career-tagline').textContent = career.tagline;
    document.getElementById('career-title').textContent = career.name;
    document.getElementById('career-icon').textContent = career.icon;

    // Actualizar contenido
    document.getElementById('career-full-description').textContent = career.fullDescription;
    document.getElementById('career-requirements').textContent = career.requirements;

    // Cargar habilidades
    const skillsList = document.getElementById('career-skills');
    skillsList.innerHTML = '';
    career.skills.forEach(skill => {
        const li = document.createElement('li');
        li.textContent = skill;
        skillsList.appendChild(li);
    });

    // Cargar salidas profesionales
    const jobsList = document.getElementById('career-jobs');
    jobsList.innerHTML = '';
    career.jobs.forEach(job => {
        const li = document.createElement('li');
        li.textContent = job;
        jobsList.appendChild(li);
    });

    // Cargar carreras relacionadas
    loadRelatedCareers(careerId);
}

// Cargar carreras relacionadas
function loadRelatedCareers(currentCareerid) {
    const relatedGrid = document.getElementById('related-grid');
    relatedGrid.innerHTML = '';

    let count = 0;
    for (const [id, career] of Object.entries(careersData)) {
        if (id !== currentCareerid && count < 3) {
            const card = document.createElement('div');
            card.className = 'related-career-card';
            card.innerHTML = `
                <div class="icon">${career.icon}</div>
                <h4>${career.name}</h4>
                <p>${career.description}</p>
            `;
            card.onclick = () => {
                window.location.href = `/career-detail?id=${id}`;
            };
            relatedGrid.appendChild(card);
            count++;
        }
    }
}

// Cargar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', loadCareerDetail);
