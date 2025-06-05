from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import requests
from datetime import timedelta
from web.models.user import User
import os
import sqlite3

# URLs for microservices
API_URL = 'http://localhost:5001'  # Projects and users API
CHAT_URL = 'http://localhost:5002'  # Chat microservice

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Configuración
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Session expires after 1 hour
app.config['SESSION_COOKIE_SECURE'] = False  # Cambiado para desarrollo local
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Cambiado para permitir acceso desde JavaScript
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['WTF_CSRF_ENABLED'] = False

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
login_manager.session_protection = 'strong'

# Database initialization for comments
def init_comments_db():
    """Initialize comments database"""
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            comment TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_comments_db()

@login_manager.user_loader
def load_user(user_id):
    try:
        # Get JWT token from session
        token = session.get('access_token')
        if not token:
            return None

        # Get user from API with JWT token
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{API_URL}/users/{user_id}', headers=headers)

        if response.status_code == 200:
            user_data = response.json()['user']
            return User.from_api_data(user_data)
    except requests.RequestException:
        pass
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            # Login using the API's authentication endpoint
            response = requests.post(f'{API_URL}/auth/login', json={
                'username': username,
                'password': password
            })

            if response.status_code == 200:
                data = response.json()
                access_token = data.get('access_token')
                user_data = data.get('user')

                user = User.from_api_data(user_data)

                # Store the JWT token in the session
                session['access_token'] = access_token

                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash('Nombre de usuario o contraseña incorrectos', 'danger')
        except requests.RequestException as e:
            flash(f'Error al conectar con el servicio: {str(e)}', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('access_token', None)
    logout_user()
    return redirect(url_for('login'))

@app.route('/usuarios')
@login_required
def usuarios():
    try:
        # Get JWT token from session
        token = session.get('access_token')
        headers = {'Authorization': f'Bearer {token}'}

        response = requests.get(f'{API_URL}/users', headers=headers)
        if response.status_code == 200:
            users = response.json().get('users', [])
            return render_template('usuarios.html', users=users)
        elif response.status_code == 403:
            flash('No tienes permisos para ver la lista de usuarios', 'danger')
            return redirect(url_for('index'))
        else:
            flash('Error al obtener usuarios', 'danger')
            return redirect(url_for('index'))
    except requests.RequestException as e:
        flash(f'Error al conectar con el servicio: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/usuario/nuevo', methods=['POST'])
@login_required
def usuario_nuevo():
    if request.method == 'POST':
        username = request.form.get('user')
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        correo = request.form.get('correo')
        password = request.form.get('contrasena')

        if not all([username, nombre, apellidos, correo, password]):
            flash('Por favor complete todos los campos', 'danger')
            return redirect(url_for('usuarios'))

        try:
            # Get JWT token from session
            token = session.get('access_token')
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

            user_data = {
                'username': username,
                'nombre': nombre,
                'apellidos': apellidos,
                'correo': correo,
                'password': password,
                'is_admin': False  # By default, new users are not admins
            }

            response = requests.post(
                f'{API_URL}/users',
                json=user_data,
                headers=headers
            )

            if response.status_code == 201:
                flash('Usuario creado exitosamente', 'success')
            else:
                flash(f'Error al crear usuario: {response.json().get("message", "Error desconocido")}', 'danger')
        except requests.RequestException as e:
            flash(f'Error al conectar con el servicio: {str(e)}', 'danger')

        return redirect(url_for('usuarios'))

@app.route('/chat')
@login_required
def chat():
    try:
        # Get JWT token from session
        token = session.get('access_token')
        headers = {'Authorization': f'Bearer {token}'}

        response = requests.get(f'{API_URL}/projects', headers=headers)
        if response.status_code == 200:
            projects = response.json().get('projects', [])
            return render_template('chat.html', proyectos=projects)
        else:
            flash('Error al obtener proyectos', 'danger')
            return redirect(url_for('index'))
    except requests.RequestException as e:
        flash(f'Error al conectar con el servicio: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/proyecto/nuevo', methods=['POST'])
@login_required
def proyecto_nuevo():
    if request.method == 'POST':
        nombre = request.form.get('project_name')
        descripcion = request.form.get('project_description')

        if not nombre or not descripcion:
            flash('Por favor complete todos los campos', 'danger')
            return redirect(url_for('chat'))

        try:
            # Get JWT token from session
            token = session.get('access_token')
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

            project_data = {
                'nombre': nombre,
                'descripcion': descripcion,
                'usuario_id': current_user.id
            }

            response = requests.post(
                f'{API_URL}/projects',
                json=project_data,
                headers=headers
            )

            if response.status_code == 201:
                flash('Proyecto creado exitosamente', 'success')
            else:
                flash(f'Error al crear proyecto: {response.json().get("message", "Error desconocido")}', 'danger')
        except requests.RequestException as e:
            flash(f'Error al conectar con el servicio: {str(e)}', 'danger')

        return redirect(url_for('chat'))

@app.route('/send-message', methods=['POST'])
@login_required
def send_message():
    text = request.json.get('message', '')

    try:
        response = requests.post(f'{CHAT_URL}/api/chat', json={'message': text})
        if response.status_code == 200:
            return response.json()
        else:
            return {'message': 'Error al enviar mensaje al servicio de chat'}, 500
    except requests.RequestException:
        return {'message': 'Error de conexión al servicio de chat'}, 500

@app.route('/api/proyecto/editar/<int:project_id>', methods=['PUT'])
@login_required
def editar_proyecto(project_id):
    try:
        # Get data from request
        data = request.get_json()
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')

        # Validate data
        if not nombre or not descripcion:
            return {'error': 'Nombre y descripción son obligatorios'}, 400

        # Get JWT token from session and prepare headers
        token = session.get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

        # Send request to API service
        response = requests.put(
            f'{API_URL}/projects/{project_id}',
            json={
                'nombre': nombre,
                'descripcion': descripcion
            },
            headers=headers
        )

        # Return API response
        return response.json(), response.status_code
    except requests.RequestException as e:
        return {'error': f'Error al conectar con el servicio: {str(e)}'}, 500

@app.route('/api/proyecto/eliminar/<int:project_id>', methods=['DELETE'])
@login_required
def eliminar_proyecto(project_id):
    try:
        # Get JWT token from session and prepare headers
        token = session.get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

        # Send request to API service
        response = requests.delete(
            f'{API_URL}/projects/{project_id}',
            headers=headers
        )

        # Return API response
        if response.status_code == 200:
            return {'success': 'Proyecto eliminado correctamente'}, 200
        else:
            return response.json(), response.status_code
    except requests.RequestException as e:
        return {'error': f'Error al conectar con el servicio: {str(e)}'}, 500

@app.route('/api/proyecto/<int:project_id>', methods=['GET'])
@login_required
def obtener_proyecto(project_id):
    try:
        # Get JWT token from session and prepare headers
        token = session.get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

        # Send request to API service
        response = requests.get(
            f'{API_URL}/projects/{project_id}',
            headers=headers
        )

        # Return API response
        if response.status_code == 200:
            return response.json().get('project', {}), 200
        else:
            return response.json(), response.status_code
    except requests.RequestException as e:
        return {'error': f'Error al conectar con el servicio: {str(e)}'}, 500

@app.route('/api/proyecto/<int:project_id>/mensajes', methods=['GET'])
@login_required
def obtener_mensajes_proyecto(project_id):
    try:
        # You would typically call your API microservice here to get messages
        # For now, we'll return an empty list since the message functionality
        # might be implemented differently or stored in a separate database
        return []
    except Exception as e:
        return {'error': f'Error al obtener mensajes: {str(e)}'}, 500

@app.route('/api/mensaje', methods=['POST'])
@login_required
def guardar_mensaje():
    try:
        # Get message data
        data = request.get_json()
        contenido = data.get('contenido')
        es_bot = data.get('es_bot', False)
        proyecto_id = data.get('proyecto_id')

        # Here you would typically call your API microservice to save the message
        # Since this is a simple implementation, we'll just return success
        return {'success': True, 'message': 'Mensaje guardado correctamente'}, 200
    except Exception as e:
        return {'error': f'Error al guardar mensaje: {str(e)}'}, 500

@app.route('/api/usuario/editar/<int:user_id>', methods=['PUT'])
@login_required
def editar_usuario(user_id):
    try:
        # Get data from request
        data = request.get_json()

        # Validate required data
        required_fields = ['nombre', 'apellidos', 'correo', 'user']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return {'error': f'Faltan campos requeridos: {", ".join(missing_fields)}'}, 400

        # Get JWT token from session and prepare headers
        token = session.get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

        # Prepare the data for the API
        user_data = {
            'nombre': data.get('nombre'),
            'apellidos': data.get('apellidos'),
            'correo': data.get('correo'),
            'username': data.get('user')  # mapping 'user' to 'username' for API
        }

        # Add password only if provided
        if 'contrasena' in data and data['contrasena']:
            user_data['password'] = data['contrasena']

        # Send request to API
        response = requests.put(
            f'{API_URL}/users/{user_id}',
            json=user_data,
            headers=headers
        )

        # Return API response
        return response.json(), response.status_code
    except requests.RequestException as e:
        return {'error': f'Error al conectar con el servicio: {str(e)}'}, 500

@app.route('/api/usuario/eliminar/<int:user_id>', methods=['DELETE'])
@login_required
def eliminar_usuario(user_id):
    try:
        # Get JWT token from session
        token = session.get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

        # Send request to API
        response = requests.delete(
            f'{API_URL}/users/{user_id}',
            headers=headers
        )

        # Return API response
        if response.status_code == 200:
            return {'success': 'Usuario eliminado correctamente'}, 200
        else:
            return response.json(), response.status_code
    except requests.RequestException as e:
        return {'error': f'Error al conectar con el servicio: {str(e)}'}, 500

@app.route('/api/usuario/<int:user_id>', methods=['GET'])
@login_required
def obtener_usuario(user_id):
    try:
        # Get JWT token from session
        token = session.get('access_token')
        headers = {'Authorization': f'Bearer {token}'}

        # Send request to API
        response = requests.get(
            f'{API_URL}/users/{user_id}',
            headers=headers
        )

        # Return API response
        if response.status_code == 200:
            user_data = response.json().get('user', {})
            # Adapt field names for frontend compatibility
            return {
                'id': user_data.get('id'),
                'nombre': user_data.get('nombre'),
                'apellidos': user_data.get('apellidos'),
                'correo': user_data.get('correo'),
                'user': user_data.get('username'),  # map 'username' to 'user' for frontend
                'is_admin': user_data.get('is_admin')
            }, 200
        else:
            return response.json(), response.status_code
    except requests.RequestException as e:
        return {'error': f'Error al conectar con el servicio: {str(e)}'}, 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

@app.route('/reflectedxss')
def reflectedxss():
    query = request.args.get('q', '')  # obtener parámetro q
    # NO se hace ninguna sanitización ni escape
    return f'<h1>Resultados para: {query}</h1>'

# === VULNERABILIDAD STORED XSS ===
@app.route('/comments')
@login_required
def comments():
    """Display comments page with all stored comments - VULNERABLE TO STORED XSS"""
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, comment, timestamp FROM comments ORDER BY timestamp DESC')
    comments_data = cursor.fetchall()
    conn.close()

    # Convert to list of dictionaries for easier template usage
    comments_list = []
    for row in comments_data:
        comments_list.append({
            'username': row[0],
            'comment': row[1],  # NO SANITIZATION - VULNERABLE!
            'timestamp': row[2]
        })

    return render_template('comments.html', comments=comments_list)

@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    """Add a new comment - VULNERABLE TO STORED XSS"""
    comment_text = request.form.get('comment', '')
    username = current_user.username if current_user.is_authenticated else 'Anónimo'

    # VULNERABLE: No input sanitization or validation
    if comment_text.strip():  # Only check if not empty
        conn = sqlite3.connect('comments.db')
        cursor = conn.cursor()
        # VULNERABLE: Storing raw user input without sanitization
        cursor.execute('INSERT INTO comments (username, comment) VALUES (?, ?)',
                      (username, comment_text))
        conn.commit()
        conn.close()

        flash('Comentario agregado exitosamente', 'success')
    else:
        flash('El comentario no puede estar vacío', 'danger')

    return redirect(url_for('comments'))

@app.route('/domxss')
def domxss():
    """Página vulnerable a DOM-based XSS"""
    return render_template('domxss.html')
