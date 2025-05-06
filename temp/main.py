from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
from services.message_service import AnimalFactsService
from controllers.message_controller import MessageController
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
from datetime import datetime

db = SQLAlchemy()

# Defino las tablas de la base de datos
class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fecha_modificacion = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

class Mensaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    es_bot = db.Column(db.Boolean, default=False)  # Para distinguir si el mensaje es del bot o del usuario
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Clave foránea para relacionar con el proyecto
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyecto.id'), nullable=False)

    # Relación con el proyecto (puedes acceder a los mensajes desde el proyecto)
    proyecto = db.relationship('Proyecto', backref=db.backref('mensajes', lazy=True))


def create_app():
    # Configura Flask usando las mismas carpetas que en tu flask_app.py original
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Añadir secret key para habilitar flash messages y sesiones
    app.secret_key = 'un_secreto_seguro_para_MNDefender'  # En producción, usar variables de entorno


    # Configura la base de datos ANTES de inicializar
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://alberto:svaia@localhost:3306/svaia'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactiva las señales para ahorrar recursos

    # Inicializa la base de datos con la aplicación
    db.init_app(app)

    # Activa CORS
    CORS(app)

    # Inicializa el MessageController (tal como hacías antes)
    message_controller = MessageController(AnimalFactsService())

    # Registra la ruta POST que usabas para tu chatbot
    app.add_url_rule('/send-message',
                     view_func=message_controller.send_message,
                     methods=['POST'])

    # FUSIÓN: aquí traes las rutas de flask_app.py
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/chat')
    def chat():
        # Coger los proyectos de la base de datos
        proyectos = db.session.scalars(db.select(Proyecto)).all()
        # Le pasamos los proyectos a la plantilla
        return render_template('chat.html', proyectos=proyectos)

    # Consulta un proyecto por id
	# @app.route("/proyecto/<int:id>")
	# def proyecto(id=None):
	#     id_proyecto = db.session.scalars(db.select(Proyecto).where(Proyecto.id == id)).one()
	#     return render_template("chat.html", proyecto=id_proyecto)

	# API para conectar con javascript, devolver mensajes de un proyecto por id
    @app.route("/proyecto/<int:id>/mensajes")
	def proyecto_mensajes(id=None):
		try:
			# Obtener los mensajes del proyecto por ID
			mensajes = db.session.scalars(db.select(Mensaje).where(Mensaje.proyecto_id == id)).all()
			# Crear una lista de diccionarios con los datos relevantes
			mensajes_data = [
			{"contenido": mensaje.contenido, "es_bot": mensaje.es_bot, "fecha_creacion": mensaje.fecha_creacion}
			for mensaje in mensajes
			]
			return jsonify(mensajes_data), 200
		except NoResultFound:
			return jsonify({"error": "No se encontraron mensajes para este proyecto."}), 404

    # Mantener la ruta existente por compatibilidad
    @app.route("/proyecto/nuevo", methods=["GET", "POST"])
    def proyecto_nuevo():
        # Si el método es POST, significa que se envió el formulario
        if request.method == "POST":
            # Get form data with correct field names
            nombre = request.form["project_name"]  # Changed from "nombre"
            descripcion = request.form["project_description"]  # Changed from "descripcion"
            fecha_creacion = datetime.now()
            fecha_modificacion = datetime.now()

            # Get the highest ID currently in the database
            max_id = db.session.query(db.func.max(Proyecto.id)).scalar() or 0

            # Create new project with ID = max_id + 1
            proyecto = Proyecto(
                id=max_id + 1,  # Explicitly set the ID to max_id + 1
                nombre=nombre,
                descripcion=descripcion,
                fecha_creacion=fecha_creacion,
                fecha_modificacion=fecha_modificacion
            )

            db.session.add(proyecto)
            db.session.commit()
            flash(f"Proyecto <em>{nombre}</em> añadido con éxito.", "exito")
            return redirect(url_for("chat"))
        # Si es GET, redirigir a la página de chat que ahora tiene el modal
        else:
            return redirect(url_for("chat"))

    # Editar un proyecto
    @app.route("/proyecto/editar/<int:id>", methods=["GET", "POST"])
    def proyecto_editar(id=None):
        # Obtener el proyecto por ID o devolver un error 404 si no existe
        try:
            p = db.one_or_404(db.select(Proyecto).where(Proyecto.id == id))
        except NoResultFound:
            flash("Proyecto no encontrado.", "error")
            return redirect(url_for("chat")), 404

        if request.method == "POST":
            # Actualizar los campos del proyecto con los datos del formulario
            p.nombre = request.form['nombre']
            p.descripcion = request.form['descripcion']

            # Convertir la fecha del formulario a un objeto date
            try:
                p.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
            except ValueError:
                flash("Formato de fecha inválido. Use YYYY-MM-DD.", "error")
                return render_template("proyecto_editar.html", proyecto=p), 400

            # Guardar los cambios en la base de datos
            db.session.commit()

            # Mostrar mensaje de éxito y redirigir a la lista de proyectos
            flash(f"Proyecto <em>{p.nombre}</em> modificado con éxito", "exito")
            return redirect(url_for("chat"))
        else:
            # Mostrar el formulario de edición con los datos actuales del proyecto
            return render_template("chat.html", proyecto=p)

    # Eliminar un proyecto
    @app.route("/proyecto/eliminar/<int:id>")
    def proyecto_eliminar(id=None):
        # Obtener el proyecto por ID o devolver un error 404 si no existe
        try:
            p = db.one_or_404(db.select(Proyecto).where(Proyecto.id == id))
        except NoResultFound:
            flash("Proyecto no encontrado.", "error")
            return redirect(url_for("chat")), 404

        # Eliminar el proyecto de la base de datos
        db.session.delete(p)
        db.session.commit()

        # Mostrar mensaje de éxito y redirigir a la lista de proyectos
        flash(f"Proyecto <em>{p.nombre}</em> eliminado con éxito.", "exito")
        return redirect(url_for("chat"))

    # Crear tablas de la base de datos
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    # Para que funcione este código, asegúrate de instalar:
    # pip install pymysql cryptography
    app = create_app()
    app.run(debug=True)
