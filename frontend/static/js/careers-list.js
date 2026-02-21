// Cargar carreras desde la API (Oracle Autonomous Database)
// Endpoint: GET /api/careers/all - datos completos (id, nombre, icono, descripción, skills, jobs)
// Con localStorage para cachear durante 1 día

const CAREERS_CACHE_KEY = 'careers_full_cache_v2';
const CAREERS_CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 1 día en milisegundos

function getCacheEntry() {
    const cached = localStorage.getItem(CAREERS_CACHE_KEY);
    if (!cached) return null;

    try {
        const parsed = JSON.parse(cached);
        if (!parsed || !parsed.data || !parsed.timestamp) {
            localStorage.removeItem(CAREERS_CACHE_KEY);
            return null;
        }
        return parsed;
    } catch (error) {
        console.error('Error leyendo cache de carreras:', error);
        localStorage.removeItem(CAREERS_CACHE_KEY);
        return null;
    }
}

/**
 * Obtener datos del cache si existen y no han expirado
 * @returns {Object|null} Datos cacheados o null
 */
function getCachedCareers() {
    const entry = getCacheEntry();
    if (!entry) return null;

    const now = Date.now();
    if (now - entry.timestamp < CAREERS_CACHE_EXPIRY) {
        console.log('Usando carreras en caché');
        return entry.data;
    }

    return null;
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
 * OPTIMIZADO: Usa /api/careers/list que es más liviano (sin skills/jobs)
 */
async function loadAllCareersToCache() {
    // Si ya hay cache válido, retornarlo
    let cached = getCachedCareers();
    if (cached) return cached;

    // Si no hay cache, cargar desde API (endpoint más liviano)
    console.log('Cargando carreras desde API...');
    const response = await fetch('/api/careers/list');
    const data = await response.json();

    if (data.success) {
        setCachedCareers(data);
        return data;
    }
    
    throw new Error(data.message || 'Error al cargar carreras');
}

async function refreshCareersInBackground(grid) {
    try {
        const response = await fetch('/api/careers/list');
        const data = await response.json();

        if (data.success) {
            setCachedCareers(data);
            renderCareers(grid, data.careers || []);
        }
    } catch (error) {
        console.warn('No se pudo refrescar carreras en background:', error);
    }
}

function renderCareers(grid, careers) {
    grid.innerHTML = '';
    
    // Usar DocumentFragment para evitar 60 reflows
    const fragment = document.createDocumentFragment();

    for (const career of careers) {
        const card = document.createElement('div');
        card.className = 'career-card';
        card.style.cursor = 'pointer';
        card.dataset.careerId = career.id;  // Guardar ID en data attribute
        card.innerHTML = `
            <div class="career-icon">${career.url ? `<img src="${career.url}" alt="${career.name}" class="career-image" loading="lazy">` : '📚'}</div>
            <h3>${career.name}</h3>
        `;

        fragment.appendChild(card);
    }

    grid.appendChild(fragment);  // Un solo reflow aquí

    // Event delegation: un listener para todas las cards
    grid.addEventListener('click', (e) => {
        const card = e.target.closest('.career-card');
        if (card) {
            const careerId = card.dataset.careerId;
            window.location.href = `/career-detail?id=${careerId}`;
        }
    });

    // Event delegation para transform hover
    grid.addEventListener('mouseenter', (e) => {
        const card = e.target.closest('.career-card');
        if (card) card.style.transform = 'translateY(-8px)';
    }, true);

    grid.addEventListener('mouseleave', (e) => {
        const card = e.target.closest('.career-card');
        if (card) card.style.transform = 'translateY(0)';
    }, true);

    if (careers.length === 0) {
        grid.innerHTML = '<p class="no-data">No hay carreras disponibles.</p>';
    }
}

async function loadCareers() {
    const grid = document.getElementById('careers-grid');
    const entry = getCacheEntry();

    // Render instantáneo si existe cache (aunque esté expirado)
    if (entry?.data?.careers?.length) {
        renderCareers(grid, entry.data.careers);

        const isExpired = (Date.now() - entry.timestamp) >= CAREERS_CACHE_EXPIRY;
        if (isExpired) {
            refreshCareersInBackground(grid);
        }
        return;
    }

    grid.innerHTML = '<p class="loading">Cargando carreras...</p>';

    try {
        const data = await loadAllCareersToCache();
        renderCareers(grid, data.careers || []);

    } catch (error) {
        console.error('Error cargando carreras:', error);
        grid.innerHTML = `<p class="error">Error al cargar las carreras. Intenta de nuevo más tarde.</p>`;
    }
}

// Cargar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', loadCareers);
