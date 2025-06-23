#!/usr/bin/env python3
"""
Archivo de prueba para verificar el análisis de código estático
Contiene vulnerabilidades intencionalmente para testing
"""

import os
import subprocess
import sqlite3

# Vulnerabilidad 1: Credenciales hardcodeadas (MEDIUM)
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"
SECRET_TOKEN = "my-secret-token-123"

# Vulnerabilidad 2: Command Injection (CRITICAL)
def execute_user_command(user_input):
    """Función vulnerable a command injection"""
    command = "ls " + user_input  # Concatenación directa sin sanitización
    result = os.system(command)
    return result

def run_shell_command(filename):
    """Otra función vulnerable"""
    cmd = f"cat {filename}"  # f-string con input no sanitizado
    return subprocess.run(cmd, shell=True, capture_output=True)

# Vulnerabilidad 3: SQL Injection (HIGH)
def get_user_data(user_id):
    """Función vulnerable a SQL injection"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Query vulnerable con string formatting
    query = "SELECT * FROM users WHERE id = '%s'" % user_id
    cursor.execute(query)
    
    return cursor.fetchall()

def search_users(search_term):
    """Otra función vulnerable a SQL injection"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Query vulnerable con concatenación
    query = "SELECT * FROM users WHERE name LIKE '" + search_term + "'"
    cursor.execute(query)
    
    return cursor.fetchall()

# Vulnerabilidad 4: eval() usage (HIGH)
def calculate_expression(expr):
    """Función que usa eval() de forma insegura"""
    result = eval(expr)  # Muy peligroso!
    return result

def dynamic_function_call(func_name, args):
    """Otra función que usa eval()"""
    code = f"{func_name}({args})"
    return eval(code)

# Vulnerabilidad 5: File Inclusion (HIGH)
def include_file(filename):
    """Función vulnerable a file inclusion"""
    with open(filename, 'r') as f:  # Sin validación de path
        return f.read()

def load_config(config_name):
    """Otra función vulnerable"""
    config_path = "/etc/configs/" + config_name  # Path traversal posible
    with open(config_path, 'r') as f:
        return f.read()

# Código JavaScript embebido con XSS
js_code = """
function updateContent(userInput) {
    document.getElementById('content').innerHTML = userInput;  // XSS vulnerability
}

function displayMessage(msg) {
    document.write('<div>' + msg + '</div>');  // Otra vulnerabilidad XSS
}
"""

# Más credenciales hardcodeadas
MYSQL_PASSWORD = "root123"
JWT_SECRET = "jwt-secret-key-456"
ENCRYPTION_KEY = "encryption-key-789"

if __name__ == "__main__":
    print("Archivo de prueba para análisis de código")
    print("Este archivo contiene vulnerabilidades intencionalmente")
    
    # Ejemplos de uso vulnerable
    user_input = input("Ingrese comando: ")
    execute_user_command(user_input)
    
    expression = input("Ingrese expresión: ")
    result = calculate_expression(expression)
    print(f"Resultado: {result}") 