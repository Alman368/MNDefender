// Función para crear y añadir mensajes al chat en el html
function createChatMessage(messageText, isFromBot) {
    if (!messageText) {
        console.error("Se intentó crear un mensaje con texto vacío o inválido");
        messageText = isFromBot ? "Error al cargar el mensaje del bot" : "Error al cargar el mensaje";
    }

    if (typeof messageText !== 'string') {
        messageText = JSON.stringify(messageText);
    }

    const chatContainer = document.getElementById('chat-messages');
    const templateId = isFromBot ? 'templateBot' : 'templateUser';
    const messageTemplate = document.getElementById(templateId);

    // Crear el mensaje usando plantillas o método manual
    if (messageTemplate) {
        try {
            const messageElement = messageTemplate.content.cloneNode(true);
            const messageContentElement = messageElement.querySelector('.message-content');
            if (messageContentElement) {
                messageContentElement.textContent = messageText;
                chatContainer.appendChild(messageElement);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                return;
            }
        } catch (error) {
            console.error("Error con la plantilla:", error);
        }
    }

    // Método alternativo si falló el uso de plantillas
    const messageDiv = document.createElement('div');
    messageDiv.className = isFromBot ? 'row p-3 pt-2 pb-0' : 'row p-3 pb-0';

    if (isFromBot) {
        messageDiv.innerHTML = `
            <div class="col-2">
                <!-- Icono del bot usando Bootstrap Icons -->
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                    class="bi bi-robot" viewBox="0 0 16 16">
                    <path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.6 26.6 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.93.93 0 0 1-.765.935c-.845.147-2.34.346-4.235.346s-3.39-.2-4.235-.346A.93.93 0 0 1 3 9.219zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a25 25 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135" />
                    <path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5" />
                </svg>
            </div>
            <div class="col-10 bg-secondary text-white justify-content-start rounded p-3">
                <p class="m-0">${messageText}</p>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="col-10 bg-primary text-white rounded p-3">
                <p class="m-0">${messageText}</p>
            </div>
            <div class="col-2 d-flex justify-content-center p-2">
                <!-- Icono del usuario usando Bootstrap Icons -->
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                    class="bi bi-person-fill" viewBox="0 0 16 16">
                    <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6" />
                </svg>
            </div>
        `;
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}


// Función para manejar el envío de mensajes
async function handleMessageSend(event = null) {
    if (event) event.preventDefault();

    // Obtener el input
    let userInput = document.getElementById('user-input') || document.getElementById('message-input');
    if (!userInput) {
        console.error("No se encontró el elemento de input");
        return;
    }

    const messageText = userInput.value.trim();
    if (messageText === "") return;

    // Obtener el proyecto activo - FIX: Asegurarse que el ID es un número
    const activeProject = document.querySelector('.item-proyecto.active');
    if (!activeProject) {
        alert("Por favor, selecciona un proyecto primero");
        return;
    }

    // FIX: Convertir a número para asegurar compatibilidad con la BD
    const proyectoId = parseInt(activeProject.dataset.id, 10);
    if (isNaN(proyectoId)) {
        console.error("ID de proyecto inválido:", activeProject.dataset.id);
        return;
    }

    // Mostrar mensaje del usuario y limpiar input
    createChatMessage(messageText, false);
    userInput.value = '';

    try {
        // Guardar mensaje del usuario
        const res = await fetch("/api/mensaje", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                contenido: messageText,
                es_bot: false,
                proyecto_id: proyectoId
            })
        });

        if (!res.ok) throw new Error(`Error al guardar el mensaje: ${res.status}`);

        // Enviar mensaje al chatbot
        const botResponse = await fetch("/send-message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: messageText,
                proyecto_id: proyectoId
            })
        });

        if (!botResponse.ok) throw new Error("Error en la respuesta del chatbot");

        const data = await botResponse.json();

        // Mostrar y guardar respuesta del bot
        if (data && data.message) {
            createChatMessage(data.message, true);

            await fetch("/api/mensaje", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    contenido: data.message,
                    es_bot: true,
                    proyecto_id: proyectoId
                })
            });
        }
    } catch (error) {
        console.error("Error:", error);
        createChatMessage("Hubo un problema al procesar tu mensaje. Por favor, inténtalo de nuevo.", true);
    }
}

