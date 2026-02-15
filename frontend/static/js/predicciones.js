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
 * Scroll automático hacia los resultados de carreras
 */
function scrollToResults() {
    const resultsContainer = document.getElementById('resultsContainer');
    console.log('Intentando scroll a resultsContainer:', resultsContainer);
    if (resultsContainer && resultsContainer.offsetParent !== null) {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
        // Si no está visible, scroll al botón de predecir
        const predictBtn = document.getElementById('predictBtn');
        if (predictBtn) {
            predictBtn.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
}

/**
 * Muestra el perfil RIASEC en la página con gráfico radar
 */
function displayProfile(profile) {
    const categories = [
        { key: 'R', label: 'Realista', color: '#ff6b6b' },
        { key: 'I', label: 'Investigador', color: '#00a8ff' },
        { key: 'A', label: 'Artístico', color: '#a855f7' },
        { key: 'S', label: 'Social', color: '#10b981' },
        { key: 'E', label: 'Emprendedor', color: '#f59e0b' },
        { key: 'C', label: 'Convencional', color: '#6b7280' }
    ];
    
    const labels = categories.map(cat => cat.label);
    const scores = categories.map(cat => (profile && profile[cat.key]) ? parseFloat(profile[cat.key]) : 0);
    const colors = categories.map(cat => cat.color);
    
    // Encontrar la dimensión con mayor valor
    let maxIndex = 0;
    let maxValue = 0;
    scores.forEach((score, index) => {
        if (score > maxValue) {
            maxValue = score;
            maxIndex = index;
        }
    });
    const maxDimensionLabel = labels[maxIndex] || 'equilibrado';
    const maxDimensionColor = colors[maxIndex] || '#333';
    
    // Actualizar el título fuera del canvas
    const titleElement = document.getElementById('riasecTitle');
    titleElement.innerHTML = `¡Tienes un perfil <span style="color: ${maxDimensionColor}; font-weight: 900;">${maxDimensionLabel}</span>!`;
    
    // Obtener elemento canvas
    const ctx = document.getElementById('riasecChart');
    
    // Destruir gráfico anterior si existe
    if (window.riasecChartInstance) {
        window.riasecChartInstance.destroy();
    }
    
    // Crear gráfico radar con hexágono
    window.riasecChartInstance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                data: scores,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.15)',
                borderWidth: 3,
                pointBackgroundColor: colors,
                pointBorderColor: '#fff',
                pointBorderWidth: 3,
                pointRadius: 7,
                pointHoverRadius: 10,
                pointHoverBorderWidth: 4,
                fill: true,
                tension: 0.0,
                shadowBlur: 20,
                shadowColor: 'rgba(0, 0, 0, 0.3)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    display: false
                },
                filler: {
                    propagate: true
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    min: 0,
                    max: 7,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 13,
                            weight: '600',
                            family: "'Poppins', sans-serif"
                        },
                        callback: function(value) {
                            return value;
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.08)',
                        lineWidth: 2,
                        circular: true
                    },
                    pointLabels: {
                        font: function(context) {
                            const index = context.index;
                            const isMax = index === maxIndex;
                            return {
                                size: isMax ? 20 : 17,
                                weight: isMax ? '900' : '700',
                                family: "'Poppins', sans-serif"
                            };
                        },
                        padding: 15,
                        backdropColor: 'rgba(255, 255, 255, 0.95)',
                        backdropPadding: 12,
                        color: function(context) {
                            return colors[context.index];
                        },
                        callback: function(label, index) {
                            const score = scores[index];
                            return `${label}: ${score.toFixed(2)}`;
                        }
                    }
                }
            },
            interaction: {
                intersect: false
            }
        },
        plugins: [{
            id: 'customCanvasBackgroundColor',
            afterDraw(chart) {
                // Efecto de brillo en los puntos
                const ctx = chart.ctx;
                ctx.save();
                ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
                ctx.beginPath();
                ctx.arc(chart.chartArea.left + chart.chartArea.width / 2, 
                        chart.chartArea.top + chart.chartArea.height / 2, 
                        chart.chartArea.width / 2, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }]
    });
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
            
            // Mostrar el perfil RIASEC escalado a 1-7 (o original si no viene escalado)
            if (data.user_profile_scaled) {
                displayProfile(data.user_profile_scaled);
                localStorage.setItem('riasec_profile', JSON.stringify(data.user_profile_scaled));
            } else if (data.user_profile) {
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
 * Prioriza carreras peruanas (carreras_peru), con fallback a carreras USA
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
    
    let careersHtml = '';
    
    // Mostrar carreras peruanas si existen
    const carrerasPeru = occupation.carreras_peru || [];
    if (carrerasPeru.length > 0) {
        carrerasPeru.forEach((carrera, index) => {
            const relevancia = carrera.relevancia || 0;
            const relevanciaColor = relevancia >= 80 ? '#10b981' : relevancia >= 50 ? '#f59e0b' : '#6b7280';
            careersHtml += `
                <div class="career-card" style="animation-delay: ${index * 0.1}s;">
                    <h4>${carrera.nombre}</h4>
                    <span style="font-size: 0.8em; color: ${relevanciaColor}; font-weight: 600;">Afinidad: ${relevancia}%</span>
                </div>
            `;
        });
    } else if (occupation.carreras && occupation.carreras.length > 0) {
        // Fallback a carreras USA si no hay peruanas
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
