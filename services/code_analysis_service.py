import os
import tempfile
import subprocess
import json
import re
from typing import List, Dict, Any
from werkzeug.utils import secure_filename
from cve_parser import search_cve
from app.models import db
from app.models.vulnerabilidad import Vulnerabilidad, AnalisisEstatico
from app.models.criterio_aceptabilidad import CriterioAceptabilidad

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
                        cve_info = self._get_cve_details(vuln['cve_id'])
                    
                    # Crear registro de vulnerabilidad
                    vulnerabilidad = Vulnerabilidad(
                        proyecto_id=proyecto_id,
                        cve_id=vuln.get('cve_id', 'N/A'),
                        descripcion=vuln.get('description', ''),
                        severidad=severity,
                        puntuacion_cvss=vuln.get('cvss_score', 0.0),
                        archivo_afectado=original_filename,  # Usar nombre original para mostrar
                        linea_codigo=vuln.get('line', 0)
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
            # Análisis básico por patrones para diferentes lenguajes
            if language == 'python':
                vulnerabilities.extend(self._analyze_python_code(filepath, filename))
            elif language in ['javascript', 'typescript']:
                vulnerabilities.extend(self._analyze_js_code(filepath, filename))
            elif language == 'php':
                vulnerabilities.extend(self._analyze_php_code(filepath, filename))
            elif language == 'java':
                vulnerabilities.extend(self._analyze_java_code(filepath, filename))
            
            # Análisis genérico para todos los lenguajes
            vulnerabilities.extend(self._analyze_generic_patterns(filepath, filename))
            
        except Exception as e:
            print(f"Error en análisis estático: {str(e)}")
            # Retornar al menos una vulnerabilidad de error para debugging
            vulnerabilities.append({
                'cve_id': 'ERROR-001',
                'description': f'Error durante el análisis: {str(e)}',
                'severity': 'bajo',
                'cvss_score': 0.0,
                'line': 0,
                'code': 'Error de análisis'
            })
        
        return vulnerabilities
    
    def _analyze_python_code(self, filepath: str, filename: str) -> List[Dict]:
        """Análisis específico para código Python"""
        vulnerabilities = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                line_content = line.strip()
                
                # SQL Injection patterns
                if re.search(r'execute\s*\(\s*["\'].*%.*["\']', line_content, re.IGNORECASE):
                    vulnerabilities.append({
                        'cve_id': 'CVE-2023-SQL01',
                        'description': 'Posible vulnerabilidad de SQL Injection - uso de string formatting en consultas SQL',
                        'severity': 'alto',
                        'cvss_score': 8.1,
                        'line': i,
                        'code': line_content
                    })
                
                # Command Injection
                if re.search(r'(os\.system|subprocess\.call)\s*\(.*\+.*\)', line_content):
                    vulnerabilities.append({
                        'cve_id': 'CVE-2023-CMD01',
                        'description': 'Posible vulnerabilidad de Command Injection - ejecución de comandos con input concatenado',
                        'severity': 'critico',
                        'cvss_score': 9.8,
                        'line': i,
                        'code': line_content
                    })
                
                # Hardcoded credentials
                if re.search(r'(password|secret|key|api_key|access_token)\s*=\s*["\'][^"\']+["\']', line_content, re.IGNORECASE):
                    vulnerabilities.append({
                        'cve_id': 'CVE-2023-CRED01',
                        'description': 'Credenciales hardcodeadas en el código fuente',
                        'severity': 'medio',
                        'cvss_score': 5.3,
                        'line': i,
                        'code': line_content
                    })
                
                # eval() usage
                if 'eval(' in line_content:
                    vulnerabilities.append({
                        'cve_id': 'CVE-2023-EVAL01',
                        'description': 'Uso peligroso de eval() - puede permitir ejecución de código arbitrario',
                        'severity': 'alto',
                        'cvss_score': 7.5,
                        'line': i,
                        'code': line_content
                    })
                    
        except Exception as e:
            print(f"Error analizando código Python: {str(e)}")
        
        return vulnerabilities
    
    def _analyze_js_code(self, filepath: str, filename: str) -> List[Dict]:
        """Análisis específico para código JavaScript/TypeScript"""
        vulnerabilities = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                line_content = line.strip()
                
                # XSS patterns
                if re.search(r'innerHTML\s*=.*\+', line_content):
                    vulnerabilities.append({
                        'cve_id': 'CVE-2023-XSS01',
                        'description': 'Posible vulnerabilidad XSS - uso de innerHTML con concatenación',
                        'severity': 'alto',
                        'cvss_score': 6.1,
                        'line': i,
                        'code': line_content
                    })
                
                # eval() usage
                if 'eval(' in line_content:
                    vulnerabilities.append({
                        'cve_id': 'CVE-2023-EVAL01',
                        'description': 'Uso peligroso de eval() - puede permitir ejecución de código arbitrario',
                        'severity': 'alto',
                        'cvss_score': 7.5,
                        'line': i,
                        'code': line_content
                    })
                    
        except Exception as e:
            print(f"Error analizando código JavaScript: {str(e)}")
        
        return vulnerabilities
    
    def _analyze_php_code(self, filepath: str, filename: str) -> List[Dict]:
        """Análisis específico para código PHP"""
        vulnerabilities = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                line_content = line.strip()
                
                # SQL Injection
                if re.search(r'mysql_query\s*\(.*\$_', line_content):
                    vulnerabilities.append({
                        'cve_id': 'CVE-2023-SQLPHP01',
                        'description': 'Posible SQL Injection en PHP - query directa con variables superglobales',
                        'severity': 'critico',
                        'cvss_score': 9.1,
                        'line': i,
                        'code': line_content
                    })
                
                # File inclusion
                if re.search(r'(include|require).*\$_', line_content):
                    vulnerabilities.append({
                        'cve_id': 'CVE-2023-LFI01',
                        'description': 'Posible Local File Inclusion - inclusión de archivos con input del usuario',
                        'severity': 'alto',
                        'cvss_score': 7.5,
                        'line': i,
                        'code': line_content
                    })
                    
        except Exception as e:
            print(f"Error analizando código PHP: {str(e)}")
        
        return vulnerabilities
    
    def _analyze_java_code(self, filepath: str, filename: str) -> List[Dict]:
        """Análisis específico para código Java"""
        vulnerabilities = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                line_content = line.strip()
                
                # SQL Injection
                if re.search(r'Statement.*executeQuery.*\+', line_content):
                    vulnerabilities.append({
                        'cve_id': 'CVE-2023-SQLJAVA01',
                        'description': 'Posible SQL Injection en Java - concatenación en executeQuery',
                        'severity': 'alto',
                        'cvss_score': 8.1,
                        'line': i,
                        'code': line_content
                    })
                    
        except Exception as e:
            print(f"Error analizando código Java: {str(e)}")
        
        return vulnerabilities
    
    def _analyze_generic_patterns(self, filepath: str, filename: str) -> List[Dict]:
        """Análisis genérico de patrones comunes de vulnerabilidades"""
        vulnerabilities = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Buscar patrones de credenciales
            credential_patterns = [
                (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'API Key hardcodeada'),
                (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', 'Secret key hardcodeada'),
                (r'access[_-]?token\s*=\s*["\'][^"\']+["\']', 'Access token hardcodeado'),
            ]
            
            for i, line in enumerate(lines, 1):
                for pattern, description in credential_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerabilities.append({
                            'cve_id': 'CVE-2023-HARDCODED01',
                            'description': description,
                            'severity': 'medio',
                            'cvss_score': 5.0,
                            'line': i,
                            'code': line.strip()
                        })
                        
        except Exception as e:
            print(f"Error en análisis genérico: {str(e)}")
        
        return vulnerabilities
    
    def _get_cve_details(self, cve_id: str) -> Dict:
        """Obtiene detalles de un CVE usando el cve_parser"""
        try:
            # Extraer el número CVE para buscar
            if cve_id.startswith('CVE-'):
                search_term = cve_id
            else:
                search_term = f"CVE-{cve_id}"
            
            # Buscar en la base de datos de CVE
            cve_info = search_cve(search_term, limit=1)
            
            if cve_info:
                return {
                    'description': cve_info,
                    'vector': '',  # El parser no retorna vector específico
                }
        except Exception as e:
            print(f"Error buscando CVE {cve_id}: {e}")
        
        return {}
    
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
            
            for analisis in analisis_list:
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
            
            # Guardar cambios
            db.session.commit()
            
            return {
                'success': True,
                'total_reevaluados': updated_count,
                'cambios_estado': status_changes,
                'mensaje': f'Se reevaluaron {updated_count} análisis. {len(status_changes)} cambiaron de estado.'
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"Error reevaluando análisis: {str(e)}")
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