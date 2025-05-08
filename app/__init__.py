from flask import Flask
from flask_cors import CORS
from app.models import db
from app.config import Config
from services.message_service import AnimalFactsService
from controllers.message_controller import MessageController
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'views.login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Cargar configuración
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    CORS(app)

    login_manager.init_app(app)

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

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.get(user_id)

    # Crear tablas de la base de datos y usuarios por defecto
    with app.app_context():
        db.create_all()

        # Crear usuarios por defecto si no existen
        from app.models.user import User
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin', is_admin=True)
            db.session.add(admin)

        if not User.query.filter_by(username='user').first():
            user = User(username='user', password='user', is_admin=False)
            db.session.add(user)

        db.session.commit()

    return app
