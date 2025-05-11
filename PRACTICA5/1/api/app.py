from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5000"]}})

# Configuración de la base de datos desde variables de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost/svaia')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')

db = SQLAlchemy(app)
api = Api(app)

# Modelos
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Proyecto(db.Model):
    __tablename__ = 'proyectos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# Recursos de la API
class UserResource(Resource):
    def get(self, user_id=None):
        try:
            if user_id:
                user = User.query.get_or_404(user_id)
                return {
                    'id': user.id,
                    'nombre': user.nombre,
                    'apellidos': user.apellidos,
                    'correo': user.correo,
                    'username': user.username,
                    'is_admin': user.is_admin
                }
            else:
                users = User.query.all()
                return [{
                    'id': user.id,
                    'nombre': user.nombre,
                    'apellidos': user.apellidos,
                    'correo': user.correo,
                    'username': user.username,
                    'is_admin': user.is_admin
                } for user in users]
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        try:
            data = request.get_json()
            if not all(k in data for k in ['nombre', 'apellidos', 'correo', 'username', 'password']):
                return {'error': 'Faltan campos requeridos'}, 400

            if User.query.filter_by(username=data['username']).first():
                return {'error': 'El nombre de usuario ya existe'}, 400

            if User.query.filter_by(correo=data['correo']).first():
                return {'error': 'El correo ya está registrado'}, 400

            user = User(
                nombre=data['nombre'],
                apellidos=data['apellidos'],
                correo=data['correo'],
                username=data['username'],
                password_hash=generate_password_hash(data['password']),
                is_admin=data.get('is_admin', False)
            )
            db.session.add(user)
            db.session.commit()
            return {'message': 'Usuario creado exitosamente', 'id': user.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        try:
            user.nombre = data.get('nombre', user.nombre)
            user.apellidos = data.get('apellidos', user.apellidos)
            user.correo = data.get('correo', user.correo)
            user.username = data.get('username', user.username)
            if 'password' in data:
                user.password_hash = generate_password_hash(data['password'])
            user.is_admin = data.get('is_admin', user.is_admin)
            db.session.commit()
            return {'message': 'Usuario actualizado exitosamente'}
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'Usuario eliminado exitosamente'}
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

class ProyectoResource(Resource):
    def get(self, proyecto_id=None):
        if proyecto_id:
            proyecto = Proyecto.query.get_or_404(proyecto_id)
            return {
                'id': proyecto.id,
                'nombre': proyecto.nombre,
                'descripcion': proyecto.descripcion,
                'usuario_id': proyecto.usuario_id,
                'fecha_creacion': proyecto.fecha_creacion.isoformat(),
                'fecha_modificacion': proyecto.fecha_modificacion.isoformat()
            }
        else:
            proyectos = Proyecto.query.all()
            return [{
                'id': p.id,
                'nombre': p.nombre,
                'descripcion': p.descripcion,
                'usuario_id': p.usuario_id,
                'fecha_creacion': p.fecha_creacion.isoformat(),
                'fecha_modificacion': p.fecha_modificacion.isoformat()
            } for p in proyectos]

    def post(self):
        data = request.get_json()
        try:
            proyecto = Proyecto(
                nombre=data['nombre'],
                descripcion=data.get('descripcion', ''),
                usuario_id=data['usuario_id']
            )
            db.session.add(proyecto)
            db.session.commit()
            return {'message': 'Proyecto creado exitosamente', 'id': proyecto.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

    def put(self, proyecto_id):
        proyecto = Proyecto.query.get_or_404(proyecto_id)
        data = request.get_json()
        try:
            proyecto.nombre = data.get('nombre', proyecto.nombre)
            proyecto.descripcion = data.get('descripcion', proyecto.descripcion)
            proyecto.usuario_id = data.get('usuario_id', proyecto.usuario_id)
            db.session.commit()
            return {'message': 'Proyecto actualizado exitosamente'}
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

    def delete(self, proyecto_id):
        proyecto = Proyecto.query.get_or_404(proyecto_id)
        try:
            db.session.delete(proyecto)
            db.session.commit()
            return {'message': 'Proyecto eliminado exitosamente'}
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

# Registrar recursos
api.add_resource(UserResource, '/api/users', '/api/users/<int:user_id>')
api.add_resource(ProyectoResource, '/api/proyectos', '/api/proyectos/<int:proyecto_id>')

# Añadir manejador de errores global
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001) 