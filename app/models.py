from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fecha_modificacion = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

class Mensaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    es_bot = db.Column(db.Boolean, default=False)  # Para distinguir si el mensaje es del bot o del usuario
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Clave foránea para relacionar con el proyecto
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyecto.id'), nullable=False)

    # Relación con el proyecto (puedes acceder a los mensajes desde el proyecto)
    proyecto = db.relationship('Proyecto', backref=db.backref('mensajes', lazy=True))
