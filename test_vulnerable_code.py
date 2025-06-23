# Archivo de prueba con vulnerabilidades de seguridad

import os
import subprocess

# Credenciales hardcodeadas (VULNERABILIDAD)
api_key = "12345abcdef"
password = "admin123"
secret_key = "my-secret-key"

# SQL Injection vulnerable (VULNERABILIDAD)
def get_user_data(username):
    query = "SELECT * FROM users WHERE username = '%s'" % username
    return execute(query)

# Command Injection vulnerable (VULNERABILIDAD)
def backup_files(filename):
    command = "tar -czf backup.tar.gz " + filename
    os.system(command)

# Otro ejemplo de command injection
def process_file(user_input):
    subprocess.call("cat " + user_input, shell=True)

# Función segura de ejemplo
def safe_function():
    return "Esta función es segura"

# Más vulnerabilidades
access_token = "token123456"

def unsafe_query(user_id):
    sql = "DELETE FROM users WHERE id = " + str(user_id)
    return sql 