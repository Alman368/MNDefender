#!/usr/bin/env python3
"""
Archivo de prueba para verificar colores y niveles
"""

import os
import subprocess

# MEDIO - Credenciales
API_KEY = "sk-test123"
PASSWORD = "admin123"

# CRITICO - Command injection (pero no está implementado aún)
def run_command(cmd):
    command = "ls " + cmd
    result = os.system(command)
    return result

# ALTO - eval usage
def calc(expr):
    result = eval(expr)
    return result

print("Test de colores y niveles") 