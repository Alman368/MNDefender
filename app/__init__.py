from flask import Flask
from flask_cors import CORS
from app.models import db
from app.config import Config
from services.message_service import AnimalFactsService
from controllers.message_controller import MessageController
from flask_login import LoginManager
from datetime import timedelta

login_manager = LoginManager()
login_manager.login_view = 'views.login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
login_manager.session_protection = 'strong'  # Protección contra sesiones concurrentes

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Cargar configuración
    app.config.from_object(config_class)

    # Configuración de sesión
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Sesión expira después de 1 hora
    app.config['SESSION_COOKIE_SECURE'] = True  # Solo enviar cookies por HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevenir acceso a cookies por JavaScript
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protección CSRF

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
            try:
                admin = User(
                    nombre='Administrador',
                    apellidos='Sistema',
                    correo='admin@example.com',
                    username='admin',
                    password='Admin123!',  # Contraseña segura por defecto
                    is_admin=True
                )
                db.session.add(admin)
            except ValueError as e:
                print(f"Error al crear usuario admin: {e}")

        if not User.query.filter_by(username='user').first():
            try:
                user = User(
                    nombre='Usuario',
                    apellidos='Normal',
                    correo='user@example.com',
                    username='user',
                    password='User123!',  # Contraseña segura por defecto
                    is_admin=False
                )
                db.session.add(user)
            except ValueError as e:
                print(f"Error al crear usuario normal: {e}")

        db.session.commit()

    return app
