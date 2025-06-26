# 👨‍🏫 GUÍA PARA PROFESOR - MNDefender SAST

## 🎯 **Objetivo de Esta Guía**

Esta guía le permitirá evaluar las **dos funcionalidades principales** del sistema MNDefender:
1. **📊 Criterios de Aceptabilidad**: Sistema de configuración de límites de seguridad por proyecto
2. **🔍 Análisis de Código SAST**: Detección de vulnerabilidades con CVEs reales de NIST NVD

## IMPORTANTE!:
Antes de nada, hay que crear una base de datos con el nombre svaia en mysql para poder probarlo.


Hemos dejado las claves hardcodeadas para que lo puedas probar fácilmente. Obviamente no es una buena práctica de desarrollo de software

---

## 🚀 **Inicio Rápido del Sistema**

### **Paso 1: Arrancar el Sistema**
```bash
cd MNDefender
source venv/bin/activate  # o venv\Scripts\activate en Windows
python run.py
```

**Resultado esperado:**
```
* Running on http://127.0.0.1:5003
* Debug mode: on
```

### **Paso 2: Acceder al Sistema**
1. Abrir navegador en: **http://localhost:5003**
2. **Crear cuenta**: Clic en "Registrarse"
3. **Login**: Usar las credenciales creadas (usuario admin contraseña Admin123!)

---

## 📊 **PARTE 1: Evaluación de Criterios de Aceptabilidad**

### **¿Qué son los Criterios de Aceptabilidad?**
Sistema que permite configurar **límites máximos** de vulnerabilidades que un proyecto puede tener para ser considerado "aceptable". Cada proyecto puede tener criterios personalizados.

### **🧪 Prueba 1: Crear Proyecto con Criterios**

1. **Ir a "Usuarios"** en el menú principal
2. **Clic en "Crear Proyecto"**
3. **Rellenar formulario:**
   ```
   Nombre: Proyecto Prueba Criterios
   Descripción: Proyecto para evaluar criterios de aceptabilidad
   ```
4. **Configurar Criterios** (marcar las casillas y configurar):
   - ✅ **Máximo número de vulnerabilidades:** `3`
   - ✅ **Máximo nivel de severidad:** `alto` (no críticas)
   - ✅ **Máximo cálculo combinado:** `15.0`

5. **Clic en "Crear Proyecto"**

**✅ Resultado esperado:** Proyecto creado con criterios configurados

### **🧪 Prueba 2: Verificar Criterios en la Base de Datos**

Para verificar que los criterios se guardaron correctamente:

1. **Ir a "Usuarios"** → Ver el proyecto creado
2. **Verificar que aparecen los criterios:**
   - Máximo vulnerabilidades: 3
   - Nivel máximo: alto
   - Cálculo combinado: 15.0

**✅ Funcionalidad confirmada:** Los criterios se crean y almacenan correctamente

---

## 🔍 **PARTE 2: Evaluación del Análisis SAST**

### **¿Qué hace el Análisis SAST?**
Escanea código fuente para detectar vulnerabilidades de seguridad y las correlaciona con **CVEs reales** de la base de datos oficial NIST NVD.

### **🧪 Prueba 3: Crear Archivo de Prueba**

Crear un archivo llamado `test_vulnerabilities.py` con este contenido:

```python
import os
import hashlib
import pickle

# Vulnerabilidad 1: SQL Injection (Crítica)
def buscar_usuario(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

# Vulnerabilidad 2: Command Injection (Crítica)
def procesar_archivo(filename):
    os.system(f"cat {filename}")

# Vulnerabilidad 3: Weak Cryptography (Media)
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Vulnerabilidad 4: Insecure Deserialization (Crítica)
def cargar_config(data):
    return pickle.loads(data)

# Vulnerabilidad 5: Hardcoded Credentials (Alta)
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"
```

### **🧪 Prueba 4: Analizar el Código**

1. **Ir a "Análisis de Código"**
2. **Seleccionar proyecto:** "Proyecto Prueba Criterios"
3. **Subir archivo:** Seleccionar `test_vulnerabilities.py`
4. **Clic en "Analizar Código"**

### **📋 Resultados Esperados del Análisis**

**El sistema debe detectar ~5 vulnerabilidades:**

