// Cargar carreras desde la API (Oracle Autonomous Database)
// Endpoint: GET /api/careers/list - solo datos básicos (id, nombre, icono, descripción)
async function loadCareers() {
    const grid = document.getElementById('careers-grid');
    grid.innerHTML = '<p class="loading">Cargando carreras...</p>';

    try {
        const response = await fetch('/api/careers/list');
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || 'Error al cargar carreras');
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
