// Cargar detalle de carrera desde la API (Oracle Autonomous Database)
// Endpoint: GET /api/careers/{id}/detail - datos completos (skills, jobs, etc.)

async function loadCareerDetail() {
    const params = new URLSearchParams(window.location.search);
    const careerId = params.get('id');

    if (!careerId) {
        showError('Carrera no especificada');
        return;
    }

    try {
        // Obtener detalle completo de la carrera
        const response = await fetch(`/api/careers/${careerId}/detail`);
        const data = await response.json();

        if (!data.success || !data.career) {
            showError('Carrera no encontrada');
            return;
        }

        const career = data.career;

        // Actualizar encabezado
        document.getElementById('career-name').textContent = career.name;
        document.getElementById('career-tagline').textContent = career.description || '';
        document.getElementById('career-title').textContent = career.name;
        document.getElementById('career-icon').textContent = career.icon || '📚';

        // Actualizar contenido
        document.getElementById('career-full-description').textContent = career.description || '';
        document.getElementById('career-requirements').textContent = career.requirements || 'Información no disponible';

        // Cargar habilidades (skills)
        const skillsList = document.getElementById('career-skills');
        skillsList.innerHTML = '';
        if (career.skills && career.skills.length > 0) {
            career.skills.forEach(skill => {
                const li = document.createElement('li');
                li.textContent = skill;
                skillsList.appendChild(li);
            });
        } else {
            skillsList.innerHTML = '<li>Información no disponible</li>';
        }

        // Cargar salidas profesionales (jobs/tareas)
        const jobsList = document.getElementById('career-jobs');
        jobsList.innerHTML = '';
        if (career.jobs && career.jobs.length > 0) {
            career.jobs.forEach(job => {
                const li = document.createElement('li');
                li.textContent = job;
                jobsList.appendChild(li);
            });
        } else {
            jobsList.innerHTML = '<li>Información no disponible</li>';
        }

        // Cargar carreras relacionadas
        loadRelatedCareers(careerId);

    } catch (error) {
        console.error('Error cargando carrera:', error);
        showError('Error al cargar la carrera');
    }
}

// Mostrar error
function showError(message) {
    document.body.innerHTML = `
        <div style="text-align: center; padding: 4rem;">
            <h1>${message}</h1>
            <a href="/careers">Volver a carreras</a>
        </div>
    `;
}

// Cargar carreras relacionadas (usa endpoint liviano /list)
async function loadRelatedCareers(currentCareerId) {
    const relatedGrid = document.getElementById('related-grid');
    relatedGrid.innerHTML = '<p>Cargando...</p>';

    try {
        const response = await fetch('/api/careers/list');
        const data = await response.json();

        if (!data.success) {
            relatedGrid.innerHTML = '';
            return;
        }

        relatedGrid.innerHTML = '';
        let count = 0;

        for (const career of data.careers) {
            if (career.id != currentCareerId && count < 3) {
                const card = document.createElement('div');
                card.className = 'related-career-card';
                card.innerHTML = `
                    <div class="icon">${career.icon || '📚'}</div>
                    <h4>${career.name}</h4>
                    <p>${career.description}</p>
                `;
                card.onclick = () => {
                    window.location.href = `/career-detail?id=${career.id}`;
                };
                relatedGrid.appendChild(card);
                count++;
            }
        }

    } catch (error) {
        console.error('Error cargando carreras relacionadas:', error);
        relatedGrid.innerHTML = '';
    }
}

// Cargar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', loadCareerDetail);