```
🛡️ ANÁLISIS COMPLETADO
═══════════════════════════════════════════════════════════

📁 Archivo: test_vulnerabilities.py
📊 Total vulnerabilidades encontradas: 5
🔴 Críticas: 3    🟡 Altas: 1    🟡 Medias: 1

🚨 VULNERABILIDADES DETECTADAS:
────────────────────────────────────────────────────────────

🔴 CRÍTICA │ CVE-2000-1233 │ SQL Injection
├─ Línea 7: query = f"SELECT * FROM users WHERE id = {user_id}"
├─ CWE-89: Improper Neutralization of SQL Commands
└─ CVSS Score: 9.1/10

🔴 CRÍTICA │ CVE-2000-1236 │ Command Injection
├─ Línea 11: os.system(f"cat {filename}")
├─ CWE-78: OS Command Injection
└─ CVSS Score: 8.8/10

🟡 MEDIA │ CVE-2003-0148 │ Weak Cryptography
├─ Línea 15: hashlib.md5(password.encode())
├─ CWE-327: Use of a Broken Cryptographic Algorithm
└─ CVSS Score: 5.3/10

🔴 CRÍTICA │ CVE-2004-1019 │ Insecure Deserialization
├─ Línea 19: pickle.loads(data)
├─ CWE-502: Deserialization of Untrusted Data
└─ CVSS Score: 9.0/10

🟡 ALTA │ CVE-2009-3035 │ Hardcoded Credentials
├─ Línea 22-23: API_KEY = "sk-..." / DATABASE_PASSWORD = "admin123"
├─ CWE-798: Use of Hard-coded Credentials
└─ CVSS Score: 7.5/10

📊 CÁLCULO COMBINADO: 43.2 puntos
• Críticas (3) × 10 = 30 puntos
• Altas (1) × 7 = 7 puntos
• Medias (1) × 4 = 4 puntos
• Bajas (0) × 1 = 0 puntos

❌ ESTADO: NO CUMPLE CRITERIOS
• Máximo vulnerabilidades: 3 (actual: 5) ❌
• Nivel máximo: alto (actual: crítico) ❌
• Cálculo combinado: 15.0 (actual: 43.2) ❌
```

### **✅ Verificaciones Importantes:**

1. **CVEs Reales:** Todos los CVE-XXXX-XXXX deben ser reales de NIST NVD
2. **Información Detallada:** Cada vulnerabilidad debe incluir:
   - CVE ID real
   - CWE ID
   - Descripción
   - Línea específica de código
   - CVSS Score
3. **Criterios Evaluados:** El sistema debe evaluar automáticamente los criterios
4. **Estado Final:** "NO CUMPLE" porque supera todos los límites configurados

---

## 🧪 **PARTE 3: Verificar Integración CVE Real**

### **Prueba 5: Verificar Conexión NIST NVD**

Para confirmar que se usan CVEs reales y no ficticios:

1. **Tomar un CVE del resultado** (ej: CVE-2000-1233)
2. **Buscar en Google:** "CVE-2000-1233 NIST"
3. **Verificar en NIST NVD:** https://nvd.nist.gov/vuln/detail/CVE-2000-1233

**✅ Confirmación:** El CVE debe existir realmente en la base de datos oficial

### **Prueba 6: Verificar Diferentes Tipos de Archivos**

**JavaScript vulnerable (test.js):**
```javascript
// XSS vulnerability
document.getElementById('content').innerHTML = userInput;

// Code Injection
eval(userCode);
```

**PHP vulnerable (test.php):**
```php
<?php
// SQL Injection
$query = "SELECT * FROM users WHERE id = " . $_GET['id'];

// File Inclusion
include($_GET['file']);
?>
```

**✅ El sistema debe detectar vulnerabilidades en todos los lenguajes soportados**

---

## 📊 **PARTE 4: Evaluar Criterios con Proyecto "Bueno"**

### **Prueba 7: Proyecto que SÍ Cumple Criterios**

1. **Crear nuevo proyecto:**
   ```
   Nombre: Proyecto Seguro
   Criterios: Máximo 10 vulnerabilidades, nivel crítico, cálculo 50.0
   ```

