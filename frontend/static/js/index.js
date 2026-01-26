// Página de Inicio - Funciones Auxiliares

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
        const response = await fetch('/api/auth/check-session', {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
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
        const response = await fetch('/api/auth/check-session', {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
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
