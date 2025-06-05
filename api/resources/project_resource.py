from flask import request
from flask_restful import Resource
from flask_praetorian import auth_required, current_user, roles_required, roles_accepted
from api.app import db
from api.models.project import Project
from api.models.user import User

class ProjectListResource(Resource):
    @auth_required
    def get(self):
        user = current_user()

        if "admin" in user.roles:
            # Admins can see all projects
            projects = Project.query.all()
        else:
            # Regular users can only see their own projects
            projects = Project.query.filter_by(usuario_id=user.id).all()

        return {'projects': [project.to_dict() for project in projects]}

    @auth_required
    def post(self):
        data = request.get_json()
        current_user_obj = current_user()

        # Set the current user as the owner if not specified
        if 'usuario_id' not in data:
            data['usuario_id'] = current_user_obj.id

        # Check if user exists
        user = User.query.get(data.get('usuario_id'))
        if not user:
            return {'message': 'Usuario no encontrado'}, 404

        # Only admins can create projects for other users
        if "admin" not in current_user_obj.roles and data.get('usuario_id') != current_user_obj.id:
            return {'message': 'No tienes permiso para crear proyectos para otros usuarios'}, 403

        try:
            project = Project(
                nombre=data.get('nombre'),
                descripcion=data.get('descripcion'),
                usuario_id=data.get('usuario_id')
            )
            db.session.add(project)
            db.session.commit()
            return {'message': 'Proyecto creado exitosamente', 'project': project.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al crear proyecto: {str(e)}'}, 500

class ProjectResource(Resource):
    @auth_required
    def get(self, project_id):
        user = current_user()

        project = Project.query.get(project_id)
        if not project:
            return {'message': 'Proyecto no encontrado'}, 404

        # Check if user has access to this project
        if "admin" not in user.roles and project.usuario_id != user.id:
            return {'message': 'No tienes acceso a este proyecto'}, 403

        return {'project': project.to_dict()}

    @auth_required
    def put(self, project_id):
        user = current_user()

        project = Project.query.get(project_id)
        if not project:
            return {'message': 'Proyecto no encontrado'}, 404

        # Check if user has access to edit this project
        if "admin" not in user.roles and project.usuario_id != user.id:
            return {'message': 'No tienes permiso para editar este proyecto'}, 403

        data = request.get_json()

        try:
            if data.get('nombre'):
                project.nombre = data.get('nombre')
            if data.get('descripcion'):
                project.descripcion = data.get('descripcion')
            if data.get('usuario_id'):
                # Only admins can change project ownership
                if "admin" not in user.roles:
                    return {'message': 'No tienes permiso para cambiar el propietario del proyecto'}, 403

                # Check if new user exists
                new_user = User.query.get(data.get('usuario_id'))
                if not new_user:
                    return {'message': 'Usuario no encontrado'}, 404
                project.usuario_id = data.get('usuario_id')

            db.session.commit()
            return {'message': 'Proyecto actualizado exitosamente', 'project': project.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al actualizar proyecto: {str(e)}'}, 500

    @auth_required
    def delete(self, project_id):
        user = current_user()

        project = Project.query.get(project_id)
        if not project:
            return {'message': 'Proyecto no encontrado'}, 404

        # Check if user has access to delete this project
        if "admin" not in user.roles and project.usuario_id != user.id:
            return {'message': 'No tienes permiso para eliminar este proyecto'}, 403

        try:
            db.session.delete(project)
            db.session.commit()
            return {'message': 'Proyecto eliminado exitosamente'}
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al eliminar proyecto: {str(e)}'}, 500
