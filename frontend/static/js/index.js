// Página de Inicio - Funciones Auxiliares

// Configuración de cache de sesión
const SESSION_CACHE_KEY = 'session_cache';
const SESSION_CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 1 día en milisegundos

/**
 * Obtiene datos de sesión del cache si existen y no han expirado
 * @returns {Object|null} Datos de sesión cacheados o null si no existen/expiraron
 */
function getCachedSession() {
    const cached = localStorage.getItem(SESSION_CACHE_KEY);
    if (!cached) return null;

    try {
        const { data, timestamp } = JSON.parse(cached);
        const now = Date.now();

        // Verificar si el cache ha expirado
        if (now - timestamp < SESSION_CACHE_EXPIRY) {
            console.log('Usando datos de sesión en caché');
            return data;
        } else {
            // Cache expirado, eliminarlo
            localStorage.removeItem(SESSION_CACHE_KEY);
            return null;
        }
    } catch (error) {
        console.error('Error leyendo cache de sesión:', error);
        localStorage.removeItem(SESSION_CACHE_KEY);
        return null;
    }
}

/**
 * Guarda datos de sesión en el cache
 * @param {Object} data - Datos de sesión a guardar
 */
function setCachedSession(data) {
    try {
        localStorage.setItem(SESSION_CACHE_KEY, JSON.stringify({
            data: data,
            timestamp: Date.now()
        }));
    } catch (error) {
        console.error('Error guardando cache de sesión:', error);
    }
}

/**
 * Elimina el cache de sesión (útil para logout)
 */
function clearSessionCache() {
    localStorage.removeItem(SESSION_CACHE_KEY);
}

/**
 * Desplaza suavemente a una sección específica
 * @param {string} sectionId - ID de la sección a la que desplazarse
 */
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Verifica si el usuario puede acceder al test
 * Si está logueado → va a test-intro
 * Si no está logueado → va a login
 */
async function startTestFlow() {
    try {
        // Intentar obtener del cache primero
        let data = getCachedSession();

        // Si no hay cache válido, hacer la petición a la API
        if (!data) {
            console.log('Verificando sesión en la API');
            const response = await fetch('/api/auth/check-session', {
                method: 'GET',
                credentials: 'include'
            });
            
            data = await response.json();
            
            // Guardar en el cache
            setCachedSession(data);
        }
        
        if (data.authenticated) {
            // Usuario logueado → ir a página de introducción del test
            window.location.href = '/test/intro';
        } else {
            // No logueado → ir a login
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error al verificar sesión:', error);
        window.location.href = '/login';
    }
}

/**
 * Verifica si hay sesión activa al cargar la página
 */
async function checkSession() {
    try {
        // Intentar obtener del cache primero
        let data = getCachedSession();

        // Si no hay cache válido, hacer la petición a la API
        if (!data) {
            console.log('Verificando sesión en la API');
            const response = await fetch('/api/auth/check-session', {
                method: 'GET',
                credentials: 'include'
            });
            
            data = await response.json();
            
            // Guardar en el cache
            setCachedSession(data);
        }
        
        const loginLink = document.getElementById('login-link');
        const userMenu = document.getElementById('user-menu');
        const userName = document.getElementById('user-name');
        
        if (data.authenticated) {
            // Usuario autenticado - mostrar menú de usuario
            loginLink.style.display = 'none';
            userMenu.style.display = 'flex';
            const nombreCompleto = `${data.user.nombre} ${data.user.apellido}`;
            userName.textContent = nombreCompleto;
        } else {
            // No autenticado - mostrar botón de login
            loginLink.style.display = 'block';
            userMenu.style.display = 'none';
        }
    } catch (error) {
        console.error('Error al verificar sesión:', error);
    }
}

/**
 * Cierra la sesión del usuario
 */
async function logout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Limpiar el cache de sesión
            clearSessionCache();
            // Redirigir a inicio después del logout
            window.location.href = '/';
        } else {
            alert('Error al cerrar sesión: ' + data.message);
        }
    } catch (error) {
        console.error('Error al cerrar sesión:', error);
        alert('Error al cerrar sesión');
    }
}

// Verificar sesión cuando carga la página
document.addEventListener('DOMContentLoaded', checkSession);
