# 📁 Ejemplos para Evaluación del Profesor

Esta carpeta contiene archivos de ejemplo para probar las funcionalidades del sistema MNDefender.

## 📄 **Archivos Incluidos**

### 🔴 **Archivos Vulnerables** (para probar detección)

#### `test_vulnerabilities.py`
- **Contenido**: 5 vulnerabilidades en Python
- **Tipos**: SQL Injection, Command Injection, Weak Crypto, Deserialization, Hardcoded Credentials
- **Resultado esperado**: 5 vulnerabilidades detectadas, NO CUMPLE criterios

#### `test_javascript.js`
- **Contenido**: 4 vulnerabilidades en JavaScript
- **Tipos**: XSS, Code Injection, Prototype Pollution, Open Redirect
- **Resultado esperado**: 4 vulnerabilidades detectadas

### ✅ **Archivos Seguros** (para probar que NO detecta falsos positivos)

#### `test_secure.py`
- **Contenido**: Código Python seguro
- **Características**: Consultas parametrizadas, SHA-256, variables de entorno
- **Resultado esperado**: 0 vulnerabilidades, CUMPLE criterios

## 🎯 **Uso Recomendado**

1. **Crear proyecto** con criterios restrictivos (3 vuln máx, nivel alto, 15.0 puntos)
2. **Analizar `test_vulnerabilities.py`** → Debe NO CUMPLIR criterios
3. **Crear proyecto** con criterios permisivos (10 vuln máx, nivel crítico, 50.0 puntos)
4. **Analizar `test_secure.py`** → Debe CUMPLIR criterios
5. **Probar `test_javascript.js`** → Verificar detección multi-lenguaje

## ✅ **Verificación de CVEs Reales**

Los CVEs mostrados en los resultados son reales y pueden verificarse en:
- **NIST NVD**: https://nvd.nist.gov/vuln/search
- **CVE Details**: https://www.cvedetails.com/
- **MITRE**: https://cve.mitre.org/

Ejemplos de CVEs que aparecerán:
- `CVE-2000-1233` (SQL Injection)
- `CVE-2000-1236` (Command Injection)
- `CVE-2003-0148` (Weak Cryptography)
- `CVE-2009-3035` (Hardcoded Credentials)
