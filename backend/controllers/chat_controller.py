"""
Controlador de Chat - Maneja solicitudes HTTP del chatbot
"""

import logging
from flask import request, jsonify, session
from services.chat_service import get_chat_service

logger = logging.getLogger(__name__)


class ChatController:
    """Controlador para endpoints de chat"""

    @staticmethod
    def send_message():
        """
        Endpoint POST /api/chat/message
        
        Request body:
        {
            "message": "¿Qué carrera me recomendas?"
        }
        
        Response:
        {
            "success": true,
            "response": "Basado en tus intereses...",
            "tokens_used": 45
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Request body requerido'
                }), 400
            
            message = data.get('message', '').strip()
            
            if not message:
                return jsonify({
                    'success': False,
                    'error': 'mensaje requerido'
                }), 400
            
            # Obtener servicio de chat
            chat_service = get_chat_service()
            
            # Enviar mensaje a Gemini
            result = chat_service.send_message(message)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'response': result['response'],
                    'tokens_used': result['tokens_used']
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
        
        except Exception as e:
            logger.error(f"Error en send_message: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor'
            }), 500

    @staticmethod
    def reset_chat():
        """
        Endpoint POST /api/chat/reset
        Reinicia la sesión de chat (sin guardar historial)
        """
        try:
            chat_service = get_chat_service()
            chat_service.reset_session()
            
            return jsonify({
                'success': True,
                'message': 'Chat reseteado'
            }), 200
        
        except Exception as e:
            logger.error(f"Error en reset_chat: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error al resetear chat'
            }), 500
