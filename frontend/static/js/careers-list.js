// Cargar carreras desde la API (Oracle Autonomous Database)
// Endpoint: GET /api/careers/all - datos completos (id, nombre, icono, descripción, skills, jobs)
// Con localStorage para cachear durante 1 día

const CAREERS_CACHE_KEY = 'careers_full_cache';
const CAREERS_CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 1 día en milisegundos

/**
 * Obtener datos del cache si existen y no han expirado
 * @returns {Object|null} Datos cacheados o null
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
        console.error('Error leyendo cache de carreras:', error);
        localStorage.removeItem(CAREERS_CACHE_KEY);
        return null;
    }
}

/**
 * Guardar datos en el cache
 * @param {Object} data - Datos a guardar
 */
function setCachedCareers(data) {
    try {
        localStorage.setItem(CAREERS_CACHE_KEY, JSON.stringify({
            data: data,
            timestamp: Date.now()
        }));
    } catch (error) {
        console.error('Error guardando cache de carreras:', error);
    }
}

/**
 * Cargar TODAS las carreras con todos sus datos
 * Se hace una sola llamada y se guarda en cache
 */
async function loadAllCareersToCache() {
    // Si ya hay cache válido, retornarlo
    let cached = getCachedCareers();
    if (cached) return cached;

    // Si no hay cache, cargar desde API
    console.log('Cargando todas las carreras desde API...');
    const response = await fetch('/api/careers/all');
    const data = await response.json();

    if (data.success) {
        setCachedCareers(data);
        return data;
    }
    
    throw new Error(data.message || 'Error al cargar carreras');
}

async function loadCareers() {
    const grid = document.getElementById('careers-grid');
    grid.innerHTML = '<p class="loading">Cargando carreras...</p>';

    try {
        const data = await loadAllCareersToCache();
        
        grid.innerHTML = '';

        for (const career of data.careers) {
            const card = document.createElement('div');
            card.className = 'career-card';
            card.style.cursor = 'pointer';
            card.innerHTML = `
                <div class="career-icon">${career.url ? `<img src="${career.url}" alt="${career.name}" style="width: 100%; height: 100%; object-fit: cover;">` : '📚'}</div>
                <h3>${career.name}</h3>
            `;
            
            // Al hacer clic, ir al detalle (usará el cache)
            card.onclick = () => {
                window.location.href = `/career-detail?id=${career.id}`;
            };

            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });

            grid.appendChild(card);
        }

        if (data.careers.length === 0) {
            grid.innerHTML = '<p class="no-data">No hay carreras disponibles.</p>';
        }

    } catch (error) {
        console.error('Error cargando carreras:', error);
        grid.innerHTML = `<p class="error">Error al cargar las carreras. Intenta de nuevo más tarde.</p>`;
    }
}

// Cargar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', loadCareers);