// Función para cargar mensajes de un proyecto
async function cargarMensajesProyecto(id) {
    try {
        // Convertir a número para asegurar compatibilidad con la BD
        id = parseInt(id, 10);
        if (isNaN(id)) {
            console.error("ID de proyecto inválido para cargar mensajes:", id);
            return;
        }

        const chatContainer = document.getElementById('chat-messages');
        chatContainer.innerHTML = '';

        // Obtener mensajes
        const res = await fetch(`/api/proyecto/${id}/mensajes`);
        if (!res.ok) throw new Error(`Error: ${res.status}`);

        const mensajes = await res.json();

        if (!mensajes || mensajes.length === 0) {
            createChatMessage("Hola, soy un bot. ¿En qué puedo ayudarte con este proyecto?", true);
            //mandar mensaje del bot a la base de datos
            await fetch("/api/mensaje", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    contenido: "Hola, soy un bot. ¿En qué puedo ayudarte con este proyecto?",
                    es_bot: true,
                    proyecto_id: id
                })
            });
        } else {
            // Ordenar mensajes por fecha
            mensajes.sort((a, b) => new Date(a.fecha_creacion) - new Date(b.fecha_creacion));

            mensajes.forEach(msg => {
                // Normalizar es_bot a booleano
                let isBot = Boolean(msg.es_bot);
                if (msg.es_bot === 1) isBot = true;
                if (msg.es_bot === 0) isBot = false;

                createChatMessage(msg.contenido, isBot);
            });
        }
    } catch (error) {
        console.error("Error:", error);
        createChatMessage("Error al cargar los mensajes del proyecto. Inténtalo de nuevo.", true);
    }
}

