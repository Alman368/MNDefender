from flask import Flask
from flask_cors import CORS
from app.models import db
from app.config import Config
from services.message_service import AnimalFactsService
from controllers.message_controller import MessageController

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Cargar configuración
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    CORS(app)

    # Inicializa el MessageController
    message_controller = MessageController(AnimalFactsService())

    # Registrar blueprints
    from app.views import views_bp
    from app.api import api_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Ruta del controlador de mensajes
    app.add_url_rule('/send-message',
                     view_func=message_controller.send_message,
                     methods=['POST'])

    # Crear tablas de la base de datos
    with app.app_context():
        db.create_all()

    return app
