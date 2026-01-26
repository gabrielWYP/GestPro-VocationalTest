/**
 * Constantes del Test RIASEC
 * 36 preguntas divididas en 6 páginas (6 preguntas por página)
 * 
 * RIASEC = Realista, Investigador, Artístico, Social, Emprendedor, Convencional
 */

const TEST_QUESTIONS = [
  // PÁGINA 1 - Preguntas 1-6
  {
    id: 1,
    text: "Trabajar con máquinas y herramientas",
    type: "Realista"
  },
  {
    id: 2,
    text: "Resolver problemas científicos complejos",
    type: "Investigador"
  },
  {
    id: 3,
    text: "Crear obras de arte o música",
    type: "Artístico"
  },
  {
    id: 4,
    text: "Ayudar a otros a resolver problemas personales",
    type: "Social"
  },
  {
    id: 5,
    text: "Dirigir un negocio o proyecto",
    type: "Emprendedor"
  },
  {
    id: 6,
    text: "Organizar datos y mantener registros",
    type: "Convencional"
  },

  // PÁGINA 2 - Preguntas 7-12
  {
    id: 7,
    text: "Reparar objetos dañados",
    type: "Realista"
  },
  {
    id: 8,
    text: "Investigar cómo funcionan las cosas",
    type: "Investigador"
  },
  {
    id: 9,
    text: "Escribir historias o poemas",
    type: "Artístico"
  },
  {
    id: 10,
    text: "Enseñar a otros nuevas habilidades",
    type: "Social"
  },
  {
    id: 11,
    text: "Persuadir a otros para que acepten mis ideas",
    type: "Emprendedor"
  },
  {
    id: 12,
    text: "Trabajar en un ambiente estructurado y ordenado",
    type: "Convencional"
  },

  // PÁGINA 3 - Preguntas 13-18
  {
    id: 13,
    text: "Trabajar en proyectos de construcción",
    type: "Realista"
  },
  {
    id: 14,
    text: "Conducir experimentos científicos",
    type: "Investigador"
  },
  {
    id: 15,
    text: "Diseñar productos o espacios",
    type: "Artístico"
  },
  {
    id: 16,
    text: "Trabajar en equipos colaborativos",
    type: "Social"
  },
  {
    id: 17,
    text: "Tomar decisiones rápidas bajo presión",
    type: "Emprendedor"
  },
  {
    id: 18,
    text: "Seguir procedimientos y normas establecidas",
    type: "Convencional"
  },

  // PÁGINA 4 - Preguntas 19-24
  {
    id: 19,
    text: "Trabajar al aire libre o en terreno",
    type: "Realista"
  },
  {
    id: 20,
    text: "Leer artículos académicos especializados",
    type: "Investigador"
  },
  {
    id: 21,
    text: "Participar en actividades culturales",
    type: "Artístico"
  },
  {
    id: 22,
    text: "Escuchar y apoyar a personas en dificultades",
    type: "Social"
  },
  {
    id: 23,
    text: "Buscar nuevas oportunidades de negocio",
    type: "Emprendedor"
  },
  {
    id: 24,
    text: "Mantener la precisión en detalles",
    type: "Convencional"
  },

  // PÁGINA 5 - Preguntas 25-30
  {
    id: 25,
    text: "Trabajar con mis manos en proyectos prácticos",
    type: "Realista"
  },
  {
    id: 26,
    text: "Desarrollar nuevas teorías o conceptos",
    type: "Investigador"
  },
  {
    id: 27,
    text: "Expresar mi creatividad en mi trabajo",
    type: "Artístico"
  },
  {
    id: 28,
    text: "Hacer diferencia positiva en la comunidad",
    type: "Social"
  },
  {
    id: 29,
    text: "Ganar dinero y tener éxito financiero",
    type: "Emprendedor"
  },
  {
    id: 30,
    text: "Trabajar con números y cálculos",
    type: "Convencional"
  },

  // PÁGINA 6 - Preguntas 31-36
  {
    id: 31,
    text: "Usar equipos técnicos especializados",
    type: "Realista"
  },
  {
    id: 32,
    text: "Analizar información y encontrar patrones",
    type: "Investigador"
  },
  {
    id: 33,
    text: "Trabajar en proyectos artísticos innovadores",
    type: "Artístico"
  },
  {
    id: 34,
    text: "Formar y desarrollar a otros",
    type: "Social"
  },
  {
    id: 35,
    text: "Liderar equipos hacia objetivos ambiciosos",
    type: "Emprendedor"
  },
  {
    id: 36,
    text: "Gestionar archivos y documentación",
    type: "Convencional"
  }
];

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

// Total de páginas
const TOTAL_PAGES = Math.ceil(TEST_QUESTIONS.length / QUESTIONS_PER_PAGE);

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
