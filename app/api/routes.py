from flask import jsonify, request, Blueprint
from sqlalchemy.exc import NoResultFound
from flask_login import login_required, current_user
from . import api_bp
from app.models import db, Mensaje, Proyecto, Usuario

api_bp = Blueprint('api', __name__)

@api_bp.route("/mensaje", methods=["POST"])
@login_required
def guardar_mensaje():
	data = request.get_json()
	if not data:
		return jsonify({"error": "No se proporcionaron datos"}), 400

	proyecto_id = data.get("proyecto_id")
	if not proyecto_id:
		return jsonify({"error": "No se proporcionó el ID del proyecto"}), 400

	try:
		# Verificar que el usuario tiene acceso al proyecto
		proyecto = Proyecto.query.get(proyecto_id)
		if not proyecto or (not current_user.is_admin and proyecto.usuario_id != current_user.id):
			return jsonify({"error": "No tienes permisos para este proyecto"}), 403

		nuevo_mensaje = Mensaje(
			contenido=data.get("contenido"),
			es_bot=data.get("es_bot", False),
			proyecto_id=proyecto_id
		)

		db.session.add(nuevo_mensaje)
		db.session.commit()

		return jsonify({"message": "Mensaje guardado correctamente", "id": nuevo_mensaje.id}), 201
	except Exception as e:
		db.session.rollback()
		return jsonify({"error": f"Error al guardar el mensaje: {str(e)}"}), 500

@api_bp.route("/proyecto/<int:id>/mensajes")
@login_required
def proyecto_mensajes(id):
	try:
		# Verificar que el usuario tiene acceso al proyecto
		proyecto = Proyecto.query.get(id)
		if not proyecto or (not current_user.is_admin and proyecto.usuario_id != current_user.id):
			return jsonify({"error": "No tienes permisos para este proyecto"}), 403

		mensajes = Mensaje.query.filter_by(proyecto_id=id).order_by(Mensaje.fecha_creacion.asc()).all()
		mensajes_data = [
			{
				"contenido": mensaje.contenido,
				"es_bot": mensaje.es_bot,
				"fecha_creacion": mensaje.fecha_creacion
			}
			for mensaje in mensajes
		]
		return jsonify(mensajes_data), 200
	except Exception as e:
		return jsonify({"error": f"Error al obtener mensajes: {str(e)}"}), 500

@api_bp.route("/proyecto/eliminar/<int:id>", methods=["DELETE"])
@login_required
def proyecto_eliminar(id):
	try:
		proyecto = Proyecto.query.get(id)
		if not proyecto:
			return jsonify({"error": "Proyecto no encontrado"}), 404

		# Verificar permisos
		if not current_user.is_admin and proyecto.usuario_id != current_user.id:
			return jsonify({"error": "No tienes permisos para eliminar este proyecto"}), 403

		db.session.delete(proyecto)
		db.session.commit()
		return jsonify({"mensaje": f"Proyecto {proyecto.nombre} eliminado con éxito"}), 200
	except Exception as e:
		db.session.rollback()
		return jsonify({"error": f"Error al eliminar el proyecto: {str(e)}"}), 500

@api_bp.route("/proyecto/editar/<int:id>", methods=["PUT"])
@login_required
def proyecto_editar(id):
	data = request.get_json()
	if not data:
		return jsonify({"error": "No se proporcionaron datos"}), 400

	try:
		proyecto = Proyecto.query.get(id)
		if not proyecto:
			return jsonify({"error": "Proyecto no encontrado"}), 404

		# Verificar permisos
		if not current_user.is_admin and proyecto.usuario_id != current_user.id:
			return jsonify({"error": "No tienes permisos para editar este proyecto"}), 403

		proyecto.nombre = data.get("nombre", proyecto.nombre)
		proyecto.descripcion = data.get("descripcion", proyecto.descripcion)
		db.session.commit()

		return jsonify({"mensaje": f"Proyecto {proyecto.nombre} editado con éxito"}), 200
	except Exception as e:
		db.session.rollback()
		return jsonify({"error": f"Error al editar el proyecto: {str(e)}"}), 500

