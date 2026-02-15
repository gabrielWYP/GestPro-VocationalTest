/**
 * NPS Universal - Sistema de encuestas Net Promoter Score
 * Se incluye en todas las páginas para usuarios logueados que completaron el test.
 * 
 * Flujo:
 * 1. Al cargar la página, verifica elegibilidad con el backend
 * 2. Si es elegible, comienza a trackear tiempo en la página
 * 3. Envía el tiempo acumulado cada 30 segundos al backend
 * 4. Cuando se alcanza un múltiplo de 5 minutos, muestra el modal NPS
 * 5. El usuario responde 2 encuestas: satisfacción de la página y del test
 * 6. Una vez completadas ambas, deja de mostrar el modal
 */

const NPS = (() => {
    // Estado interno
    let isEligible = false;
    let estado = 0;           // 0: sin responder, 1: una respondida, 2: ambas respondidas
    let pendingPagina = true;
    let pendingTest = true;
    let tiempoAcumulado = 0;
    let localTimer = 0;       // Segundos acumulados localmente desde última sincronización
    let syncInterval = null;
    let isModalOpen = false;
    let selectedScore = null;
    let currentSurveyType = null;

    const SYNC_INTERVAL_MS = 30000;  // Sincronizar cada 30 segundos
    const NPS_THRESHOLD = 300;        // 5 minutos en segundos

    /**
     * Inicializa el sistema NPS
     */
    async function init() {
        try {
            const response = await fetch('/api/nps/check', {
                method: 'GET',
                credentials: 'include'
            });

            const data = await response.json();

            if (!data.success || !data.eligible) {
                console.log('NPS: Usuario no elegible -', data.reason || 'no eligible');
                return;
            }

            // Usuario es elegible
            isEligible = true;
            estado = data.estado || 0;
            tiempoAcumulado = data.tiempo_acumulado || 0;
            pendingPagina = data.pending_pagina !== false;
            pendingTest = data.pending_test !== false;

            console.log(`NPS: Elegible. Estado=${estado}, Tiempo=${tiempoAcumulado}s, PendPag=${pendingPagina}, PendTest=${pendingTest}`);

            // Generar los botones de puntaje para ambas encuestas
            generateScaleButtons('nps-numbers-pagina', 'pagina');
            generateScaleButtons('nps-numbers-test', 'test');

            // Iniciar tracking de tiempo
            startTimeTracking();

        } catch (error) {
            console.error('NPS: Error en inicialización:', error);
        }
    }

    /**
     * Genera los botones del 0-10 para la escala NPS
     */
    function generateScaleButtons(containerId, tipo) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        for (let i = 0; i <= 10; i++) {
            const btn = document.createElement('button');
            btn.className = 'nps-number';
            btn.setAttribute('data-value', i);
            btn.textContent = i;
            btn.onclick = () => selectScore(i, tipo);
            container.appendChild(btn);
        }
    }

    /**
     * Selecciona un puntaje en la escala
     */
    function selectScore(score, tipo) {
        selectedScore = score;
        currentSurveyType = tipo;

        // Actualizar UI - deseleccionar todos y seleccionar el elegido
        const containerId = `nps-numbers-${tipo}`;
        const buttons = document.querySelectorAll(`#${containerId} .nps-number`);
        buttons.forEach(btn => {
            btn.classList.toggle('selected', parseInt(btn.getAttribute('data-value')) === score);
        });

        // Habilitar botón de envío
        const submitBtn = document.getElementById(`nps-submit-${tipo}`);
        if (submitBtn) {
            submitBtn.disabled = false;
        }
    }

    /**
     * Inicia el tracking de tiempo en la página
     */
    function startTimeTracking() {
        // Contar segundos localmente cada segundo
        setInterval(() => {
            if (!document.hidden) {
                localTimer++;
            }
        }, 1000);

        // Sincronizar con el backend cada 30 segundos
        syncInterval = setInterval(syncTime, SYNC_INTERVAL_MS);

        // Sincronizar antes de que el usuario se vaya
        window.addEventListener('beforeunload', () => {
            if (localTimer > 0) {
                // Usar sendBeacon para enviar datos antes de cerrar
                const data = JSON.stringify({ seconds: localTimer });
                navigator.sendBeacon('/api/nps/update-time', new Blob([data], { type: 'application/json' }));
            }
        });

        // Verificar inmediatamente si ya debería mostrar NPS
        checkIfShouldShowNps();
    }

    /**
     * Sincroniza el tiempo local con el backend
     */
    async function syncTime() {
        if (localTimer <= 0 || isModalOpen) return;

        const secondsToSync = localTimer;
        localTimer = 0;

        try {
            const response = await fetch('/api/nps/update-time', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ seconds: secondsToSync })
            });

            const data = await response.json();

            if (data.success) {
                tiempoAcumulado = data.tiempo_acumulado;
                estado = data.estado;

                // Si el backend dice que hay que mostrar NPS
                if (data.show_nps && estado < 2 && !isModalOpen) {
                    showModal();
                }
            }
        } catch (error) {
            // Si falla, devolver los segundos al timer local
            localTimer += secondsToSync;
            console.error('NPS: Error sincronizando tiempo:', error);
        }
    }

    /**
     * Verifica si debería mostrar el NPS inmediatamente
     * (para cuando la página se recarga y ya pasaron los 5 min)
     */
    function checkIfShouldShowNps() {
        if (estado >= 2 || isModalOpen) return;

        // Si ya tiene más de 5 minutos acumulados y tiene encuestas pendientes
        if (tiempoAcumulado >= NPS_THRESHOLD && (pendingPagina || pendingTest)) {
            // Esperar un poco para no mostrar el modal inmediatamente al cargar
            setTimeout(() => {
                if (!isModalOpen && estado < 2) {
                    showModal();
                }
            }, 3000);
        }
    }

    /**
     * Muestra el modal NPS con la encuesta pendiente
     */
    function showModal() {
        if (isModalOpen || estado >= 2) return;

        const overlay = document.getElementById('nps-overlay');
        if (!overlay) return;

        isModalOpen = true;
        selectedScore = null;
        currentSurveyType = null;

        // Ocultar todas las secciones
        document.getElementById('nps-pagina').style.display = 'none';
        document.getElementById('nps-test').style.display = 'none';
        document.getElementById('nps-thanks').style.display = 'none';

        // Determinar cuál mostrar
        if (pendingPagina) {
            document.getElementById('nps-pagina').style.display = 'block';
            currentSurveyType = 'pagina';
            updateProgress();
        } else if (pendingTest) {
            document.getElementById('nps-test').style.display = 'block';
            currentSurveyType = 'test';
            updateProgress();
        }

        // Resetear botones de envío
        const submitPagina = document.getElementById('nps-submit-pagina');
        const submitTest = document.getElementById('nps-submit-test');
        if (submitPagina) submitPagina.disabled = true;
        if (submitTest) submitTest.disabled = true;

        // Deseleccionar todos los botones
        document.querySelectorAll('.nps-number').forEach(btn => btn.classList.remove('selected'));

        overlay.style.display = 'flex';
    }

    /**
     * Cierra el modal NPS
     */
    function closeModal() {
        const overlay = document.getElementById('nps-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
        isModalOpen = false;
    }

    /**
     * Envía la respuesta NPS al backend
     */
    async function submitResponse(tipo) {
        if (selectedScore === null || !tipo) return;

        const submitBtn = document.getElementById(`nps-submit-${tipo}`);
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Enviando...';
        }

        try {
            const response = await fetch('/api/nps/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    tipo: tipo,
                    puntuacion: selectedScore
                })
            });

            const data = await response.json();

            if (data.success) {
                estado = data.estado;

                if (tipo === 'pagina') {
                    pendingPagina = false;
                } else {
                    pendingTest = false;
                }

                // Si aún falta la otra encuesta, mostrarla
                if (!data.completed && (pendingPagina || pendingTest)) {
                    // Mostrar agradecimiento brevemente, luego la siguiente encuesta
                    showThanksAndNext();
                } else {
                    // Ambas completadas, mostrar agradecimiento y cerrar
                    showFinalThanks();
                }
            } else {
                alert(data.message || 'Error al enviar respuesta');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Enviar';
                }
            }

        } catch (error) {
            console.error('NPS: Error enviando respuesta:', error);
            alert('Error al enviar la respuesta. Intenta de nuevo.');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Enviar';
            }
        }
    }

    /**
     * Muestra agradecimiento breve y luego la siguiente encuesta
     */
    function showThanksAndNext() {
        // Ocultar encuesta actual
        document.getElementById('nps-pagina').style.display = 'none';
        document.getElementById('nps-test').style.display = 'none';

        // Mostrar agradecimiento
        const thanks = document.getElementById('nps-thanks');
        thanks.style.display = 'block';

        // Después de 2 segundos, mostrar la siguiente encuesta
        setTimeout(() => {
            thanks.style.display = 'none';
            selectedScore = null;

            if (pendingPagina) {
                document.getElementById('nps-pagina').style.display = 'block';
                currentSurveyType = 'pagina';
                const btn = document.getElementById('nps-submit-pagina');
                if (btn) { btn.disabled = true; btn.textContent = 'Enviar'; }
            } else if (pendingTest) {
                document.getElementById('nps-test').style.display = 'block';
                currentSurveyType = 'test';
                const btn = document.getElementById('nps-submit-test');
                if (btn) { btn.disabled = true; btn.textContent = 'Enviar'; }
            }

            // Deseleccionar botones
            document.querySelectorAll('.nps-number').forEach(btn => btn.classList.remove('selected'));
            updateProgress();
        }, 2000);
    }

    /**
     * Muestra agradecimiento final y cierra el modal
     */
    function showFinalThanks() {
        document.getElementById('nps-pagina').style.display = 'none';
        document.getElementById('nps-test').style.display = 'none';
        document.getElementById('nps-thanks').style.display = 'block';
        document.getElementById('nps-progress').style.display = 'none';

        // Cerrar automáticamente después de 3 segundos
        setTimeout(() => {
            closeModal();
            // Detener sincronización
            if (syncInterval) {
                clearInterval(syncInterval);
            }
        }, 3000);
    }

    /**
     * Actualiza el texto de progreso
     */
    function updateProgress() {
        const progressText = document.getElementById('nps-progress-text');
        if (!progressText) return;

        const total = 2;
        const completadas = total - (pendingPagina ? 1 : 0) - (pendingTest ? 1 : 0);
        const currentNum = completadas + 1;

        progressText.textContent = `Encuesta ${currentNum} de ${total}`;
        document.getElementById('nps-progress').style.display = 'block';
    }

    // API pública
    return {
        init,
        closeModal,
        submitResponse
    };
})();

// Iniciar NPS cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Pequeño delay para no interferir con la carga inicial de la página
    setTimeout(() => NPS.init(), 1500);
});
