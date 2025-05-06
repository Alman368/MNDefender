// Función para crear y añadir mensajes al chat en el html - VERSIÓN HÍBRIDA
function createChatMessage(messageText, isFromBot) {
    // Verificar que messageText no sea nulo o undefined
    if (!messageText) {
        console.error("Se intentó crear un mensaje con texto vacío o inválido");
        messageText = isFromBot ? "Error al cargar el mensaje del bot" : "Error al cargar el mensaje";
    }
    
    // Convertir a string si no lo es
    if (typeof messageText !== 'string') {
        messageText = JSON.stringify(messageText);
    }
    
    // Obtener referencia al contenedor del chat
    const chatContainer = document.getElementById('chat-messages');
    if (!chatContainer) {
        console.error("No se encontró el contenedor de chat 'chat-messages'");
        return;
    }
    
    // Intentar usar las plantillas primero
    const messageTemplate = document.getElementById(
        isFromBot ? 'templateBot' : 'templateUser'
    );
    
    if (messageTemplate) {
        console.log("Usando plantilla para:", isFromBot ? "bot" : "usuario");
        // Usar el método de plantilla
        try {
            // Clona el template para crear una nueva instancia del mensaje
            const messageElement = messageTemplate.content.cloneNode(true);
            
            // Busca el elemento donde irá el contenido del mensaje
            const messageContentElement = messageElement.querySelector('.message-content');
            
            if (messageContentElement) {
                // Inserta el texto del mensaje
                messageContentElement.textContent = messageText;
                
                // Añade el mensaje al final del chat
                chatContainer.appendChild(messageElement);
                
                // Desplaza el scroll hacia abajo para mostrar el nuevo mensaje
                chatContainer.scrollTop = chatContainer.scrollHeight;
                return;
            }
        } catch (error) {
            console.error("Error al usar plantilla:", error);
            // Si falla, continuará con el método alternativo
        }
    }
    
    // Método alternativo: crear elementos directamente con el estilo adecuado
    console.log("Creando mensaje manualmente:", isFromBot ? "bot" : "usuario");
    
    // Crear el contenedor del mensaje
    const messageDiv = document.createElement('div');
    messageDiv.className = isFromBot ? 'row p-3 pt-2 pb-0' : 'row p-3 pb-0';
    
    // Crear el avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = isFromBot ? 'col-2' : 'col-2 d-flex justify-content-center p-2';
    
    // Agregar el ícono
    const iconElement = document.createElement('i');
    iconElement.className = isFromBot ? 'fas fa-robot' : 'fas fa-user';
    avatarDiv.appendChild(iconElement);
    
    // Crear el contenido del mensaje
    const contentDiv = document.createElement('div');
    contentDiv.className = isFromBot ? 'col-10 bg-secondary text-white justify-content-start rounded p-3' : 'col-10 bg-primary text-white rounded p-3';
    contentDiv.textContent = messageText;
    
    // Ensamblar todo
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Desplazar el scroll
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    console.log("Mensaje creado manualmente con éxito");
}

