/**
 * Listado de carreras con paginación
 * Carga 12 carreras por página con botón "Cargar más"
 * Cache en localStorage para visitas repetidas
 */

const PER_PAGE = 12;
const CAREERS_CACHE_KEY = 'careers_full_cache_v4';
const LEGACY_CACHE_KEYS = ['careers_full_cache', 'careers_full_cache_v2', 'careers_full_cache_v3'];
const CAREERS_CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 1 día

// Estado de paginación
let currentPage = 1;
let totalPages = 1;
let accumulatedCareers = [];

// ─── Cache helpers ──────────────────────────────────────────

function clearLegacyCaches() {
    for (const key of LEGACY_CACHE_KEYS) {
        localStorage.removeItem(key);
    }
}

function getCachedCareers() {
    const cached = localStorage.getItem(CAREERS_CACHE_KEY);
    if (!cached) return null;
    try {
        const parsed = JSON.parse(cached);
        if (!parsed?.careers || !parsed?.timestamp) {
            localStorage.removeItem(CAREERS_CACHE_KEY);
            return null;
        }
        if (Date.now() - parsed.timestamp < CAREERS_CACHE_EXPIRY) {
            return parsed.careers;
        }
    } catch (e) {
        localStorage.removeItem(CAREERS_CACHE_KEY);
    }
    return null;
}

function setCachedCareers(careers) {
    try {
        localStorage.setItem(CAREERS_CACHE_KEY, JSON.stringify({
            careers: careers,
            timestamp: Date.now()
        }));
    } catch (e) {
        console.warn('No se pudo guardar cache de carreras:', e);
    }
}

// ─── Fetch ──────────────────────────────────────────────────

/**
 * Obtiene una página de carreras desde la API
 * @returns {{careers:Array, total:number, total_pages:number, has_next:boolean}}
 */
async function fetchCareersPage(page) {
    const response = await fetch(`/api/careers/list?page=${page}&per_page=${PER_PAGE}`);
    const data = await response.json();

    if (!data.success) {
        throw new Error(data.message || 'Error al cargar carreras');
    }
    return data;
}

// ─── Render ─────────────────────────────────────────────────

function createCareerCard(career) {
    const card = document.createElement('div');
    card.className = 'career-card';
    card.style.cursor = 'pointer';
    card.dataset.careerId = career.id;
    card.innerHTML = `
        <div class="career-icon">${career.url ? `<img src="${career.url}" alt="${career.name}" class="career-image" loading="lazy">` : ''}</div>
        <h3>${career.name}</h3>
    `;
    return card;
}

/**
 * Agrega carreras al grid (modo append para paginación)
 */
function appendCareers(grid, careers) {
    const fragment = document.createDocumentFragment();
    for (const career of careers) {
        fragment.appendChild(createCareerCard(career));
    }
    grid.appendChild(fragment);
}

function setupEventDelegation(grid) {
    // Click -> navegar a detalle
    grid.addEventListener('click', (e) => {
        const card = e.target.closest('.career-card');
        if (card) {
            window.location.href = `/career-detail?id=${card.dataset.careerId}`;
        }
    });

    // Hover effect con event delegation
    grid.addEventListener('mouseenter', (e) => {
        const card = e.target.closest('.career-card');
        if (card) card.style.transform = 'translateY(-8px)';
    }, true);

    grid.addEventListener('mouseleave', (e) => {
        const card = e.target.closest('.career-card');
        if (card) card.style.transform = 'translateY(0)';
    }, true);
}

// ─── Load More Button ───────────────────────────────────────

