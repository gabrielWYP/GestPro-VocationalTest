// Test de Orientación Vocacional - Lógica del Test

let questions = [];
let currentQuestion = 0;
let answers = [];

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const questionsData = document.getElementById('questionsData');
    if (questionsData) {
        questions = JSON.parse(questionsData.textContent);
    }
});

/**
 * Inicia el test después de validar los datos del usuario
 */
function startTest() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    
    if (!name || !email) {
        alert('Por favor completa todos los campos');
        return;
    }
    
    document.getElementById('intro').style.display = 'none';
    document.getElementById('questions').style.display = 'block';
    loadQuestion();
}

/**
 * Carga la pregunta actual y la muestra en la interfaz
 */
function loadQuestion() {
    if (currentQuestion >= questions.length) {
        submitTest();
        return;
    }

    const question = questions[currentQuestion];
    const html = `
        <div class="question-card">
            <h3>Pregunta ${currentQuestion + 1} de ${questions.length}</h3>
            <p class="question-text">${question.question}</p>
            <div class="options">
                ${question.options.map((option, idx) => `
                    <label class="option-label">
                        <input type="radio" name="option" value="${option.text}" 
                            ${answers[currentQuestion] === option.text ? 'checked' : ''}>
                        <span>${option.text}</span>
                    </label>
                `).join('')}
            </div>
        </div>
        <div class="navigation">
            <button onclick="previousQuestion()" class="btn btn-secondary" 
                ${currentQuestion === 0 ? 'disabled' : ''}>Anterior</button>
            <button onclick="nextQuestion()" class="btn btn-primary">Siguiente</button>
        </div>
    `;
    document.getElementById('question-container').innerHTML = html;
    updateProgress();
}

/**
 * Avanza a la siguiente pregunta
 */
function nextQuestion() {
    const selected = document.querySelector('input[name="option"]:checked');
    if (!selected) {
        alert('Por favor selecciona una respuesta');
        return;
    }
    
    answers[currentQuestion] = selected.value;
    currentQuestion++;
    loadQuestion();
}

/**
 * Retrocede a la pregunta anterior
 */
function previousQuestion() {
    if (currentQuestion > 0) {
        const selected = document.querySelector('input[name="option"]:checked');
        if (selected) {
            answers[currentQuestion] = selected.value;
        }
        currentQuestion--;
        loadQuestion();
    }
}

/**
 * Actualiza la barra de progreso del test
 */
function updateProgress() {
    const progress = ((currentQuestion + 1) / questions.length) * 100;
    document.getElementById('progress').style.width = progress + '%';
}

/**
 * Envía el test completado al servidor
 */
async function submitTest() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    
    try {
        const response = await fetch('/api/test-submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                answers: answers
            })
        });

        const data = await response.json();
        
        if (data.success) {
            displayResults(data.career, data.scores);
        } else {
            alert('Error al procesar el test');
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
            <div class="result-icon">${career.icon}</div>
            <h3>${career.name}</h3>
            <p>${career.description}</p>
            <div class="skills">
                <h4>Habilidades Clave:</h4>
                <ul>
                    ${career.skills.map(skill => `<li>${skill}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
    
    const scoresHtml = `
        <div class="scores-detail">
            <h4>Puntuación por Carrera:</h4>
            <div class="scores-list">
                ${Object.entries(scores).map(([id, score]) => {
                    return `<div class="score-item">
                        <span>Carrera ${id}:</span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${(score / 4) * 100}%"></div>
                        </div>
                        <span>${score}</span>
                    </div>`;
                }).join('')}
            </div>
        </div>
    `;
    
    document.getElementById('result-career').innerHTML = careerHtml;
    document.getElementById('result-scores').innerHTML = scoresHtml;
}
