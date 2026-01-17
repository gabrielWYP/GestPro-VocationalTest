// Sistema de Asesoría - Lógica de Agendamiento

let bookedSlots = [];

/**
 * Inicializar cuando el DOM esté listo
 */
document.addEventListener('DOMContentLoaded', function() {
    // Establecer fecha mínima como hoy
    const today = new Date();
    const minDate = today.toISOString().split('T')[0];
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.setAttribute('min', minDate);
    }

    // Obtener slots reservados si existe el elemento
    const bookedSlotsElement = document.getElementById('bookedSlots');
    if (bookedSlotsElement) {
        bookedSlots = JSON.parse(bookedSlotsElement.textContent || '[]');
    }

    // Generar fechas disponibles
    generateAvailableDates();

    // Agregar event listener al cambio de fecha
    const dateElement = document.getElementById('date');
    if (dateElement) {
        dateElement.addEventListener('change', function() {
            loadAvailableTimes(this.value);
        });
    }

    // Manejar envío del formulario
    const advisoryForm = document.getElementById('advisoryForm');
    if (advisoryForm) {
        advisoryForm.addEventListener('submit', handleSubmit);
    }
});

/**
 * Genera las fechas disponibles para los próximos 14 días
 */
function generateAvailableDates() {
    const container = document.getElementById('availableDates');
    if (!container) return;
    
    let html = '';
    
    for (let i = 1; i <= 14; i++) {
        const date = new Date();
        date.setDate(date.getDate() + i);
        const dateStr = date.toISOString().split('T')[0];
        const formatted = date.toLocaleDateString('es-ES', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        html += `<button type="button" class="date-button" onclick="selectDate('${dateStr}')">${formatted}</button>`;
    }
    
    container.innerHTML = html;
}

/**
 * Selecciona una fecha del calendario
 * @param {string} dateStr - Fecha en formato YYYY-MM-DD
 */
function selectDate(dateStr) {
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = dateStr;
        loadAvailableTimes(dateStr);
    }
}

/**
 * Carga los horarios disponibles para una fecha específica
 * @param {string} date - Fecha en formato YYYY-MM-DD
 */
async function loadAvailableTimes(date) {
    try {
        const response = await fetch(`/api/available-times?date=${date}`);
        const data = await response.json();
        
        const timeSelect = document.getElementById('time');
        if (!timeSelect) return;
        
        timeSelect.innerHTML = '<option value="">Selecciona una hora</option>';
        
        if (data.available_times.length === 0) {
            timeSelect.innerHTML += '<option disabled>No hay horas disponibles</option>';
        } else {
            data.available_times.forEach(time => {
                const option = document.createElement('option');
                option.value = time;
                option.textContent = time;
                timeSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar horarios:', error);
        alert('Error al cargar los horarios disponibles');
    }
}

/**
 * Maneja el envío del formulario de asesoría
 * @param {Event} event - Evento del formulario
 */
async function handleSubmit(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;

    if (!name || !email || !date || !time) {
        alert('Por favor completa todos los campos');
        return;
    }

    try {
        const response = await fetch('/api/advisory-submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                date: date,
                time: time
            })
        });

        const data = await response.json();
        
        if (data.success) {
            showSuccessMessage(data.message);
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al agendar la asesoría');
    }
}

/**
 * Muestra el mensaje de éxito al agendar
 * @param {string} message - Mensaje a mostrar
 */
function showSuccessMessage(message) {
    const advisoryForm = document.getElementById('advisoryForm');
    const successMessage = document.getElementById('successMessage');
    const successText = document.getElementById('successText');
    
    if (advisoryForm) {
        advisoryForm.style.display = 'none';
    }
    if (successMessage) {
        successMessage.style.display = 'block';
    }
    if (successText) {
        successText.textContent = message;
    }
}
