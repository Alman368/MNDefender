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
    fecha = db.Column(db.Date, nullable=False)

class Etiqueta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class ProyectoEtiqueta(db.Model):
    __tablename__ = 'proyecto_etiqueta'  # Esto lo descomentamos para especificar el nombre de la tabla
    proyecto_id = db.Column(db.Integer, db.ForeignKey(Proyecto.id), primary_key=True)
    etiqueta_id = db.Column(db.Integer, db.ForeignKey(Etiqueta.id), primary_key=True)

# Añado modelo para Usuarios
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    rol = db.Column(db.String(50), default='usuario')  # puede ser 'administrador' o 'usuario'
    fecha_registro = db.Column(db.Date, nullable=False, default=datetime.now().date())

def create_app():
    # Configura Flask usando las mismas carpetas que en tu flask_app.py original
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:contraseña@localhost:3306/gestion_proyectos'
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
        return render_template('chat.html')

    # Ruta para la consultar proyectos
    # Consulta todos los proyectos
    @app.route("/proyectos/")
    def proyectos():
        p = db.session.scalars(db.select(Proyecto).order_by(
            Proyecto.fecha.desc())).all()
        return render_template("proyectos.html", proyectos=p)

    # Consulta un proyecto por id
    @app.route("/proyecto/<int:id>")
    def proyecto(id=None):
        p = db.session.scalars(db.select(Proyecto).where(Proyecto.id == id)).one()
        return render_template("proyecto.html", proyecto=p)

    # Crear un nuevo proyecto
    @app.route("/proyecto/nuevo", methods=["GET", "POST"])
    def proyecto_nuevo():
        if request.method == "POST":
            nombre = request.form["nombre"]
            descripcion = request.form["descripcion"]
            fecha = request.form["fecha"]
            p = Proyecto(nombre=nombre, descripcion=descripcion, fecha=fecha)
            db.session.add(p)
            db.session.commit()
            flash(f"Proyecto <em>{nombre}</em> añadido con éxito.", "exito")
            return redirect(url_for("proyectos"))
        else:
            return render_template("proyecto_nuevo.html")

    # Editar un proyecto
    @app.route("/proyecto/editar/<int:id>", methods=["GET", "POST"])
    def proyecto_editar(id=None):
        # Obtener el proyecto por ID o devolver un error 404 si no existe
        try:
            p = db.one_or_404(db.select(Proyecto).where(Proyecto.id == id))
        except NoResultFound:
            flash("Proyecto no encontrado.", "error")
            return redirect(url_for("proyectos")), 404

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
            return redirect(url_for("proyectos"))
        else:
            # Mostrar el formulario de edición con los datos actuales del proyecto
            return render_template("proyecto_editar.html", proyecto=p)

    # Eliminar un proyecto
    @app.route("/proyecto/eliminar/<int:id>")
    def proyecto_eliminar(id=None):
        # Obtener el proyecto por ID o devolver un error 404 si no existe
        try:
            p = db.one_or_404(db.select(Proyecto).where(Proyecto.id == id))
        except NoResultFound:
            flash("Proyecto no encontrado.", "error")
            return redirect(url_for("proyectos")), 404

        # Eliminar el proyecto de la base de datos
        db.session.delete(p)
        db.session.commit()

        # Mostrar mensaje de éxito y redirigir a la lista de proyectos
        flash(f"Proyecto <em>{p.nombre}</em> eliminado con éxito.", "exito")
        return redirect(url_for("proyectos"))

    # Rutas para gestión de usuarios
    @app.route("/usuarios/")
    def usuarios():
        u = db.session.scalars(db.select(Usuario).order_by(Usuario.nombre)).all()
        return render_template("usuarios.html", usuarios=u)

    @app.route("/usuario/<int:id>")
    def usuario(id=None):
        try:
            u = db.session.scalars(db.select(Usuario).where(Usuario.id == id)).one()
            return render_template("usuario.html", usuario=u)
        except NoResultFound:
            flash("Usuario no encontrado.", "error")
            return redirect(url_for("usuarios")), 404

    @app.route("/usuario/nuevo", methods=["GET", "POST"])
    def usuario_nuevo():
        if request.method == "POST":
            nombre = request.form["nombre"]
            email = request.form["email"]
            rol = request.form.get("rol", "usuario")
            u = Usuario(nombre=nombre, email=email, rol=rol, fecha_registro=datetime.now().date())
            db.session.add(u)
            db.session.commit()
            flash(f"Usuario <em>{nombre}</em> añadido con éxito.", "exito")
            return redirect(url_for("usuarios"))
        else:
            return render_template("usuario_nuevo.html")

    @app.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
    def usuario_editar(id=None):
        try:
            u = db.one_or_404(db.select(Usuario).where(Usuario.id == id))
        except NoResultFound:
            flash("Usuario no encontrado.", "error")
            return redirect(url_for("usuarios")), 404

        if request.method == "POST":
            u.nombre = request.form['nombre']
            u.email = request.form['email']
            u.rol = request.form.get('rol', 'usuario')
            db.session.commit()
            flash(f"Usuario <em>{u.nombre}</em> modificado con éxito", "exito")
            return redirect(url_for("usuarios"))
        else:
            return render_template("usuario_editar.html", usuario=u)

    @app.route("/usuario/eliminar/<int:id>")
    def usuario_eliminar(id=None):
        try:
            u = db.one_or_404(db.select(Usuario).where(Usuario.id == id))
        except NoResultFound:
            flash("Usuario no encontrado.", "error")
            return redirect(url_for("usuarios")), 404

        db.session.delete(u)
        db.session.commit()
        flash(f"Usuario <em>{u.nombre}</em> eliminado con éxito.", "exito")
        return redirect(url_for("usuarios"))

    # Crear tablas de la base de datos
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