@api_bp.route("/proyecto/<int:id>", methods=["GET"])
def proyecto_obtener(id=None):
    try:
        proyecto = db.session.query(Proyecto).filter(Proyecto.id == id).one()
        return jsonify({
            "id": proyecto.id,
            "nombre": proyecto.nombre,
            "descripcion": proyecto.descripcion,
            "fecha_creacion": proyecto.fecha_creacion,
            "fecha_modificacion": proyecto.fecha_modificacion
        }), 200
    except NoResultFound:
        return jsonify({"error": "Proyecto no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al obtener el proyecto: {str(e)}"}), 500

# API para usuarios
@api_bp.route("/usuario", methods=["POST"])
def crear_usuario():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400

    try:
        # Obtener el último ID de la base de datos y calcular el nuevo ID
        ultimo_usuario = db.session.query(Usuario).order_by(Usuario.id.desc()).first()
        nuevo_id = (ultimo_usuario.id + 1) if ultimo_usuario else 1

        nuevo_usuario = Usuario(
            id=nuevo_id,
            nombre=data.get("nombre"),
            apellidos=data.get("apellidos"),
            correo=data.get("correo"),
            contrasena=data.get("contrasena")
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({
            "mensaje": "Usuario creado con éxito",
            "id": nuevo_usuario.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al crear el usuario: {str(e)}"}), 500

@api_bp.route("/usuario/editar/<int:id>", methods=["PUT"])
def usuario_editar(id=None):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400

    try:
        u = db.session.query(Usuario).filter(Usuario.id == id).one()
        u.nombre = data.get("nombre", u.nombre)
        u.apellidos = data.get("apellidos", u.apellidos)
        u.correo = data.get("correo", u.correo)
        if "contrasena" in data and data["contrasena"]:
            u.contrasena = data.get("contrasena")

        db.session.commit()

        return jsonify({"mensaje": f"Usuario {u.nombre} {u.apellidos} editado con éxito", "id": id}), 200
    except NoResultFound:
        return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al editar el usuario: {str(e)}"}), 500

@api_bp.route("/usuario/eliminar/<int:id>", methods=["DELETE"])
def usuario_eliminar(id=None):
    try:
        u = db.session.query(Usuario).filter(Usuario.id == id).one()
        db.session.delete(u)
        db.session.commit()

        return jsonify({"mensaje": f"Usuario {u.nombre} {u.apellidos} eliminado con éxito", "id": id}), 200
    except NoResultFound:
        return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar el usuario: {str(e)}"}), 500

@api_bp.route("/usuario/<int:id>", methods=["GET"])
def usuario_obtener(id=None):
    try:
        usuario = db.session.query(Usuario).filter(Usuario.id == id).one()
        return jsonify({
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "fecha_creacion": usuario.fecha_creacion,
            "fecha_modificacion": usuario.fecha_modificacion
        }), 200
    except NoResultFound:
        return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al obtener el usuario: {str(e)}"}), 500

@api_bp.route('/proyectos', methods=['GET'])
@login_required
def get_proyectos():
    try:
        if current_user.is_admin:
            proyectos = Proyecto.query.all()
        else:
            proyectos = Proyecto.query.filter_by(usuario_id=current_user.id).all()

        return jsonify([{
            'id': p.id,
            'nombre': p.nombre,
            'descripcion': p.descripcion,
            'usuario_id': p.usuario_id
        } for p in proyectos])
    except Exception as e:
        return jsonify({"error": f"Error al obtener proyectos: {str(e)}"}), 500

@api_bp.route('/usuarios', methods=['GET'])
@login_required
def get_usuarios():
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403

    try:
        usuarios = Usuario.query.all()
        return jsonify([{
            'id': u.id,
            'nombre': u.nombre,
            'apellidos': u.apellidos,
            'correo': u.correo
        } for u in usuarios])
    except Exception as e:
        return jsonify({"error": f"Error al obtener usuarios: {str(e)}"}), 500
