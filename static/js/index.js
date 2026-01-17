// Página de Inicio - Funciones Auxiliares

/**
 * Desplaza suavemente a una sección específica
 * @param {string} sectionId - ID de la sección a la que desplazarse
 */
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}
