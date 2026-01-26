// Test de Orientación Vocacional - Lógica del Test
// Sistema de preguntas por página con sliders de 1-5

let currentPage = 1;
let testAnswers = {}; // Objeto para almacenar respuestas: { questionId: score }

/**
 * Inicia el test - muestra la primera página
 */
function startTest() {
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
        const score = testAnswers[question.id] || 3; // Default a 3 (neutral)
        html += `
            <div class="question-item">
                <div class="question-header">
                    <h4>Pregunta ${question.id}</h4>
                    <span class="question-type">${question.type}</span>
                </div>
                <p class="question-text">${question.text}</p>
                
                <div class="slider-container">
                    <div class="slider-labels">
                        <span class="label-min">Me desagrada mucho</span>
                        <span class="label-max">Me encanta hacerlo</span>
                    </div>
                    <input type="range" 
                        id="slider-${question.id}" 
                        class="score-slider" 
                        min="${SCORE_MIN}" 
                        max="${SCORE_MAX}" 
                        value="${score}"
                        onchange="updateScore(${question.id}, this.value)"
                        oninput="updateSliderLabel(${question.id}, this.value)">
                    <div class="slider-value">
                        <span class="score-number">${score}</span>
                        <span class="score-label" id="label-${question.id}">${SCORE_LABELS[score]}</span>
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
 * @param {number} value - Valor del slider (1-5)
 */
function updateScore(questionId, value) {
    testAnswers[questionId] = parseInt(value);
    updateSliderLabel(questionId, value);
}

/**
 * Actualiza la etiqueta mostrada bajo el slider
 * @param {number} questionId - ID de la pregunta
 * @param {number} value - Valor del slider
 */
function updateSliderLabel(questionId, value) {
    const labelElement = document.getElementById(`label-${questionId}`);
    if (labelElement) {
        labelElement.textContent = SCORE_LABELS[value];
    }
    
    // También actualizar el número mostrado
    const numberElement = document.querySelector(`#slider-${questionId}`).parentElement.querySelector('.score-number');
    if (numberElement) {
        numberElement.textContent = value;
    }
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

