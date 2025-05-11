from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import requests
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv
from functools import wraps

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

API_URL = os.getenv('API_URL', 'http://localhost:5001')

class User(UserMixin):
    def __init__(self, id, username, is_admin=False):
        self.id = id
        self.username = username
        self.is_admin = is_admin
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    try:
        response = requests.get(f'{API_URL}/api/users/{user_id}')
        if response.status_code == 200:
            user_data = response.json()
            return User(user_data['id'], user_data['username'], user_data['is_admin'])
    except requests.RequestException:
        flash('Error al conectar con el servidor', 'error')
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor, completa todos los campos', 'error')
            return render_template('login.html')
        
        try:
            response = requests.get(f'{API_URL}/api/users')
            if response.status_code == 200:
                users = response.json()
                user = next((u for u in users if u['username'] == username), None)
                if user and check_password_hash(user['password_hash'], password):
                    user_obj = User(user['id'], user['username'], user['is_admin'])
                    login_user(user_obj)
                    return redirect(url_for('index'))
                flash('Usuario o contraseña incorrectos', 'error')
            else:
                flash('Error al conectar con el servidor', 'error')
        except requests.RequestException:
            flash('Error al conectar con el servidor', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/usuarios')
@login_required
@admin_required
def usuarios():
    try:
        response = requests.get(f'{API_URL}/api/users')
        if response.status_code == 200:
            usuarios = response.json()
            return render_template('usuarios.html', usuarios=usuarios)
        flash('Error al obtener los usuarios', 'error')
    except requests.RequestException:
        flash('Error al conectar con el servidor', 'error')
    return redirect(url_for('index'))

@app.route('/usuario/nuevo', methods=['POST'])
@login_required
@admin_required
def usuario_nuevo():
    try:
        data = {
            'nombre': request.form['nombre'],
            'apellidos': request.form['apellidos'],
            'correo': request.form['correo'],
            'username': request.form['user'],
            'password': request.form['contrasena'],
            'is_admin': False
        }
        
        response = requests.post(f'{API_URL}/api/users', json=data)
        if response.status_code == 201:
            flash(f"Usuario <em>{data['nombre']} {data['apellidos']}</em> añadido con éxito.", "exito")
        else:
            error_data = response.json()
            flash(f"Error al crear el usuario: {error_data.get('error', 'Error desconocido')}", 'error')
    except requests.RequestException:
        flash('Error al conectar con el servidor', 'error')
    return redirect(url_for('usuarios'))

@app.route('/proyectos')
@login_required
def proyectos():
    try:
        response = requests.get(f'{API_URL}/api/proyectos')
        if response.status_code == 200:
            proyectos = response.json()
            if not current_user.is_admin:
                proyectos = [p for p in proyectos if p['usuario_id'] == current_user.id]
            return render_template('proyectos.html', proyectos=proyectos)
        flash('Error al obtener los proyectos', 'error')
    except requests.RequestException:
        flash('Error al conectar con el servidor', 'error')
    return redirect(url_for('index'))

@app.route('/proyecto/nuevo', methods=['POST'])
@login_required
def proyecto_nuevo():
    try:
        data = {
            'nombre': request.form['project_name'],
            'descripcion': request.form['project_description'],
            'usuario_id': current_user.id
        }
        
        response = requests.post(f'{API_URL}/api/proyectos', json=data)
        if response.status_code == 201:
            flash(f"Proyecto <em>{data['nombre']}</em> añadido con éxito.", "exito")
        else:
            error_data = response.json()
            flash(f"Error al crear el proyecto: {error_data.get('error', 'Error desconocido')}", 'error')
    except requests.RequestException:
        flash('Error al conectar con el servidor', 'error')
    return redirect(url_for('proyectos'))

if __name__ == '__main__':
    app.run(debug=True, port=5000) 