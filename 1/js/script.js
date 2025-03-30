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

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Crea un mensaje inicial del bot
    createChatMessage("Hola, soy un bot, ¿en qué puedo ayudarte?", true);
});