// Cargar carreras desde la API (Oracle Autonomous Database)
// Endpoint: GET /api/careers/list - solo datos básicos (id, nombre, icono, descripción)
// Con localStorage para cachear durante 1 día

const CACHE_KEY = 'careers_cache';
const CACHE_EXPIRY_TIME = 24 * 60 * 60 * 1000; // 1 día en milisegundos

// Obtener datos del cache si existen y no han expirado
function getCachedCareers() {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return null;

    try {
        const { data, timestamp } = JSON.parse(cached);
        const now = Date.now();

        // Verificar si el cache ha expirado
        if (now - timestamp < CACHE_EXPIRY_TIME) {
            console.log('Usando datos en caché');
            return data;
        } else {
            // Cache expirado, eliminarlo
            localStorage.removeItem(CACHE_KEY);
            return null;
        }
    } catch (error) {
        console.error('Error leyendo cache:', error);
        localStorage.removeItem(CACHE_KEY);
        return null;
    }
}

// Guardar datos en el cache
function setCachedCareers(data) {
    try {
        localStorage.setItem(CACHE_KEY, JSON.stringify({
            data: data,
            timestamp: Date.now()
        }));
    } catch (error) {
        console.error('Error guardando en cache:', error);
    }
}

async function loadCareers() {
    const grid = document.getElementById('careers-grid');
    grid.innerHTML = '<p class="loading">Cargando carreras...</p>';

    try {
        // Intentar obtener del cache primero
        let data = getCachedCareers();

        // Si no hay cache válido, hacer la petición a la API
        if (!data) {
            console.log('Obteniendo carreras de la API');
            const response = await fetch('/api/careers/list');
            data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Error al cargar carreras');
            }

            // Guardar en el cache
            setCachedCareers(data);
        }

        grid.innerHTML = '';

        for (const career of data.careers) {
            const card = document.createElement('div');
            card.className = 'career-card';
            card.style.cursor = 'pointer';
            card.innerHTML = `
                <div class="career-icon">${career.icon || '📚'}</div>
                <h3>${career.name}</h3>
                <p class="career-description">${career.description}</p>
            `;
            
            // Al hacer clic, ir al detalle (ahí se carga toda la info)
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
