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
    1: "Me cuesta mucho realizar esto",
    2: "Me cuesta un poco",
    3: "Neutral",
    4: "Me resulta relativamente fácil",
    5: "Creo que puedo hacer esto con facilidad"
};

// Configuración de preguntas por test
const RIASEC_QUESTIONS_PER_PAGE = 6;
const SKILLS_QUESTIONS_PER_PAGE = 5;

// Variables de estado global
let currentTest = TEST_STATES.RIASEC; // Qué test se está tomando
let currentPage = 1;
let riasecAnswers = {}; // { questionId: score }
let skillsAnswers = {}; // { questionId: score }
let ALL_QUESTIONS = []; // Todas las preguntas cargadas desde la API (ID 1-42)
let RIASEC_QUESTIONS = []; // Preguntas filtradas RIASEC (ID 1-30)
let SKILLS_QUESTIONS = []; // Preguntas filtradas Habilidades (ID 31-42)
let TEST_QUESTIONS = []; // Referencias dinámicamente según currentTest
let TOTAL_PAGES = 0;
let TOTAL_SKILLS_QUESTIONS = 12; // Las pruebas de habilidades tendrán 12 preguntas (31-42)
let QUESTIONS_PER_PAGE = RIASEC_QUESTIONS_PER_PAGE;

// Constantes de rangos de IDs
const RIASEC_ID_MIN = 1;
const RIASEC_ID_MAX = 30;
const SKILLS_ID_MIN = 31;
const SKILLS_ID_MAX = 42;

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
 * Separa automáticamente entre RIASEC (1-30) e Habilidades (31-42)
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

        // Almacenar todas las preguntas
        ALL_QUESTIONS = questions;
        
        // Debug: mostrar los IDs de las preguntas cargadas
        console.log('IDs cargados:', ALL_QUESTIONS.map(q => q.id));
        
        // Separar por rango de ID (convertir a número para comparación segura)
        RIASEC_QUESTIONS = ALL_QUESTIONS.filter(q => {
            const id = parseInt(q.id);
            return id >= RIASEC_ID_MIN && id <= RIASEC_ID_MAX;
        });
        
        SKILLS_QUESTIONS = ALL_QUESTIONS.filter(q => {
            const id = parseInt(q.id);
            return id >= SKILLS_ID_MIN && id <= SKILLS_ID_MAX;
        });
        
        console.log(`RIASEC preguntas: ${RIASEC_QUESTIONS.length}, SKILLS preguntas: ${SKILLS_QUESTIONS.length}`);
        
        // Cargar respuestas guardadas de la BD
        await loadSavedAnswers();
        
        return true;
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar las preguntas: ' + error.message);
        return false;
    }
}

/**
 * Carga las respuestas guardadas en la BD si existen
 */
async function loadSavedAnswers() {
    try {
        const response = await fetch('/api/test-status', {
            method: 'GET',
            credentials: 'include'
        });

        const data = await response.json();

        if (data.success && data.status.answers && Object.keys(data.status.answers).length > 0) {
            console.log('📥 Cargando respuestas guardadas:', data.status.answers);
            
            // Restaurar respuestas en memoria
            Object.entries(data.status.answers).forEach(([questionId, answer]) => {
                const qId = parseInt(questionId);
                if (qId >= RIASEC_ID_MIN && qId <= RIASEC_ID_MAX) {
                    riasecAnswers[questionId] = answer;
                } else if (qId >= SKILLS_ID_MIN && qId <= SKILLS_ID_MAX) {
                    skillsAnswers[questionId] = answer;
                }
            });
            
            console.log('✅ Respuestas restauradas. RIASEC:', riasecAnswers, 'SKILLS:', skillsAnswers);
        }
    } catch (error) {
        console.error('Error cargando respuestas guardadas:', error);
        // No es fatal - solo continuar sin respuestas previas
    }
}

/**
 * Actualiza TEST_QUESTIONS según el test actual
 */
