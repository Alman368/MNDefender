from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
from services.message_service import AnimalFactsService
from controllers.message_controller import MessageController
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
login_manager = LoginManager()

# Defino las tablas de la base de datos
class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fecha_modificacion = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    # Relación con usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('proyectos', lazy=True))

class Etiqueta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class ProyectoEtiqueta(db.Model):
    __tablename__ = 'proyecto_etiqueta'  # Esto lo descomentamos para especificar el nombre de la tabla
    proyecto_id = db.Column(db.Integer, db.ForeignKey(Proyecto.id), primary_key=True)
    etiqueta_id = db.Column(db.Integer, db.ForeignKey(Etiqueta.id), primary_key=True)

# Modelo Usuario modificado para Flask-Login
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)  # Añadido campo apellidos
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(50), default='usuario')  # 'administrador' o 'usuario'
    fecha_registro = db.Column(db.Date, nullable=False, default=datetime.now().date())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:contraseña@localhost:3306/gestion_proyectos'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'clave-secreta-para-la-app'  # Necesario para sesiones

    # Inicialización
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Función para cargar usuario desde ID de sesión
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    CORS(app)
    message_controller = MessageController(AnimalFactsService())
    app.add_url_rule('/send-message',
                     view_func=message_controller.send_message,
                     methods=['POST'])

    # Rutas de autenticación
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = db.session.scalar(db.select(Usuario).where(Usuario.username == username))

            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash('Nombre de usuario o contraseña incorrectos', 'error')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    # Rutas públicas
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/chat')
    def chat():
        return render_template('chat.html')

    # Ruta para consultar proyectos (protegida)
    @app.route("/proyectos/")
    @login_required
    def proyectos():
        if current_user.rol == 'administrador':
            # Admin ve todos los proyectos
            p = db.session.scalars(db.select(Proyecto).order_by(
                Proyecto.fecha_modificacion.desc())).all()
        else:
            # Usuario normal solo ve sus proyectos
            p = db.session.scalars(db.select(Proyecto).where(
                Proyecto.usuario_id == current_user.id).order_by(
                Proyecto.fecha_modificacion.desc())).all()
        return render_template("proyectos.html", proyectos=p)

    # Consulta un proyecto por id (protegida)
    @app.route("/proyecto/<int:id>")
    @login_required
    def proyecto(id=None):
        try:
            p = db.session.scalars(db.select(Proyecto).where(Proyecto.id == id)).one()
            # Comprobar permisos
            if current_user.rol != 'administrador' and p.usuario_id != current_user.id:
                flash("No tienes permiso para ver este proyecto.", "error")
                return redirect(url_for("proyectos")), 403
            return render_template("proyecto.html", proyecto=p)
        except NoResultFound:
            flash("Proyecto no encontrado.", "error")
            return redirect(url_for("proyectos")), 404

    # Crear un nuevo proyecto (protegida)
    @app.route("/proyecto/nuevo", methods=["GET", "POST"])
    @login_required
    def proyecto_nuevo():
        if request.method == "POST":
            nombre = request.form["nombre"]
            descripcion = request.form["descripcion"]
            now = datetime.now()
            p = Proyecto(nombre=nombre,
                         descripcion=descripcion,
                         fecha_creacion=now,
                         fecha_modificacion=now,
                         usuario_id=current_user.id)
            db.session.add(p)
            db.session.commit()
            flash(f"Proyecto <em>{nombre}</em> añadido con éxito.", "exito")
            return redirect(url_for("proyectos"))
        else:
            return render_template("proyecto_nuevo.html")

    # Editar un proyecto (protegida)
    @app.route("/proyecto/editar/<int:id>", methods=["GET", "POST"])
    @login_required
    def proyecto_editar(id=None):
        try:
            p = db.one_or_404(db.select(Proyecto).where(Proyecto.id == id))
            # Comprobar permisos
            if current_user.rol != 'administrador' and p.usuario_id != current_user.id:
                flash("No tienes permiso para editar este proyecto.", "error")
                return redirect(url_for("proyectos")), 403
        except NoResultFound:
            flash("Proyecto no encontrado.", "error")
            return redirect(url_for("proyectos")), 404

        if request.method == "POST":
            p.nombre = request.form['nombre']
            p.descripcion = request.form['descripcion']
            p.fecha_modificacion = datetime.now()
            db.session.commit()
            flash(f"Proyecto <em>{p.nombre}</em> modificado con éxito", "exito")
            return redirect(url_for("proyectos"))
        else:
            return render_template("proyecto_editar.html", proyecto=p)

    # Eliminar un proyecto (protegida)
    @app.route("/proyecto/eliminar/<int:id>")
    @login_required
    def proyecto_eliminar(id=None):
        try:
            p = db.one_or_404(db.select(Proyecto).where(Proyecto.id == id))
            # Comprobar permisos
            if current_user.rol != 'administrador' and p.usuario_id != current_user.id:
                flash("No tienes permiso para eliminar este proyecto.", "error")
                return redirect(url_for("proyectos")), 403
        except NoResultFound:
            flash("Proyecto no encontrado.", "error")
            return redirect(url_for("proyectos")), 404

        db.session.delete(p)
        db.session.commit()
        flash(f"Proyecto <em>{p.nombre}</em> eliminado con éxito.", "exito")
        return redirect(url_for("proyectos"))

    # Rutas para gestión de usuarios (admin)
    @app.route("/usuarios/")
    @login_required
    def usuarios():
        if current_user.rol != 'administrador':
            flash("No tienes permiso para acceder a esta página.", "error")
            return redirect(url_for("index")), 403

        u = db.session.scalars(db.select(Usuario).order_by(Usuario.nombre)).all()
        return render_template("usuarios.html", usuarios=u)

    @app.route("/usuario/<int:id>")
    @login_required  # Falta esta decoración para proteger la ruta
    def usuario(id=None):
        if current_user.rol != 'administrador':  # Falta verificación de permisos
            flash("No tienes permiso para acceder a esta página.", "error")
            return redirect(url_for("index")), 403

        try:
            u = db.session.scalars(db.select(Usuario).where(Usuario.id == id)).one()
            return render_template("usuario.html", usuario=u)
        except NoResultFound:
            flash("Usuario no encontrado.", "error")
            return redirect(url_for("usuarios")), 404

    @app.route("/usuario/nuevo", methods=["GET", "POST"])
    @login_required
    def usuario_nuevo():
        if current_user.rol != 'administrador':
            flash("No tienes permiso para acceder a esta página.", "error")
            return redirect(url_for("index")), 403

        if request.method == "POST":
            nombre = request.form["nombre"]
            apellidos = request.form["apellidos"]  # Añadido campo apellidos
            email = request.form["email"]
            username = request.form["username"]
            password = request.form["password"]
            rol = request.form.get("rol", "usuario")
            u = Usuario(nombre=nombre, apellidos=apellidos, email=email, username=username, rol=rol, fecha_registro=datetime.now().date())
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            flash(f"Usuario <em>{nombre}</em> añadido con éxito.", "exito")
            return redirect(url_for("usuarios"))
        else:
            return render_template("usuario_nuevo.html")

    @app.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
    @login_required
    def usuario_editar(id=None):
        if current_user.rol != 'administrador':
            flash("No tienes permiso para acceder a esta página.", "error")
            return redirect(url_for("index")), 403

        try:
            u = db.one_or_404(db.select(Usuario).where(Usuario.id == id))
        except NoResultFound:
            flash("Usuario no encontrado.", "error")
            return redirect(url_for("usuarios")), 404

        if request.method == "POST":
            u.nombre = request.form['nombre']
            u.apellidos = request.form['apellidos']  # Añadido campo apellidos
            u.email = request.form['email']
            u.rol = request.form.get('rol', 'usuario')
            db.session.commit()
            flash(f"Usuario <em>{u.nombre}</em> modificado con éxito", "exito")
            return redirect(url_for("usuarios"))
        else:
            return render_template("usuario_editar.html", usuario=u)

    # Eliminar un usuario (solo administrador)
    @app.route("/usuario/eliminar/<int:id>")
    @login_required
    def usuario_eliminar(id=None):
        if current_user.rol != 'administrador':
            flash("No tienes permiso para eliminar usuarios.", "error")
            return redirect(url_for("index")), 403

        try:
            u = db.one_or_404(db.select(Usuario).where(Usuario.id == id))

            # Evitar eliminar el propio usuario admin que está logueado
            if u.id == current_user.id:
                flash("No puedes eliminar tu propio usuario.", "error")
                return redirect(url_for("usuarios"))

            nombre_usuario = u.nombre
            db.session.delete(u)
            db.session.commit()
            flash(f"Usuario <em>{nombre_usuario}</em> eliminado con éxito.", "exito")
            return redirect(url_for("usuarios"))
        except NoResultFound:
            flash("Usuario no encontrado.", "error")
            return redirect(url_for("usuarios")), 404

    # Nueva ruta para que los usuarios editen su propio perfil
    @app.route("/perfil", methods=["GET", "POST"])
    @login_required
    def editar_perfil():
        u = current_user

        if request.method == "POST":
            u.nombre = request.form['nombre']
            u.apellidos = request.form['apellidos']
            u.email = request.form['email']

            # Cambio de contraseña opcional
            if request.form.get('password') and request.form.get('password').strip():
                u.set_password(request.form['password'])

            db.session.commit()
            flash("Tu perfil ha sido actualizado con éxito", "exito")
            return redirect(url_for("index"))
        else:
            return render_template("perfil.html", usuario=u)

    # Crear tablas y usuarios iniciales
    with app.app_context():
        db.create_all()

        # Crear usuarios predeterminados si no existen
        admin = db.session.scalar(db.select(Usuario).where(Usuario.username == 'admin'))
        if not admin:
            admin = Usuario(
                nombre='Administrador',
                apellidos='Sistema',  # Añadido el apellido
                email='admin@example.com',
                username='admin',
                rol='administrador',
                fecha_registro=datetime.now().date()
            )
            admin.set_password('admin')
            db.session.add(admin)

        user = db.session.scalar(db.select(Usuario).where(Usuario.username == 'user'))
        if not user:
            user = Usuario(
                nombre='Usuario',
                apellidos='Normal',  # Añadido el apellido
                email='user@example.com',
                username='user',
                rol='usuario',
                fecha_registro=datetime.now().date()
            )
            user.set_password('user')
            db.session.add(user)

        db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
