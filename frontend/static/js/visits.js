/**
 * Sistema de rastreo de visitas para usuarios anónimos
 * Genera UUID, almacena en cookies y envía al backend
 */

// Nombre de la cookie para el visitor_id
const VISITOR_COOKIE_NAME = 'visitor_id';
const COOKIE_EXPIRY_DAYS = 365; // 1 año

/**
 * Genera un UUID v4
 * @returns {string} UUID generado
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

/**
 * Obtiene o crea el visitor_id desde cookies
 * @returns {string} visitor_id (UUID)
 */
function getOrCreateVisitorId() {
    let visitorId = getCookie(VISITOR_COOKIE_NAME);
    
    if (!visitorId) {
        // Generar nuevo UUID
        visitorId = generateUUID();
        // Guardar en cookie por 1 año
        setCookie(VISITOR_COOKIE_NAME, visitorId, COOKIE_EXPIRY_DAYS);
        console.log('✨ Nuevo visitor_id creado:', visitorId);
    } else {
        console.log('📌 Visitor_id recuperado de cookie:', visitorId);
    }
    
    return visitorId;
}

/**
 * Obtiene el valor de una cookie por su nombre
 * @param {string} name - Nombre de la cookie
 * @returns {string|null} Valor de la cookie o null
 */
function getCookie(name) {
    const nameEQ = name + "=";
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.indexOf(nameEQ) === 0) {
            return decodeURIComponent(cookie.substring(nameEQ.length));
        }
    }
    return null;
}

/**
 * Establece una cookie
 * @param {string} name - Nombre de la cookie
 * @param {string} value - Valor de la cookie
 * @param {number} days - Cantidad de días para expiración
 */
function setCookie(name, value, days = 365) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = name + "=" + encodeURIComponent(value) + ";" + expires + ";path=/";
}

/**
 * Detecta el tipo de dispositivo basado en user agent
 * @returns {string} 'mobile', 'tablet' o 'desktop'
 */
function detectDeviceType() {
    const userAgent = navigator.userAgent.toLowerCase();
    
    if (/mobile|android|iphone|ipod|blackberry|iemobile|opera mini/i.test(userAgent)) {
        return 'mobile';
    } else if (/ipad|android(?!.*mobile)/i.test(userAgent)) {
        return 'tablet';
    }
    return 'desktop';
}

/**
 * Obtiene la IP pública del usuario (mejor esfuerzo)
 * Nota: Las APIs públicas pueden tener limitaciones de rate
 * @returns {Promise<string|null>} IP del usuario o null si no se puede obtener
 */
async function getClientIp() {
    try {
        // Intentar obtener IP de una API pública
        // Esta es una alternativa más confiable que otros métodos
        const response = await fetch('https://api.ipify.org?format=json', {
            method: 'GET',
            timeout: 5000
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.ip;
        }
        return null;
    } catch (error) {
        console.warn('No se pudo obtener IP pública:', error);
        return null;
    }
}

/**
 * Registra una visita en el backend
 * @param {string} page - Página visitada (ej: '/')
 * @param {string|null} visitorId - visitor_id (si no se proporciona, se obtiene de cookies)
 */
async function recordVisit(page = window.location.pathname, visitorId = null) {
    try {
        // Obtener o crear visitor_id
        visitorId = visitorId || getOrCreateVisitorId();
        
        // Obtener información del dispositivo
        const deviceType = detectDeviceType();
        const userAgent = navigator.userAgent;
        
        // Obtener IP (opcional, mejor esfuerzo)
        const ipAddress = await getClientIp();
        
        // Preparar datos para enviar
        const visitData = {
            visitor_id: visitorId,
            page: page,
            user_agent: userAgent,
            ip_address: ipAddress,
            device_type: deviceType
        };
        
        console.log('📊 Registrando visita:', visitData);
        
        // Enviar al backend
        const response = await fetch('/api/visits/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(visitData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Visita registrada exitosamente');
            if (result.visitor_data) {
                console.log(`   Visitante: ${result.visitor_data.visitor_id}`);
                console.log(`   Cantidad de visitas: ${result.visitor_data.cantidad_visitas}`);
            }
        } else {
            console.warn('⚠️ Error registrando visita:', result.message);
        }
        
        return result;
        
    } catch (error) {
        console.error('❌ Error registrando visita:', error);
        return {
            success: false,
            message: error.message
        };
    }
}

/**
 * Obtiene información del visitante actual
 * @param {string|null} visitorId - visitor_id (si no se proporciona, se obtiene de cookies)
 * @returns {Promise<object>} Información del visitante
 */
async function getVisitorInfo(visitorId = null) {
    try {
        visitorId = visitorId || getOrCreateVisitorId();
        
        const response = await fetch(`/api/visits/info?visitor_id=${encodeURIComponent(visitorId)}`, {
            method: 'GET'
        });
        
        const result = await response.json();
        
        if (result.success && result.data) {
            console.log('📋 Información del visitante:', result.data);
            return result.data;
        }
        
        return null;
        
    } catch (error) {
        console.error('Error obteniendo info del visitante:', error);
        return null;
    }
}

/**
 * Obtiene estadísticas generales de visitas
 * @returns {Promise<object>} Estadísticas de visitas
 */
async function getVisitStatistics() {
    try {
        const response = await fetch('/api/visits/statistics', {
            method: 'GET'
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('📈 Estadísticas de visitas:', result.statistics);
            return result.statistics;
        }
        
        return null;
        
    } catch (error) {
        console.error('Error obteniendo estadísticas:', error);
        return null;
    }
}

/**
 * Inicializa el sistema de rastreo de visitas
 * Llamar en el evento DOMContentLoaded de páginas públicas
 */
function initializeVisitTracking() {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Inicializando sistema de rastreo de visitas...');
        recordVisit();
    });
}

// Auto-inicializar si el script se carga después del DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (document.body) {
            console.log('🚀 Rastreo de visitas iniciado (DOM ready)');
            recordVisit();
        }
    });
} else {
    // DOM ya está cargado
    console.log('🚀 Rastreo de visitas iniciado (DOM pre-loaded)');
    recordVisit();
}
