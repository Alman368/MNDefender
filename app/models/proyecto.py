from datetime import datetime
from . import db

class Proyecto(db.Model):
    __tablename__ = 'proyectos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relaciones
    usuario = db.relationship('User', backref=db.backref('proyectos', lazy=True))
    mensajes = db.relationship('Mensaje', backref='proyecto', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Proyecto {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
            'usuario_id': self.usuario_id
        }
