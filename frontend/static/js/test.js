// Test de Orientación Vocacional - Lógica del Test
// Sistema multi-test: RIASEC (60 preguntas) → Habilidades (10 preguntas)

// Configuración de cache de preguntas
const QUESTIONS_CACHE_KEY = 'test_questions_cache';
const QUESTIONS_CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 1 día en milisegundos

// Estados del test
const TEST_STATES = {
    RIASEC: 'riasec',
    SKILLS: 'skills',
    COMPLETED: 'completed'
};

// Constantes de puntaje RIASEC
const SCORE_MIN = 1;
const SCORE_MAX = 5;
const SCORE_LABELS = {
    1: "Me desagrada mucho",
    2: "No me atrae",
    3: "Neutral",
    4: "Me gusta",
    5: "Me encanta hacerlo"
};

// Constantes de habilidades
const SKILLS_SCORE_LABELS = {
    1: "Novato",
    2: "Básico",
    3: "Intermedio",
    4: "Avanzado",
    5: "Experto"
};

// Configuración de preguntas por test
const RIASEC_QUESTIONS_PER_PAGE = 6;
const SKILLS_QUESTIONS_PER_PAGE = 5;

// Variables de estado global
let currentTest = TEST_STATES.RIASEC; // Qué test se está tomando
let currentPage = 1;
let riasecAnswers = {}; // { questionId: score }
let skillsAnswers = {}; // { questionId: score }
let TEST_QUESTIONS = []; // Preguntas cargadas
let TOTAL_PAGES = 0;
let TOTAL_SKILLS_QUESTIONS = 10; // Las pruebas de habilidades tendrán 10 preguntas
let QUESTIONS_PER_PAGE = RIASEC_QUESTIONS_PER_PAGE;

// QUESTIONS_PER_PAGE se define en test-constants.js

/**
 * Obtiene las preguntas de una página específica
 * @param {number} pageNumber - Número de página (1-indexed)
 * @returns {array} Array de preguntas para esa página
 */
function getQuestionsForPage(pageNumber) {
    const startIdx = (pageNumber - 1) * QUESTIONS_PER_PAGE;
    const endIdx = startIdx + QUESTIONS_PER_PAGE;
    return TEST_QUESTIONS.slice(startIdx, endIdx);
}

/**
 * Obtiene una pregunta por su ID
 * @param {number} questionId - ID de la pregunta
 * @returns {object} Objeto de pregunta
 */
function getQuestionById(questionId) {
    return TEST_QUESTIONS.find(q => q.id === questionId);
}

/**
 * Obtiene preguntas del cache si existen y no han expirado
 * @returns {Array|null} Preguntas cacheadas o null si no existen/expiraron
 */
function getCachedQuestions() {
    const cached = localStorage.getItem(QUESTIONS_CACHE_KEY);
    if (!cached) return null;

    try {
        const { data, timestamp } = JSON.parse(cached);
        const now = Date.now();

        // Verificar si el cache ha expirado
        if (now - timestamp < QUESTIONS_CACHE_EXPIRY) {
            console.log('Usando preguntas en caché');
            return data;
        } else {
            // Cache expirado, eliminarlo
            localStorage.removeItem(QUESTIONS_CACHE_KEY);
            return null;
        }
    } catch (error) {
        console.error('Error leyendo cache de preguntas:', error);
        localStorage.removeItem(QUESTIONS_CACHE_KEY);
        return null;
    }
}

/**
 * Guarda preguntas en el cache
 * @param {Array} questions - Preguntas a guardar
 */
function setCachedQuestions(questions) {
    try {
        localStorage.setItem(QUESTIONS_CACHE_KEY, JSON.stringify({
            data: questions,
            timestamp: Date.now()
        }));
    } catch (error) {
        console.error('Error guardando cache de preguntas:', error);
    }
}

/**
 * Carga las preguntas del test desde la API o del cache
 */