function updateTestQuestions() {
    if (currentTest === TEST_STATES.RIASEC) {
        TEST_QUESTIONS = RIASEC_QUESTIONS;
    } else if (currentTest === TEST_STATES.SKILLS) {
        TEST_QUESTIONS = SKILLS_QUESTIONS;
    }
    
    TOTAL_PAGES = Math.ceil(TEST_QUESTIONS.length / QUESTIONS_PER_PAGE);
    console.log(`Test ${currentTest}: ${TEST_QUESTIONS.length} preguntas en ${TOTAL_PAGES} páginas`);
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
    
    // Resetear posición a la primera página del RIASEC
    currentTest = TEST_STATES.RIASEC;
    currentPage = 1;
    QUESTIONS_PER_PAGE = RIASEC_QUESTIONS_PER_PAGE;
    updateTestQuestions();
    
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
        const labelMin = currentTest === TEST_STATES.RIASEC 
            ? 'Me desagrada mucho' 
            : 'Me cuesta mucho realizar esto';
        const labelMax = currentTest === TEST_STATES.RIASEC 
            ? 'Me encanta hacerlo' 
            : 'Creo que puedo hacer esto con facilidad';
        
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
    
    // Actualizar las preguntas según el nuevo test
    updateTestQuestions();
    
    // Mostrar la primera página del nuevo test
    loadPage(currentPage);
}

/**
 * Completa todas las pruebas
 * Guarda respuestas finales, calcula perfil RIASEC y redirige a predicciones
 */
async function completeAllTests() {
    // Guardar respuestas finales
    await saveAnswersForCurrentPage();
    
    console.log('✓ Todas las pruebas completadas');
    console.log('Respuestas RIASEC:', riasecAnswers);
    console.log('Respuestas Habilidades:', skillsAnswers);
    
    // Calcular perfil RIASEC del usuario
    const riasecProfile = calculateRIASECProfile();
    console.log('Perfil RIASEC calculado:', riasecProfile);
    
    // Guardar perfil en localStorage para la página de predicciones
    localStorage.setItem('riasec_profile', JSON.stringify(riasecProfile));
    
    // Redirigir a la página de predicciones con parámetro para recalcular
    window.location.href = '/predicciones?recalculate=true';
}

/**
 * Calcula el perfil RIASEC basado en las respuestas
 * Las preguntas están mapeadas a categorías RIASEC
 */
function calculateRIASECProfile() {
    // Mapeo de preguntas a categorías RIASEC
    // Este mapeo debería venir de la BD, pero por ahora lo hacemos en el frontend
    // Asumiendo que las preguntas están distribuidas equitativamente
    
    const riasecMap = {
        // Preguntas 1-5: Realista (Realistic)
        1: 'R', 2: 'R', 3: 'R', 4: 'R', 5: 'R',
        // Preguntas 6-10: Investigador (Investigative)
        6: 'I', 7: 'I', 8: 'I', 9: 'I', 10: 'I',
        // Preguntas 11-15: Artístico (Artistic)
        11: 'A', 12: 'A', 13: 'A', 14: 'A', 15: 'A',
        // Preguntas 16-20: Social
        16: 'S', 17: 'S', 18: 'S', 19: 'S', 20: 'S',
        // Preguntas 21-25: Emprendedor (Enterprising)
        21: 'E', 22: 'E', 23: 'E', 24: 'E', 25: 'E',
        // Preguntas 26-30: Convencional (Conventional)
        26: 'C', 27: 'C', 28: 'C', 29: 'C', 30: 'C'
    };
    
    // Inicializar contadores
    const categoryScores = {
        'R': { sum: 0, count: 0 },
        'I': { sum: 0, count: 0 },
        'A': { sum: 0, count: 0 },
        'S': { sum: 0, count: 0 },
        'E': { sum: 0, count: 0 },
        'C': { sum: 0, count: 0 }
    };
    
    // Procesar respuestas RIASEC
    Object.entries(riasecAnswers).forEach(([questionId, score]) => {
        const qId = parseInt(questionId);
        const category = riasecMap[qId];
        
        if (category && categoryScores[category]) {
            categoryScores[category].sum += score;
            categoryScores[category].count += 1;
        }
    });
    
    // Calcular promedios
    const profile = {};
    Object.entries(categoryScores).forEach(([category, data]) => {
        if (data.count > 0) {
            profile[category] = data.sum / data.count;
        } else {
            profile[category] = 0; // Si no hay respuestas para esta categoría
        }
    });
    
    return profile;
}