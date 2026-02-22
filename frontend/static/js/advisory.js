// Sistema de Asesoría - Lógica de Agendamiento
// Conecta con: /api/advisors, /api/available-times, /api/advisory-submit, /api/advisory/my-bookings

let selectedAdvisorId = null;
let selectedDate = null;
let currentUser = null;

/**
 * Inicializar cuando el DOM esté listo
 */
document.addEventListener('DOMContentLoaded', async function() {
    // Verificar sesión del usuario
    await checkUserSession();

    // Cargar asesores desde el backend
    await loadAdvisors();

    // Cargar mis asesorías si el usuario está logueado
    if (currentUser) {
        await loadMyBookings();
    }

    // Establecer fecha mínima como mañana
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.setAttribute('min', tomorrow.toISOString().split('T')[0]);

        dateInput.addEventListener('change', function() {
            selectedDate = this.value;
            if (selectedAdvisorId && selectedDate) {
                loadAvailableTimes(selectedAdvisorId, selectedDate);
            }
        });
    }

    // Generar fechas disponibles (próximos 14 días)
    generateAvailableDates();

    // Manejar envío del formulario
    const advisoryForm = document.getElementById('advisoryForm');
    if (advisoryForm) {
        advisoryForm.addEventListener('submit', handleSubmit);
    }
});

/**
 * Verificar si el usuario tiene sesión activa
 */
async function checkUserSession() {
    try {
        const response = await fetch('/api/auth/check-session');
        const data = await response.json();
        if (data.success && data.authenticated) {
            currentUser = data.user;
            // Rellenar campos de nombre y email automáticamente
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            if (nameInput) {
                nameInput.value = `${currentUser.nombre} ${currentUser.apellido}`;
                nameInput.setAttribute('readonly', true);
            }
            if (emailInput) {
                emailInput.value = currentUser.correo;
                emailInput.setAttribute('readonly', true);
            }
            // Mostrar sección de mis asesorías
            const myBookingsSection = document.getElementById('myBookingsSection');
            if (myBookingsSection) myBookingsSection.style.display = 'block';
        } else {
            // Mostrar mensaje de login requerido
            showLoginRequired();
        }
    } catch (error) {
        console.error('Error verificando sesión:', error);
        showLoginRequired();
    }
}

/**
 * Muestra un mensaje indicando que se necesita iniciar sesión
 */
