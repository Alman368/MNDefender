from flask import render_template, request, flash, redirect, url_for
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from . import views_bp
from app.models import db, Proyecto

@views_bp.route('/')
def index():
    return render_template('index.html')

@views_bp.route('/chat')
def chat():
    # Coger los proyectos de la base de datos
    proyectos = db.session.scalars(db.select(Proyecto)).all()
    # Le pasamos los proyectos a la plantilla
    return render_template('chat.html', proyectos=proyectos)

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

@views_bp.route("/proyecto/editar/<int:id>", methods=["GET", "POST"])
def proyecto_editar(id=None):
    # Obtener el proyecto por ID o devolver un error 404 si no existe
    try:
        p = db.one_or_404(db.select(Proyecto).where(Proyecto.id == id))
    except NoResultFound:
        flash("Proyecto no encontrado.", "error")
        return redirect(url_for("views.chat")), 404

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
        return redirect(url_for("views.chat"))
    else:
        # Mostrar el formulario de edición con los datos actuales del proyecto
        return render_template("chat.html", proyecto=p)

@views_bp.route("/proyecto/eliminar/<int:id>")
def proyecto_eliminar(id=None):
    # Obtener el proyecto por ID o devolver un error 404 si no existe
    try:
        p = db.one_or_404(db.select(Proyecto).where(Proyecto.id == id))
    except NoResultFound:
        flash("Proyecto no encontrado.", "error")
        return redirect(url_for("views.chat")), 404

    # Eliminar el proyecto de la base de datos
    db.session.delete(p)
    db.session.commit()

    # Mostrar mensaje de éxito y redirigir a la lista de proyectos
    flash(f"Proyecto <em>{p.nombre}</em> eliminado con éxito.", "exito")
    return redirect(url_for("views.chat"))
