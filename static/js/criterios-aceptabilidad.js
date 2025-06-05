/**
 * Módulo para manejar Criterios de Aceptabilidad
 * Funcionalidad completa para agregar, editar y gestionar criterios en proyectos
 */

class CriteriosAceptabilidad {
    constructor() {
        this.criteriosTemporales = [];
        this.tiposCriterios = {};
        this.modoActual = 'create'; // 'create' o 'edit'
        this.proyectoActualId = null;
        this.init();
    }

    async init() {
        await this.cargarTiposCriterios();
        this.configurarEventos();
        this.interceptarFormularios();
        this.inicializarTooltips();
    }

    async cargarTiposCriterios() {
        try {
            const response = await fetch('/api/criterios/tipos');
            if (response.ok) {
                this.tiposCriterios = await response.json();
                this.llenarSelectTiposCriterios();
            } else {
                console.error('Error al cargar tipos de criterios:', response.statusText);
            }
        } catch (error) {
            console.error('Error al cargar tipos de criterios:', error);
        }
    }

    llenarSelectTiposCriterios() {
        const select = document.getElementById('tipoCriterio');
        if (!select) return;
        
        select.innerHTML = '<option value="">Seleccione un criterio...</option>';
        
        Object.keys(this.tiposCriterios).forEach(key => {
            const criterio = this.tiposCriterios[key];
            const option = document.createElement('option');
            option.value = key;
            option.textContent = criterio.nombre;
            select.appendChild(option);
        });
    }

    configurarEventos() {
        // Cambio en el tipo de criterio
        const tipoCriterioSelect = document.getElementById('tipoCriterio');
        if (tipoCriterioSelect) {
            tipoCriterioSelect.addEventListener('change', (e) => {
                this.actualizarCampoValor(e.target.value);
            });
        }

        // Agregar criterio
        const btnAgregar = document.getElementById('btnAgregarCriterio');
        if (btnAgregar) {
            btnAgregar.addEventListener('click', () => this.agregarCriterio());
        }

        // Guardar criterios
        const btnGuardar = document.getElementById('btnGuardarCriterios');
        if (btnGuardar) {
            btnGuardar.addEventListener('click', () => this.guardarCriterios());
        }

        // Configurar botones para abrir modal
        const btnAddCreate = document.getElementById('btnAddCriteriosCreate');
        if (btnAddCreate) {
            btnAddCreate.addEventListener('click', () => {
                this.modoActual = 'create';
                this.proyectoActualId = null;
                this.abrirModalCriterios();
            });
        }

        const btnAddEdit = document.getElementById('btnAddCriteriosEdit');
        if (btnAddEdit) {
            btnAddEdit.addEventListener('click', () => {
                this.modoActual = 'edit';
                this.proyectoActualId = this.obtenerProyectoActualId();
                this.abrirModalCriterios();
            });
        }

        // Al cerrar el modal, limpiar datos
        const modal = document.getElementById('criteriosModal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', () => {
                this.limpiarModalCriterios();
            });
        }

        // Configurar eventos para proyectos
        this.configurarEventosProyectos();
        
