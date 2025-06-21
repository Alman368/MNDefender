from datetime import datetime
from . import db

class CriterioAceptabilidad(db.Model):
    __tablename__ = 'criterios_aceptabilidad'

    id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=False)
    tipo_criterio = db.Column(db.String(100), nullable=False)  # Tipo de criterio
    valor = db.Column(db.String(255), nullable=False)  # Valor del criterio
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con Proyecto
    proyecto = db.relationship('Proyecto', backref=db.backref('criterios_aceptabilidad', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<CriterioAceptabilidad {self.tipo_criterio}: {self.valor}>'

    def to_dict(self):
        return {
            'id': self.id,
            'proyecto_id': self.proyecto_id,
            'tipo_criterio': self.tipo_criterio,
            'valor': self.valor,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None
        }

# Definir los tipos de criterios disponibles
TIPOS_CRITERIOS = {
    'max_calculo_combinado': {
        'nombre': 'Máximo Cálculo combinado',
        'tipo_valor': 'number',
        'min': 0
    },
    'max_vulnerabilidades_no_solucionables': {
        'nombre': 'Solucionabilidad vulnerabilidades (máximo nº de vulnerabilidades no solucionables)',
        'tipo_valor': 'number',
        'min': 0
    },
    'nivel_max_vulnerabilidades': {
        'nombre': 'Nivel máximo de vulnerabilidades',
        'opciones': ['bajo', 'medio', 'alto', 'crítico'],
        'tipo_valor': 'select'
    },
    'max_numero_vulnerabilidades': {
        'nombre': 'Máximo número de vulnerabilidades',
        'tipo_valor': 'number',
        'min': 0
    }
} 