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
        this.guardandoCriterios = false; // Flag para evitar conflictos entre eventos
        this.eventListenerConfigured = false; // Flag para evitar duplicación de event listeners
        this.eliminandoProyecto = false; // Flag para evitar eliminación múltiple
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
            // Quitar atributos de Bootstrap para manejar manualmente
            btnAddCreate.removeAttribute('data-bs-toggle');
            btnAddCreate.removeAttribute('data-bs-target');
            
            btnAddCreate.addEventListener('click', (e) => {
                e.preventDefault();
                this.modoActual = 'create';
                this.proyectoActualId = null;
                this.abrirModalCriterios();
            });
        }

        const btnAddEdit = document.getElementById('btnAddCriteriosEdit');
        if (btnAddEdit) {
            // Quitar atributos de Bootstrap para manejar manualmente
            btnAddEdit.removeAttribute('data-bs-toggle');
            btnAddEdit.removeAttribute('data-bs-target');
            
            btnAddEdit.addEventListener('click', (e) => {
                e.preventDefault();
                this.modoActual = 'edit';
                this.proyectoActualId = this.obtenerProyectoActualId();
                this.abrirModalCriterios();
            });
        }

        // Al cerrar el modal de criterios, limpiar datos y volver al modal principal
        const modal = document.getElementById('criteriosModal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', () => {
                this.limpiarModalCriterios();
                
                // Solo volver al modal principal si no se está guardando criterios
                // (para evitar conflicto con la función guardarCriterios)
                if (!this.guardandoCriterios) {
                    setTimeout(() => {
                        const modalId = this.modoActual === 'create' ? 'createProjectModal' : 'editProjectModal';
                        const mainModal = document.getElementById(modalId);
                        
                        if (mainModal) {
                            let mainModalInstance = bootstrap.Modal.getInstance(mainModal);
                            if (!mainModalInstance) {
                                mainModalInstance = new bootstrap.Modal(mainModal);
                            }
                            mainModalInstance.show();
                        }
                    }, 100);
                }
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
        // Solo configurar el listener una vez - verificar si ya existe
        if (this.eventListenerConfigured) {
            return;
        }
        
        // Crear función de manejo de eventos como método de la clase para poder referenciarla
        this.handleProjectButtonClick = (e) => {
            // Verificar si el clic fue en el SVG de información o en alguno de sus elementos path
            const infoIcon = e.target.closest('.btn-info-proyecto') ||
                           (e.target.tagName === 'path' && e.target.parentNode.classList.contains('btn-info-proyecto'));
            
            if (infoIcon) {
                e.preventDefault();
                e.stopPropagation();
                
                const proyectoId = infoIcon.dataset ? infoIcon.dataset.proyectoId : 
                                  infoIcon.parentNode.dataset.proyectoId;
                this.mostrarInfoProyecto(proyectoId);
                return;
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
                return;
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
                return;
            }
        };
        
        // Añadir el listener solo una vez
        document.addEventListener('click', this.handleProjectButtonClick);
        this.eventListenerConfigured = true;
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
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/>
                        </svg>
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
        // Primero ocultar el modal principal
        const modalId = this.modoActual === 'create' ? 'createProjectModal' : 'editProjectModal';
        const mainModal = document.getElementById(modalId);
        
        if (mainModal) {
            const mainModalInstance = bootstrap.Modal.getInstance(mainModal);
            if (mainModalInstance) {
                mainModalInstance.hide();
            }
        }
        
        // Cargar criterios existentes si estamos en modo edición
        if (this.modoActual === 'edit' && this.proyectoActualId) {
            this.cargarCriteriosExistentes(this.proyectoActualId);
        } else {
            this.criteriosTemporales = [];
            this.actualizarListaCriterios();
        }
        
        // Abrir el modal de criterios después de un pequeño delay
        setTimeout(() => {
            const criteriosModal = document.getElementById('criteriosModal');
            if (criteriosModal) {
                let modalInstance = bootstrap.Modal.getInstance(criteriosModal);
                if (!modalInstance) {
                    modalInstance = new bootstrap.Modal(criteriosModal);
                }
                modalInstance.show();
            }
        }, 300);
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
        this.guardandoCriterios = true; // Activar flag para evitar conflictos
        
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

        // Cerrar el modal de criterios
        const criteriosModal = document.getElementById('criteriosModal');
        const criteriosModalInstance = bootstrap.Modal.getInstance(criteriosModal);
        
        if (criteriosModalInstance) {
            criteriosModalInstance.hide();
        }

        // Volver a mostrar el modal principal después de cerrar criterios
        setTimeout(() => {
            const modalId = this.modoActual === 'create' ? 'createProjectModal' : 'editProjectModal';
            const mainModal = document.getElementById(modalId);
            
            if (mainModal) {
                let mainModalInstance = bootstrap.Modal.getInstance(mainModal);
                if (!mainModalInstance) {
                    mainModalInstance = new bootstrap.Modal(mainModal);
                }
                mainModalInstance.show();
                
                // Mostrar confirmación de criterios guardados en el modal principal
                setTimeout(() => {
                    this.mostrarAlerta(`${this.criteriosTemporales.length} criterios configurados correctamente`, 'success');
                    this.guardandoCriterios = false; // Desactivar flag
                }, 200);
            }
        }, 300);
        
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
            
            // Limpiar criterios temporales
            this.criteriosTemporales = [];
            this.actualizarInterfazPrincipal();
            
            // Si estamos creando un proyecto nuevo, añadirlo directamente a la lista para mayor velocidad
            if (modo === 'create' && proyectoId) {
                this.agregarProyectoALista({
                    id: proyectoId,
                    nombre: formData.get('project_name'),
                    descripcion: formData.get('project_description')
                });
            } else {
                // Para edición, actualizar la lista completa y mantener el proyecto activo
                await this.actualizarListaProyectos();
                
                // Asegurar que el proyecto editado esté seleccionado y cargar sus mensajes
                setTimeout(() => {
                    const proyectoElement = document.querySelector(`.item-proyecto[data-id="${proyectoId}"]`);
                    if (proyectoElement) {
                        // Remover active de otros proyectos
                        document.querySelectorAll('.item-proyecto').forEach(p => p.classList.remove('active'));
                        // Activar el proyecto editado
                        proyectoElement.classList.add('active');
                        
                        // Cargar mensajes del proyecto editado
                        if (window.cargarMensajesProyecto) {
                            window.cargarMensajesProyecto(proyectoId);
                        }
                    }
                }, 300);
            }
            
            // Mostrar mensaje de éxito
            this.mostrarAlerta('¡Proyecto guardado exitosamente!', 'success');
            
            // Cerrar el modal principal inmediatamente
            const modalId = modo === 'create' ? 'createProjectModal' : 'editProjectModal';
            const mainModal = document.getElementById(modalId);
            
            if (mainModal) {
                const modalInstance = bootstrap.Modal.getInstance(mainModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
                
                // Asegurar que no quede backdrop gris
                setTimeout(() => {
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    // Restaurar scroll del body
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }, 300);
            }
            
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
        
        // Buscar el modal activo específico para mostrar la alerta
        const activeModal = document.querySelector('.modal.show .modal-body');
        const target = activeModal || document.querySelector('.container');
        
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
            
            // Mostrar modal con manejo mejorado
            const modalElement = document.getElementById('infoProjectModal');
            let modal = bootstrap.Modal.getInstance(modalElement);
            
            if (!modal) {
                modal = new bootstrap.Modal(modalElement, {
                    keyboard: true,
                    backdrop: true,
                    focus: true
                });
            }
            
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
        // Evitar ejecución múltiple
        if (this.eliminandoProyecto) {
            console.log('Ya se está eliminando un proyecto, ignorando clic adicional');
            return;
        }
        
        // Confirmar eliminación
        if (!confirm('¿Estás seguro de que quieres eliminar este proyecto? Esta acción no se puede deshacer.')) {
            return;
        }
        
        this.eliminandoProyecto = true;
        
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
            
            // Actualizar la lista de proyectos inmediatamente
            await this.actualizarListaProyectos();
            
            this.mostrarAlerta('Proyecto eliminado exitosamente', 'success');
            
        } catch (error) {
            console.error('Error al eliminar proyecto:', error);
            this.mostrarAlerta('Error al eliminar el proyecto: ' + error.message, 'danger');
        } finally {
            // Resetear el flag después de un pequeño delay para evitar clics rápidos
            setTimeout(() => {
                this.eliminandoProyecto = false;
            }, 1000);
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

    async actualizarListaProyectos() {
        try {
            // Guardar el proyecto activo actual para mantenerlo seleccionado
            const proyectoActivoId = document.querySelector('.item-proyecto.active')?.getAttribute('data-id');
            
            // Buscar el contenedor específico de proyectos
            const contenedorProyectos = document.querySelector('.list-group.text-start');
            if (!contenedorProyectos) {
                console.error('No se encontró el contenedor de proyectos');
                return;
            }
            
            // Mostrar indicador de carga
            contenedorProyectos.style.opacity = '0.7';
            
            // Cargar lista actualizada de proyectos
            const response = await fetch('/api/proyectos');
            if (!response.ok) {
                throw new Error('Error al cargar proyectos');
            }
            
            const proyectos = await response.json();
            console.log('Proyectos recibidos:', proyectos);
            
            // Actualizar el contenedor de proyectos en el DOM (estructura idéntica al template)
                let html = '';
                proyectos.forEach(proyecto => {
                    const isActive = proyecto.id.toString() === proyectoActivoId ? 'active' : '';
                    html += `
                        <div class="item-proyecto list-group-item list-group-item-action d-flex justify-content-between align-items-center ${isActive} proyecto" data-id="${proyecto.id}">
                            <div class="flex-grow-1 me-2">
                                ${proyecto.nombre}
                            </div>
                            <div class="proyecto-acciones">
                                <!-- Icono de información -->
                                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="rgb(62, 63, 91)" 
                                    class="bi bi-info-circle btn-info-proyecto me-2" viewBox="0 0 16 16" 
                                    data-proyecto-id="${proyecto.id}">
                                    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
                                    <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0"/>
                                </svg>
                                
                                <!-- Icono de editar -->
                                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="rgb(138, 178, 166)" 
                                    class="bi bi-pencil-square btn-edit-proyecto me-2" viewBox="0 0 16 16" 
                                    data-proyecto-id="${proyecto.id}">
                                    <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
                                    <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
                                </svg>
                                
                                <!-- Icono de eliminar -->
                                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="rgb(231, 76, 60)" 
                                    class="bi bi-trash btn-delete-proyecto" viewBox="0 0 16 16" 
                                    data-proyecto-id="${proyecto.id}">
                                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                                    <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                                </svg>
                            </div>
                        </div>
                    `;
                });
                contenedorProyectos.innerHTML = html;
                
                // Restaurar opacidad con animación suave
                contenedorProyectos.style.opacity = '1';
                
                // Reconfigurar eventos para los nuevos elementos (solo proyectos, no botones)
                this.configurarEventosProyectos();
                
                // Limpiar instancias de modales Bootstrap para evitar conflictos
                const modalElement = document.getElementById('infoProjectModal');
                const existingModal = bootstrap.Modal.getInstance(modalElement);
                if (existingModal) {
                    existingModal.dispose();
                }
            
            console.log('Lista de proyectos actualizada exitosamente via Ajax');
            
        } catch (error) {
            console.error('Error al actualizar lista de proyectos:', error);
            this.mostrarAlerta('Error al actualizar la lista de proyectos', 'warning');
            
            // Restaurar opacidad en caso de error
            const contenedorProyectos = document.querySelector('.list-group.text-start');
            if (contenedorProyectos) {
                contenedorProyectos.style.opacity = '1';
            }
        }
    }

    agregarProyectoALista(proyecto) {
        try {
            const contenedorProyectos = document.querySelector('.list-group.text-start');
            if (!contenedorProyectos) {
                console.error('No se encontró el contenedor de proyectos');
                return;
            }

            // Crear el HTML del nuevo proyecto
            const nuevoProyectoHTML = `
                <div class="item-proyecto list-group-item list-group-item-action d-flex justify-content-between align-items-center proyecto" data-id="${proyecto.id}">
                    <div class="flex-grow-1 me-2">
                        ${proyecto.nombre}
                    </div>
                    <div class="proyecto-acciones">
                        <!-- Icono de información -->
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="rgb(62, 63, 91)" 
                            class="bi bi-info-circle btn-info-proyecto me-2" viewBox="0 0 16 16" 
                            data-proyecto-id="${proyecto.id}">
                            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
                            <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0"/>
                        </svg>
                        
                        <!-- Icono de editar -->
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="rgb(138, 178, 166)" 
                            class="bi bi-pencil-square btn-edit-proyecto me-2" viewBox="0 0 16 16" 
                            data-proyecto-id="${proyecto.id}">
                            <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
                            <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5-.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
                        </svg>
                        
                        <!-- Icono de eliminar -->
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="rgb(231, 76, 60)" 
                            class="bi bi-trash btn-delete-proyecto" viewBox="0 0 16 16" 
                            data-proyecto-id="${proyecto.id}">
                            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                            <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                        </svg>
                    </div>
                </div>
            `;

            // Quitar la clase active de otros proyectos
            const proyectosActivos = contenedorProyectos.querySelectorAll('.item-proyecto.active');
            proyectosActivos.forEach(p => p.classList.remove('active'));

            // Insertar el nuevo proyecto al final de la lista
            contenedorProyectos.insertAdjacentHTML('beforeend', nuevoProyectoHTML);

            // Hacer que el nuevo proyecto sea el activo
            const nuevoElemento = contenedorProyectos.querySelector(`.item-proyecto[data-id="${proyecto.id}"]`);
            if (nuevoElemento) {
                nuevoElemento.classList.add('active');
                
                // Añadir efecto visual de nuevo elemento
                nuevoElemento.style.opacity = '0';
                nuevoElemento.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    nuevoElemento.style.transition = 'all 0.3s ease';
                    nuevoElemento.style.opacity = '1';
                    nuevoElemento.style.transform = 'translateX(0)';
                }, 50);
            }

            // Reconfigurar eventos para el nuevo elemento (solo proyectos, no botones)
            this.configurarEventosProyectos();
            
            // Limpiar instancias de modales Bootstrap para evitar conflictos
            const modalElement = document.getElementById('infoProjectModal');
            const existingModal = bootstrap.Modal.getInstance(modalElement);
            if (existingModal) {
                existingModal.dispose();
            }

            console.log('Proyecto agregado directamente a la lista:', proyecto);

        } catch (error) {
            console.error('Error al agregar proyecto a la lista:', error);
            // Si hay error, hacer actualización completa como fallback
            this.actualizarListaProyectos();
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.criteriosManager = new CriteriosAceptabilidad();
});

// Exportar para uso global
window.CriteriosAceptabilidad = CriteriosAceptabilidad; 