        // Configurar eventos para botones de acción
        this.configurarEventosBotones();
    }

    configurarEventosProyectos() {
        const proyectoItems = document.querySelectorAll('.item-proyecto');
        proyectoItems.forEach((item) => {
            item.addEventListener('click', (e) => {
                // Solo manejar el clic si no viene de un botón
                if (e.target.closest('button')) {
                    return;
                }
                
                e.preventDefault();
                
                // Obtener ID del proyecto
                const id = item.dataset.id;
                if (!id) {
                    console.error('El elemento seleccionado no tiene un data-id válido');
                    return;
                }

                // Actualizar proyecto activo
                proyectoItems.forEach(p => p.classList.remove('active'));
                item.classList.add('active');

                // Cargar mensajes del proyecto
                if (window.cargarMensajesProyecto) {
                    window.cargarMensajesProyecto(id);
                }
            });
        });
    }

    configurarEventosBotones() {
        // Botones de información
        document.addEventListener('click', (e) => {
            // Verificar si el clic fue en el SVG de información o en alguno de sus elementos path
            const infoIcon = e.target.closest('.btn-info-proyecto') ||
                           (e.target.tagName === 'path' && e.target.parentNode.classList.contains('btn-info-proyecto'));
            
            if (infoIcon) {
                e.preventDefault();
                e.stopPropagation();
                
                const proyectoId = infoIcon.dataset ? infoIcon.dataset.proyectoId : 
                                  infoIcon.parentNode.dataset.proyectoId;
                this.mostrarInfoProyecto(proyectoId);
            }
            
            // Botones de editar
            const editIcon = e.target.closest('.btn-edit-proyecto') ||
                           (e.target.tagName === 'path' && e.target.parentNode.classList.contains('btn-edit-proyecto'));
            
            if (editIcon) {
                e.preventDefault();
                e.stopPropagation();
                
                const proyectoId = editIcon.dataset ? editIcon.dataset.proyectoId : 
                                  editIcon.parentNode.dataset.proyectoId;
                this.editarProyecto(proyectoId);
            }
            
            // Botones de eliminar
            const deleteIcon = e.target.closest('.btn-delete-proyecto') ||
                             (e.target.tagName === 'path' && e.target.parentNode.classList.contains('btn-delete-proyecto'));
            
            if (deleteIcon) {
                e.preventDefault();
                e.stopPropagation();
                
                const proyectoId = deleteIcon.dataset ? deleteIcon.dataset.proyectoId : 
                                  deleteIcon.parentNode.dataset.proyectoId;
                this.eliminarProyecto(proyectoId);
            }
        });
    }

    obtenerProyectoActualId() {
        // Obtener el ID del proyecto activo o en edición
        const proyectoActivo = document.querySelector('.item-proyecto.active');
        return proyectoActivo ? proyectoActivo.getAttribute('data-id') : null;
    }

    actualizarCampoValor(tipo) {
        const container = document.getElementById('valorCriterioContainer');
        if (!container) return;
        
        const criterio = this.tiposCriterios[tipo];
        
        if (!criterio) {
            container.innerHTML = '<input type="text" class="form-control" id="valorCriterio" placeholder="Ingrese el valor">';
            return;
        }

        let inputHtml = '';
        if (criterio.tipo_valor === 'select') {
            inputHtml = '<select class="form-select" id="valorCriterio">';
            inputHtml += '<option value="">Seleccione...</option>';
            criterio.opciones.forEach(opcion => {
                inputHtml += `<option value="${opcion}">${opcion.charAt(0).toUpperCase() + opcion.slice(1)}</option>`;
            });
            inputHtml += '</select>';
        } else if (criterio.tipo_valor === 'number') {
            const min = criterio.min || 0;
            const max = criterio.max || '';
            inputHtml = `<input type="number" class="form-control" id="valorCriterio" 
                        placeholder="Ingrese el valor" min="${min}" ${max ? `max="${max}"` : ''}>`;
        } else {
            inputHtml = '<input type="text" class="form-control" id="valorCriterio" placeholder="Ingrese el valor">';
        }
        
        container.innerHTML = inputHtml;
    }

    agregarCriterio() {
        const tipoCriterio = document.getElementById('tipoCriterio')?.value;
        const valorCriterio = document.getElementById('valorCriterio')?.value;

        if (!tipoCriterio || !valorCriterio) {
            this.mostrarAlerta('Por favor, seleccione un tipo de criterio y ingrese un valor.', 'warning');
            return;
        }

        // Verificar si ya existe este tipo de criterio
        const yaExiste = this.criteriosTemporales.some(c => c.tipo_criterio === tipoCriterio);
        if (yaExiste) {
            this.mostrarAlerta('Este tipo de criterio ya ha sido agregado. Elimínelo primero si desea modificarlo.', 'warning');
            return;
        }

        const criterio = {
            tipo_criterio: tipoCriterio,
            valor: valorCriterio,
            nombre: this.tiposCriterios[tipoCriterio].nombre
        };

        this.criteriosTemporales.push(criterio);
        this.actualizarListaCriterios();
        
        // Limpiar campos
        document.getElementById('tipoCriterio').value = '';
        const valorInput = document.getElementById('valorCriterio');
        if (valorInput) valorInput.value = '';
        this.actualizarCampoValor('');

        this.mostrarAlerta('Criterio agregado exitosamente', 'success');
    }

    actualizarListaCriterios() {
        const container = document.getElementById('criteriosAgregados');
        if (!container) return;
        
        if (this.criteriosTemporales.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No hay criterios agregados</p>';
            return;
        }

        let html = '';
        this.criteriosTemporales.forEach((criterio, index) => {
            html += `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-white rounded border">
                    <div>
                        <strong>${criterio.nombre}:</strong> 
                        <span class="badge bg-primary">${criterio.valor}</span>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="window.criteriosManager.eliminarCriterio(${index})" title="Eliminar criterio">
                        <i class="bi bi-x text-danger" style="font-size: 1.2em; font-weight: bold;"></i>
                    </button>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    eliminarCriterio(index) {
        this.criteriosTemporales.splice(index, 1);
        this.actualizarListaCriterios();
        this.mostrarAlerta('Criterio eliminado', 'info');
    }

    abrirModalCriterios() {
        // Cargar criterios existentes si estamos en modo edición
        if (this.modoActual === 'edit' && this.proyectoActualId) {
            this.cargarCriteriosExistentes(this.proyectoActualId);
        } else {
            this.criteriosTemporales = [];
            this.actualizarListaCriterios();
        }
    }

    async cargarCriteriosExistentes(proyectoId) {
        try {
            const response = await fetch(`/api/proyecto/${proyectoId}/criterios`);
            if (response.ok) {
                const criterios = await response.json();
                this.criteriosTemporales = criterios.map(c => ({
                    tipo_criterio: c.tipo_criterio,
                    valor: c.valor,
                    nombre: this.tiposCriterios[c.tipo_criterio]?.nombre || c.tipo_criterio
                }));
                this.actualizarListaCriterios();
            } else {
                console.error('Error al cargar criterios existentes:', response.statusText);
            }
        } catch (error) {
            console.error('Error al cargar criterios existentes:', error);
        }
    }

    guardarCriterios() {
        // Actualizar la interfaz principal con los criterios
        const suffix = this.modoActual === 'create' ? 'Create' : 'Edit';
        const countElement = document.getElementById(`criteriosCount${suffix}`);
        const listElement = document.getElementById(`criteriosList${suffix}`);
        
        if (countElement) {
            countElement.textContent = `${this.criteriosTemporales.length} criterios agregados`;
        }
        
        if (listElement) {
            let html = '';
            if (this.criteriosTemporales.length > 0) {
                html = '<div class="mt-2">';
                this.criteriosTemporales.forEach(criterio => {
                    html += `<span class="badge bg-secondary me-1 mb-1">${criterio.nombre}: ${criterio.valor}</span>`;
                });
                html += '</div>';
            }
            listElement.innerHTML = html;
        }

        // SOLO cerrar el modal de criterios, NO el modal principal
        const modal = bootstrap.Modal.getInstance(document.getElementById('criteriosModal'));
        if (modal) {
            modal.hide();
        }

        // NO mostrar alerta aquí para evitar confusión
        console.log('Criterios configurados:', this.criteriosTemporales);
    }

    limpiarModalCriterios() {
        const tipoCriterio = document.getElementById('tipoCriterio');
        const valorCriterio = document.getElementById('valorCriterio');
        
        if (tipoCriterio) tipoCriterio.value = '';
        if (valorCriterio) valorCriterio.value = '';
        
        this.actualizarCampoValor('');
    }

    async enviarCriteriosConProyecto(proyectoId) {
        if (this.criteriosTemporales.length === 0) {
            console.log('No hay criterios para enviar');
            return true;
        }
        
        try {
            // Si estamos en modo edición, primero eliminar criterios existentes
            if (this.modoActual === 'edit') {
                console.log('Modo edición: eliminando criterios existentes primero');
                const deleteResponse = await fetch(`/api/proyecto/${proyectoId}/criterios`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (!deleteResponse.ok) {
                    console.warn('No se pudieron eliminar criterios existentes, continuando...');
                }
            }
            
            // Enviar nuevos criterios
            console.log('Enviando criterios:', this.criteriosTemporales);
            const response = await fetch(`/api/proyecto/${proyectoId}/criterios`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    criterios: this.criteriosTemporales
                })
            });

            if (!response.ok) {
                throw new Error('Error al guardar criterios');
            }

            const result = await response.json();
            console.log('Criterios guardados exitosamente:', result);
            
            return true;
        } catch (error) {
            console.error('Error al enviar criterios:', error);
            this.mostrarAlerta('Error al guardar criterios: ' + error.message, 'danger');
            return false;
        }
    }

    actualizarInterfazPrincipal() {
        // Actualizar contadores en la interfaz principal
        ['Create', 'Edit'].forEach(suffix => {
            const countElement = document.getElementById(`criteriosCount${suffix}`);
            const listElement = document.getElementById(`criteriosList${suffix}`);
            
            if (countElement) {
                countElement.textContent = '0 criterios agregados';
            }
            if (listElement) {
                listElement.innerHTML = '';
            }
        });
    }

    interceptarFormularios() {
        // Interceptar el envío del formulario de crear proyecto
        const createForm = document.getElementById('createProjectForm');
        if (createForm) {
            createForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.manejarEnvioFormulario(createForm, 'create');
            });
        }

        // Interceptar el envío del formulario de editar proyecto  
        const editForm = document.getElementById('editProjectForm');
        if (editForm) {
            editForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.manejarEnvioFormulario(editForm, 'edit');
            });
        }
    }

    async manejarEnvioFormulario(form, modo) {
        const formData = new FormData(form);
        
        try {
            let proyectoId = null;
            
            if (modo === 'create') {
                // Para crear nuevo proyecto, convertir FormData a JSON
                const proyectoData = {
                    nombre: formData.get('project_name'),
                    descripcion: formData.get('project_description')
                };
                
                const response = await fetch('/api/proyecto/crear', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(proyectoData)
                });

                if (response.ok) {
                    const result = await response.json();
                    proyectoId = result.proyecto.id;
                    this.mostrarAlerta(result.mensaje, 'success');
                } else {
                    const error = await response.json();
                    this.mostrarAlerta(error.error || 'Error al crear el proyecto', 'danger');
                    return;
                }
            } else if (modo === 'edit') {
                // Para editar proyecto existente
                proyectoId = this.proyectoActualId;
                
                const response = await fetch(`/api/proyecto/editar/${proyectoId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        nombre: formData.get('project_name'),
                        descripcion: formData.get('project_description')
                    })
                });

                if (response.ok) {
                    const result = await response.json();
                    this.mostrarAlerta(result.mensaje, 'success');
                } else {
                    const error = await response.json();
                    this.mostrarAlerta(error.error || 'Error al editar el proyecto', 'danger');
                    return;
                }
            }

            // Guardar criterios si existen
            if (proyectoId && this.criteriosTemporales.length > 0) {
                console.log('Guardando criterios:', this.criteriosTemporales);
                const criteriosGuardados = await this.enviarCriteriosConProyecto(proyectoId);
                if (!criteriosGuardados) {
                    this.mostrarAlerta('Proyecto guardado, pero hubo un error al guardar los criterios', 'warning');
                    return;
                }
            }
            
            // Mostrar mensaje de éxito y dar tiempo para verlo
            this.mostrarAlerta('Operación completada exitosamente. Recargando...', 'success');
            
            // Limpiar criterios temporales
            this.criteriosTemporales = [];
            this.actualizarInterfazPrincipal();
            
            // Cerrar modal y recargar página después de dar tiempo a leer el mensaje
            setTimeout(() => {
                // Cerrar todos los modales abiertos
                const modals = document.querySelectorAll('.modal.show');
                modals.forEach(modal => {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                });
                
                // Recargar después de un delay más largo
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            }, 2000);
            
        } catch (error) {
            console.error('Error al enviar formulario:', error);
            this.mostrarAlerta('Error al procesar el formulario: ' + error.message, 'danger');
        }
    }

    mostrarAlerta(mensaje, tipo = 'info') {
        // Crear y mostrar alerta temporal
        const alertContainer = document.createElement('div');
        alertContainer.innerHTML = `
            <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
                ${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const target = document.querySelector('.modal-body') || document.querySelector('.container');
        if (target) {
            target.insertBefore(alertContainer, target.firstChild);
            
            // Auto-remover después de 5 segundos
            setTimeout(() => {
                const alert = alertContainer.querySelector('.alert');
                if (alert) {
                    alert.remove();
                }
            }, 5000);
        }
    }

    // Método público para obtener criterios actuales
    getCriteriosTemporales() {
        return this.criteriosTemporales;
    }

    // Método público para establecer criterios
    setCriteriosTemporales(criterios) {
        this.criteriosTemporales = criterios;
        this.actualizarListaCriterios();
    }

    inicializarTooltips() {
        // Inicializar tooltips básicos de Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                html: true,
                trigger: 'hover focus'
            });
        });
    }

    async mostrarInfoProyecto(proyectoId) {
        try {
            // Cargar información del proyecto
            const response = await fetch(`/api/proyecto/${proyectoId}`);
            if (!response.ok) {
                throw new Error('Error al cargar información del proyecto');
            }
            
            const proyecto = await response.json();
            
            // Actualizar descripción
            const descElement = document.getElementById('infoProjectDescription');
            if (descElement) {
                descElement.textContent = proyecto.descripcion || 'Sin descripción disponible';
            }
            
            // Cargar criterios
            const criteriosResponse = await fetch(`/api/proyecto/${proyectoId}/criterios`);
            const criteriosElement = document.getElementById('infoProjectCriterios');
            
            if (criteriosResponse.ok) {
                const criterios = await criteriosResponse.json();
                
                if (criterios.length === 0) {
                    criteriosElement.innerHTML = '<span class="text-muted">No hay criterios definidos</span>';
                } else {
                    let criteriosHtml = '';
                    criterios.forEach(criterio => {
                        const tipoCriterio = this.tiposCriterios[criterio.tipo_criterio];
                        const nombre = tipoCriterio ? tipoCriterio.nombre : criterio.tipo_criterio;
                        criteriosHtml += `
                            <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                                <span><strong>${nombre}:</strong></span>
                                <span class="badge bg-primary">${criterio.valor}</span>
                            </div>
                        `;
                    });
                    criteriosElement.innerHTML = criteriosHtml;
                }
            } else {
                criteriosElement.innerHTML = '<span class="text-danger">Error al cargar criterios</span>';
            }
            
            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('infoProjectModal'));
            modal.show();
            
        } catch (error) {
            console.error('Error al mostrar información del proyecto:', error);
            this.mostrarAlerta('Error al cargar la información del proyecto: ' + error.message, 'danger');
        }
    }

    async editarProyecto(proyectoId) {
        try {
            // Cargar datos del proyecto
            const response = await fetch(`/api/proyecto/${proyectoId}`);
            if (!response.ok) {
                throw new Error('Error al cargar datos del proyecto');
            }
            
            const proyecto = await response.json();
            
            // Rellenar el formulario del modal con los datos actuales
            const modal = document.getElementById('editProjectModal');
            const nameInput = modal.querySelector('input[name="project_name"]');
            const descriptionInput = modal.querySelector('textarea[name="project_description"]');

            if (nameInput && descriptionInput) {
                nameInput.value = proyecto.nombre || '';
                descriptionInput.value = proyecto.descripcion || '';

                // Configurar el modo de edición
                this.modoActual = 'edit';
                this.proyectoActualId = proyectoId;
                
                // Añadir un atributo data-id al formulario
                const form = document.getElementById('editProjectForm');
                form.setAttribute('data-project-id', proyectoId);

                // Cargar criterios existentes
                console.log('Cargando criterios para proyecto:', proyectoId);
                await this.cargarCriteriosExistentes(proyectoId);
                this.actualizarInterfazEditCriterios();

                // Mostrar el modal
                const modalInstance = new bootstrap.Modal(modal);
                modalInstance.show();
            }
        } catch (error) {
            console.error('Error al editar proyecto:', error);
            this.mostrarAlerta('Error al cargar los datos del proyecto: ' + error.message, 'danger');
        }
    }

    async eliminarProyecto(proyectoId) {
        // Confirmar eliminación
        if (!confirm('¿Estás seguro de que quieres eliminar este proyecto? Esta acción no se puede deshacer.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/proyecto/eliminar/${proyectoId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Error al eliminar el proyecto');
            }
            
            // Remover el elemento del DOM
            const projectElement = document.querySelector(`.item-proyecto[data-id="${proyectoId}"]`);
            if (projectElement) {
                projectElement.remove();
            }
            
            this.mostrarAlerta('Proyecto eliminado exitosamente', 'success');
            
            // Recargar la página después de un breve delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
            
        } catch (error) {
            console.error('Error al eliminar proyecto:', error);
            this.mostrarAlerta('Error al eliminar el proyecto: ' + error.message, 'danger');
        }
    }

    actualizarInterfazEditCriterios() {
        const countElement = document.getElementById('criteriosCountEdit');
        const listElement = document.getElementById('criteriosListEdit');
        
        if (countElement) {
            countElement.textContent = `${this.criteriosTemporales.length} criterios agregados`;
        }
        
        if (listElement) {
            let html = '';
            if (this.criteriosTemporales.length > 0) {
                html = '<div class="mt-2">';
                this.criteriosTemporales.forEach(criterio => {
                    html += `<span class="badge bg-secondary me-1 mb-1">${criterio.nombre}: ${criterio.valor}</span>`;
                });
                html += '</div>';
            }
            listElement.innerHTML = html;
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.criteriosManager = new CriteriosAceptabilidad();
});

// Exportar para uso global
window.CriteriosAceptabilidad = CriteriosAceptabilidad; 