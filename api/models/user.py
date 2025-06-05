from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re
from api.app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Changed from password_hash for Praetorian
    is_admin = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Flask-Praetorian specific roles property
    @property
    def roles(self):
        """Required by flask-praetorian for role-based authentication"""
        if self.is_admin:
            return ["admin", "user"]
        return ["user"]

    # Flask-Praetorian specific identity property
    @property
    def identity(self):
        """Required by flask-praetorian for JWT token generation"""
        return self.id

    # Flask-Praetorian specific rolenames property
    @property
    def rolenames(self):
        """Required by flask-praetorian for role-based authentication"""
        return self.roles

    # Required by flask-praetorian for password checking
    @classmethod
    def lookup(cls, username):
        """Required by flask-praetorian for username lookup"""
        return cls.query.filter_by(username=username).one_or_none()

    # Required by flask-praetorian for password validation
    @classmethod
    def identify(cls, id):
        """Required by flask-praetorian for id lookup"""
        return cls.query.get(id)

    def is_valid(self):
        """Required by flask-praetorian to ensure user account is active"""
        return True

    def __init__(self, nombre, apellidos, correo, username, password, is_admin=False):
        self.nombre = nombre
        self.apellidos = apellidos
        self.correo = correo
        self.username = username
        self.password = password  # Hashing handled by Flask-Praetorian
        self.is_admin = is_admin

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'correo': self.correo,
            'username': self.username,
            'is_admin': self.is_admin,
            'roles': self.roles,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None
        }

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(correo):
        return User.query.filter_by(correo=correo).first()

    def __repr__(self):
        return f'<User {self.username}>'
