"""
Servicio de Chat con Groq
Sistema de guardrails para asesoramiento vocacional
"""

import os
import re
import logging
from typing import Dict, List, Tuple
from groq import Groq

logger = logging.getLogger(__name__)

# Configuración de Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
CHAT_TEMPERATURE = float(os.getenv('CHAT_TEMPERATURE', '0.4'))
CHAT_MAX_RESPONSE_TOKENS = int(os.getenv('CHAT_MAX_RESPONSE_TOKENS', '1000'))
CHAT_MAX_MESSAGE_LENGTH = int(os.getenv('CHAT_MAX_MESSAGE_LENGTH', '500'))
CHAT_MODEL = os.getenv('CHAT_MODEL', 'llama-3.3-70b-versatile')

# Palabras prohibidas/sensibles
BLOCKED_KEYWORDS = [
    'contraseña', 'password', 'api key', 'apikey', 'secret', 'token',
    'base de datos', 'database', 'admin', 'root', 'sql injection',
    'hack', 'cracking', 'numero de tarjeta', 'credit card'
]

# System prompt para vocational guidance
SYSTEM_PROMPT = """Eres un asistente vocacional llamado Pingüinito. Tu objetivo es ayudar estudiantes 
a explorar carreras y orientación vocacional basada en sus intereses y habilidades.

RESTRICCIONES:
- Solo responde sobre orientación vocacional, carreras, habilidades y educación
- Si preguntan sobre algo fuera de tema, responde amablemente redirigiéndolos al tema
- Sé conciso y amigable (máximo 3 párrafos)
- Usa datos sobre carreras RIASEC (Realista, Investigador, Artístico, Social, Emprendedor, Convencional)
- No guardes información personal del usuario

TONO: Amigable, profesional, motivador. Actúa como un mentor vocacional."""


class ChatService:
    """Servicio principal de chat con Groq"""

    def __init__(self):
        """Inicializa cliente de Groq"""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY no configurada en .env")
        
        self.client = Groq(api_key=GROQ_API_KEY)
        self.conversation_history = []
        logger.info(f"ChatService inicializado con Groq (modelo: {CHAT_MODEL})")

    def validate_message(self, message: str) -> Tuple[bool, str]:
        """
        Valida mensaje de usuario
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            (is_valid, error_message)
        """
        # Validar vacío
        if not message or not message.strip():
            return False, "El mensaje no puede estar vacío"
        
        # Validar longitud
        if len(message) > CHAT_MAX_MESSAGE_LENGTH:
            return False, f"Mensaje muy largo (máx {CHAT_MAX_MESSAGE_LENGTH} caracteres)"
        
        # Detectar inyección de prompt
        injection_patterns = [
            r'ignore.*instruction',
            r'system prompt',
            r'you are now',
            r'olvidar|forget.*previous',
            r'act as if'
        ]
        
        message_lower = message.lower()
        for pattern in injection_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return False, "Mensaje contiene patrones sospechosos"
        
        # Detectar palabras prohibidas
        for keyword in BLOCKED_KEYWORDS:
            if keyword.lower() in message_lower:
                return False, "Tu mensaje contiene palabras que no puedo procesar"
        
        return True, ""

    def send_message(self, message: str) -> Dict:
        """
        Envía mensaje a Groq y obtiene respuesta
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            {
                'success': bool,
                'response': str,
                'error': str,
                'tokens_used': int
            }
        """
        # Validar mensaje
        is_valid, error = self.validate_message(message)
        if not is_valid:
            return {
                'success': False,
                'response': '',
                'error': error,
                'tokens_used': 0
            }
        
        try:
            # Agregar mensaje a historial
            self.conversation_history.append({
                "role": "user",
                "content": message
            })
            
            # Enviar a Groq
            response = self.client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    }
                ] + self.conversation_history,
                temperature=CHAT_TEMPERATURE,
                max_tokens=CHAT_MAX_RESPONSE_TOKENS,
            )
            
            response_text = response.choices[0].message.content
            
            # Validar respuesta
            if not response_text or len(response_text.strip()) == 0:
                return {
                    'success': False,
                    'response': '',
                    'error': 'No se pudo obtener respuesta',
                    'tokens_used': 0
                }
            
            # Agregar respuesta al historial
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            # Obtener token count
            tokens_used = response.usage.completion_tokens + response.usage.prompt_tokens
            
            logger.info(f"Chat response generado exitosamente (tokens: {tokens_used})")
            
            return {
                'success': True,
                'response': response_text,
                'error': '',
                'tokens_used': tokens_used
            }
        
        except Exception as e:
            logger.error(f"Error en Groq API: {str(e)}")
            return {
                'success': False,
                'response': '',
                'error': 'Error al conectar con el asistente. Intenta de nuevo.',
                'tokens_used': 0
            }

    def reset_session(self):
        """Reinicia la sesión de chat y limpia historial"""
        self.conversation_history = []
        logger.info("Sesión de chat reseteada")


# Instancia global del servicio
_chat_service_instance = None


def get_chat_service() -> ChatService:
    """Factory para obtener instancia del servicio"""
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService()
    return _chat_service_instance
