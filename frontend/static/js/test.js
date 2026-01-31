// Test de Orientación Vocacional - Lógica del Test
// Sistema de preguntas por página con sliders de 1-5

// Configuración de cache de preguntas
const QUESTIONS_CACHE_KEY = 'test_questions_cache';
const QUESTIONS_CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 1 día en milisegundos

// Constantes de puntaje
const SCORE_MIN = 1;
const SCORE_MAX = 5;
const SCORE_LABELS = {
    1: "Me desagrada mucho",
    2: "No me atrae",
    3: "Neutral",
    4: "Me gusta",
    5: "Me encanta hacerlo"
};

// Preguntas por página
const QUESTIONS_PER_PAGE = 6;

let currentPage = 1;
let testAnswers = {}; // Objeto para almacenar respuestas: { questionId: score }
let TEST_QUESTIONS = []; // Se cargarán desde la API
let TOTAL_PAGES = 0;

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
    
    document.getElementById('intro').style.display = 'none';
    document.getElementById('questions').style.display = 'block';
    loadPage(currentPage);
}

/**
 * Carga una página específica del test con 6 preguntas
 * @param {number} pageNumber - Número de página (1-indexed)
 */
function loadPage(pageNumber) {
    if (pageNumber < 1 || pageNumber > TOTAL_PAGES) {
        return;
    }
    
    currentPage = pageNumber;
    const pageQuestions = getQuestionsForPage(pageNumber);
    
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
        const score = testAnswers[question.id] || null; // null = no seleccionado
        html += `
            <div class="question-item">
                <div class="question-header">
                    <h4>Pregunta ${question.id}</h4>
                </div>
                <p class="question-text">${question.text}</p>
                
                <div class="score-buttons-container">
                    <div class="score-labels">
                        <span class="label-min">Me desagrada mucho</span>
                        <span class="label-max">Me encanta hacerlo</span>
                    </div>
                    <div class="score-buttons">
                        ${[1, 2, 3, 4, 5].map(value => `
                            <button 
                                class="score-btn score-btn-${value} ${score === value ? 'selected' : ''}"
                                onclick="updateScore(${question.id}, ${value})"
                                title="${SCORE_LABELS[value]}">
                                <span class="score-btn-number">${value}</span>
                            </button>
                        `).join('')}
                    </div>
                    <div class="score-feedback" id="feedback-${question.id}">
                        ${score ? `<span class="feedback-text">${SCORE_LABELS[score]}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    
    // Botones de navegación
    html += `
        <div class="navigation">
            <button onclick="previousPage()" class="btn btn-secondary" ${pageNumber === 1 ? 'disabled' : ''}>
                ← Página Anterior
            </button>
            <button onclick="submitTest()" class="btn btn-primary" ${pageNumber === TOTAL_PAGES ? '' : 'style="display: none;"'}>
                Enviar Test
            </button>
            <button onclick="nextPage()" class="btn btn-primary" ${pageNumber === TOTAL_PAGES ? 'disabled' : ''}>
                Siguiente Página →
            </button>
        </div>
    `;
    
    document.getElementById('question-container').innerHTML = html;
    updateProgressBar();
}

/**
 * Actualiza el puntaje de una pregunta
 * @param {number} questionId - ID de la pregunta
 * @param {number} value - Valor del selector (1-5)
 */
function updateScore(questionId, value) {
    testAnswers[questionId] = parseInt(value);
    
    // Actualizar los botones: remover "selected" de todos y agregar al nuevo
    const buttons = document.querySelectorAll(`button[onclick*="updateScore(${questionId}"]`);
    buttons.forEach(btn => btn.classList.remove('selected'));
    document.querySelector(`button[onclick="updateScore(${questionId}, ${value})"]`).classList.add('selected');
    
    // Actualizar feedback
    const feedbackElement = document.getElementById(`feedback-${questionId}`);
    if (feedbackElement) {
        feedbackElement.innerHTML = `<span class="feedback-text">${SCORE_LABELS[value]}</span>`;
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
 * Carga la siguiente página
 */
function nextPage() {
    if (currentPage < TOTAL_PAGES) {
        loadPage(currentPage + 1);
    }
}

/**
 * Carga la página anterior
 */
function previousPage() {
    if (currentPage > 1) {
        loadPage(currentPage - 1);
    }
}

/**
 * Actualiza la barra de progreso
 */
function updateProgressBar() {
    const progress = (currentPage / TOTAL_PAGES) * 100;
    document.getElementById('progress').style.width = progress + '%';
}

/**
 * Envía el test completado al servidor
 */
async function submitTest() {
    // Validar que todas las preguntas estén respondidas
    if (Object.keys(testAnswers).length < TEST_QUESTIONS.length) {
        alert('Por favor responde todas las preguntas antes de enviar');
        return;
    }
    
    try {
        const response = await fetch('/api/test-submit', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                answers: testAnswers
            })
        });

        const data = await response.json();
        
        if (data.success) {
            displayResults(data.career, data.scores);
        } else {
            alert('Error al procesar el test: ' + (data.message || 'Intenta de nuevo'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al procesar el test');
    }
}

/**
 * Muestra los resultados del test
 * @param {Object} career - Objeto con información de la carrera recomendada
 * @param {Object} scores - Objeto con puntuaciones de todas las carreras
 */
function displayResults(career, scores) {
    document.getElementById('questions').style.display = 'none';
    document.getElementById('results').style.display = 'block';
    
    const careerHtml = `
        <div class="career-result">
            <h3>${career.name}</h3>
            <p>${career.description}</p>
            <div class="skills">
                <h4>Habilidades Clave:</h4>
                <ul>
                    ${(career.skills || []).map(skill => `<li>${skill}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
    
    const scoresHtml = `
        <div class="scores-detail">
            <h4>Tus Resultados:</h4>
            <div class="scores-list">
                ${Object.entries(scores).map(([type, score]) => {
                    return `<div class="score-item">
                        <span>${type}:</span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${score * 10}%"></div>
                        </div>
                        <span>${score}/10</span>
                    </div>`;
                }).join('')}
            </div>
        </div>
    `;
    
    document.getElementById('result-career').innerHTML = careerHtml;
    document.getElementById('result-scores').innerHTML = scoresHtml;
}

