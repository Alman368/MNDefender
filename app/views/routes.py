from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from . import views_bp
from app.models import db, Proyecto, User

views_bp = Blueprint('views', __name__)

@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get_by_username(username)

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('views.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')

    return render_template('login.html')

@views_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.login'))

@views_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@views_bp.route('/chat')
@login_required
def chat():
    if current_user.is_admin:
        proyectos = Proyecto.query.all()
    else:
        proyectos = Proyecto.query.filter_by(usuario_id=current_user.id).all()
    return render_template('chat.html', proyectos=proyectos)

@views_bp.route('/usuarios')
@login_required
def usuarios():
    if not current_user.is_admin:
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('views.index'))
    usuarios = User.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@views_bp.route("/proyecto/nuevo", methods=["GET", "POST"])
@login_required
def proyecto_nuevo():
    if request.method == "POST":
        nombre = request.form["project_name"]
        descripcion = request.form["project_description"]

        proyecto = Proyecto(
            nombre=nombre,
            descripcion=descripcion,
            usuario_id=current_user.id
        )

        db.session.add(proyecto)
        db.session.commit()
        flash(f"Proyecto <em>{nombre}</em> añadido con éxito.", "exito")
        return redirect(url_for("views.chat"))
    return redirect(url_for("views.chat"))

@views_bp.route("/usuario/nuevo", methods=["GET", "POST"])
@login_required
def usuario_nuevo():
    if not current_user.is_admin:
        flash('No tienes permisos para crear usuarios', 'error')
        return redirect(url_for('views.index'))

    if request.method == "POST":
        usuario = User(
            nombre=request.form["nombre"],
            apellidos=request.form["apellidos"],
            correo=request.form["correo"],
            username=request.form["user"],
            password=request.form["contrasena"]
        )

        db.session.add(usuario)
        db.session.commit()
        flash(f"Usuario <em>{usuario.nombre} {usuario.apellidos}</em> añadido con éxito.", "exito")
        return redirect(url_for("views.usuarios"))
    return redirect(url_for("views.usuarios"))
