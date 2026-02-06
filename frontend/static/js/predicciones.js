/**
 * Lógica para la página de predicciones de carreras
 * Maneja la carga del perfil RIASEC y la predicción de carreras
 */

/**
 * Carga el perfil RIASEC del usuario desde la BD (no desde cache)
 * El perfil se recalcula cada vez desde las respuestas guardadas
 */
function loadUserProfile() {
    try {
        const storedProfile = localStorage.getItem('riasec_profile');
        
        if (storedProfile) {
            const profile = JSON.parse(storedProfile);
            console.log('📊 Perfil RIASEC cargado del cache:', profile);
            displayProfile(profile);
            return true;
        } else {
            console.log('⚠️ No hay perfil guardado - Completa el test primero');
            // Mostrar boxes vacíos
            displayProfile({});
            return true;
        }
        
    } catch (error) {
        console.error('Error cargando perfil:', error);
        showError('Error al cargar tu perfil. Por favor, intenta de nuevo.');
        return false;
    }
}

/**
 * Muestra el perfil RIASEC en la página
 */
function displayProfile(profile) {
    const riasecScores = document.getElementById('riasecScores');
    
    const categories = [
        { key: 'R', label: 'Realista' },
        { key: 'I', label: 'Investigador' },
        { key: 'A', label: 'Artístico' },
        { key: 'S', label: 'Social' },
        { key: 'E', label: 'Emprendedor' },
        { key: 'C', label: 'Convencional' }
    ];
    
    let html = '';
    categories.forEach(cat => {
        const score = (profile && profile[cat.key]) ? parseFloat(profile[cat.key]).toFixed(2) : '-';
        html += `
            <div class="riasec-score">
                <div class="label">${cat.key}</div>
                <div class="label-name" style="font-size: 0.9em; opacity: 0.9;">${cat.label}</div>
                <div class="value">${score}</div>
            </div>
        `;
    });
    
    riasecScores.innerHTML = html;
}

/**
 * Realiza la predicción de carreras
 */
async function predictCareers() {
    const btn = document.getElementById('predictBtn');
    const errorMsg = document.getElementById('errorMessage');
    
    // Deshabilitar botón y mostrar animación
    btn.disabled = true;
    btn.classList.add('loading');
    errorMsg.classList.remove('showing');
    
    try {
        const response = await fetch('/api/predict-careers', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
            // Guardar resultados en localStorage
            localStorage.setItem('prediction_results', JSON.stringify(data));
            
            // Mostrar el perfil RIASEC calculado desde BD
            if (data.user_profile) {
                displayProfile(data.user_profile);
                localStorage.setItem('riasec_profile', JSON.stringify(data.user_profile));
            }
            
            // Limpiar parámetro de URL para evitar recalcular si vuelves a entrar
            const newUrl = window.location.pathname;
            window.history.replaceState({}, document.title, newUrl);
            
        } else {
            showError(data.message || 'Error al realizar la predicción');
        }
        
    } catch (error) {
        console.error('Error en predicción:', error);
        showError('Error de conexión. Por favor, intenta de nuevo.');
    } finally {
        // Habilitar botón y quitar animación
        btn.disabled = false;
        btn.classList.remove('loading');
    }
}

/**
 * Muestra los resultados de la predicción con top 5 ocupaciones clickeables
 */
function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Crear sección de top 5 ocupaciones
    const occupationsHtml = document.createElement('div');
    occupationsHtml.className = 'occupations-grid';
    occupationsHtml.id = 'occupationsGrid';
    
    data.top_occupations.forEach((occ, index) => {
        const card = document.createElement('div');
        card.className = 'occupation-card';
        card.style.animationDelay = `${index * 0.1}s`;
        card.onclick = () => displayCareersForOccupation(occ);
        
        const similarityPercent = (occ.similarity * 100).toFixed(1);
        
        card.innerHTML = `
            <div class="occupation-card-content">
                <h3>${occ.name}</h3>
                <div class="similarity-badge">${similarityPercent}%</div>
            </div>
        `;
        
        occupationsHtml.appendChild(card);
    });
    
    // Limpiar y mostrar
    const occupationSection = document.querySelector('.occupation-result');
    if (occupationSection) {
        occupationSection.innerHTML = '<h2>Top 5 Ocupaciones que se ajustan a tu perfil</h2>';
        occupationSection.appendChild(occupationsHtml);
    }
    
    // Mostrar las carreras de la primera ocupación por defecto
    displayCareersForOccupation(data.top_occupations[0]);
    
    // Mostrar resultados con animación
    resultsContainer.classList.add('showing');
    
    // Scroll a resultados
    setTimeout(() => {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
}

/**
 * Muestra las carreras sugeridas para una ocupación específica
 */
function displayCareersForOccupation(occupation) {
    const careersList = document.getElementById('careersList');
    
    // Actualizar cards para marcar seleccionada
    document.querySelectorAll('.occupation-card').forEach(card => {
        card.classList.remove('active');
        if (card.textContent.includes(occupation.name)) {
            card.classList.add('active');
        }
    });
    
    // Llenar lista de carreras
    let careersHtml = '';
    if (occupation.carreras && occupation.carreras.length > 0) {
        occupation.carreras.forEach((carrera, index) => {
            careersHtml += `
                <div class="career-card" style="animation-delay: ${index * 0.1}s;">
                    <h4>${carrera}</h4>
                </div>
            `;
        });
    } else {
        careersHtml = '<p style="text-align: center; color: #999;">No hay carreras sugeridas para esta ocupación</p>';
    }
    
    careersList.innerHTML = careersHtml;
}

/**
 * Muestra un mensaje de error
 */
function showError(message) {
    const errorMsg = document.getElementById('errorMessage');
    errorMsg.textContent = message;
    errorMsg.classList.add('showing');
}

/**
 * Inicialización de la página
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 Página de predicciones cargada');
    
    // Cargar perfil del usuario
    const profile = loadUserProfile();
    
    if (!profile) {
        document.getElementById('predictBtn').disabled = true;
    }
    
    // Verificar si viene del test (parámetro recalculate=true)
    const params = new URLSearchParams(window.location.search);
    if (params.get('recalculate') === 'true') {
        console.log('📊 Viniendo desde test - Recalculando predicción automáticamente...');
        // Hacer predicción automática después de cargar la página
        setTimeout(() => {
            predictCareers();
        }, 500);
    }
});
