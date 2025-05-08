from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .proyecto import Proyecto
from .usuario import Usuario
from .mensaje import Mensaje
