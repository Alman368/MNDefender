from flask import request, jsonify
from flask_restful import Resource
from flask_praetorian import auth_required, current_user, roles_required, roles_accepted
from api.app import db, guard
from api.models.user import User

class UserListResource(Resource):
    @auth_required
    @roles_accepted('admin')
    def get(self):
        # Only admin users can list all users
        users = User.query.all()
        return {'users': [user.to_dict() for user in users]}

    @auth_required
    @roles_accepted('admin')
    def post(self):
        # Only admin users can create new users
        data = request.get_json()

        # Check if user with username or email already exists
        if User.get_by_username(data.get('username')):
            return {'message': 'Usuario con ese nombre de usuario ya existe'}, 409

        if User.get_by_email(data.get('correo')):
            return {'message': 'Usuario con ese correo ya existe'}, 409

        try:
            # Hash the password with Praetorian
            hashed_password = guard.hash_password(data.get('password'))

            user = User(
                nombre=data.get('nombre'),
                apellidos=data.get('apellidos'),
                correo=data.get('correo'),
                username=data.get('username'),
                password=hashed_password,
                is_admin=data.get('is_admin', False)
            )
            db.session.add(user)
            db.session.commit()
            return {'message': 'Usuario creado exitosamente', 'user': user.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al crear usuario: {str(e)}'}, 500

class UserResource(Resource):
    @auth_required
    def get(self, user_id):
        current_user_obj = current_user()

        # Users can access their own information, admins can access any user
        if "admin" not in current_user_obj.roles and current_user_obj.id != user_id:
            return {'message': 'Acceso denegado'}, 403

        user = User.query.get(user_id)
        if user:
            return {'user': user.to_dict()}
        return {'message': 'Usuario no encontrado'}, 404

    @auth_required
    def put(self, user_id):
        current_user_obj = current_user()

        # Users can update their own information, admins can update any user
        if "admin" not in current_user_obj.roles and current_user_obj.id != user_id:
            return {'message': 'Acceso denegado'}, 403

        user = User.query.get(user_id)
        if not user:
            return {'message': 'Usuario no encontrado'}, 404

        data = request.get_json()

        # Check for existing username or email if changing them
        if data.get('username') and data.get('username') != user.username:
            if User.get_by_username(data.get('username')):
                return {'message': 'Nombre de usuario ya está en uso'}, 409

        if data.get('correo') and data.get('correo') != user.correo:
            if User.get_by_email(data.get('correo')):
                return {'message': 'Correo ya está en uso'}, 409

        # Only admins can change admin status
        if 'is_admin' in data and "admin" not in current_user_obj.roles:
            return {'message': 'No tienes permiso para cambiar el estado de administrador'}, 403

        try:
            if data.get('nombre'):
                user.nombre = data.get('nombre')
            if data.get('apellidos'):
                user.apellidos = data.get('apellidos')
            if data.get('correo'):
                user.correo = data.get('correo')
            if data.get('username'):
                user.username = data.get('username')
            if data.get('password'):
                user.password = guard.hash_password(data.get('password'))
            if 'is_admin' in data and "admin" in current_user_obj.roles:
                user.is_admin = data.get('is_admin')

            db.session.commit()
            return {'message': 'Usuario actualizado exitosamente', 'user': user.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al actualizar usuario: {str(e)}'}, 500

    @auth_required
    @roles_accepted('admin')
    def delete(self, user_id):
        current_user_obj = current_user()

        if int(current_user_obj.id) == int(user_id):
            return {'message': 'No puedes eliminar tu propia cuenta'}, 403

        user = User.query.get(user_id)
        if not user:
            return {'message': 'Usuario no encontrado'}, 404

        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'Usuario eliminado exitosamente'}
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al eliminar usuario: {str(e)}'}, 500
