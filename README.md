# 🛡️ SVAIA - Sistema de Soporte para Vulnerabilidades y Amenazas basado en Inteligencia Artificial

## 📋 Tabla de Contenidos
1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Características Principales](#características-principales)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Tecnologías Utilizadas](#tecnologías-utilizadas)
5. [Instalación y Configuración](#instalación-y-configuración)
6. [Uso del Sistema](#uso-del-sistema)
7. [Estructura del Proyecto](#estructura-del-proyecto)
8. [Funcionalidades Implementadas](#funcionalidades-implementadas)
9. [Usuarios por Defecto](#usuarios-por-defecto)
10. [Base de Datos](#base-de-datos)
11. [API Endpoints](#api-endpoints)
12. [Demostración](#demostración)
13. [Roadmap](#roadmap)
14. [Contribuir](#contribuir)

---

## 🎯 Descripción del Proyecto

**SVAIA** es un sistema innovador diseñado para proporcionar soporte automatizado en la identificación y análisis de vulnerabilidades y amenazas de seguridad utilizando inteligencia artificial. El proyecto está desarrollado como una aplicación web que permite a los usuarios describir sus proyectos y recibir sugerencias personalizadas sobre seguridad.

### 🚀 Propósito

El objetivo principal de SVAIA es democratizar el acceso a conocimientos especializados en ciberseguridad, proporcionando una herramienta accesible que ayude a desarrolladores y organizaciones a:

- Identificar potenciales vulnerabilidades en sus proyectos
- Recibir recomendaciones de seguridad específicas
- Acceder a información actualizada sobre amenazas
- Implementar mejores prácticas de seguridad

---

## ✨ Características Principales

### 🤖 Inteligencia Artificial Integrada
- **Chat interactivo** con modelo DeepSeek via OpenRouter API
- **Análisis automático** de descripciones de proyectos de seguridad
- **Sugerencias personalizadas** generadas por IA en tiempo real
- **Respuestas especializadas** en ciberseguridad y vulnerabilidades

### 👥 Sistema de Usuarios
- **Autenticación segura** con hash de contraseñas
- **Roles diferenciados** (usuarios normales y administradores)
- **Gestión de sesiones** con protección CSRF
- **Panel de administración** para gestión de usuarios

### 💬 Sistema de Chat Avanzado
- **Interfaz moderna** y responsive
- **Múltiples servicios de IA** (hechos de animales, saludos, mensajes aleatorios)
- **Historial de conversaciones**
- **Respuestas en tiempo real**

### 🎨 Interfaz de Usuario
- **Diseño moderno** con Bootstrap
- **Responsive design** para móviles y escritorio
- **Animaciones CSS** para mejor experiencia de usuario
- **Tema profesional** con degradados y efectos visuales

---

## 🏗️ Arquitectura del Sistema

SVAIA sigue una arquitectura **MVC (Modelo-Vista-Controlador)** con separación clara de responsabilidades:

```
📁 SVAIA/
├── 🎮 controllers/     # Lógica de controladores
├── 🧠 services/        # Servicios de IA y lógica de negocio
├── 📊 models/          # Modelos de datos (SQLAlchemy)
├── 🎨 templates/       # Plantillas HTML (Jinja2)
├── 🎯 static/          # Archivos estáticos (CSS, JS, imágenes)
├── 🌐 api/             # Endpoints de API REST
└── ⚙️ config/          # Configuraciones del sistema
```

### Patrones de Diseño Implementados
- **Factory Pattern**: Para la creación de la aplicación Flask
- **Service Layer**: Separación de lógica de negocio
- **Repository Pattern**: Acceso a datos a través de modelos SQLAlchemy
- **Dependency Injection**: Inyección de servicios en controladores

---

## 🛠️ Tecnologías Utilizadas

### Backend
- ![Flask](https://img.shields.io/badge/Flask-3.0.0-green) - Framework web principal
- ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.40-blue) - ORM para base de datos
- ![Flask-Login](https://img.shields.io/badge/Flask--Login-0.6.3-orange) - Gestión de autenticación
- ![PyMySQL](https://img.shields.io/badge/PyMySQL-1.1.1-red) - Conector MySQL
- ![Werkzeug](https://img.shields.io/badge/Werkzeug-3.0.1-purple) - Utilidades WSGI

### Frontend
- ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
- ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
- ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
- ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=white)

### Base de Datos
- ![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white)

### Herramientas de Desarrollo
- ![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
- ![Flask-CORS](https://img.shields.io/badge/Flask--CORS-4.0.0-lightblue) - Soporte CORS
- ![python-dotenv](https://img.shields.io/badge/python--dotenv-1.0.0-yellow) - Gestión de variables de entorno
- ![Requests](https://img.shields.io/badge/Requests-2.31.0-orange) - Cliente HTTP para APIs

### APIs Externas
- ![OpenRouter](https://img.shields.io/badge/OpenRouter-API-purple) - Gateway para modelos de IA
- ![DeepSeek](https://img.shields.io/badge/DeepSeek-v2-green) - Modelo de IA especializado

---

## 🚀 Instalación y Configuración

### Prerrequisitos
```bash
- Python 3.8+
- MySQL 8.0+
- Git
```

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd practica4
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos MySQL
```sql
-- Conectar a MySQL como root
mysql -u root -p

-- Crear base de datos
CREATE DATABASE svaia;

-- Crear usuario
CREATE USER 'alberto'@'localhost' IDENTIFIED BY 'svaia';
GRANT ALL PRIVILEGES ON svaia.* TO 'alberto'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configurar Variables de Entorno (Opcional)
Crear archivo `.env`:
```env
SECRET_KEY=tu-clave-secreta-super-segura
MYSQL_HOST=localhost
MYSQL_USER=alberto
MYSQL_PASSWORD=svaia
MYSQL_DB=svaia
```

### 6. Ejecutar la aplicación
```bash
python run.py
```

La aplicación estará disponible en: `http://localhost:5000`

---

## 🎮 Uso del Sistema

### 1. Acceso Inicial
- Navega a `http://localhost:5000`
- La página principal muestra el logo de SVAIA y las opciones disponibles

### 2. Inicio de Sesión
- Haz clic en "Login" o accede a `/login`
- Usa las credenciales por defecto (ver sección de usuarios)

### 3. Chat con IA
- Accede a `/chat` después de iniciar sesión
- Describe tu proyecto en el chat
- Recibe sugerencias automáticas sobre seguridad

### 4. Gestión de Usuarios (Solo Administradores)
- Accede a `/usuarios`
- Visualiza y gestiona todos los usuarios del sistema

---

## 📁 Estructura del Proyecto

```
practica4/
│
├── 📁 app/
│   ├── 📁 api/                 # API REST endpoints
│   ├── 📁 models/              # Modelos de datos
│   │   ├── __init__.py         # Configuración SQLAlchemy
│   │   ├── user.py             # Modelo de Usuario
│   │   ├── mensaje.py          # Modelo de Mensaje
│   │   └── proyecto.py         # Modelo de Proyecto
│   ├── 📁 views/               # Vistas principales
│   ├── __init__.py             # Factory de aplicación Flask
│   └── config.py               # Configuración de la aplicación
│
├── 📁 controllers/
│   └── message_controller.py   # Controlador de mensajes
│
├── 📁 services/
│   └── message_service.py      # Servicios de IA
│
├── 📁 templates/               # Plantillas HTML
│   ├── layout.html             # Layout base
│   ├── index.html              # Página principal
│   ├── login.html              # Página de login
│   ├── chat.html               # Interfaz de chat
│   └── usuarios.html           # Gestión de usuarios
│
├── 📁 static/                  # Archivos estáticos
│   ├── 📁 css/                 # Estilos CSS
│   ├── 📁 js/                  # JavaScript
│   └── 📁 imagenes/            # Imágenes
│
├── 📁 mysql/                   # Scripts de base de datos
├── requirements.txt            # Dependencias Python
└── run.py                      # Punto de entrada de la aplicación
```

---

## ⚙️ Funcionalidades Implementadas

### 🔐 Sistema de Autenticación
- **Login/Logout** con sesiones seguras
- **Hash de contraseñas** con Werkzeug
- **Protección CSRF** habilitada
- **Validación de contraseñas** (implementación flexible)

### 🤖 Servicios de Inteligencia Artificial

#### 1. AnimalFactsService (DeepSeek Integration)
```python
# Servicio principal que utiliza OpenRouter API con modelo DeepSeek
# Especializado en consultas de ciberseguridad y análisis de vulnerabilidades
# Incluye system prompt personalizado para respuestas especializadas
# Manejo robusto de errores con fallback messages
```

#### 2. RandomMessageService
```python
# Mensajes aleatorios de respuesta (servicio auxiliar)
```

#### 3. GreetingMessageService
```python
# Saludos automáticos (servicio auxiliar)
```

### 💬 Sistema de Chat
- **Interfaz moderna** con burbujas de conversación
- **Envío asíncrono** de mensajes
- **Respuestas automáticas** de la IA
- **Historial persistente** en sesión

### 👥 Gestión de Usuarios
- **CRUD completo** de usuarios
- **Roles y permisos** diferenciados
- **Panel de administración** intuitivo

---

## 👤 Usuarios por Defecto

El sistema crea automáticamente dos usuarios al iniciar:

### 👑 Administrador
```
Usuario: admin
Contraseña: Admin123!
Rol: Administrador
Permisos: Acceso completo al sistema
```

### 👤 Usuario Normal
```
Usuario: user
Contraseña: User123!
Rol: Usuario estándar
Permisos: Acceso al chat y funcionalidades básicas
```

---

## 🗄️ Base de Datos

### Modelo de Datos

#### Tabla: users
```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- nombre (VARCHAR(50), NOT NULL)
- apellidos (VARCHAR(100), NOT NULL)
- correo (VARCHAR(120), UNIQUE, NOT NULL)
- username (VARCHAR(80), UNIQUE, NOT NULL)
- password_hash (VARCHAR(255), NOT NULL)
- is_admin (BOOLEAN, DEFAULT FALSE)
- fecha_creacion (DATETIME, DEFAULT NOW())
- fecha_modificacion (DATETIME, DEFAULT NOW())
```

#### Tabla: mensajes
```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- contenido (TEXT, NOT NULL)
- usuario_id (INT, FOREIGN KEY)
- fecha_creacion (DATETIME, DEFAULT NOW())
```

#### Tabla: proyectos
```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- nombre (VARCHAR(100), NOT NULL)
- descripcion (TEXT)
- usuario_id (INT, FOREIGN KEY)
- fecha_creacion (DATETIME, DEFAULT NOW())
```

---

## 🌐 API Endpoints

### Autenticación
```http
POST /login              # Iniciar sesión
POST /logout             # Cerrar sesión
```

### Chat y Mensajes
```http
POST /send-message       # Enviar mensaje al chat
GET  /api/messages       # Obtener historial de mensajes
```

### Usuarios (Solo Administradores)
```http
GET  /usuarios           # Listar todos los usuarios
POST /api/users          # Crear nuevo usuario
PUT  /api/users/:id      # Actualizar usuario
DELETE /api/users/:id    # Eliminar usuario
```

### Páginas Principales
```http
GET  /                   # Página principal
GET  /chat               # Interfaz de chat
GET  /usuarios           # Gestión de usuarios
```

---

## 🎥 Demostración

### Para la Presentación en Clase

#### 1. Introducción (2 minutos)
- **Mostrar página principal** con logo y descripción
- **Explicar el propósito** del sistema SVAIA
- **Destacar las tecnologías** utilizadas

#### 2. Demostración de Funcionalidades (5 minutos)

##### Login y Autenticación
```bash
# Mostrar pantalla de login
# Iniciar sesión con usuario admin
Usuario: admin
Contraseña: Admin123!
```

##### Chat con IA
```bash
# Navegar a /chat
# Escribir: "Tengo un proyecto web en Flask, ¿qué vulnerabilidades debería considerar?"
# Mostrar respuesta automática de la IA
```

##### Panel de Administración
```bash
# Acceder a /usuarios
# Mostrar lista de usuarios
# Demostrar funcionalidades CRUD
```

#### 3. Código Destacado (3 minutos)

##### Servicio de IA
```python
# Mostrar services/message_service.py
class AnimalFactsService:
    def get_response(self, input_text):
        # Lógica de respuesta inteligente
```

##### Seguridad
```python
# Mostrar models/user.py
def set_password(self, password):
    self.password_hash = generate_password_hash(password)
```

##### Arquitectura Flask
```python
# Mostrar app/__init__.py
def create_app():
    # Factory pattern implementation
```

---

## 🗺️ Roadmap

### 🎯 Próximas Funcionalidades

#### Fase 1: Mejoras de IA
- [ ] Integración con APIs reales de vulnerabilidades (CVE)
- [ ] Análisis de código fuente automático
- [ ] Base de conocimiento ampliada

#### Fase 2: Funcionalidades Avanzadas
- [ ] Sistema de reportes PDF
- [ ] Notificaciones en tiempo real
- [ ] Dashboard de métricas de seguridad

#### Fase 3: Escalabilidad
- [ ] API REST completa
- [ ] Integración con CI/CD
- [ ] Microservicios

### 🔧 Mejoras Técnicas
- [ ] Tests unitarios y de integración
- [ ] Containerización con Docker
- [ ] Despliegue en cloud (AWS/Azure)
- [ ] Monitoreo y logging avanzado

---

## 🤝 Contribuir

### Cómo Contribuir
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Estándares de Código
- Sigue PEP 8 para Python
- Documenta las funciones importantes
- Incluye tests para nuevas funcionalidades
- Mantén el código limpio y legible

---

## 📞 Contacto y Soporte

### Equipo de Desarrollo
- **Desarrollador Principal**: Alberto
- **Email**: admin@svaia.com
- **Versión**: 1.0.0

### Reportar Problemas
- Usa el sistema de issues de GitHub
- Incluye detalles de reproducción
- Especifica versión y entorno

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- **Flask Community** por el excelente framework
- **Bootstrap** por los componentes UI
- **SQLAlchemy** por el ORM robusto
- **Profesores y compañeros** por el feedback y apoyo

---

## 🔬 Pruebas del Sistema

### Scripts de Prueba de IA
```bash
# Ejecutar pruebas de integración con OpenRouter
python3 test_ai.py

# Debug directo del servicio
python3 debug_service.py

# Probar respuestas conversacionales (verificar que no devuelve código)
python3 test_conversacion.py
```

### Ejemplos de Interacción
- **Pregunta**: "Tengo una aplicación web en Flask. ¿Qué vulnerabilidades debería considerar?"
- **Respuesta IA**: Análisis detallado de vulnerabilidades específicas de Flask (XSS, CSRF, SQLi, etc.)

- **Pregunta**: "¿Cuáles son las mejores prácticas de seguridad para MySQL?"
- **Respuesta IA**: Guía completa de hardening de bases de datos MySQL

---

## 🚨 Solución de Problemas

### Error: "Hubo un problema al procesar tu mensaje"

**Causa**: Problema de autenticación o sesión expirada

**Solución**:
1. Asegúrate de estar logueado en el sistema
2. Ve a `/login` e inicia sesión con:
   - **Admin**: `admin` / `Admin123!`
   - **Usuario**: `user` / `User123!`
3. Selecciona un proyecto antes de enviar mensajes
4. Si persiste, recarga la página

### Error: "Sesión expirada"

**Causa**: La sesión ha caducado (1 hora de inactividad)

**Solución**:
- El sistema te redirigirá automáticamente al login
- Inicia sesión nuevamente

### Error de Conexión IA

**Causa**: Problema con OpenRouter API

**Solución**:
```bash
# Verificar conectividad
python3 debug_service.py

# Verificar endpoint directo
curl -X POST http://localhost:5000/send-message \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### Proyecto no seleccionado

**Error**: "Por favor, selecciona un proyecto primero"

**Solución**:
1. Haz clic en uno de los proyectos de la barra lateral
2. El proyecto activo se resalta en azul
3. Luego puedes enviar mensajes

---

## 📊 Estadísticas del Proyecto

```
📈 Líneas de código: ~2500+
🗂️  Archivos: 22+ archivos
🛠️  Tecnologías: 12+ tecnologías
⏱️  Tiempo de desarrollo: 4 semanas
🎯 Funcionalidades: 18+ características
🤖 Integración IA: OpenRouter + DeepSeek
```

---

**¡Gracias por tu interés en SVAIA! 🛡️✨**

*Sistema de Soporte para Vulnerabilidades y Amenazas basado en Inteligencia Artificial*
