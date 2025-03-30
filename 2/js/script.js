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

function handleMessageSend(){
	//obtiene el elmento de input
	const userInput = document.getElementById('user-input');
	const messageText = userInput.value.trim();
	if (messageText !== ""){
		createChatMessage(messageText, false);
		userInput.value = '';
		
		// Añade un pequeño retraso antes de que el bot responda (opcional)
		setTimeout(() => {
			// El bot responde con el mismo mensaje que el usuario
			createChatMessage(messageText, true);
		}, 001); // Retraso de 500ms para simular procesamiento
	}
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Crea un mensaje inicial del bot
    createChatMessage("Hola, soy un bot, ¿en qué puedo ayudarte?", true);

	//Obtiene el botón de envío
	const sendButton = document.getElementById('send-button');

	// Añade un evento al botón de envío
	sendButton.addEventListener("click", handleMessageSend);

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