async function loadTestQuestions() {
    try {
        // Intentar obtener del cache primero
        let questions = getCachedQuestions();

        // Si no hay cache válido, hacer la petición a la API
        if (!questions) {
            console.log('Obteniendo preguntas de la API');
            const response = await fetch('/api/test-questions', {
                method: 'GET',
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (!data.success || !data.questions) {
                throw new Error(data.message || 'Error al obtener preguntas');
            }
            
            questions = data.questions;
            
            // Guardar en el cache
            setCachedQuestions(questions);
        }

        TEST_QUESTIONS = questions;
        TOTAL_PAGES = Math.ceil(TEST_QUESTIONS.length / QUESTIONS_PER_PAGE);
        
        return true;
    } catch (error) {
        console.error('Error al cargar preguntas:', error);
        alert('Error al cargar las preguntas del test. Intenta de nuevo.');
        return false;
    }
}

/**
 * Inicia el test - carga las preguntas y muestra la primera página
 */
async function startTest() {
    // Cargar preguntas antes de iniciar
    const questionsLoaded = await loadTestQuestions();
    
    if (!questionsLoaded) {
        return;
    }
    
    // Recuperar respuestas guardadas si existen (para continuar un test en progreso)
    // Nota: Las respuestas se recuperan desde la BD en el próximo acceso
    // Por ahora, comenzamos con testAnswers vacío
    
    document.getElementById('intro').style.display = 'none';
    document.getElementById('questions').style.display = 'block';
    loadPage(currentPage);
}

/**
 * Carga una página específica del test actual
 * @param {number} pageNumber - Número de página (1-indexed)
 */
function loadPage(pageNumber) {
    if (pageNumber < 1 || pageNumber > TOTAL_PAGES) {
        return;
    }
    
    currentPage = pageNumber;
    const pageQuestions = getQuestionsForPage(pageNumber);
    
    // Obtener respuestas del test actual
    const currentAnswers = currentTest === TEST_STATES.RIASEC ? riasecAnswers : skillsAnswers;
    const scoreLabels = currentTest === TEST_STATES.RIASEC ? SCORE_LABELS : SKILLS_SCORE_LABELS;
    
    // Construir título del test
    const testTitle = currentTest === TEST_STATES.RIASEC 
        ? 'Prueba 1: Orientación Vocacional (RIASEC)' 
        : 'Prueba 2: Evaluación de Habilidades';
    document.getElementById('test-title').innerHTML = `<h3>${testTitle}</h3>`;
    
    // Construir HTML de la página
    let html = `
        <div class="page-header">
            <h2>Página ${pageNumber} de ${TOTAL_PAGES}</h2>
            <p class="page-progress">Preguntas ${(pageNumber - 1) * QUESTIONS_PER_PAGE + 1} a ${Math.min(pageNumber * QUESTIONS_PER_PAGE, TEST_QUESTIONS.length)}</p>
        </div>
        
        <div class="questions-grid">
    `;
    
    // Agregar cada pregunta con su slider
    pageQuestions.forEach(question => {
        const score = currentAnswers[question.id] || null; // null = no seleccionado
        const labelMin = currentTest === TEST_STATES.RIASEC ? 'Me desagrada mucho' : 'Novato';
        const labelMax = currentTest === TEST_STATES.RIASEC ? 'Me encanta hacerlo' : 'Experto';
        
        html += `
            <div class="question-item">
                <div class="question-header">
                    <h4>Pregunta ${question.id}</h4>
                </div>
                <p class="question-text">${question.text}</p>
                
                <div class="score-buttons-container">
                    <div class="score-labels">
                        <span class="label-min">${labelMin}</span>
                        <span class="label-max">${labelMax}</span>
                    </div>
                    <div class="score-buttons">
                        ${[1, 2, 3, 4, 5].map(value => `
                            <button 
                                class="score-btn score-btn-${value} ${score === value ? 'selected' : ''}"
                                onclick="updateScore(${question.id}, ${value})"
                                title="${scoreLabels[value]}">
                                <span class="score-btn-number">${value}</span>
                            </button>
                        `).join('')}
                    </div>
                    <div class="score-feedback" id="feedback-${question.id}">
                        ${score ? `<span class="feedback-text">${scoreLabels[score]}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    
    // Botones de navegación
    let nextButtonText = 'Siguiente Página →';
    let lastPageButtonText = '';
    let lastPageButtonAction = '';
    
    if (pageNumber === TOTAL_PAGES) {
        if (currentTest === TEST_STATES.RIASEC) {
            lastPageButtonText = 'Siguiente Prueba →';
            lastPageButtonAction = 'onclick="proceedToNextTest()"';
        } else if (currentTest === TEST_STATES.SKILLS) {
            lastPageButtonText = 'Completar';
            lastPageButtonAction = 'onclick="completeAllTests()"';
        }
    }
    
    html += `
        <div class="navigation">
            <button onclick="previousPage()" class="btn btn-secondary" ${pageNumber === 1 ? 'disabled' : ''}>
                ← Página Anterior
            </button>
            ${pageNumber === TOTAL_PAGES ? `<button ${lastPageButtonAction} class="btn btn-primary">${lastPageButtonText}</button>` : `<button onclick="nextPage()" class="btn btn-primary">Siguiente Página →</button>`}
        </div>
    `;
    
    document.getElementById('question-container').innerHTML = html;
    updateProgressBar();
}

/**
 * Actualiza el puntaje de una pregunta según el test actual
 * @param {number} questionId - ID de la pregunta
 * @param {number} value - Valor del selector (1-5)
 */
function updateScore(questionId, value) {
    // Guardar en el objeto correcto según cuál test se está tomando
    if (currentTest === TEST_STATES.RIASEC) {
        riasecAnswers[questionId] = parseInt(value);
    } else if (currentTest === TEST_STATES.SKILLS) {
        skillsAnswers[questionId] = parseInt(value);
    }
    
    // Actualizar los botones: remover "selected" de todos y agregar al nuevo
    const buttons = document.querySelectorAll(`button[onclick*="updateScore(${questionId}"]`);
    buttons.forEach(btn => btn.classList.remove('selected'));
    document.querySelector(`button[onclick="updateScore(${questionId}, ${value})"]`).classList.add('selected');
    
    // Actualizar feedback con la etiqueta correcta
    const feedbackElement = document.getElementById(`feedback-${questionId}`);
    if (feedbackElement) {
        const labels = currentTest === TEST_STATES.RIASEC ? SCORE_LABELS : SKILLS_SCORE_LABELS;
        feedbackElement.innerHTML = `<span class="feedback-text">${labels[value]}</span>`;
    }
}

/**
 * Actualiza la etiqueta mostrada bajo el slider
 * @param {number} questionId - ID de la pregunta
 * @param {number} value - Valor del slider
 */
function updateSliderLabel(questionId, value) {
    // Esta función se mantiene por compatibilidad pero no se usa en el nuevo diseño
}

/**
 * Carga la siguiente página (con autoguardado)
 */
async function nextPage() {
    if (currentPage < TOTAL_PAGES) {
        // Autoguardar respuestas antes de cambiar página
        await saveAnswersForCurrentPage();
        loadPage(currentPage + 1);
    }
}

/**
 * Carga la página anterior (con autoguardado)
 */
async function previousPage() {
    if (currentPage > 1) {
        // Autoguardar respuestas antes de cambiar página
        await saveAnswersForCurrentPage();
        loadPage(currentPage - 1);
    }
}

/**
 * Guarda las respuestas actuales al servidor
 * Se ejecuta automáticamente al cambiar de página o completar un test
 */
async function saveAnswersForCurrentPage() {
    // Obtener respuestas según el test actual
    let currentAnswers = {};
    if (currentTest === TEST_STATES.RIASEC) {
        currentAnswers = riasecAnswers;
    } else if (currentTest === TEST_STATES.SKILLS) {
        currentAnswers = skillsAnswers;
    }
    
    // Convertir a formato esperado por el backend
    const answersToSave = Object.entries(currentAnswers).map(([questionId, riasecId]) => ({
        afirmacion_id: parseInt(questionId),
        riasec_id: parseInt(riasecId)
    }));
    
    if (answersToSave.length === 0) {
        return; // No hay respuestas para guardar
    }
    
    try {
        console.log(`Guardando ${answersToSave.length} respuesta(s) de ${currentTest}...`);
        
        const response = await fetch('/api/save-answers', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answers: answersToSave })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✓ Respuestas guardadas:', data.message);
        } else {
            console.warn('⚠ Error al guardar respuestas:', data.message);
        }
    } catch (error) {
        console.error('Error guardando respuestas:', error);
    }
}


function updateProgressBar() {
    const progress = (currentPage / TOTAL_PAGES) * 100;
    document.getElementById('progress').style.width = progress + '%';
}

/**
 * Pasa a la siguiente prueba (de RIASEC a Habilidades)
 */
async function proceedToNextTest() {
    // Guardar respuestas del RIASEC
    await saveAnswersForCurrentPage();
    
    // Cambiar a prueba de Habilidades
    currentTest = TEST_STATES.SKILLS;
    currentPage = 1;
    QUESTIONS_PER_PAGE = SKILLS_QUESTIONS_PER_PAGE;
    TOTAL_PAGES = Math.ceil(TOTAL_SKILLS_QUESTIONS / SKILLS_QUESTIONS_PER_PAGE);
    
    // Las siguientes preguntas se cargarían aquí (placeholder por ahora)
    // TODO: Cargar preguntas de habilidades desde una fuente
    TEST_QUESTIONS = generateDummySkillsQuestions();
    
    // Mostrar la primera página del nuevo test
    loadPage(currentPage);
}

/**
 * Genera preguntas dummy de habilidades (TODO: reemplazar con datos reales)
 */
function generateDummySkillsQuestions() {
    const dummyQuestions = [];
    for (let i = 1; i <= TOTAL_SKILLS_QUESTIONS; i++) {
        dummyQuestions.push({
            id: i,
            text: `Pregunta de Habilidad ${i}: ¿Qué tan competente eres en esta área?`
        });
    }
    return dummyQuestions;
}

/**
 * Completa todas las pruebas
 * Guarda respuestas finales y muestra resultados (placeholder)
 */
async function completeAllTests() {
    // Guardar respuestas finales
    await saveAnswersForCurrentPage();
    
    console.log('✓ Todas las pruebas completadas');
    console.log('Respuestas RIASEC:', riasecAnswers);
    console.log('Respuestas Habilidades:', skillsAnswers);
    
    // TODO: Aquí se llamaría al endpoint de procesamiento final
    // Por ahora mostramos un mensaje de éxito
    document.getElementById('questions').style.display = 'none';
    document.getElementById('results').style.display = 'block';
    
    const completionHtml = `
        <div class="completion-message">
            <h2>✓ Tests Completados</h2>
            <p>Tus respuestas han sido guardadas exitosamente.</p>
            <p>Nos pondremos en contacto pronto con los resultados de tu evaluación.</p>
            <div class="result-actions">
                <a href="/advisory" class="btn btn-primary">Agendar Asesoría</a>
                <a href="/" class="btn btn-secondary">Volver al Inicio</a>
            </div>
        </div>
    `;
    
    document.getElementById('result-career').innerHTML = completionHtml;
    document.getElementById('result-scores').innerHTML = '';
}