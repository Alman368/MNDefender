from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .proyecto import Proyecto
from .mensaje import Mensaje
from .criterio_aceptabilidad import CriterioAceptabilidad
from .vulnerabilidad import Vulnerabilidad, AnalisisEstatico
