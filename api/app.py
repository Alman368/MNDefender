from flask import Flask, request, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_praetorian import Praetorian
from datetime import timedelta

# Initialize SQLAlchemy
db = SQLAlchemy()
guard = Praetorian()

def create_app():
    app = Flask(__name__)

    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://alberto:svaia@localhost/svaia'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 1}
    app.config['JWT_REFRESH_LIFESPAN'] = {'days': 7}

    # Initialize CORS


    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Import User model and initialize Flask-Praetorian
    from api.models.user import User
    guard.init_app(app, User)

    # Initialize API
    api = Api(app)

    # Import resources
    from api.resources.user_resource import UserListResource, UserResource
    from api.resources.project_resource import ProjectListResource, ProjectResource
    from api.resources.auth_resource import LoginResource, AuthTestResource, RefreshResource
    # Register API routes
    api.add_resource(UserListResource, '/users')
    api.add_resource(UserResource, '/users/<int:user_id>')
    api.add_resource(ProjectListResource, '/projects')
    api.add_resource(ProjectResource, '/projects/<int:project_id>')
    api.add_resource(LoginResource, '/auth/login')
    api.add_resource(RefreshResource, '/auth/refresh')
    api.add_resource(AuthTestResource, '/auth/test')

    # Create database tables
    with app.app_context():
        from api.models.user import User
        from api.models.project import Project
        db.create_all()

        # Create default users if they don't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                nombre='Administrador',
                apellidos='Sistema',
                correo='admin@example.com',
                username='admin',
                password=guard.hash_password('Admin123!'),  # Hash with Praetorian
                is_admin=True
            )
            db.session.add(admin)

        if not User.query.filter_by(username='user').first():
            user = User(
                nombre='Usuario',
                apellidos='Normal',
                correo='user@example.com',
                username='user',
                password=guard.hash_password('User123!'),  # Hash with Praetorian
                is_admin=False
            )
            db.session.add(user)

        db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
