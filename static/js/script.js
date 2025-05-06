// Función para crear y añadir mensajes al chat en el html
function createChatMessage(messageText, isFromBot) {
    // Selecciona la plantilla según quien envía el mensaje (bot o usuario)
    const messageTemplate = document.getElementById(
        isFromBot ? 'templateBot' : 'templateUser'
    );

    // Clona el template para crear una nueva instancia del mensaje
    const messageElement = messageTemplate.content.cloneNode(true);

    // Busca el elemento donde irá el contenido del mensaje
    const messageContentElement = messageElement.querySelector('.message-content');

    // Inserta el texto del mensaje
    messageContentElement.textContent = messageText;

    // Obtiene la referencia al contenedor del chat
    const chatContainer = document.getElementById('chat-messages');

    // Añade el mensaje al final del chat
    chatContainer.appendChild(messageElement);

	// Desplaza el scroll hacia abajo para mostrar el nuevo mensaje
	chatContainer.scrollTop = chatContainer.scrollHeight;
}

//Función para manejar el input del usuario y enviar el mensaje al bot
async function handleMessageSend(){
	//obtiene el elemento de input
	const userInput = document.getElementById('user-input');
	const messageText = userInput.value.trim();

	// Obtiene el proyecto activo y su data-id
	const activeProject = document.querySelector('.item-proyecto.active');
	if (!activeProject) {
		alert("Por favor, selecciona un proyecto primero");
		return;
	}
	const proyectoId = activeProject.dataset.id;

	if (messageText !== ""){
		createChatMessage(messageText, false);
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
					proyecto_id: proyectoId // Asegúrate de que proyectoId esté definido
				})
			});

			if (!res.ok) {
				throw new Error("Error al guardar el mensaje");
			}

			const dataGuardar = await res.json();
			console.log("Mensaje guardado:", dataGuardar);

		} catch (error) {
			console.error("Error al guardar el mensaje:", error);
			// Puedes notificarlo al usuario si quieres
		}
		try {
			// Petición POST a la API del chatbot
			const response = await fetch("http://127.0.0.1:5000/send-message", {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify({
					message: messageText,
					proyecto_id: proyectoId
				})
			})
			if (!response.ok) {
				throw new Error("Error en la respuesta del chatbot");
			}
			const data = await response.json();
			// Mostrar respuesta del bot
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

		} catch (error) {
			console.error("Error al comunicarse con el chatbot:", error);
			createChatMessage("Hubo un problema al procesar tu mensaje. Por favor, inténtalo de nuevo.", true);
		}
		// Limpiar el input
		userInput.value = '';
	}
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Crea un mensaje inicial del bot
    createChatMessage("Hola, soy un bot, ¿tú cómo te llamas?", true);

	//Obtiene el botón de envío
	const sendButton = document.getElementById('send-button');

	// Añade un evento al botón de envío
	sendButton.addEventListener("click", function(event) {
		event.preventDefault();
		handleMessageSend();
	});

	const userInput = document.getElementById('user-input');
	// Añade un evento al input para enviar el mensaje al presionar Enter
	userInput.addEventListener("keypress", function(event) {
		if (event.key === 'Enter') {
			event.preventDefault(); // Evita el comportamiento por defecto del Enter
			handleMessageSend();
		}
	});

    // Manejo de la selección de proyectos clickando en ellos
	const proyectoItems = document.querySelectorAll('.item-proyecto');
	proyectoItems.forEach(function(item) {
		item.addEventListener('click', async function(e) {
			e.preventDefault();

			// Quita la clase 'active' de todos los proyectos
			proyectoItems.forEach(function(proyecto) {
				proyecto.classList.remove('active');
			});

			// Añade la clase 'active' al proyecto seleccionado
			this.classList.add('active');

			// Obtener el ID del proyecto seleccionado
			const id = this.dataset.id; // Corregido: datas.id → dataset.id
			if (!id) {
				console.error('El elemento seleccionado no tiene un data-id válido.');
				return;
			}
			console.log('Proyecto seleccionado:', id);

			try {
				 // Limpiar el contenedor de chat antes de cargar nuevos mensajes
				const chatContainer = document.getElementById('chat-messages');
				chatContainer.innerHTML = '';

				// Consultar la API para cargar el contenido del proyecto
				const res = await fetch(`/api/proyecto/${id}/mensajes`); // Corregido: /api/ → /api/proyecto/
				if (!res.ok) {
					throw new Error("Error al cargar el contenido del proyecto");
				}

				const mensajes = await res.json();

				mensajes.forEach(msg => {
					// Usar contenido en lugar de mensaje y es_bot es booleano, no string
					createChatMessage(msg.contenido, msg.es_bot);
				});
			} catch (error) {
				console.error("Error al cargar el contenido del proyecto:", error);
			}
		});
	});
});
