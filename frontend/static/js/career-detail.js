// Cargar detalle de carrera desde CACHE o API
// Usa el mismo cache que careers-list.js para evitar llamadas innecesarias

const CAREERS_CACHE_KEY = 'careers_full_cache';
const CAREERS_CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 1 día en milisegundos

/**
 * Obtener datos del cache si existen y no han expirado
 */
function getCachedCareers() {
    const cached = localStorage.getItem(CAREERS_CACHE_KEY);
    if (!cached) return null;

    try {
        const { data, timestamp } = JSON.parse(cached);
        const now = Date.now();

        if (now - timestamp < CAREERS_CACHE_EXPIRY) {
            console.log('Usando carreras en caché');
            return data;
        } else {
            localStorage.removeItem(CAREERS_CACHE_KEY);
            return null;
        }
    } catch (error) {
        console.error('Error leyendo cache:', error);
        localStorage.removeItem(CAREERS_CACHE_KEY);
        return null;
    }
}

/**
 * Guardar datos en el cache
 */
function setCachedCareers(data) {
    try {
        localStorage.setItem(CAREERS_CACHE_KEY, JSON.stringify({
            data: data,
            timestamp: Date.now()
        }));
    } catch (error) {
        console.error('Error guardando cache:', error);
    }
}

/**
 * Obtener una carrera por ID desde el cache o API
 */
async function getCareerById(careerId) {
    // Intentar obtener del cache primero
    let cached = getCachedCareers();
    
    if (cached && cached.careers) {
        const career = cached.careers.find(c => c.id == careerId);
        if (career) {
            console.log('Carrera encontrada en caché');
            return career;
        }
    }
    
    // Si no está en cache, cargar todas las carreras
    console.log('Cargando carreras desde API...');
    const response = await fetch('/api/careers/all');
    const data = await response.json();
    
    if (data.success) {
        setCachedCareers(data);
        return data.careers.find(c => c.id == careerId);
    }
    
    return null;
}

async function loadCareerDetail() {
    const params = new URLSearchParams(window.location.search);
    const careerId = params.get('id');

    if (!careerId) {
        showError('Carrera no especificada');
        return;
    }

    try {
        const career = await getCareerById(careerId);

        if (!career) {
            showError('Carrera no encontrada');
            return;
        }

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

        // Cargar carreras relacionadas (desde cache)
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

// Cargar carreras relacionadas (usa el cache)
async function loadRelatedCareers(currentCareerId) {
    const relatedGrid = document.getElementById('related-grid');
    relatedGrid.innerHTML = '<p>Cargando...</p>';

    try {
        // Obtener del cache
        let cached = getCachedCareers();
        
        if (!cached) {
            // Si no hay cache, cargar desde API
            const response = await fetch('/api/careers/all');
            const data = await response.json();
            if (data.success) {
                setCachedCareers(data);
                cached = data;
            } else {
                relatedGrid.innerHTML = '';
                return;
            }
        }

        relatedGrid.innerHTML = '';
        let count = 0;

        for (const career of cached.careers) {
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
