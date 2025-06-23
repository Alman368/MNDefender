from flask import request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from services.code_analysis_service import CodeAnalysisService
from app.models.proyecto import Proyecto
from app.models import db

class CodeAnalysisController:
    """Controlador para análisis estático de código"""
    
    def __init__(self):
        self.code_service = CodeAnalysisService()
    
    @login_required
    def index(self):
        """Página principal de análisis de código"""
        # Obtener proyectos del usuario
        proyectos = Proyecto.query.filter_by(usuario_id=current_user.id).all()
        
        return render_template('code_analysis.html', proyectos=proyectos)
    
    @login_required
    def upload_and_analyze(self):
        """Subir archivo y realizar análisis"""
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No se seleccionó ningún archivo'})
            
            file = request.files['file']
            proyecto_id = request.form.get('proyecto_id')
            
            if not file or file.filename == '':
                return jsonify({'success': False, 'error': 'No se seleccionó ningún archivo'})
            
            if not proyecto_id:
                return jsonify({'success': False, 'error': 'No se seleccionó ningún proyecto'})
            
            # Verificar que el proyecto pertenece al usuario
            proyecto = Proyecto.query.filter_by(id=proyecto_id, usuario_id=current_user.id).first()
            if not proyecto:
                return jsonify({'success': False, 'error': 'Proyecto no encontrado'})
            
            # Verificar tipo de archivo
            if not self.code_service.is_allowed_file(file.filename):
                return jsonify({'success': False, 'error': f'Tipo de archivo no soportado: {file.filename}'})
            
            # Realizar análisis
            resultado = self.code_service.analyze_code_file(file, int(proyecto_id))
            
            return jsonify(resultado)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @login_required
    def get_project_analysis(self, proyecto_id):
        """Obtener historial de análisis de un proyecto"""
        try:
            # Verificar que el proyecto pertenece al usuario
            proyecto = Proyecto.query.filter_by(id=proyecto_id, usuario_id=current_user.id).first()
            if not proyecto:
                return jsonify({'success': False, 'error': 'Proyecto no encontrado'})
            
            # Obtener historial de análisis
            analisis_history = self.code_service.get_project_analysis_history(int(proyecto_id))
            vulnerabilidades = self.code_service.get_project_vulnerabilities(int(proyecto_id))
            
            return jsonify({
                'success': True,
                'proyecto': proyecto.to_dict(),
                'analisis_history': analisis_history,
                'vulnerabilidades': vulnerabilidades
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @login_required
    def get_supported_languages(self):
        """Obtener lista de lenguajes soportados"""
        return jsonify({
            'success': True,
            'languages': self.code_service.ALLOWED_EXTENSIONS
        })
    
    @login_required
    def get_project_stats(self, proyecto_id):
        """Obtener estadísticas de un proyecto específico"""
        try:
            # Verificar que el proyecto pertenece al usuario
            proyecto = Proyecto.query.filter_by(id=proyecto_id, usuario_id=current_user.id).first()
            if not proyecto:
                return jsonify({'success': False, 'error': 'Proyecto no encontrado'})
            
            # Obtener estadísticas
            from app.models.vulnerabilidad import AnalisisEstatico, Vulnerabilidad
            
            total_analisis = AnalisisEstatico.query.filter_by(proyecto_id=proyecto_id).count()
            total_vulnerabilidades = Vulnerabilidad.query.filter_by(proyecto_id=proyecto_id).count()
            archivos_almacenados = self.code_service.get_project_file_count(int(proyecto_id))
            
            # Últimos análisis
            ultimo_analisis = AnalisisEstatico.query.filter_by(proyecto_id=proyecto_id)\
                .order_by(AnalisisEstatico.fecha_analisis.desc()).first()
            
            return jsonify({
                'success': True,
                'proyecto': proyecto.to_dict(),
                'estadisticas': {
                    'total_analisis': total_analisis,
                    'total_vulnerabilidades': total_vulnerabilidades,
                    'archivos_almacenados': archivos_almacenados,
                    'ultimo_analisis': ultimo_analisis.fecha_analisis.isoformat() if ultimo_analisis else None
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @login_required
    def reevaluate_project_criteria(self, proyecto_id):
        """Reevaluar todos los análisis de un proyecto tras cambiar criterios"""
        try:
            # Verificar que el proyecto pertenece al usuario
            proyecto = Proyecto.query.filter_by(id=proyecto_id, usuario_id=current_user.id).first()
            if not proyecto:
                return jsonify({'success': False, 'error': 'Proyecto no encontrado'})
            
            # Reevaluar análisis
            resultado = self.code_service.reevaluate_project_analysis(int(proyecto_id))
            
            return jsonify(resultado)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}) 