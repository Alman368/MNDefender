from flask import jsonify, request
from sqlalchemy.exc import NoResultFound
from . import api_bp
from app.models import db, Mensaje, Proyecto

@api_bp.route("/mensaje", methods=["POST"])
def guardar_mensaje():
	data = request.get_json()
	if not data:
		return jsonify({"error": "No se proporcionaron datos"}), 400

	# Verificar que se proporciona el proyecto_id
	proyecto_id = data.get("proyecto_id")
	if not proyecto_id:
		return jsonify({"error": "No se proporcionó el ID del proyecto"}), 400

	try:
		# Obtener el último ID de la base de datos para ese proyecto específico y calcular el nuevo ID
		ultimo_mensaje = db.session.query(Mensaje).order_by(Mensaje.id.desc()).first()
		nuevo_id = (ultimo_mensaje.id + 1) if ultimo_mensaje else 1

		nuevo_mensaje = Mensaje(
			id=nuevo_id,
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

# Obtener mensaje del id seleccionado
@api_bp.route("/proyecto/<int:id>/mensajes")
def proyecto_mensajes(id=None):
	try:
		# Obtener los mensajes del proyecto por ID, ordenados por fecha de creación ascendente
		mensajes = db.session.scalars(
			db.select(Mensaje).where(Mensaje.proyecto_id == id).order_by(Mensaje.fecha_creacion.asc())
		).all()
		# Crear una lista de diccionarios con los datos relevantes
		mensajes_data = [
			{"contenido": mensaje.contenido, "es_bot": mensaje.es_bot, "fecha_creacion": mensaje.fecha_creacion}
			for mensaje in mensajes
		]
		return jsonify(mensajes_data), 200
	except NoResultFound:
		return jsonify({"error": "No se encontraron mensajes para este proyecto."}), 404
	
@api_bp.route("/proyecto/eliminar/<int:id>", methods=["DELETE"])
def proyecto_eliminar(id=None):
    # Obtener el proyecto por ID o devolver un error 404 si no existe
    try:
        p = db.session.query(Proyecto).filter(Proyecto.id == id).one()
        
        # Primero eliminar todos los mensajes asociados al proyecto
        db.session.query(Mensaje).filter(Mensaje.proyecto_id == id).delete()
        
        # Luego eliminar el proyecto de la base de datos
        db.session.delete(p)
        db.session.commit()
        
        # Devolver respuesta de éxito
        return jsonify({"mensaje": f"Proyecto {p.nombre} eliminado con éxito", "id": id}), 200
    except NoResultFound:
        return jsonify({"error": "Proyecto no encontrado"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar el proyecto: {str(e)}"}), 500