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
    createChatMessage("Hola, soy un bot, ¿tú cómo te llamas?", true);
	createChatMessage("Hola, soy un usuario, ¿tú cómo te llamas?", false);
});


/*
// Función para manejar el envío de mensajes del usuario
async function handleUserSubmit(event) {
    event.preventDefault();

    // Obtener el input del usuario
    const userInput = document.getElementById('user-input');
    const messageText = userInput.value.trim();

    if (messageText === '') return;

    // Mostrar mensaje del usuario
    createChatMessage(messageText, false);

    // Limpiar el input
    userInput.value = '';

    try {
        // Llamada a la API del chatbot (sustituir con tu endpoint real)
        const response = await fetch('https://tu-api-de-chatbot.com/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: messageText,
                // Añadir cualquier otro parámetro necesario
            })
        });

        if (!response.ok) {
            throw new Error('Error en la respuesta del chatbot');
        }

        const data = await response.json();

        // Mostrar respuesta del bot
        createChatMessage(data.response || 'Lo siento, no puedo procesar tu mensaje en este momento.');
    } catch (error) {
        console.error('Error al comunicarse con el chatbot:', error);
        createChatMessage('Hubo un problema al procesar tu mensaje. Por favor, inténtalo de nuevo.');
    }
}

// Inicializar event listeners cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Añadir listener al formulario de chat
    const chatForm = document.getElementById('chat-form');
    chatForm.addEventListener('submit', handleUserSubmit);

    // Mensaje inicial del bot
    createChatMessage("Hola, soy un asistente de SVAIA. ¿En qué puedo ayudarte hoy?");
});





*/
