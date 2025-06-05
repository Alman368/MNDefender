#!/usr/bin/env python3
"""
Script para iniciar todos los microservicios del proyecto.
Ejecuta los tres servicios en procesos separados.
"""

import subprocess
import sys
import time
import signal
import os

def start_service(script_name, service_name, port):
    """Inicia un servicio en un proceso separado."""
    print(f"🚀 Iniciando {service_name} en puerto {port}...")
    return subprocess.Popen(['python3', script_name])

def main():
    """Función principal para iniciar todos los servicios."""
    print("=" * 50)
    print("🏗️  INICIANDO MICROSERVICIOS FLASK")
    print("=" * 50)

    processes = []

    try:
        # Iniciar servicios
        api_process = start_service("run_api.py", "API Service", 5001)
        processes.append(("API Service", api_process))
        time.sleep(2)

        chat_process = start_service("run_chat.py", "Chat Service", 5002)
        processes.append(("Chat Service", chat_process))
        time.sleep(2)

        web_process = start_service("run.py", "Web Service", 5000)
        processes.append(("Web Service", web_process))

        print("\n" + "=" * 50)
        print("✅ TODOS LOS SERVICIOS INICIADOS")
        print("=" * 50)
        print("🌐 Accede a la aplicación en: http://localhost:5000")
        print("🔗 API disponible en: http://localhost:5001")
        print("💬 Chat disponible en: http://localhost:5002")
        print("🚨 Página vulnerable (Stored XSS): http://localhost:5000/comments")
        print("\n⚠️  Presiona Ctrl+C para detener todos los servicios")
        print("=" * 50)

        # Esperar hasta que el usuario presione Ctrl+C
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo todos los servicios...")

        for service_name, process in processes:
            if process.poll() is None:  # Si el proceso sigue corriendo
                print(f"⏹️  Deteniendo {service_name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

        print("✅ Todos los servicios han sido detenidos.")
        sys.exit(0)

if __name__ == "__main__":
    main()
