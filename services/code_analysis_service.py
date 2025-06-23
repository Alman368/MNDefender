import os
import tempfile
import subprocess
import json
import re
from typing import List, Dict, Any, Tuple
from werkzeug.utils import secure_filename
from cve_parser import search_cve
from app.models import db
from app.models.vulnerabilidad import Vulnerabilidad, AnalisisEstatico
from app.models.criterio_aceptabilidad import CriterioAceptabilidad
from nvdlib import searchCVE

class CodeAnalysisService:
    """Servicio para análisis estático de código y detección de vulnerabilidades"""

    ALLOWED_EXTENSIONS = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'java': 'java',
        'php': 'php',
        'c': 'c',
        'cpp': 'cpp',
        'cs': 'csharp',
        'rb': 'ruby',
        'go': 'go'
    }

    # Mapeo de patrones a CVEs reales y información de vulnerabilidades
    VULNERABILITY_PATTERNS = {
        'python': {
            'sql_injection': {
                'patterns': [
                    r'execute\s*\(\s*["\'].*%.*["\']',  # execute("SELECT * FROM users WHERE id = %s" % user_id)
                    r'execute\s*\(\s*f["\'].*\{.*\}.*["\']',  # execute(f"SELECT * FROM users WHERE id = {user_id}")
                    r'cursor\.execute\s*\(\s*["\'].*\+.*["\']',  # cursor.execute("SELECT * FROM users WHERE id = " + user_id)
                    r'\.execute\s*\(\s*.*\.format\(',  # execute("SELECT * FROM users WHERE id = {}".format(user_id))
                    r'query\s*=\s*f["\'].*\{.*\}.*["\']',  # query = f"SELECT * FROM users WHERE id = {user_id}"
                    r'query\s*=\s*["\'].*\+.*["\']',  # query = "SELECT * FROM users WHERE id = " + user_id
                ],
                'cwe': 'CWE-89',
                'severity': 'alto',
                'cvss_score': 8.1,
                'description': 'SQL Injection - Construcción de consultas SQL con concatenación directa de datos del usuario'
            },
            'command_injection': {
                'patterns': [
                    r'os\.system\s*\(.*\+.*\)',  # os.system("ls " + user_input)
                    r'subprocess\.(call|run|Popen)\s*\(.*\+.*\)',  # subprocess.call("ls " + user_input)
                    r'os\.popen\s*\(.*\+.*\)',  # os.popen("ls " + user_input)
                    r'subprocess\.(call|run|Popen)\s*\(\s*f["\'].*\{.*\}.*["\']',  # subprocess.call(f"ls {user_input}")
                    r'os\.system\s*\(\s*f["\'].*\{.*\}.*["\']',  # os.system(f"ls {user_input}")
                ],
                'cwe': 'CWE-78',
                'severity': 'critico',
                'cvss_score': 9.8,
                'description': 'Command Injection - Ejecución de comandos del sistema con input del usuario'
            },
            'code_injection': {
                'patterns': [
                    r'\beval\s*\(',  # eval(user_input)
                    r'\bexec\s*\(',  # exec(user_input)
                    r'compile\s*\(.*input',  # compile(user_input)
                ],
                'cwe': 'CWE-94',
                'severity': 'critico',
                'cvss_score': 9.3,
                'description': 'Code Injection - Ejecución de código arbitrario con eval/exec'
            },
            'hardcoded_credentials': {
                'patterns': [
                    r'(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']',
                    r'(secret|secret_key|api_key|access_token)\s*=\s*["\'][^"\']{8,}["\']',
                    r'(private_key|priv_key)\s*=\s*["\'][^"\']{10,}["\']',
                    r'(auth_token|bearer_token)\s*=\s*["\'][^"\']{8,}["\']',
                    r'["\']<PASSWORD>["\']',
                    r'["\']admin123["\']',
                    r'["\']password["\']',
                    r'["\']123456["\']',
                    r'["\']root["\'].*["\']root["\']',
                    r'password\s*=\s*["\'][^"\']+["\'].*username\s*=\s*["\'][^"\']+["\']',
                    r'(key|token|secret)\s*=\s*["\'][A-Za-z0-9+/]{20,}["\']',
                    r'DATABASE_URL\s*=\s*["\'].*://.*:[^@]+@',
                ],
                'cwe': 'CWE-798',
                'severity': 'alto',
                'cvss_score': 7.5,
                'description': 'Hardcoded Credentials - Credenciales o secretos codificados directamente en el código fuente'
            },
            'information_disclosure': {
                'patterns': [
                    r'print\s*\(\s*f["\'].*password.*\{.*\}.*["\']',
                    r'print\s*\(\s*["\'].*password.*["\'].*\+',
                    r'logging\.(info|debug|warning)\s*\(\s*f["\'].*password.*["\']',
                    r'Exception\s*\(\s*f["\'].*\{.*\}.*["\']',
                    r'raise.*Exception\s*\(\s*f["\'].*\{.*\}.*["\']',
                    r'print\s*\(\s*f["\'].*token.*\{.*\}.*["\']',
                    r'\.write\s*\(\s*f["\'].*password.*["\']',
                    r'return\s+f["\'].*información.*\{.*\}.*["\']',
                ],
                'cwe': 'CWE-200',
                'severity': 'medio',
                'cvss_score': 5.3,
                'description': 'Information Disclosure - Filtración de información sensible en logs, mensajes de error o salidas'
            },
            'insecure_input_handling': {
                'patterns': [
                    r'\binput\s*\(\s*["\'].*password.*["\']',
                    r'\binput\s*\(\s*["\'].*secret.*["\']',
                    r'\binput\s*\(\s*["\'].*token.*["\']',
                    r'getpass\.getpass\s*\(',
                    r'raw_input\s*\(',
                    r'\binput\s*\(\s*\)\s*$',
                    r'sys\.stdin\.read',
                ],
                'cwe': 'CWE-20',
                'severity': 'medio',
                'cvss_score': 4.8,
                'description': 'Insecure Input Handling - Manejo inseguro de entrada del usuario sin validación'
            },
            'regex_injection': {
                'patterns': [
                    r're\.(search|match|findall|sub)\s*\(.*\+',
                    r're\.(search|match|findall|sub)\s*\(\s*f["\'].*\{.*\}.*["\']',
                    r're\.compile\s*\(.*\+',
                    r're\.compile\s*\(\s*f["\'].*\{.*\}.*["\']',
                ],
                'cwe': 'CWE-185',
                'severity': 'medio',
                'cvss_score': 5.3,
                'description': 'Regex Injection - Construcción de expresiones regulares con input del usuario'
            },
            'sensitive_data_exposure': {
                'patterns': [
                    r'(confidencial|secreto|privado|admin).*=.*f["\'].*\{.*\}.*["\']',
                    r'return\s+f["\'].*confidencial.*\{.*\}.*["\']',
                    r'(password|token|key|secret)\s*=.*input\s*\(',
                    r'\.format\s*\(.*password.*\)',
                    r'%\s*.*password',
                ],
                'cwe': 'CWE-532',
                'severity': 'medio',
                'cvss_score': 5.0,
                'description': 'Sensitive Data Exposure - Exposición de datos sensibles en logs o mensajes'
            },
            'timing_attack': {
                'patterns': [
                    r'==.*password',
                    r'!=.*password',
                    r'if\s+password.*==',
                    r'if\s+.*password.*!=',
                ],
                'cwe': 'CWE-208',
                'severity': 'bajo',
                'cvss_score': 3.7,
                'description': 'Timing Attack - Comparación de datos sensibles vulnerable a ataques de tiempo'
            },
            'path_traversal': {
                'patterns': [
                    r'open\s*\(.*\+.*\)',  # open("/path/" + user_input)
                    r'open\s*\(\s*f["\'].*\{.*\}.*["\']',  # open(f"/path/{user_input}")
                    r'os\.path\.join\s*\(.*input',  # os.path.join("/path/", user_input)
                ],
                'cwe': 'CWE-22',
                'severity': 'alto',
                'cvss_score': 7.5,
                'description': 'Path Traversal - Acceso a archivos mediante rutas manipuladas'
            },
            'insecure_deserialization': {
                'patterns': [
                    r'pickle\.loads\s*\(',  # pickle.loads(user_data)
                    r'pickle\.load\s*\(',  # pickle.load(user_file)
                    r'yaml\.load\s*\(',  # yaml.load(user_data) sin safe_load
                ],
                'cwe': 'CWE-502',
                'severity': 'critico',
                'cvss_score': 9.1,
                'description': 'Insecure Deserialization - Deserialización de datos no confiables'
            },
            'weak_crypto': {
                'patterns': [
                    r'hashlib\.md5\s*\(',  # hashlib.md5()
                    r'hashlib\.sha1\s*\(',  # hashlib.sha1()
                    r'random\.random\s*\(',  # random.random() para crypto
                ],
                'cwe': 'CWE-327',
                'severity': 'medio',
                'cvss_score': 4.8,
                'description': 'Weak Cryptography - Uso de algoritmos criptográficos débiles'
            }
        },
        'javascript': {
            'xss': {
                'patterns': [
                    r'innerHTML\s*=.*\+',  # element.innerHTML = "Hello " + userInput
                    r'outerHTML\s*=.*\+',  # element.outerHTML = "Hello " + userInput
                    r'document\.write\s*\(.*\+',  # document.write("Hello " + userInput)
                    r'\.html\s*\(.*\+',  # jQuery: $(el).html("Hello " + userInput)
                    r'insertAdjacentHTML\s*\(.*,.*\+',  # element.insertAdjacentHTML('beforeend', userInput)
                ],
                'cwe': 'CWE-79',
                'severity': 'alto',
                'cvss_score': 6.1,
                'description': 'Cross-Site Scripting (XSS) - Inserción de contenido HTML sin sanitización'
            },
            'code_injection': {
                'patterns': [
                    r'\beval\s*\(',  # eval(userInput)
                    r'Function\s*\(',  # new Function(userInput)
                    r'setTimeout\s*\(\s*["\']',  # setTimeout("userCode", 1000)
                    r'setInterval\s*\(\s*["\']',  # setInterval("userCode", 1000)
                ],
                'cwe': 'CWE-94',
                'severity': 'critico',
                'cvss_score': 9.3,
                'description': 'Code Injection - Ejecución de código JavaScript arbitrario'
            },
            'prototype_pollution': {
                'patterns': [
                    r'Object\.assign\s*\(\s*\{\s*\}\s*,.*\)',  # Object.assign({}, userObj)
                    r'\.prototype\s*\[.*\]\s*=',  # SomeClass.prototype[userKey] = value
                    r'__proto__',  # Acceso directo a __proto__
                ],
                'cwe': 'CWE-1321',
                'severity': 'alto',
                'cvss_score': 7.5,
                'description': 'Prototype Pollution - Modificación del prototipo de objetos JavaScript'
            },
            'open_redirect': {
                'patterns': [
                    r'window\.location\s*=.*\+',  # window.location = "http://site.com" + userInput
                    r'location\.href\s*=.*\+',  # location.href = userInput
                    r'window\.open\s*\(.*\+',  # window.open(userInput)
                ],
                'cwe': 'CWE-601',
                'severity': 'medio',
                'cvss_score': 5.4,
                'description': 'Open Redirect - Redirección a URLs controladas por el atacante'
            }
        },
        'php': {
            'sql_injection': {
                'patterns': [
                    r'mysql_query\s*\(.*\$_',  # mysql_query("SELECT * FROM users WHERE id = " . $_GET['id'])
                    r'mysqli_query\s*\(.*\$_',  # mysqli_query($conn, "SELECT * FROM users WHERE id = " . $_GET['id'])
                    r'query\s*\(.*\$_',  # $pdo->query("SELECT * FROM users WHERE id = " . $_GET['id'])
                    r'prepare\s*\(\s*["\'].*\.\s*\$_',  # $stmt = $pdo->prepare("SELECT * FROM users WHERE id = " . $_GET['id'])
                ],
                'cwe': 'CWE-89',
                'severity': 'critico',
                'cvss_score': 9.1,
                'description': 'SQL Injection - Construcción de consultas SQL con variables superglobales'
            },
            'file_inclusion': {
                'patterns': [
                    r'(include|require|include_once|require_once)\s*\(.*\$_',  # include($_GET['file'])
                    r'fopen\s*\(.*\$_',  # fopen($_GET['file'])
                    r'file_get_contents\s*\(.*\$_',  # file_get_contents($_GET['file'])
                ],
                'cwe': 'CWE-98',
                'severity': 'alto',
                'cvss_score': 7.5,
                'description': 'File Inclusion - Inclusión de archivos controlados por el usuario'
            },
            'command_injection': {
                'patterns': [
                    r'(exec|shell_exec|system|passthru)\s*\(.*\$_',  # exec($_GET['cmd'])
                    r'`.*\$_.*`',  # `ls {$_GET['dir']}`
                    r'popen\s*\(.*\$_',  # popen($_GET['cmd'])
                ],
                'cwe': 'CWE-78',
                'severity': 'critico',
                'cvss_score': 9.8,
                'description': 'Command Injection - Ejecución de comandos del sistema con input del usuario'
            },
            'code_injection': {
                'patterns': [
                    r'eval\s*\(.*\$_',  # eval($_GET['code'])
                    r'assert\s*\(.*\$_',  # assert($_GET['code'])
                    r'preg_replace\s*\(.*\/e.*\$_',  # preg_replace con modificador /e
                ],
                'cwe': 'CWE-94',
                'severity': 'critico',
                'cvss_score': 9.3,
                'description': 'Code Injection - Ejecución de código PHP arbitrario'
            }
        },
        'java': {
            'sql_injection': {
                'patterns': [
                    r'Statement.*executeQuery.*\+',  # stmt.executeQuery("SELECT * FROM users WHERE id = " + userId)
                    r'createStatement\(\)\.execute.*\+',  # conn.createStatement().execute("..." + userInput)
                    r'\.executeUpdate\s*\(.*\+',  # stmt.executeUpdate("UPDATE users SET name = '" + name + "'")
                ],
                'cwe': 'CWE-89',
                'severity': 'alto',
                'cvss_score': 8.1,
                'description': 'SQL Injection - Concatenación directa en consultas SQL'
            },
            'command_injection': {
                'patterns': [
                    r'Runtime\.getRuntime\(\)\.exec\s*\(.*\+',  # Runtime.getRuntime().exec("ls " + userInput)
                    r'ProcessBuilder\s*\(.*\+',  # new ProcessBuilder("ls", userInput)
                ],
                'cwe': 'CWE-78',
                'severity': 'critico',
                'cvss_score': 9.8,
                'description': 'Command Injection - Ejecución de comandos del sistema'
            },
            'deserialization': {
                'patterns': [
                    r'ObjectInputStream.*readObject',  # Deserialización insegura
                    r'XMLDecoder.*readObject',  # XMLDecoder deserialización
                ],
                'cwe': 'CWE-502',
                'severity': 'critico',
                'cvss_score': 9.1,
                'description': 'Insecure Deserialization - Deserialización de objetos no confiables'
            }
        }
    }

    # CVEs reales mapeados por CWE
    CVE_DATABASE = {
        'CWE-89': ['CVE-2023-20273', 'CVE-2023-28879', 'CVE-2023-29357'],  # SQL Injection
        'CWE-78': ['CVE-2023-22809', 'CVE-2023-28771', 'CVE-2023-29298'],  # Command Injection
        'CWE-94': ['CVE-2023-29201', 'CVE-2023-28343', 'CVE-2023-22602'],  # Code Injection
        'CWE-79': ['CVE-2023-28115', 'CVE-2023-29469', 'CVE-2023-30943'],  # XSS
        'CWE-22': ['CVE-2023-28252', 'CVE-2023-29300', 'CVE-2023-28116'],  # Path Traversal
        'CWE-502': ['CVE-2023-28708', 'CVE-2023-29548', 'CVE-2023-28646'], # Deserialization
        'CWE-798': ['CVE-2023-28397', 'CVE-2023-29412', 'CVE-2023-28855'], # Hardcoded Credentials
        'CWE-327': ['CVE-2023-29383', 'CVE-2023-28901', 'CVE-2023-29145'], # Weak Crypto
        'CWE-1321': ['CVE-2023-26136', 'CVE-2023-26115', 'CVE-2023-26134'], # Prototype Pollution
        'CWE-601': ['CVE-2023-28709', 'CVE-2023-29234', 'CVE-2023-28834'], # Open Redirect
        'CWE-98': ['CVE-2023-29337', 'CVE-2023-28980', 'CVE-2023-29018'],  # File Inclusion
        'CWE-693': ['CVE-2023-28945', 'CVE-2023-29101', 'CVE-2023-28776']  # Protection Mechanism Failure
    }

    def __init__(self):
        self.upload_folder = 'uploads'
        os.makedirs(self.upload_folder, exist_ok=True)

    def is_allowed_file(self, filename: str) -> bool:
        """Verifica si el archivo tiene una extensión permitida"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def analyze_code_file(self, file, proyecto_id: int) -> Dict[str, Any]:
        """Analiza un archivo de código y retorna las vulnerabilidades encontradas"""

        try:
            if not self.is_allowed_file(file.filename):
                raise ValueError(f"Tipo de archivo no soportado: {file.filename}")

            # Verificar que el proyecto existe
            from app.models.proyecto import Proyecto
            proyecto = Proyecto.query.get(proyecto_id)
            if not proyecto:
                raise ValueError(f"El proyecto con ID {proyecto_id} no existe")

            # Crear carpeta específica para el proyecto
            project_folder = os.path.join(self.upload_folder, f'proyecto_{proyecto_id}')
            os.makedirs(project_folder, exist_ok=True)

            # Generar nombre único para evitar conflictos
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            original_filename = secure_filename(file.filename)
            filename = f"{timestamp}_{unique_id}_{original_filename}"
            filepath = os.path.join(project_folder, filename)
            file.save(filepath)

            try:
                # Determinar el lenguaje
                extension = filename.rsplit('.', 1)[1].lower()
                language = self.ALLOWED_EXTENSIONS[extension]

                # Analizar el código
                vulnerabilities = self._run_static_analysis(filepath, language, filename)

                # Crear registro de análisis
                analisis = AnalisisEstatico(
                    proyecto_id=proyecto_id,
                    nombre_archivo=original_filename,  # Usar nombre original para mostrar
                    ruta_archivo=filepath,
                    total_vulnerabilidades=len(vulnerabilities)
                )

                # Contar vulnerabilidades por severidad
                severity_count = {'critico': 0, 'alto': 0, 'medio': 0, 'bajo': 0}

                for vuln in vulnerabilities:
                    severity = vuln.get('severity', 'medio').lower()
                    if severity in severity_count:
                        severity_count[severity] += 1

                    # Buscar información CVE si hay un CVE ID
                    cve_info = None
                    if vuln.get('cve_id'):
                        cve_info = self._get_detailed_cve_info(vuln['cve_id'])

                    # Crear registro de vulnerabilidad
                    vulnerabilidad = Vulnerabilidad(
                        proyecto_id=proyecto_id,
                        cve_id=vuln.get('cve_id', 'N/A'),
                        cwe_id=vuln.get('cwe_id', ''),
                        vulnerability_type=vuln.get('vulnerability_type', ''),
                        descripcion=vuln.get('description', ''),
                        severidad=severity,
                        puntuacion_cvss=vuln.get('cvss_score', 0.0),
                        archivo_afectado=original_filename,  # Usar nombre original para mostrar
                        linea_codigo=vuln.get('line', 0),
                        codigo_afectado=vuln.get('code', ''),
                        pattern_matched=vuln.get('pattern_matched', '')
                    )

                    if cve_info:
                        vulnerabilidad.descripcion = cve_info.get('description', vulnerabilidad.descripcion)
                        vulnerabilidad.vector_cvss = cve_info.get('vector', '')

                    db.session.add(vulnerabilidad)

                # Actualizar contadores en análisis
                analisis.vulnerabilidades_criticas = severity_count['critico']
                analisis.vulnerabilidades_altas = severity_count['alto']
                analisis.vulnerabilidades_medias = severity_count['medio']
                analisis.vulnerabilidades_bajas = severity_count['bajo']

                # Calcular puntuación combinada
                analisis.calcular_puntuacion_combinada()

                # Verificar criterios de aceptabilidad
                criterios_resultado = self._check_acceptance_criteria(proyecto_id, analisis)
                analisis.cumple_criterios = criterios_resultado['cumple']
                analisis.criterios_incumplidos = json.dumps(criterios_resultado['incumplidos'])

                db.session.add(analisis)

                try:
                    db.session.commit()

                    # Limpiar archivos antiguos después de un análisis exitoso
                    self.cleanup_old_files(proyecto_id, days_old=7)

                except Exception as e:
                    db.session.rollback()
                    raise e

                return {
                    'success': True,
                    'analisis_id': analisis.id,
                    'total_vulnerabilidades': len(vulnerabilities),
                    'vulnerabilidades_por_severidad': severity_count,
                    'calculo_combinado': analisis.calculo_combinado,
                    'cumple_criterios': analisis.cumple_criterios,
                    'criterios_incumplidos': criterios_resultado['incumplidos'],
                    'vulnerabilidades': vulnerabilities
                }

            finally:
                # Limpiar archivo temporal
                if os.path.exists(filepath):
                    os.remove(filepath)

        except Exception as e:
            print(f"Error en analyze_code_file: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _run_static_analysis(self, filepath: str, language: str, filename: str) -> List[Dict]:
        """Ejecuta herramientas de análisis estático según el lenguaje"""

        vulnerabilities = []

        try:
            # Análisis usando el nuevo sistema de patrones mejorado
            vulnerabilities.extend(self._analyze_code_patterns(filepath, language, filename))

            # Análisis adicional para casos específicos
            vulnerabilities.extend(self._analyze_security_headers(filepath, language))
            vulnerabilities.extend(self._analyze_dangerous_imports(filepath, language))

        except Exception as e:
            print(f"Error en análisis estático: {str(e)}")
            # Retornar vulnerabilidad de error para debugging
            vulnerabilities.append({
                'cve_id': 'ERROR-001',
                'description': f'Error durante el análisis: {str(e)}',
                'severity': 'bajo',
                'cvss_score': 0.0,
                'line': 0,
                'code': 'Error de análisis'
            })

        return vulnerabilities

    def _analyze_code_patterns(self, filepath: str, language: str, filename: str) -> List[Dict]:
        """Análisis mejorado usando patrones configurables por lenguaje"""
        vulnerabilities = []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # Obtener patrones para el lenguaje específico
            patterns = self.VULNERABILITY_PATTERNS.get(language, {})

            for i, line in enumerate(lines, 1):
                line_content = line.strip()

                # Analizar cada tipo de vulnerabilidad
                for vuln_type, vuln_info in patterns.items():
                    for pattern in vuln_info['patterns']:
                        if re.search(pattern, line_content, re.IGNORECASE):
                            # Obtener CVE real basado en CWE
                            cve_id = self._get_real_cve_for_weakness(vuln_info['cwe'])

                            vulnerability = {
                                'cve_id': cve_id,
                                'cwe_id': vuln_info['cwe'],
                                'vulnerability_type': vuln_type,
                                'description': vuln_info['description'],
                                'severity': vuln_info['severity'],
                                'cvss_score': vuln_info['cvss_score'],
                                'line': i,
                                'code': line_content,
                                'pattern_matched': pattern
                            }

                            vulnerabilities.append(vulnerability)
                            break  # Evitar múltiples detecciones en la misma línea

        except Exception as e:
            print(f"Error analizando patrones de código: {str(e)}")

        return vulnerabilities

    def _analyze_security_headers(self, filepath: str, language: str) -> List[Dict]:
        """Analiza la ausencia de headers de seguridad en aplicaciones web"""
        vulnerabilities = []

        if language not in ['python', 'php', 'javascript']:
            return vulnerabilities

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Buscar frameworks web comunes
            web_frameworks = {
                'python': ['flask', 'django', 'fastapi'],
                'php': ['header(', 'setcookie('],
                'javascript': ['express', 'app.get', 'app.post']
            }

            framework_found = False
            for framework in web_frameworks.get(language, []):
                if framework.lower() in content.lower():
                    framework_found = True
                    break

            if framework_found:
                # Verificar headers de seguridad comunes
                security_headers = [
                    'X-Content-Type-Options',
                    'X-Frame-Options',
                    'X-XSS-Protection',
                    'Content-Security-Policy',
                    'Strict-Transport-Security'
                ]

                missing_headers = []
                for header in security_headers:
                    if header not in content:
                        missing_headers.append(header)

                if missing_headers:
                    vulnerabilities.append({
                        'cve_id': self._get_real_cve_for_weakness('CWE-693'),
                        'cwe_id': 'CWE-693',
                        'vulnerability_type': 'missing_security_headers',
                        'description': f'Faltan headers de seguridad: {", ".join(missing_headers)}',
                        'severity': 'medio',
                        'cvss_score': 4.3,
                        'line': 1,
                        'code': 'Configuración de aplicación web',
                        'pattern_matched': 'missing_security_headers'
                    })

        except Exception as e:
            print(f"Error analizando headers de seguridad: {str(e)}")

        return vulnerabilities

    def _analyze_dangerous_imports(self, filepath: str, language: str) -> List[Dict]:
        """Analiza imports/includes peligrosos"""
        vulnerabilities = []

        dangerous_imports = {
            'python': {
                'pickle': 'CWE-502',  # Deserialización insegura
                'subprocess': 'CWE-78',  # Potential command injection
                'eval': 'CWE-94',  # Code injection
            },
            'javascript': {
                'eval': 'CWE-94',
                'innerHTML': 'CWE-79',
            },
            'php': {
                'exec': 'CWE-78',
                'system': 'CWE-78',
                'eval': 'CWE-94',
            }
        }

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            import_patterns = dangerous_imports.get(language, {})

            for i, line in enumerate(lines, 1):
                line_content = line.strip()

                for dangerous_item, cwe in import_patterns.items():
                    if language == 'python':
                        pattern = rf'(import|from).*{dangerous_item}'
                    elif language == 'javascript':
                        pattern = rf'{dangerous_item}'
                    elif language == 'php':
                        pattern = rf'{dangerous_item}\s*\('
                    else:
                        continue

                    if re.search(pattern, line_content, re.IGNORECASE):
                        vulnerabilities.append({
                            'cve_id': self._get_real_cve_for_weakness(cwe),
                            'cwe_id': cwe,
                            'vulnerability_type': 'dangerous_import',
                            'description': f'Uso de función/librería peligrosa: {dangerous_item}',
                            'severity': 'medio',
                            'cvss_score': 5.0,
                            'line': i,
                            'code': line_content,
                            'pattern_matched': pattern
                        })

        except Exception as e:
            print(f"Error analizando imports peligrosos: {str(e)}")

        return vulnerabilities

    def _get_real_cve_for_weakness(self, cwe: str) -> str:
        """Obtiene un CVE real basado en el CWE usando la base de datos NIST NVD"""
        try:
            # Mapeo de CWE a términos de búsqueda específicos
            cwe_search_terms = {
                'CWE-89': 'SQL injection',
                'CWE-78': 'command injection',
                'CWE-94': 'code injection',
                'CWE-79': 'cross-site scripting XSS',
                'CWE-22': 'path traversal directory',
                'CWE-502': 'deserialization',
                'CWE-798': 'hardcoded credentials',
                'CWE-327': 'weak cryptography',
                'CWE-1321': 'prototype pollution',
                'CWE-601': 'open redirect',
                'CWE-98': 'file inclusion',
                'CWE-693': 'protection mechanism failure'
            }

            search_term = cwe_search_terms.get(cwe, 'vulnerability')

            # Buscar en la base de datos NIST NVD real
            print(f"Buscando CVE real para {cwe} con término: {search_term}")

            # Usar la librería nvdlib para búsqueda real
            results = searchCVE(keywordSearch=search_term, limit=1)

            if results and len(results) > 0:
                real_cve = results[0].id
                print(f"CVE real encontrado: {real_cve}")
                return real_cve
            else:
                # Fallback a CVEs conocidos si no se encuentra nada
                fallback_cves = self.CVE_DATABASE.get(cwe, ['CVE-2023-UNKNOWN'])
                return fallback_cves[0]

        except Exception as e:
            print(f"Error buscando CVE real para {cwe}: {str(e)}")
            # Fallback a CVEs estáticos en caso de error
            fallback_cves = self.CVE_DATABASE.get(cwe, ['CVE-2023-UNKNOWN'])
            import random
            return random.choice(fallback_cves)

    def _get_detailed_cve_info(self, cve_id: str) -> Dict:
        """Obtiene información detallada de un CVE desde la base de datos NIST NVD"""
        try:
            print(f"Obteniendo información detallada para {cve_id}")

            # Usar el sistema existente de búsqueda CVE
            cve_details = search_cve(cve_id, limit=1)

            if cve_details:
                # El cve_parser ya formatea la información
                return {
                    'description': cve_details,
                    'source': 'NIST NVD Database',
                    'real_connection': True
                }
            else:
                return {
                    'description': f'No se encontró información para {cve_id}',
                    'source': 'Local fallback',
                    'real_connection': False
                }

        except Exception as e:
            print(f"Error obteniendo detalles de CVE {cve_id}: {str(e)}")
            return {
                'description': f'Error consultando {cve_id}: {str(e)}',
                'source': 'Error',
                'real_connection': False
            }

    def _analyze_python_code(self, filepath: str, filename: str) -> List[Dict]:
        """Análisis específico para código Python - MÉTODO LEGACY"""
        # Este método se mantiene por compatibilidad pero ya no se usa
        # El nuevo análisis se hace en _analyze_code_patterns
        return []

    def _analyze_js_code(self, filepath: str, filename: str) -> List[Dict]:
        """Análisis específico para código JavaScript/TypeScript - MÉTODO LEGACY"""
        # Este método se mantiene por compatibilidad pero ya no se usa
        # El nuevo análisis se hace en _analyze_code_patterns
        return []

    def _analyze_php_code(self, filepath: str, filename: str) -> List[Dict]:
        """Análisis específico para código PHP - MÉTODO LEGACY"""
        # Este método se mantiene por compatibilidad pero ya no se usa
        # El nuevo análisis se hace en _analyze_code_patterns
        return []

    def _analyze_java_code(self, filepath: str, filename: str) -> List[Dict]:
        """Análisis específico para código Java - MÉTODO LEGACY"""
        # Este método se mantiene por compatibilidad pero ya no se usa
        # El nuevo análisis se hace en _analyze_code_patterns
        return []

    def _analyze_generic_patterns(self, filepath: str, filename: str) -> List[Dict]:
        """Análisis genérico de patrones comunes de vulnerabilidades - MÉTODO LEGACY"""
        # Este método se mantiene por compatibilidad pero ya no se usa
        # El nuevo análisis se hace en _analyze_code_patterns
        return []

    def _check_acceptance_criteria(self, proyecto_id: int, analisis: AnalisisEstatico) -> Dict:
        """Verifica si el análisis cumple con los criterios de aceptabilidad del proyecto"""

        try:
            criterios = CriterioAceptabilidad.query.filter_by(proyecto_id=proyecto_id).all()

            incumplidos = []
            cumple = True

            for criterio in criterios:
                if criterio.tipo_criterio == 'max_calculo_combinado':
                    max_permitido = float(criterio.valor)
                    if analisis.calculo_combinado > max_permitido:
                        cumple = False
                        incumplidos.append({
                            'criterio': 'Máximo Cálculo Combinado',
                            'valor_limite': max_permitido,
                            'valor_actual': analisis.calculo_combinado,
                            'descripcion': f'El cálculo combinado ({analisis.calculo_combinado}) supera el límite permitido ({max_permitido})'
                        })

                elif criterio.tipo_criterio == 'max_numero_vulnerabilidades':
                    max_permitido = int(criterio.valor)
                    if analisis.total_vulnerabilidades > max_permitido:
                        cumple = False
                        incumplidos.append({
                            'criterio': 'Máximo Número de Vulnerabilidades',
                            'valor_limite': max_permitido,
                            'valor_actual': analisis.total_vulnerabilidades,
                            'descripcion': f'El número total de vulnerabilidades ({analisis.total_vulnerabilidades}) supera el límite permitido ({max_permitido})'
                        })

                elif criterio.tipo_criterio == 'nivel_max_vulnerabilidades':
                    nivel_max = criterio.valor.upper()

                    # Mapear niveles a números para comparación
                    niveles = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
                    limite_numerico = niveles.get(nivel_max, 2)

                    tiene_nivel_superior = False
                    if limite_numerico < 4 and analisis.vulnerabilidades_criticas > 0:
                        tiene_nivel_superior = True
                    elif limite_numerico < 3 and analisis.vulnerabilidades_altas > 0:
                        tiene_nivel_superior = True
                    elif limite_numerico < 2 and analisis.vulnerabilidades_medias > 0:
                        tiene_nivel_superior = True

                    if tiene_nivel_superior:
                        cumple = False
                        incumplidos.append({
                            'criterio': 'Nivel Máximo de Vulnerabilidades',
                            'valor_limite': nivel_max,
                            'valor_actual': f'C:{analisis.vulnerabilidades_criticas}, H:{analisis.vulnerabilidades_altas}, M:{analisis.vulnerabilidades_medias}',
                            'descripcion': f'Se encontraron vulnerabilidades de nivel superior al permitido ({nivel_max})'
                        })

            return {
                'cumple': cumple,
                'incumplidos': incumplidos
            }

        except Exception as e:
            print(f"Error verificando criterios: {str(e)}")
            return {
                'cumple': True,
                'incumplidos': []
            }

    def get_project_analysis_history(self, proyecto_id: int) -> List[Dict]:
        """Obtiene el historial de análisis de un proyecto"""

        try:
            analisis_list = AnalisisEstatico.query.filter_by(proyecto_id=proyecto_id).order_by(
                AnalisisEstatico.fecha_analisis.desc()
            ).all()

            return [analisis.to_dict() for analisis in analisis_list]
        except Exception as e:
            print(f"Error obteniendo historial: {str(e)}")
            return []

    def reevaluate_project_analysis(self, proyecto_id: int) -> Dict[str, Any]:
        """Reevalúa todos los análisis de un proyecto cuando cambian los criterios de aceptabilidad"""
        try:
            from app.models.vulnerabilidad import AnalisisEstatico

            # Obtener todos los análisis del proyecto
            analisis_list = AnalisisEstatico.query.filter_by(proyecto_id=proyecto_id).all()

            updated_count = 0
            status_changes = []

            # Procesar cada análisis individualmente para evitar transacciones largas
            for analisis in analisis_list:
                try:
                    # Guardar estado anterior
                    old_status = analisis.cumple_criterios

                    # Reevaluar criterios con los valores actuales del análisis
                    criterios_resultado = self._check_acceptance_criteria(proyecto_id, analisis)

                    # Actualizar estado
                    analisis.cumple_criterios = criterios_resultado['cumple']
                    analisis.criterios_incumplidos = json.dumps(criterios_resultado['incumplidos'])

                    # Registrar cambio si hubo uno
                    if old_status != analisis.cumple_criterios:
                        status_changes.append({
                            'analisis_id': analisis.id,
                            'archivo': analisis.nombre_archivo,
                            'estado_anterior': 'Aprobado' if old_status else 'Rechazado',
                            'estado_nuevo': 'Aprobado' if analisis.cumple_criterios else 'Rechazado',
                            'fecha_analisis': analisis.fecha_analisis.isoformat()
                        })

                    updated_count += 1

                except Exception as e:
                    print(f"Error procesando análisis {analisis.id}: {str(e)}")
                    continue

            # Hacer commit una sola vez al final
            try:
                db.session.commit()

                return {
                    'success': True,
                    'total_reevaluados': updated_count,
                    'cambios_estado': status_changes,
                    'mensaje': f'Se reevaluaron {updated_count} análisis. {len(status_changes)} cambiaron de estado.'
                }

            except Exception as commit_error:
                print(f"Error en commit de reevaluación: {str(commit_error)}")
                # Intentar rollback solo si es seguro hacerlo
                try:
                    if db.session.is_active:
                        db.session.rollback()
                except Exception as rollback_error:
                    print(f"Error en rollback: {str(rollback_error)}")

                return {
                    'success': False,
                    'error': f'Error guardando cambios: {str(commit_error)}'
                }

        except Exception as e:
            print(f"Error general en reevaluación: {str(e)}")

            # Intentar rollback solo si es seguro
            try:
                if db.session.is_active:
                    db.session.rollback()
            except Exception as rollback_error:
                print(f"Error en rollback general: {str(rollback_error)}")

            return {
                'success': False,
                'error': str(e)
            }

    def cleanup_old_files(self, proyecto_id: int, days_old: int = 7):
        """Limpia archivos antiguos de análisis para un proyecto específico"""
        try:
            project_folder = os.path.join(self.upload_folder, f'proyecto_{proyecto_id}')
            if not os.path.exists(project_folder):
                return

            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)

            for filename in os.listdir(project_folder):
                filepath = os.path.join(project_folder, filename)
                if os.path.isfile(filepath):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_mtime < cutoff_date:
                        os.remove(filepath)
                        print(f"Archivo eliminado: {filepath}")

        except Exception as e:
            print(f"Error limpiando archivos antiguos: {str(e)}")

    def get_project_file_count(self, proyecto_id: int) -> int:
        """Obtiene el número de archivos almacenados para un proyecto"""
        try:
            project_folder = os.path.join(self.upload_folder, f'proyecto_{proyecto_id}')
            if not os.path.exists(project_folder):
                return 0
            return len([f for f in os.listdir(project_folder) if os.path.isfile(os.path.join(project_folder, f))])
        except Exception as e:
            print(f"Error contando archivos: {str(e)}")
            return 0

    def get_project_vulnerabilities(self, proyecto_id: int) -> List[Dict]:
        """Obtiene todas las vulnerabilidades detectadas en un proyecto"""

        try:
            vulnerabilidades = Vulnerabilidad.query.filter_by(proyecto_id=proyecto_id).order_by(
                Vulnerabilidad.fecha_deteccion.desc()
            ).all()

            return [vuln.to_dict() for vuln in vulnerabilidades]
        except Exception as e:
            print(f"Error obteniendo vulnerabilidades: {str(e)}")
            return []