function createLoadMoreButton() {
    const container = document.querySelector('.careers-section .container');
    if (!container) return;

    // Remover botón anterior si existe
    const existing = document.getElementById('load-more-btn');
    if (existing) existing.remove();

    const btn = document.createElement('button');
    btn.id = 'load-more-btn';
    btn.className = 'btn btn-primary';
    btn.style.cssText = `
        display: block;
        margin: 2rem auto;
        padding: 12px 40px;
        font-size: 1.1em;
        cursor: pointer;
        background: #f3f9ff;
        color: #4a4a4a;
        border: 2px solid transparent;
        background-image: linear-gradient(#f3f9ff, #f3f9ff),
                          linear-gradient(90deg, rgba(143,191,224,0.25) 0%, rgba(168,214,206,0.25) 33%,
                                                   rgba(186,231,221,0.25) 66%, rgba(205,236,226,0.25) 100%);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        box-shadow: 0 2px 6px rgba(60,60,60,0.12);
        border-radius: 8px;
    `;
    btn.textContent = 'Cargar más carreras';
    btn.addEventListener('click', loadMore);

    container.appendChild(btn);
}

function updateLoadMoreButton() {
    const btn = document.getElementById('load-more-btn');
    if (!btn) return;

    if (currentPage >= totalPages) {
        btn.remove();
    }
}

function setLoadMoreButtonLoading(isLoading) {
    const btn = document.getElementById('load-more-btn');
    if (!btn) return;
    btn.disabled = isLoading;
    btn.textContent = isLoading ? 'Cargando...' : 'Cargar más carreras';
}

// ─── Main Logic ─────────────────────────────────────────────

async function loadMore() {
    const grid = document.getElementById('careers-grid');
    if (!grid) return;

    setLoadMoreButtonLoading(true);

    try {
        const nextPage = currentPage + 1;
        const data = await fetchCareersPage(nextPage);

        currentPage = data.page;
        totalPages = data.total_pages;

        // Append nuevas carreras
        appendCareers(grid, data.careers);

        // Acumular para cache
        accumulatedCareers = accumulatedCareers.concat(data.careers);
        setCachedCareers(accumulatedCareers);

        updateLoadMoreButton();
    } catch (error) {
        console.error('Error cargando más carreras:', error);
        const btn = document.getElementById('load-more-btn');
        if (btn) btn.textContent = 'Error al cargar. Reintentar';
    } finally {
        setLoadMoreButtonLoading(false);
    }
}

async function loadCareers() {
    const grid = document.getElementById('careers-grid');
    if (!grid) return;

    // 1. Intentar render desde cache (instantáneo)
    const cachedCareers = getCachedCareers();
    if (cachedCareers?.length) {
        accumulatedCareers = cachedCareers;
        grid.innerHTML = '';
        appendCareers(grid, accumulatedCareers);

        // Refrescar silenciosamente página 1 para datos frescos
        setTimeout(async () => {
            try {
                const data = await fetchCareersPage(1);
                // Solo reemplazar si hay datos nuevos o distintos
                if (data.careers.length > 0) {
                    currentPage = data.page;
                    totalPages = data.total_pages;
                }
            } catch (e) {
                // Silencioso - el cache ya muestra datos
            }
        }, 100);

        // Mostrar botón si hay más páginas (asumimos más de 12 si ya tenemos muchas cacheadas)
        if (accumulatedCareers.length >= PER_PAGE) {
            createLoadMoreButton();
        }
        setupEventDelegation(grid);
        return;
    }

    // 2. Sin cache: mostrar loading y cargar página 1
    grid.innerHTML = '<p class="loading">Cargando carreras...</p>';

    try {
        const data = await fetchCareersPage(1);

        currentPage = data.page;
        totalPages = data.total_pages;
        accumulatedCareers = [...data.careers];

        grid.innerHTML = '';
        appendCareers(grid, data.careers);
        setCachedCareers(accumulatedCareers);
        setupEventDelegation(grid);

        if (currentPage < totalPages) {
            createLoadMoreButton();
        }
    } catch (error) {
        console.error('Error cargando carreras:', error);
        grid.innerHTML = '<p class="error">Error al cargar las carreras. Intenta de nuevo más tarde.</p>';
    }
}

// ─── Init ───────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    clearLegacyCaches();
    loadCareers();
});