//Función para manejar el input del usuario y enviar el mensaje al bot
async function handleMessageSend(event = null) {
    // Evitar la acción predeterminada del formulario si es necesario
    if (event) event.preventDefault();

    // Obtener el elemento de input
    let userInput = document.getElementById('message-input'); // Cambiado de user-input a message-input
    if (!userInput) {
        // Intentar con el otro ID posible
        userInput = document.getElementById('user-input');
        if (!userInput) {
            console.error("No se encontró el elemento input ni con 'message-input' ni con 'user-input'");
            return;
        }
    }

    const messageText = userInput.value.trim();

    // Obtiene el proyecto activo y su data-id
    const activeProject = document.querySelector('.item-proyecto.active');
    if (!activeProject) {
        alert("Por favor, selecciona un proyecto primero");
        return;
    }
    const proyectoId = activeProject.dataset.id;

    if (messageText !== "") {
        // Mostrar mensaje del usuario inmediatamente
        createChatMessage(messageText, false);
        
        // Limpiar el input antes de la petición
        userInput.value = '';

        try {
            // Guardar el mensaje en la base de datos (backend)
            const res = await fetch("/api/mensaje", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    contenido: messageText,
                    es_bot: false,
                    proyecto_id: proyectoId
                })
            });

            if (!res.ok) {
                throw new Error("Error al guardar el mensaje");
            }

            const dataGuardar = await res.json();
            console.log("Mensaje guardado:", dataGuardar);

        } catch (error) {
            console.error("Error al guardar el mensaje:", error);
        }

        try {
            // Petición POST a la API del chatbot
            const response = await fetch("/send-message", { // Ruta relativa
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: messageText,
                    proyecto_id: proyectoId
                })
            });

            if (!response.ok) {
                throw new Error("Error en la respuesta del chatbot");
            }

            const data = await response.json();

            // Mostrar respuesta del bot
            if (data && data.message) {
                createChatMessage(data.message, true);

                // También guardar la respuesta del bot en la base de datos
                try {
                    await fetch("/api/mensaje", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            contenido: data.message,
                            es_bot: true,
                            proyecto_id: proyectoId
                        })
                    });
                } catch (error) {
                    console.error("Error al guardar la respuesta del bot:", error);
                }
            }
        } catch (error) {
            console.error("Error al comunicarse con el chatbot:", error);
            createChatMessage("Hubo un problema al procesar tu mensaje. Por favor, inténtalo de nuevo.", true);
        }
    }
}

// Función para cargar mensajes de un proyecto
async function cargarMensajesProyecto(id) {
    try {
        console.log(`Cargando mensajes para el proyecto ${id}`);
        
        // Limpiar el contenedor de chat antes de cargar nuevos mensajes
        const chatContainer = document.getElementById('chat-messages');
        if (!chatContainer) {
            console.error("No se encontró el contenedor de chat 'chat-messages'");
            return;
        }
        
        chatContainer.innerHTML = '';
        console.log("Contenedor de chat limpiado correctamente");

        // Consultar la API para cargar el contenido del proyecto
        const res = await fetch(`/api/proyecto/${id}/mensajes`);
        
        console.log("Estado de la respuesta:", res.status);
        
        if (!res.ok) {
            throw new Error(`Error al cargar el contenido del proyecto: ${res.status}`);
        }

        const mensajes = await res.json();
        console.log("Mensajes recuperados:", mensajes);
        
        // Si no hay mensajes, mostrar un mensaje inicial para este proyecto
        if (!mensajes || mensajes.length === 0) {
            console.log("No hay mensajes, mostrando mensaje inicial");
            createChatMessage("Hola, soy un bot. ¿En qué puedo ayudarte con este proyecto?", true);
        } else {
            console.log(`Mostrando ${mensajes.length} mensajes`);
            // Ordenar mensajes por fecha
            mensajes.sort((a, b) => new Date(a.fecha_creacion) - new Date(b.fecha_creacion));
            
            mensajes.forEach(msg => {
                console.log("Mensaje a mostrar:", msg);
                // Asegurarse de que es_bot sea un valor booleano
                let isBot = Boolean(msg.es_bot);
                if (msg.es_bot === 1) isBot = true;
                if (msg.es_bot === 0) isBot = false;
                
                createChatMessage(msg.contenido, isBot);
            });
        }
    } catch (error) {
        console.error("Error al cargar el contenido del proyecto:", error);
        createChatMessage("Error al cargar los mensajes del proyecto. Inténtalo de nuevo.", true);
    }
}

