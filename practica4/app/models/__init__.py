from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .proyecto import Proyecto
from .mensaje import Mensaje
