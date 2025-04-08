from flask import Flask
from app.services.message_service import AnimalFactsService
from app.controllers.message_controller import MessageController
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    # Enable CORS
    CORS(app)
    
    # Initialize the MessageController
    message_controller = MessageController(AnimalFactsService())
    
    # Register the routes
    app.add_url_rule('/send-message', view_func=message_controller.send_message, methods=['POST'])
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)