// Función para eliminar un proyecto
async function deleteProject(projectId, projectElement) {
    try {
        // Añadir confirmación para evitar eliminaciones accidentales
        const confirmar = confirm(`¿Estás seguro que deseas eliminar este proyecto?`);
        if (!confirmar) {
            return; // El usuario canceló la eliminación
        }

        // Convertir a número para asegurar compatibilidad con la BD
        projectId = parseInt(projectId, 10);
        if (isNaN(projectId)) {
            console.error("ID de proyecto inválido para eliminar:", projectId);
            return;
        }

        console.log("Intentando eliminar proyecto con ID:", projectId);

        // Verificar si hay restricciones de eliminación (como mensajes asociados)
        const response = await fetch(`/api/proyecto/eliminar/${projectId}`, {
            method: 'DELETE',
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"  // Indicar que es una petición AJAX
            },
            credentials: 'same-origin'  // Incluir cookies para autenticación si es necesario
        });

        console.log("Respuesta del servidor:", response.status, response.statusText);

        // Verificar si la respuesta fue exitosa (código 200-299)
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error del servidor: ${response.status}`);
        }

        // Procesar la respuesta exitosa
        const responseData = await response.json();
        console.log("Proyecto eliminado exitosamente:", responseData);

        // Limpiar chat si era el proyecto activo
        if (projectElement.classList.contains('active')) {
            const chatContainer = document.getElementById('chat-messages');
            if (chatContainer) {
                chatContainer.innerHTML = '';
                createChatMessage("Selecciona un proyecto para comenzar.", true);
            }
        }

        // Eliminar el elemento del DOM
        projectElement.remove();

        // Mostrar notificación de éxito
        alert('Proyecto eliminado correctamente');

    } catch (error) {
        console.error('Error al eliminar proyecto:', error);
        alert('No se pudo eliminar el proyecto: ' + error.message + '. Revisa la consola para más detalles.');
    }
}

//Función para editar un proyecto
async function editProject(projectId, projectName, projectDescription) {
    try {
        // Convertir a número para asegurar compatibilidad con la BD
        projectId = parseInt(projectId, 10);
        if (isNaN(projectId)) {
            console.error("ID de proyecto inválido para editar:", projectId);
            return;
        }

        // Realizar la petición PUT a la API
        const response = await fetch(`/api/proyecto/editar/${projectId}`, {
            method: 'PUT',
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({
                nombre: projectName,
                descripcion: projectDescription
            }),
            credentials: 'same-origin'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error del servidor: ${response.status}`);
        }

        const responseData = await response.json();
        console.log("Proyecto editado exitosamente:", responseData);

        // Actualizar el nombre del proyecto en la interfaz
        const projectElement = document.querySelector(`.item-proyecto[data-id="${projectId}"]`);
        if (projectElement) {
            // Obtener el nodo de texto que contiene el nombre del proyecto
            const textNode = Array.from(projectElement.childNodes)
                .find(node => node.nodeType === Node.TEXT_NODE);

            if (textNode) {
                textNode.nodeValue = projectName;
            }
        }

        // Cerrar el modal
        const modalElement = document.getElementById('editProjectModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();

        // Mostrar notificación de éxito
        alert('Proyecto modificado correctamente');

    } catch (error) {
        console.error('Error al editar proyecto:', error);
        alert('No se pudo editar el proyecto: ' + error.message);
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-messages');
    if (!chatContainer) {
        console.error("ERROR CRÍTICO: No se encontró el elemento 'chat-messages'");
        return;
    }

    // Cargar mensajes del proyecto activo
    const proyectoActivo = document.querySelector('.item-proyecto.active');
    if (proyectoActivo) {
        cargarMensajesProyecto(proyectoActivo.dataset.id);
    } else {
        createChatMessage("Hola, soy un bot. Selecciona un proyecto para comenzar.", true);
    }

    // Configurar evento para botón de envío
    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        sendButton.addEventListener("click", handleMessageSend);
    }

    // Configurar evento para input (tecla Enter)
    const messageInput = document.getElementById('user-input') || document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener("keypress", function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                handleMessageSend();
            }
        });
    }

    // Configurar eventos para proyectos
    const proyectoItems = document.querySelectorAll('.item-proyecto');
    proyectoItems.forEach(function(item) {
        item.addEventListener('click', function(e) {
            e.preventDefault();

            // Obtener ID del proyecto
            const id = this.dataset.id;
            if (!id) {
                console.error('El elemento seleccionado no tiene un data-id válido');
                return;
            }

            // Actualizar proyecto activo
            proyectoItems.forEach(p => p.classList.remove('active'));
            this.classList.add('active');

            // Cargar mensajes
            cargarMensajesProyecto(id);
        });
    });

    // Manejar eventos para eliminar proyectos
    document.addEventListener('click', function(e) {
        // Verificar si el clic fue en el SVG o en alguno de sus elementos path
        const trashIcon = e.target.closest('.bi-trash') ||
                        (e.target.tagName === 'path' && e.target.parentNode.classList.contains('bi-trash'));

        if (trashIcon) {
            e.preventDefault();
            e.stopPropagation();

            // Buscar el elemento padre del proyecto
            const projectElement = e.target.closest('.item-proyecto');
            if (projectElement) {
                deleteProject(projectElement.dataset.id, projectElement);
            }
        }
    });

    // Manejar eventos para editar proyectos
    document.addEventListener('click', function(e) {
        // Verificar si el clic fue en el SVG de edición o en alguno de sus elementos path
        const pencilIcon = e.target.closest('.bi-pencil-square') ||
                        (e.target.tagName === 'path' && e.target.parentNode.classList.contains('bi-pencil-square'));

        if (pencilIcon) {
            e.preventDefault();
            e.stopPropagation();

            // Buscar el elemento padre del proyecto
            const projectElement = e.target.closest('.item-proyecto');
            if (projectElement) {
                const projectId = projectElement.dataset.id;

                // Obtener el nombre actual del proyecto (texto dentro del elemento)
                const textContent = Array.from(projectElement.childNodes)
                    .find(node => node.nodeType === Node.TEXT_NODE)?.nodeValue?.trim();

                // Obtener la descripción actual del proyecto desde el servidor
                fetch(`/api/proyecto/${projectId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Rellenar el formulario del modal con los datos actuales
                        const modal = document.getElementById('editProjectModal');
                        const nameInput = modal.querySelector('input[name="project_name"]');
                        const descriptionInput = modal.querySelector('textarea[name="project_description"]');

                        if (nameInput && descriptionInput) {
                            nameInput.value = textContent || data.nombre || '';
                            descriptionInput.value = data.descripcion || '';

                            // Añadir un atributo data-id al formulario
                            const form = document.getElementById('editProjectForm');
                            form.setAttribute('data-project-id', projectId);

                            // Mostrar el modal
                            const modalInstance = new bootstrap.Modal(modal);
                            modalInstance.show();
                        }
                    })
                    .catch(error => {
                        console.error('Error al obtener datos del proyecto:', error);
                        alert('Error al cargar los datos del proyecto');
                    });
            }
        }
    });

    // Configurar el evento submit para el formulario de edición
    const editProjectForm = document.getElementById('editProjectForm');
    if (editProjectForm) {
        editProjectForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const projectId = this.getAttribute('data-project-id');
            const projectName = this.querySelector('input[name="project_name"]').value;
            const projectDescription = this.querySelector('textarea[name="project_description"]').value;

            if (projectId && projectName && projectDescription) {
                editProject(projectId, projectName, projectDescription);
            } else {
                alert('Faltan datos para editar el proyecto');
            }
        });
    }
});