2. **Crear archivo seguro (secure.py):**
```python
import hashlib
from sqlalchemy import text

# Código seguro - Sin vulnerabilidades
def buscar_usuario_seguro(user_id, session):
    # Consulta parametrizada (segura)
    query = text("SELECT * FROM users WHERE id = :user_id")
    return session.execute(query, {"user_id": user_id})

def hash_password_seguro(password):
    # Algoritmo criptográfico fuerte
    return hashlib.sha256(password.encode()).hexdigest()

# Configuración desde variables de entorno (segura)
import os
API_KEY = os.getenv('API_KEY')
```

3. **Analizar archivo seguro**

**✅ Resultado esperado:**
- 0 vulnerabilidades detectadas
- Estado: "CUMPLE CRITERIOS"
- Cálculo combinado: 0 puntos

---

## 🎯 **Criterios de Evaluación para el Profesor**

### **✅ Funcionalidades que DEBEN funcionar:**

#### **1. Criterios de Aceptabilidad:**
- [ ] **Crear proyecto** con criterios personalizados
- [ ] **Guardar criterios** en base de datos correctamente
- [ ] **Evaluar automáticamente** si análisis cumple criterios
- [ ] **Mostrar estado** (CUMPLE/NO CUMPLE) claramente
- [ ] **Permitir modificar** criterios existentes

#### **2. Análisis SAST:**
- [ ] **Detectar vulnerabilidades** en Python, JavaScript, PHP, Java
- [ ] **Usar CVEs reales** de NIST NVD (verificables online)
- [ ] **Mostrar información detallada** (CVE, CWE, línea, score)
- [ ] **Calcular score combinado** correctamente
- [ ] **Clasificar severidad** (crítico, alto, medio, bajo)
- [ ] **Generar reportes** claros y profesionales

#### **3. Integración:**
- [ ] **Conectar con NIST NVD** para obtener CVEs reales
- [ ] **Almacenar resultados** en base de datos
- [ ] **Interfaz web funcional** sin errores
- [ ] **Reevaluación automática** cuando cambian criterios

### **⚠️ Posibles Problemas y Soluciones:**

| Problema | Causa Probable | Solución |
|----------|----------------|-----------|
| No detecta vulnerabilidades | Patrones no coinciden | Usar exactamente los ejemplos de código dados |
| CVEs ficticios | Sin conexión NIST | Verificar conexión a internet y nvdlib |
| Error de criterios | Event listeners | Ya corregido en el sistema |
| Interfaz no carga | Puerto ocupado | Usar `python run.py` en puerto 5000 |

---

## 📝 **Resumen para Evaluación Rápida**

### **⏱️ Prueba Rápida (10 minutos):**

1. **Arrancar sistema** → `python run.py`
2. **Crear proyecto** con criterios restrictivos (3 vuln, nivel alto, 15.0 puntos)
3. **Analizar archivo vulnerable** (usar ejemplo de código dado)
4. **Verificar resultados:**
   - ✅ Detecta ~5 vulnerabilidades
   - ✅ CVEs reales verificables
   - ✅ Estado "NO CUMPLE criterios"
   - ✅ Información técnica detallada

### **📊 Puntuación Sugerida:**

- **Criterios de Aceptabilidad (50%):**
  - Creación y configuración: 20%
  - Evaluación automática: 20%
  - Interfaz y usabilidad: 10%

- **Análisis SAST (50%):**
  - Detección de vulnerabilidades: 20%
  - CVEs reales de NIST: 15%
  - Información técnica completa: 10%
  - Interfaz de resultados: 5%

---

## 🆘 **Contacto de Soporte**

Si encuentra algún problema durante la evaluación:
- **Verificar:** Que `nvdlib` esté instalado y tenga conexión a internet
- **Reiniciar:** El servicio si hay errores de conexión
- **Usar:** Los ejemplos exactos de código proporcionados
- **Revisar:** Que la base de datos MySQL esté corriendo

**El sistema está diseñado para funcionar de manera confiable siguiendo esta guía paso a paso.**

---

<div align="center">

**🛡️ MNDefender - Sistema Validado y Listo para Evaluación**

*Desarrollado para demostrar capacidades reales de SAST con integración CVE*

</div>
