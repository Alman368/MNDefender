from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, correo, nombre, apellidos, is_admin, roles=None):
        self.id = id
        self.username = username
        self.correo = correo
        self.nombre = nombre
        self.apellidos = apellidos
        self.is_admin = is_admin
        self.roles = roles or []

    @classmethod
    def from_api_data(cls, data):
        """
        Creates a User instance from API data
        """
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            correo=data.get('correo'),
            nombre=data.get('nombre'),
            apellidos=data.get('apellidos'),
            is_admin=data.get('is_admin', False),
            roles=data.get('roles', [])
        )