// Función para eliminar un proyecto de la base de datos y de la página
async function deleteProject(projectId, projectElement) {
    try {
        const response = await fetch(`/api/proyecto/${projectId}`, {
            method: 'DELETE',
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Error al eliminar el proyecto');
        }

        // Si el proyecto eliminado era el activo, limpiar el chat
        if (projectElement.classList.contains('active')) {
            const chatContainer = document.getElementById('chat-messages');
            if (chatContainer) {
                chatContainer.innerHTML = '';
                createChatMessage("Selecciona un proyecto para comenzar.", true);
            }
        }

        // Eliminar el elemento del DOM
        projectElement.remove();

    } catch (error) {
        console.error('Error al eliminar proyecto:', error);
        alert('No se pudo eliminar el proyecto de la base de datos');
    }
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM cargado, inicializando aplicación");
    
    // Verificar si existe el contenedor de chat
    const chatContainer = document.getElementById('chat-messages');
    if (!chatContainer) {
        console.error("ERROR CRÍTICO: No se encontró el elemento 'chat-messages'");
        alert("Error: No se encontró el contenedor de chat. Contacta con el administrador.");
        return;
    }
    
    // Cargamos los mensajes del proyecto activo si existe
    const proyectoActivo = document.querySelector('.item-proyecto.active');
    if (proyectoActivo) {
        console.log("Hay proyecto activo:", proyectoActivo.dataset.id);
        const id = proyectoActivo.dataset.id;
        cargarMensajesProyecto(id);
    } else {
        console.log("No hay proyecto activo, mostrando mensaje genérico");
        // Solo si no hay proyectos activos, mostramos un mensaje genérico
        createChatMessage("Hola, soy un bot. Selecciona un proyecto para comenzar.", true);
    }

    // Obtiene el botón de envío
    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        console.log("Botón de envío encontrado, añadiendo evento");
        // Añade un evento al botón de envío
        sendButton.addEventListener("click", function(event) {
            event.preventDefault();
            handleMessageSend();
        });
    } else {
        console.error("Elemento 'send-button' no encontrado");
    }

    // Verificar si el input existe y añadir evento de Enter (probando ambos posibles IDs)
    let messageInput = document.getElementById('message-input');
    if (!messageInput) {
        messageInput = document.getElementById('user-input');
    }
    
    if (messageInput) {
        console.log("Input de mensaje encontrado, añadiendo evento Enter");
        // Añade un evento al input para enviar el mensaje al presionar Enter
        messageInput.addEventListener("keypress", function(event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // Evita el comportamiento por defecto del Enter
                handleMessageSend();
            }
        });
    } else {
        console.error("No se encontró ningún input para mensajes");
        alert("Error: No se encontró el campo para ingresar mensajes. Contacta con el administrador.");
    }

    // Buscar los elementos de proyecto
    const proyectoItems = document.querySelectorAll('.item-proyecto');
    if (proyectoItems.length === 0) {
        console.warn("No se encontraron elementos con la clase 'item-proyecto'");
    } else {
        console.log(`Se encontraron ${proyectoItems.length} proyectos`);
    }
    
    // Manejo de la selección de proyectos clickando en ellos
    proyectoItems.forEach(function(item, index) {
        console.log(`Proyecto ${index}:`, item.dataset.id, item.textContent.trim());
        
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            console.log("Proyecto seleccionado:", this.dataset.id);

            // Quita la clase 'active' de todos los proyectos
            proyectoItems.forEach(function(proyecto) {
                proyecto.classList.remove('active');
            });

            // Añade la clase 'active' al proyecto seleccionado
            this.classList.add('active');

            // Obtener el ID del proyecto seleccionado
            const id = this.dataset.id;
            if (!id) {
                console.error('El elemento seleccionado no tiene un data-id válido.');
                return;
            }
            
            // Usar la función para cargar mensajes
            cargarMensajesProyecto(id);
        });
    });

    // Manejo global de clic en los íconos de papelera (.bi-trash) mediante event delegation
    document.addEventListener('click', function(e) {
        const trashIcon = e.target.closest('.bi-trash');
        if (trashIcon) {
            e.preventDefault();
            e.stopPropagation();
            const projectElement = trashIcon.closest('.item-proyecto');
            if (projectElement) {
                const projectId = projectElement.dataset.id;
                deleteProject(projectId, projectElement);
            }
        }
    });
});