function showLoginRequired() {
    const formContainer = document.querySelector('.advisory-form-container');
    if (formContainer) {
        const form = document.getElementById('advisoryForm');
        if (form) form.style.display = 'none';

        const loginMsg = document.createElement('div');
        loginMsg.className = 'login-required-msg';
        loginMsg.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <h3 style="color: #3B8FB3; margin-bottom: 1rem;">Inicia sesión para agendar</h3>
                <p style="margin-bottom: 1.5rem; color: #666;">Necesitas tener una cuenta para poder reservar una asesoría con nuestros orientadores.</p>
                <a href="/login" class="btn" style="margin-right: 0.5rem; background: #3B8FB3; color: #fff; border-radius: 50px; padding: 0.6rem 1.5rem;">Iniciar Sesión</a>
                <a href="/register" class="btn" style="background: #3B8FB3; color: #fff; border-radius: 50px; padding: 0.6rem 1.5rem;">Registrarse</a>
            </div>
        `;
        formContainer.appendChild(loginMsg);
    }
}

/**
 * Carga la lista de asesores desde el backend
 */
async function loadAdvisors() {
    try {
        const response = await fetch('/api/advisors');
        const data = await response.json();

        if (!data.success) {
            console.error('Error cargando asesores:', data.message);
            return;
        }

        const advisorSelect = document.getElementById('advisor');
        if (!advisorSelect) return;

        advisorSelect.innerHTML = '<option value="">Selecciona un asesor</option>';

        // Agrupar por carrera
        const grouped = {};
        data.advisors.forEach(adv => {
            const carrera = adv.carrera_nombre || 'General';
            if (!grouped[carrera]) grouped[carrera] = [];
            grouped[carrera].push(adv);
        });

        Object.keys(grouped).sort().forEach(carrera => {
            const optgroup = document.createElement('optgroup');
            optgroup.label = carrera;
            grouped[carrera].forEach(adv => {
                const option = document.createElement('option');
                option.value = adv.id;
                option.textContent = `${adv.nombre} ${adv.apellido}`;
                optgroup.appendChild(option);
            });
            advisorSelect.appendChild(optgroup);
        });

        // Listener para cambio de asesor
        advisorSelect.addEventListener('change', function() {
            selectedAdvisorId = this.value ? parseInt(this.value) : null;
            // Resetear horarios al cambiar asesor
            resetTimeSlots();
            // Si ya hay fecha seleccionada, cargar horarios
            if (selectedAdvisorId && selectedDate) {
                loadAvailableTimes(selectedAdvisorId, selectedDate);
            }
        });

    } catch (error) {
        console.error('Error al cargar asesores:', error);
    }
}

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

        // Saltar fines de semana
        if (date.getDay() === 0 || date.getDay() === 6) continue;

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
 */
function selectDate(dateStr) {
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = dateStr;
        selectedDate = dateStr;

        // Marcar botón activo
        document.querySelectorAll('.date-button').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');

        if (selectedAdvisorId) {
            loadAvailableTimes(selectedAdvisorId, dateStr);
        }
    }
}

/**
 * Resetea los botones de horario
 */
function resetTimeSlots() {
    const container = document.getElementById('timeSlots');
    const hiddenInput = document.getElementById('time');
    if (container) {
        container.innerHTML = '<p class="time-slots-placeholder">Primero selecciona un asesor y una fecha</p>';
    }
    if (hiddenInput) hiddenInput.value = '';
}

/**
 * Selecciona un horario (botón)
 */
function selectTime(timeValue, btn) {
    // Remover selección previa
    document.querySelectorAll('.time-slot-btn').forEach(b => b.classList.remove('selected'));
    // Marcar botón seleccionado
    btn.classList.add('selected');
    // Guardar valor en el input hidden
    document.getElementById('time').value = timeValue;
}

/**
 * Formatea hora 24h a AM/PM
 */
function formatTimeAMPM(time24) {
    const [h, m] = time24.split(':');
    const hour = parseInt(h);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour === 0 ? 12 : (hour > 12 ? hour - 12 : hour);
    return `${displayHour}:${m} ${ampm}`;
}

/**
 * Carga los horarios disponibles para un asesor en una fecha (como botones)
 */
async function loadAvailableTimes(advisorId, date) {
    const container = document.getElementById('timeSlots');
    const hiddenInput = document.getElementById('time');
    if (!container) return;

    // Reset
    if (hiddenInput) hiddenInput.value = '';
    container.innerHTML = '<p class="time-slots-placeholder">Cargando horarios...</p>';

    try {
        const response = await fetch(`/api/available-times?advisor_id=${advisorId}&date=${date}`);
        const data = await response.json();

        if (!data.success) {
            container.innerHTML = '<p class="time-slots-placeholder">Error al cargar horarios</p>';
            return;
        }

        if (data.available_times.length === 0) {
            container.innerHTML = '<p class="time-slots-placeholder">No hay horarios disponibles para esta fecha</p>';
            return;
        }

        // Separar en mañana y tarde
        const morning = data.available_times.filter(t => parseInt(t.split(':')[0]) < 12);
        const afternoon = data.available_times.filter(t => parseInt(t.split(':')[0]) >= 12);

        let html = '';

        if (morning.length > 0) {
            html += '<div class="time-period">';
            html += '<span class="time-period-label">☀️ Mañana</span>';
            html += '<div class="time-buttons-row">';
            morning.forEach(time => {
                html += `<button type="button" class="time-slot-btn" onclick="selectTime('${time}', this)">${formatTimeAMPM(time)}</button>`;
            });
            html += '</div></div>';
        }

        if (afternoon.length > 0) {
            html += '<div class="time-period">';
            html += '<span class="time-period-label">🌙 Tarde</span>';
            html += '<div class="time-buttons-row">';
            afternoon.forEach(time => {
                html += `<button type="button" class="time-slot-btn" onclick="selectTime('${time}', this)">${formatTimeAMPM(time)}</button>`;
            });
            html += '</div></div>';
        }

        container.innerHTML = html;

    } catch (error) {
        console.error('Error al cargar horarios:', error);
        container.innerHTML = '<p class="time-slots-placeholder">Error al cargar horarios</p>';
    }
}

/**
 * Maneja el envío del formulario de asesoría
 */
async function handleSubmit(event) {
    event.preventDefault();

    if (!currentUser) {
        alert('Debes iniciar sesión para agendar una asesoría');
        window.location.href = '/login';
        return;
    }

    const advisorId = document.getElementById('advisor').value;
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;

    if (!advisorId) {
        alert('Por favor selecciona un asesor');
        return;
    }
    if (!date) {
        alert('Por favor selecciona una fecha');
        return;
    }
    if (!time) {
        alert('Por favor selecciona un horario');
        return;
    }

    // Deshabilitar botón mientras se envía
    const submitBtn = document.querySelector('#advisoryForm button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Agendando...';
    }

    try {
        const response = await fetch('/api/advisory-submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                advisor_id: parseInt(advisorId),
                date: date,
                time: time
            })
        });

        const data = await response.json();

        if (data.success) {
            showSuccessMessage(data.message, data.booking);
            // Recargar mis asesorías
            await loadMyBookings();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al agendar la asesoría. Intenta nuevamente.');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Agendar Asesoría';
        }
    }
}

/**
 * Muestra el mensaje de éxito al agendar
 */
function showSuccessMessage(message, booking) {
    const advisoryForm = document.getElementById('advisoryForm');
    const successMessage = document.getElementById('successMessage');
    const successText = document.getElementById('successText');

    if (advisoryForm) advisoryForm.style.display = 'none';
    if (successMessage) successMessage.style.display = 'block';
    if (successText) {
        let html = message;
        if (booking && booking.link) {
            html += `<br><br><strong>Link de reunión:</strong><br>
                     <a href="${booking.link}" target="_blank" class="meeting-link">${booking.link}</a>`;
        }
        successText.innerHTML = html;
    }
}

/**
 * Carga las asesorías del usuario logueado
 */
async function loadMyBookings() {
    if (!currentUser) return;

    const container = document.getElementById('myBookingsList');
    if (!container) return;

    try {
        const response = await fetch('/api/advisory/my-bookings');
        const data = await response.json();

        if (!data.success) {
            container.innerHTML = '<p>Error cargando tus asesorías</p>';
            return;
        }

        if (data.bookings.length === 0) {
            container.innerHTML = '<p class="no-bookings">No tienes asesorías agendadas</p>';
            return;
        }

        let html = '';
        data.bookings.forEach(booking => {
            const fecha = new Date(booking.dia + 'T00:00:00');
            const fechaFormateada = fecha.toLocaleDateString('es-ES', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });

            html += `
                <div class="booking-card">
                    <div class="booking-info">
                        <h4>${booking.asesor_nombre} ${booking.asesor_apellido}</h4>
                        <p class="booking-career">${booking.carrera_nombre}</p>
                        <p class="booking-datetime">📅 ${fechaFormateada} - 🕐 ${booking.hora}</p>
                        ${booking.link ? `<a href="${booking.link}" target="_blank" class="booking-link">🔗 Link de reunión</a>` : ''}
                    </div>
                    <button class="btn-cancel" onclick="cancelBooking(${booking.id})" title="Cancelar asesoría">✕</button>
                </div>
            `;
        });

        container.innerHTML = html;
    } catch (error) {
        console.error('Error cargando mis asesorías:', error);
        container.innerHTML = '<p>Error cargando tus asesorías</p>';
    }
}

/**
 * Cancela una asesoría
 */
async function cancelBooking(bookingId) {
    if (!confirm('¿Estás seguro de que deseas cancelar esta asesoría?')) return;

    try {
        const response = await fetch(`/api/advisory/${bookingId}`, {
            method: 'DELETE'
        });
        const data = await response.json();

        if (data.success) {
            alert('Asesoría cancelada exitosamente');
            await loadMyBookings();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error cancelando asesoría:', error);
        alert('Error al cancelar la asesoría');
    }
}

/**
 * Volver al formulario después de agendar exitosamente
 */
function resetForm() {
    const advisoryForm = document.getElementById('advisoryForm');
    const successMessage = document.getElementById('successMessage');

    if (advisoryForm) {
        advisoryForm.style.display = 'block';
        advisoryForm.reset();
        // Restaurar datos del usuario
        if (currentUser) {
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            if (nameInput) nameInput.value = `${currentUser.nombre} ${currentUser.apellido}`;
            if (emailInput) emailInput.value = currentUser.correo;
        }
    }
    if (successMessage) successMessage.style.display = 'none';

    selectedAdvisorId = null;
    selectedDate = null;
    resetTimeSlots();
}
