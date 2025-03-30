// Función para crear y añadir mensajes al chat
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

async function handleMessageSend(){
	//obtiene el elemento de input
	const userInput = document.getElementById('user-input');
	const messageText = userInput.value.trim();
	if (messageText !== ""){
		createChatMessage(messageText, false);
		try {
			// Petición POSt a la API del chatbot
			const response = await fetch("http://127.0.0.1:5000/send-message", {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify({
					message: messageText
				})
			})
			if (!response.ok) {
				throw new Error("Error en la respuesta del chatbot");
			}
			const data = await response.json();
			// Mostrar respuesta del bot
			createChatMessage(data.message, true);
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
	// Añade un evento al botón de envío
	sendButton.addEventListener("click", function(event) {
		event.preventDefault(); // Añade esta línea
		handleMessageSend();
	});

	const userInput = document.getElementById('user-input');
	// Añade un evento al input para enviar el mensaje al presionar Enter
	userInput.addEventListener("keypress", function(event) {
		if (event.key === 'Enter') {
			event.preventDefault(); // Evita el comportamiento por defecto del Enter
			handleMessageSend();
		}
	}
	);
});