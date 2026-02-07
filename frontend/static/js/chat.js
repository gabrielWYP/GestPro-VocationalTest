/**
 * Chat Widget - Lógica del Chatbot con Pingüinito
 */

class ChatWidget {
    constructor() {
        this.toggleBtn = document.getElementById('chat-toggle-btn');
        this.panel = document.getElementById('chat-panel');
        this.closeBtn = document.getElementById('chat-close-btn');
        this.messagesContainer = document.getElementById('chat-messages');
        this.input = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('chat-send-btn');
        this.resetBtn = document.getElementById('chat-reset-btn');

        this.isOpen = false;
        this.isLoading = false;

        this.init();
    }

    init() {
        /**
         * Event Listeners
         */
        this.toggleBtn.addEventListener('click', () => this.toggle());
        this.closeBtn.addEventListener('click', () => this.close());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.resetBtn.addEventListener('click', () => this.resetChat());
        
        // Enter para enviar
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isLoading) {
                this.sendMessage();
            }
        });

        console.log('✅ ChatWidget inicializado');
    }

    /**
     * Abre/cierra el panel del chat
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.panel.classList.add('open');
        this.isOpen = true;
        this.input.focus();
        this.toggleBtn.classList.remove('pulse');
    }

    close() {
        this.panel.classList.remove('open');
        this.isOpen = false;
    }

    /**
     * Envía mensaje al backend
     */
    async sendMessage() {
        const message = this.input.value.trim();

        if (!message) {
            return;
        }

        if (this.isLoading) {
            return;
        }

        // Limpiar input
        this.input.value = '';
        this.input.disabled = true;
        this.sendBtn.disabled = true;
        this.isLoading = true;

        // Agregar mensaje del usuario al UI
        this.addMessage(message, 'user');

        // Mostrar indicador de "escribiendo"
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (data.success) {
                // Remover indicador de escritura
                this.removeTypingIndicator();

                // Agregar respuesta del bot
                this.addMessage(data.response, 'bot');

                // Logging
                console.log(`📊 Tokens usados: ${data.tokens_used}`);
            } else {
                this.removeTypingIndicator();
                const errorMsg = data.error || 'Error al procesar tu pregunta';
                this.addMessage(errorMsg, 'bot');
                console.error('❌ Error:', errorMsg);
            }
        } catch (error) {
            this.removeTypingIndicator();
            console.error('❌ Error de red:', error);
            this.addMessage(
                'Disculpa, hubo un problema conectando con el asistente. Intenta de nuevo.',
                'bot'
            );
        } finally {
            this.input.disabled = false;
            this.sendBtn.disabled = false;
            this.isLoading = false;
            this.input.focus();
        }
    }

    /**
     * Agrega un mensaje al historial visual
     */
    addMessage(text, sender) {
        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${sender}-message`;

        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        contentEl.textContent = text;

        messageEl.appendChild(contentEl);
        this.messagesContainer.appendChild(messageEl);

        // Scroll al último mensaje
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    /**
     * Muestra indicador de "escribiendo"
     */
    showTypingIndicator() {
        const indicatorEl = document.createElement('div');
        indicatorEl.className = 'chat-message bot-message';
        indicatorEl.id = 'typing-indicator';
        indicatorEl.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;

        this.messagesContainer.appendChild(indicatorEl);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    /**
     * Remueve el indicador de "escribiendo"
     */
    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    /**
     * Reinicia la sesión del chat
     */
    async resetChat() {
        // Confirmar acción
        if (!confirm('¿Deseas empezar una nueva conversación?\nSe borrarán todos los mensajes.')) {
            return;
        }

        try {
            // Llamar al endpoint de reset
            const response = await fetch('/api/chat/reset', {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                // Limpiar el UI
                this.messagesContainer.innerHTML = `
                    <div class="chat-message bot-message">
                        <div class="message-content">
                            Hola! Soy Pingüinito 🐧, tu asistente vocacional. 
                            ¿En qué puedo ayudarte hoy? Pregúntame sobre carreras, habilidades, 
                            o cualquier duda sobre tu futuro profesional.
                        </div>
                    </div>
                `;
                console.log('✅ Chat reseteado');
            } else {
                alert('Error al resetear el chat. Intenta de nuevo.');
            }
        } catch (error) {
            console.error('❌ Error al resetear:', error);
            alert('Error al resetear el chat. Intenta de nuevo.');
        }
    }

    /**
     * Notifica al usuario cuando hay un nuevo mensaje (si está cerrado)
     */
    notifyNewMessage() {
        if (!this.isOpen) {
            this.toggleBtn.classList.add('pulse');
        }
    }
}

/**
 * Inicializa el widget cuando el DOM esté listo
 */
document.addEventListener('DOMContentLoaded', () => {
    window.chatWidget = new ChatWidget();
    console.log('🐧 Chatbot listo para usar');
});
