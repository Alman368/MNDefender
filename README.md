# SVAIA 🛡️
## Sistema de Soporte para Vulnerabilidades y Amenazas basado en Inteligencia Artificial

<div align="center">

![SVAIA Logo](static/imagenes/logo.svg)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Powered-purple.svg)](https://ai.google.dev)

**Una plataforma avanzada para la gestión de vulnerabilidades de ciberseguridad con asistencia de IA**

</div>

---

## 📋 Tabla de Contenidos

- [🎯 Características](#-características)
- [🏗️ Arquitectura](#️-arquitectura)
- [⚡ Instalación Rápida](#-instalación-rápida)
- [🔧 Configuración](#-configuración)
- [🚀 Uso](#-uso)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🔒 Seguridad](#-seguridad)
- [🤝 Contribución](#-contribución)
- [📄 Licencia](#-licencia)

---

## 🎯 Características

### 🤖 **Asistente IA Especializado**
- **Chat inteligente** con Gemini AI especializado en ciberseguridad
- **Respuestas en Markdown** convertidas a HTML con formato profesional
- **Conocimiento especializado** en vulnerabilidades, ataques y mejores prácticas
- **Soporte para tablas, listas, código** y formato rico

### 📊 **Gestión de Proyectos**
- **Crear, editar y eliminar** proyectos de seguridad
- **Criterios de aceptabilidad** personalizables para cada proyecto
- **Historial de conversaciones** por proyecto
- **Información detallada** de cada proyecto con criterios asociados

### 👥 **Sistema de Usuarios**
- **Autenticación segura** con roles de usuario y administrador
- **Sesiones protegidas** con expiración automática
- **Gestión de usuarios** para administradores
- **Protección CSRF** y medidas de seguridad avanzadas

### 🔍 **Análisis Estático de Código**
- **Detección automática** de vulnerabilidades en múltiples lenguajes
- **Integración con CVE** para información detallada de vulnerabilidades
- **Criterios de aceptabilidad** con reevaluación automática
- **Separación completa** por proyecto con carpetas individuales
- **Historial de análisis** y estadísticas por proyecto

### 🎨 **Interfaz Moderna**
- **Diseño responsive** con Bootstrap 5
- **Ventanas modales** para gestión de proyectos
- **Chat en tiempo real** con interfaz intuitiva
- **Efectos visuales** y animaciones suaves

---

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   External      │
│                 │    │                  │    │                 │
│ • Bootstrap 5   │◄──►│ • Flask 3.0      │◄──►│ • Gemini AI     │
│ • JavaScript    │    │ • SQLAlchemy     │    │ • MySQL DB      │
│ • CSS3/HTML5    │    │ • Flask-Login    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Stack Tecnológico**
- **Backend:** Python 3.8+ con Flask
- **Base de Datos:** MySQL 8.0+ con SQLAlchemy ORM
- **Frontend:** HTML5, CSS3, JavaScript ES6+, Bootstrap 5
- **IA:** Google Gemini API
- **Autenticación:** Flask-Login con sesiones seguras
- **Deployment:** Docker (MySQL), Python virtual environment

---

## ⚡ Instalación Rápida

### **Prerrequisitos**
- Python 3.8 o superior
- MySQL 8.0 o superior
- Git

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/tu-usuario/gitmndefender.git
cd gitmndefender
```

### **2. Crear Entorno Virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate  # Windows
```

### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **4. Configurar Base de Datos**
```bash
# Opción A: Docker (Recomendado)
cd mysql
docker-compose up -d

# Opción B: MySQL Local
mysql -u root -p
CREATE DATABASE gitmndefender;
```

### **5. Configurar Variables de Entorno**
```bash
# Crear archivo de configuración
cp config.env.example config.env

# Editar config.env con tus valores
GEMINI_API_KEY=tu_clave_api_gemini
GEMINI_MODEL=gemini-1.5-flash
```

### **6. Ejecutar la Aplicación**
```bash
python run.py
```

🎉 **¡Aplicación disponible en http://localhost:5003!**

---

## 📦 Distribución del Proyecto

### **Crear ZIP Limpio para Distribución**
```bash
# Ejecutar el script de distribución
chmod +x scripts/create_distribution.sh
./scripts/create_distribution.sh
```

El script automáticamente excluye:
- **Entornos virtuales** (`venv/`, `.venv/`)
- **Historial de Git** (`.git/`)
- **Cache de Python** (`__pycache__/`, `*.pyc`)
- **Archivos temporales** (`uploads/`, `*.log`, `*.tmp`)
- **Configuración privada** (`config.env`)
- **Archivos de prueba** (`test_*.py`, `debug_*.py`)

**Resultado:** ZIP de ~270KB en lugar de 260MB

---

## 🔧 Configuración

### **Archivo `config.env`**
```env
# API de Gemini (Obligatorio)
GEMINI_API_KEY=tu_clave_api_gemini

# Modelo de IA (Opcional)
GEMINI_MODEL=gemini-1.5-flash

# Base de Datos (Opcional)
DATABASE_URL=mysql+pymysql://usuario:password@localhost/gitmndefender

# Flask (Opcional)
SECRET_KEY=clave_secreta_segura
FLASK_ENV=development
```

### **Obtener API Key de Gemini**
1. Visita [Google AI Studio](https://ai.google.dev)
2. Crea una cuenta y genera una API key
3. Añade la clave a tu archivo `config.env`

### **Usuarios por Defecto**
```
Administrador:
- Usuario: admin
- Contraseña: Admin123!

Usuario Normal:
- Usuario: user
- Contraseña: User123!
```

---

## 🚀 Uso

### **1. Inicio de Sesión**
- Accede a `/login` con las credenciales por defecto
- Los administradores pueden gestionar usuarios en `/usuarios`

### **2. Gestión de Proyectos**
- **Crear:** Clic en el icono ➕ en la barra lateral
- **Editar:** Clic en el icono ✏️ sobre un proyecto
- **Ver Info:** Clic en el icono ℹ️ para detalles
- **Eliminar:** Clic en el icono 🗑️ (con confirmación)

### **3. Criterios de Aceptabilidad**
- Añade criterios personalizados desde el modal de proyecto
- Define tipos de criterio y valores específicos
- Los criterios se asocian automáticamente al proyecto

### **4. Chat con IA**
- Selecciona un proyecto activo
- Escribe tu consulta sobre ciberseguridad
- SVAIA responderá con información especializada
- Las respuestas incluyen formato rico (tablas, listas, etc.)

### **5. Análisis Estático de Código**
- **Acceder:** Navega a `/code-analysis`
- **Seleccionar proyecto:** Elige el proyecto donde realizar el análisis
- **Subir archivo:** Arrastra o selecciona un archivo de código
- **Revisar resultados:** Analiza vulnerabilidades, severidades y criterios
- **Ver historial:** Consulta análisis previos del proyecto

#### **Lenguajes Soportados**
- **Python** (.py) - SQL Injection, Command Injection, eval() usage
- **JavaScript/TypeScript** (.js, .ts) - XSS, eval() usage, innerHTML
- **Java** (.java) - SQL Injection en executeQuery
- **PHP** (.php) - SQL Injection, File Inclusion
- **C/C++** (.c, .cpp) - Buffer overflow patterns
- **C#** (.cs) - Patrones de vulnerabilidades .NET
- **Ruby** (.rb) - Patrones específicos de Ruby
- **Go** (.go) - Patrones específicos de Go

#### **Tipos de Vulnerabilidades Detectadas**
- **CRÍTICO:** Command Injection, SQL Injection avanzado
- **ALTO:** SQL Injection básico, XSS, eval() usage, File Inclusion
- **MEDIO:** Credenciales hardcodeadas, configuraciones inseguras
- **BAJO:** Patrones de código sospechoso

#### **Reevaluación Automática de Criterios**
- **Automática:** Al modificar criterios de aceptabilidad del proyecto
- **Manual:** Botón "Reevaluar Criterios" en el historial de análisis
- **Notificaciones:** Cambios de estado detallados (Aprobado ↔ Rechazado)
- **Historial:** Registro completo de cambios de estado por archivo
- **Separación:** Cada proyecto mantiene sus análisis completamente separados

#### **Gestión de Archivos por Proyecto**
- **Carpetas separadas:** `uploads/proyecto_{id}/` para cada proyecto
- **Nombres únicos:** Timestamp + UUID + nombre original
- **Limpieza automática:** Archivos antiguos se eliminan después de 7 días
- **Seguridad:** Solo puedes acceder a archivos de tus propios proyectos

### **6. Ejemplos de Consultas**
```
• "Explica las vulnerabilidades más comunes en aplicaciones web"
• "Dame una tabla comparando XSS y SQL Injection"
• "¿Cómo proteger mi aplicación Flask contra CSRF?"
• "Lista las mejores prácticas para autenticación segura"
```

---

## 📁 Estructura del Proyecto

```
gitmndefender/
├── 📁 app/                    # Aplicación Flask principal
│   ├── 📁 api/               # API endpoints
│   ├── 📁 models/            # Modelos de base de datos
│   ├── 📁 views/             # Vistas y rutas web
│   ├── __init__.py           # Factory de la aplicación
│   └── config.py             # Configuración Flask
├── 📁 controllers/           # Controladores de lógica
│   ├── message_controller.py # Controlador de mensajes
│   └── code_analysis_controller.py # Controlador de análisis de código
├── 📁 services/              # Servicios y lógica de negocio
│   ├── message_service.py    # Servicio de IA (Gemini)
│   └── code_analysis_service.py # Servicio de análisis estático
├── 📁 static/                # Recursos estáticos
│   ├── 📁 css/              # Hojas de estilo
│   ├── 📁 js/               # JavaScript
│   └── 📁 imagenes/         # Recursos gráficos
├── 📁 templates/             # Plantillas HTML
│   ├── chat.html            # Interfaz principal de chat
│   ├── code_analysis.html   # Interfaz de análisis de código
│   ├── login.html           # Página de inicio de sesión
│   └── usuarios.html        # Gestión de usuarios
├── 📁 uploads/               # Archivos de análisis por proyecto
│   ├── proyecto_1/          # Archivos del proyecto 1
│   └── proyecto_2/          # Archivos del proyecto 2
├── 📁 mysql/                # Configuración Docker MySQL
├── config.env               # Variables de entorno (PRIVADO)
├── requirements.txt         # Dependencias Python
└── run.py                   # Punto de entrada de la aplicación
```

---

## 🔒 Seguridad

### **Características de Seguridad Implementadas**

✅ **Autenticación y Autorización**
- Contraseñas hasheadas con Werkzeug
- Sesiones seguras con Flask-Login
- Protección contra sesiones concurrentes
- Roles de usuario (admin/normal)

✅ **Protección Web**
- Protección CSRF integrada
- Cookies HTTPOnly y Secure
- Validación de entrada de datos
- Escape automático en plantillas

✅ **Base de Datos**
- SQLAlchemy ORM (previene SQL injection)
- Validación de tipos de datos
- Transacciones seguras

✅ **Configuración**
- API keys en archivos externos
- Variables de entorno protegidas
- `.gitignore` para archivos sensibles

### **Recomendaciones de Producción**
- Usar HTTPS en producción
- Configurar proxy reverso (nginx)
- Implementar rate limiting
- Monitoreo de logs de seguridad
- Actualizaciones regulares de dependencias

---

## 🤝 Contribución

### **Cómo Contribuir**
1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abre** un Pull Request

### **Estándares de Código**
- Seguir PEP 8 para Python
- Comentar código complejo
- Escribir tests para nuevas funcionalidades
- Actualizar documentación cuando sea necesario

### **Reportar Bugs**
- Usar el sistema de issues de GitHub
- Incluir pasos para reproducir el error
- Especificar versión de Python y SO
- Adjuntar logs relevantes

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- **Google Gemini** por proporcionar la API de IA
- **Flask Community** por el excelente framework
- **Bootstrap Team** por los componentes UI
- **Todos los contribuidores** que hacen posible este proyecto

---

<div align="center">

**Desarrollado con ❤️ para la comunidad de ciberseguridad**

[🌟 Star este proyecto](https://github.com/tu-usuario/gitmndefender) | [🐛 Reportar Bug](https://github.com/tu-usuario/gitmndefender/issues) | [💡 Solicitar Feature](https://github.com/tu-usuario/gitmndefender/issues)

</div>
