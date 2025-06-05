from flask import request
from flask_restful import Resource
from flask_praetorian import auth_required, current_user
from api.app import guard

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'message': 'Se requiere nombre de usuario y contraseña'}, 400

        user = guard.authenticate(username, password)
        if not user:
            return {'message': 'Credenciales inválidas'}, 401

        # Create an access token with Flask-Praetorian
        access_token = guard.encode_jwt_token(user)

        return {
            'message': 'Login exitoso',
            'access_token': access_token,
            'user': user.to_dict()
        }

class RefreshResource(Resource):
    @auth_required
    def post(self):
        """
        Refreshes an existing JWT by creating a new one that is a copy of the old
        except that it has a refreshed access expiration.
        """
        old_token = guard.read_token_from_header()
        new_token = guard.refresh_jwt_token(old_token)

        return {'access_token': new_token}

class AuthTestResource(Resource):
    @auth_required
    def get(self):
        """
        A simple endpoint to test authentication
        """
        user = current_user()

        return {'message': 'Autenticado correctamente', 'user': user.to_dict()}
