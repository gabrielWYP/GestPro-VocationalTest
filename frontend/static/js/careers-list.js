// Datos de carreras (mismo en career-detail.js)
const careersData = {
    'software-engineer': {
        name: 'Ingeniería de Software',
        icon: '💻',
        description: 'Desarrolla soluciones tecnológicas innovadoras y aplicaciones de software.'
    },
    'business-admin': {
        name: 'Administración de Empresas',
        icon: '📊',
        description: 'Lidera y gestiona organizaciones con estrategia y eficiencia.'
    },
    'medicine': {
        name: 'Medicina',
        icon: '⚕️',
        description: 'Dedícate a cuidar la salud y el bienestar de las personas.'
    },
    'psychology': {
        name: 'Psicología',
        icon: '🧠',
        description: 'Comprende el comportamiento humano y apoya el bienestar mental.'
    },
    'engineering': {
        name: 'Ingeniería Civil',
        icon: '🏗️',
        description: 'Construye infraestructuras y contribuye al desarrollo urbano.'
    },
    'graphic-design': {
        name: 'Diseño Gráfico',
        icon: '🎨',
        description: 'Comunica ideas a través de soluciones visuales creativas.'
    },
    'education': {
        name: 'Educación',
        icon: '📚',
        description: 'Forma educadores comprometidos con el aprendizaje integral.'
    },
    'marketing': {
        name: 'Marketing y Publicidad',
        icon: '📢',
        description: 'Conecta marcas con sus audiencias y crea campañas efectivas.'
    }
};

// Cargar carreras dinámicamente
function loadCareers() {
    const grid = document.getElementById('careers-grid');
    grid.innerHTML = '';

    for (const [id, career] of Object.entries(careersData)) {
        const card = document.createElement('div');
        card.className = 'career-card';
        card.style.cursor = 'pointer';
        card.innerHTML = `
            <div class="career-icon">${career.icon}</div>
            <h3>${career.name}</h3>
            <p class="career-description">${career.description}</p>
        `;
        
        card.onclick = () => {
            window.location.href = `/career-detail?id=${id}`;
        };

        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });

        grid.appendChild(card);
    }
}

// Cargar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', loadCareers);
