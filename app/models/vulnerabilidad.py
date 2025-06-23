from datetime import datetime
from . import db

class Vulnerabilidad(db.Model):
    __tablename__ = 'vulnerabilidades'

    id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=False)
    cve_id = db.Column(db.String(20), nullable=False)  # CVE-2023-12345
    descripcion = db.Column(db.Text)
    severidad = db.Column(db.String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    puntuacion_cvss = db.Column(db.Float)  # 0.0 - 10.0
    vector_cvss = db.Column(db.String(100))
    archivo_afectado = db.Column(db.String(255))  # Archivo donde se detectó
    linea_codigo = db.Column(db.Integer)  # Línea específica
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, revisado, solucionado
    fecha_deteccion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con Proyecto
    proyecto = db.relationship('Proyecto', backref=db.backref('vulnerabilidades', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Vulnerabilidad {self.cve_id} - {self.severidad}>'

    def to_dict(self):
        return {
            'id': self.id,
            'proyecto_id': self.proyecto_id,
            'cve_id': self.cve_id,
            'descripcion': self.descripcion,
            'severidad': self.severidad,
            'puntuacion_cvss': self.puntuacion_cvss,
            'vector_cvss': self.vector_cvss,
            'archivo_afectado': self.archivo_afectado,
            'linea_codigo': self.linea_codigo,
            'estado': self.estado,
            'fecha_deteccion': self.fecha_deteccion.isoformat() if self.fecha_deteccion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None
        }

class AnalisisEstatico(db.Model):
    __tablename__ = 'analisis_estaticos'

    id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    total_vulnerabilidades = db.Column(db.Integer, default=0)
    vulnerabilidades_criticas = db.Column(db.Integer, default=0)
    vulnerabilidades_altas = db.Column(db.Integer, default=0)
    vulnerabilidades_medias = db.Column(db.Integer, default=0)
    vulnerabilidades_bajas = db.Column(db.Integer, default=0)
    calculo_combinado = db.Column(db.Float, default=0.0)  # Cálculo basado en severidad
    cumple_criterios = db.Column(db.Boolean, default=True)
    criterios_incumplidos = db.Column(db.Text)  # JSON con criterios que no se cumplen
    fecha_analisis = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con Proyecto
    proyecto = db.relationship('Proyecto', backref=db.backref('analisis_estaticos', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<AnalisisEstatico {self.nombre_archivo} - {self.total_vulnerabilidades} vulns>'

    def calcular_puntuacion_combinada(self):
        """Calcula una puntuación combinada basada en la severidad de las vulnerabilidades"""
        # Pesos para cada nivel de severidad
        pesos = {
            'CRITICAL': 10,
            'HIGH': 7,
            'MEDIUM': 4,
            'LOW': 1
        }
        
        puntuacion = (
            self.vulnerabilidades_criticas * pesos['CRITICAL'] +
            self.vulnerabilidades_altas * pesos['HIGH'] +
            self.vulnerabilidades_medias * pesos['MEDIUM'] +
            self.vulnerabilidades_bajas * pesos['LOW']
        )
        
        self.calculo_combinado = puntuacion
        return puntuacion

    def to_dict(self):
        return {
            'id': self.id,
            'proyecto_id': self.proyecto_id,
            'nombre_archivo': self.nombre_archivo,
            'ruta_archivo': self.ruta_archivo,
            'total_vulnerabilidades': self.total_vulnerabilidades,
            'vulnerabilidades_criticas': self.vulnerabilidades_criticas,
            'vulnerabilidades_altas': self.vulnerabilidades_altas,
            'vulnerabilidades_medias': self.vulnerabilidades_medias,
            'vulnerabilidades_bajas': self.vulnerabilidades_bajas,
            'calculo_combinado': self.calculo_combinado,
            'cumple_criterios': self.cumple_criterios,
            'criterios_incumplidos': self.criterios_incumplidos,
            'fecha_analisis': self.fecha_analisis.isoformat() if self.fecha_analisis else None
        } 