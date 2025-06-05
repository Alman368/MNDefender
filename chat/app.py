from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import functools
import os

app = Flask(__name__)
CORS(app)

# API Key for simple authentication
API_KEY = os.environ.get('CHAT_API_KEY', 'your-api-key')

# Predefined responses for the chat
responses = [
    "¡Hola! ¿En qué puedo ayudarte hoy?",
    "Muy bien, pero sabes que los gatos tienen 32 músculos en cada oreja.",
    "No me importa porque yo sé que los osos polares son zurdos.",
    "A qué tú no sabías que las abejas tienen 5 ojos.",
    "¿Sabías que los elefantes son los únicos animales que no pueden saltar?",
    "A mí me gusta saber que las jirafas tienen la lengua de color azul oscuro.",
    "Te va a parecer increible pero ¿sabías que los pingüinos tienen rodillas?",
    "¿Sabías que los cocodrilos no pueden sacar la lengua?",
    "Hoy no tengo ganas de trabajar pero te diré que los flamencos son rosados por comer camarones.",
    "No sé de qué me hablas pero yo sé que los perros son capaces de oír sonidos a 225 metros de distancia.",
    "Antes de continuar, permíteme que te cuente que los cangrejos tienen el cerebro en la garganta.",
    "Qué pereza, pero te diré que los ratones no pueden vomitar.",
    "Cuéntame algo que no sepa, como que las mariposas saborean con sus patas."
]

def require_api_key(view_function):
    @functools.wraps(view_function)
    def decorated_function(*args, **kwargs):
        # For browser-based requests using JavaScript, we'll accept the API key in a header
        api_key = request.headers.get('X-API-Key')

        # For direct API calls, we'll also accept the API key as a query parameter
        if not api_key:
            api_key = request.args.get('api_key')

        # For testing purposes, don't enforce API key in development
        if app.debug and not api_key:
            return view_function(*args, **kwargs)

        if api_key and api_key == API_KEY:
            return view_function(*args, **kwargs)
        else:
            return jsonify({'error': 'Acceso no autorizado'}), 401

    return decorated_function

@app.route('/api/chat', methods=['POST'])
@require_api_key
def chat():
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({'error': 'No se proporcionó ningún mensaje'}), 400

    # Generate a random response from the predefined list
    response = random.choice(responses)

    return jsonify({'message': response})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'chat-microservice'})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
