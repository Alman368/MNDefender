from flask import request, jsonify
import traceback


class MessageController:
    def __init__(self, message_service):
        self.message_service = message_service

    def send_message(self):
        try:
            # Verificar que existe el JSON y el campo message
            if not request.json:
                return jsonify({'error': 'No se recibió datos JSON'}), 400

            if 'message' not in request.json:
                return jsonify({'error': 'Campo "message" requerido'}), 400

            text = request.json['message']

            # Verificar que el mensaje no esté vacío
            if not text or not text.strip():
                return jsonify({'error': 'El mensaje no puede estar vacío'}), 400

            print(f"Procesando mensaje: {text}")  # Debug log

            # Obtener respuesta del servicio de IA
            response_message = self.message_service.get_response(text)

            print(f"Respuesta obtenida: {response_message[:100]}...")  # Debug log

            return jsonify({'message': response_message})

        except KeyError as e:
            error_msg = f"Campo requerido faltante: {str(e)}"
            print(f"Error KeyError: {error_msg}")
            return jsonify({'error': error_msg}), 400

        except Exception as e:
            error_msg = f"Error interno del servidor: {str(e)}"
            print(f"Error inesperado: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': error_msg}), 500
