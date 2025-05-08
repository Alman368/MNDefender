from flask import render_template, request, flash, redirect, url_for
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from . import views_bp
from app.models import db, Proyecto, Usuario

@views_bp.route('/')
def index():
    return render_template('index.html')

@views_bp.route('/chat')
def chat():
    # Coger los proyectos de la base de datos
    proyectos = db.session.scalars(db.select(Proyecto)).all()
    # Le pasamos los proyectos a la plantilla
    return render_template('chat.html', proyectos=proyectos)

@views_bp.route("/usuarios")
def gestionar_usuarios():
    # Obtener todos los usuarios de la base de datos
    usuarios = db.session.scalars(db.select(Usuario)).all()
    return render_template('usuarios.html', usuarios=usuarios)

@views_bp.route("/proyecto/nuevo", methods=["GET", "POST"])
def proyecto_nuevo():
    # Si el método es POST, significa que se envió el formulario
    if request.method == "POST":
        # Get form data with correct field names
        nombre = request.form["project_name"]
        descripcion = request.form["project_description"]
        fecha_creacion = datetime.now()
        fecha_modificacion = datetime.now()

        # Get the highest ID currently in the database
        max_id = db.session.query(db.func.max(Proyecto.id)).scalar() or 0

        # Create new project with ID = max_id + 1
        proyecto = Proyecto(
            id=max_id + 1,
            nombre=nombre,
            descripcion=descripcion,
            fecha_creacion=fecha_creacion,
            fecha_modificacion=fecha_modificacion
        )

        db.session.add(proyecto)
        db.session.commit()
        flash(f"Proyecto <em>{nombre}</em> añadido con éxito.", "exito")
        return redirect(url_for("views.chat"))
    # Si es GET, redirigir a la página de chat que ahora tiene el modal
    else:
        return redirect(url_for("views.chat"))

@views_bp.route("/usuario/nuevo", methods=["GET", "POST"])
def usuario_nuevo():
    # Si el método es POST, significa que se envió el formulario
    if request.method == "POST":
        # Get form data
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]
        fecha_creacion = datetime.now()
        fecha_modificacion = datetime.now()

        # Get the highest ID currently in the database
        max_id = db.session.query(db.func.max(Usuario.id)).scalar() or 0

        # Create new usuario with ID = max_id + 1
        usuario = Usuario(
            id=max_id + 1,
            nombre=nombre,
            apellidos=apellidos,
            correo=correo,
            contrasena=contrasena,
            fecha_creacion=fecha_creacion,
            fecha_modificacion=fecha_modificacion
        )

        db.session.add(usuario)
        db.session.commit()
        flash(f"Usuario <em>{nombre} {apellidos}</em> añadido con éxito.", "exito")
        return redirect(url_for("views.gestionar_usuarios"))
    # Si es GET, redirigir a la página de usuarios
    else:
        return redirect(url_for("views.gestionar_usuarios"))
