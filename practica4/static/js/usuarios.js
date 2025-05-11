// Función para eliminar un usuario
async function deleteUser(userId, userElement) {
    try {
        // Añadir confirmación para evitar eliminaciones accidentales
        const confirmar = confirm(`¿Estás seguro que deseas eliminar este usuario?`);
        if (!confirmar) {
            return; // El usuario canceló la eliminación
        }

        // Convertir a número para asegurar compatibilidad con la BD
        userId = parseInt(userId, 10);
        if (isNaN(userId)) {
            console.error("ID de usuario inválido para eliminar:", userId);
            return;
        }

        console.log("Intentando eliminar usuario con ID:", userId);

        // Enviar la solicitud DELETE
        const response = await fetch(`/api/usuario/eliminar/${userId}`, {
            method: 'DELETE',
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
            credentials: 'same-origin'
        });

        console.log("Respuesta del servidor:", response.status, response.statusText);

        // Verificar si la respuesta fue exitosa
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error del servidor: ${response.status}`);
        }

        // Procesar la respuesta exitosa
        const responseData = await response.json();
        console.log("Usuario eliminado exitosamente:", responseData);

        // Eliminar el elemento del DOM
        userElement.remove();

        // Mostrar notificación de éxito
        alert('Usuario eliminado correctamente');

    } catch (error) {
        console.error('Error al eliminar usuario:', error);
        alert('No se pudo eliminar el usuario: ' + error.message);
    }
}

// Función para editar un usuario
async function editUser(userId, userName, userLastName, userEmail, userPassword, username) {
    try {
        // Convertir a número para asegurar compatibilidad con la BD
        userId = parseInt(userId, 10);
        if (isNaN(userId)) {
            console.error("ID de usuario inválido para editar:", userId);
            return;
        }

        // Crear objeto con datos a enviar
        const userData = {
            nombre: userName,
            apellidos: userLastName,
            correo: userEmail,
            user: username  // Añadido el username
        };

        // Solo incluir contraseña si se proporcionó una nueva
        if (userPassword) {
            userData.contrasena = userPassword;
        }

        // Realizar la petición PUT a la API
        const response = await fetch(`/api/usuario/editar/${userId}`, {
            method: 'PUT',
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify(userData),
            credentials: 'same-origin'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error del servidor: ${response.status}`);
        }

        const responseData = await response.json();
        console.log("Usuario editado exitosamente:", responseData);

        // Actualizar el nombre del usuario en la interfaz
        const userElement = document.querySelector(`.item-usuario[data-id="${userId}"]`);
        if (userElement) {
            // Obtener el nodo de texto que contiene el nombre del usuario
            const textNode = Array.from(userElement.childNodes)
                .find(node => node.nodeType === Node.TEXT_NODE);

            if (textNode) {
                textNode.nodeValue = `${userName} ${userLastName}`;
            }
        }

        // Cerrar el modal
        const modalElement = document.getElementById('editUserModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();

        // Mostrar notificación de éxito
        alert('Usuario modificado correctamente');

    } catch (error) {
        console.error('Error al editar usuario:', error);
        alert('No se pudo editar el usuario: ' + error.message);
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Manejar eventos para eliminar usuarios
    document.addEventListener('click', function(e) {
        // Verificar si el clic fue en el SVG o en alguno de sus elementos path
        const trashIcon = e.target.closest('.bi-trash-usuario') ||
                        (e.target.tagName === 'path' && e.target.parentNode.classList.contains('bi-trash-usuario'));

        if (trashIcon) {
            e.preventDefault();
            e.stopPropagation();

            // Buscar el elemento padre del usuario
            const userElement = e.target.closest('.item-usuario');
            if (userElement) {
                deleteUser(userElement.dataset.id, userElement);
            }
        }
    });

    // Manejar eventos para editar usuarios
    document.addEventListener('click', function(e) {
        // Verificar si el clic fue en el SVG de edición o en alguno de sus elementos path
        const pencilIcon = e.target.closest('.bi-pencil-square-usuario') ||
                        (e.target.tagName === 'path' && e.target.parentNode.classList.contains('bi-pencil-square-usuario'));

        if (pencilIcon) {
            e.preventDefault();
            e.stopPropagation();

            // Buscar el elemento padre del usuario
            const userElement = e.target.closest('.item-usuario');
            if (userElement) {
                const userId = userElement.dataset.id;

                // Obtener el nombre completo del usuario (texto dentro del elemento)
                const fullName = Array.from(userElement.childNodes)
                    .find(node => node.nodeType === Node.TEXT_NODE)?.nodeValue?.trim();

                // Dividir el nombre completo
                const nameParts = fullName ? fullName.split(' ') : ['', ''];
                const firstName = nameParts[0] || '';
                const lastName = nameParts.slice(1).join(' ') || '';

                // Obtener datos adicionales del usuario desde el servidor
                fetch(`/api/usuario/${userId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Rellenar el formulario del modal con los datos actuales
                        const modal = document.getElementById('editUserModal');
                        const nameInput = modal.querySelector('input[name="nombre"]');
                        const lastNameInput = modal.querySelector('input[name="apellidos"]');
                        const emailInput = modal.querySelector('input[name="correo"]');
                        const usernameInput = modal.querySelector('input[name="user"]');

                        if (nameInput && lastNameInput && emailInput && usernameInput) {
                            nameInput.value = data.nombre || firstName;
                            lastNameInput.value = data.apellidos || lastName;
                            emailInput.value = data.correo || '';
                            usernameInput.value = data.user || '';

                            // Añadir ID al formulario
                            const form = document.getElementById('editUserForm');
                            form.setAttribute('data-user-id', userId);

                            // Mostrar el modal
                            const modalInstance = new bootstrap.Modal(modal);
                            modalInstance.show();
                        }
                    })
                    .catch(error => {
                        console.error('Error al obtener datos del usuario:', error);
                        alert('Error al cargar los datos del usuario');
                    });
            }
        }
    });

    // Configurar el evento submit para el formulario de edición
    const editUserForm = document.getElementById('editUserForm');
    if (editUserForm) {
        editUserForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const userId = this.getAttribute('data-user-id');
            const userName = this.querySelector('input[name="nombre"]').value;
            const userLastName = this.querySelector('input[name="apellidos"]').value;
            const userEmail = this.querySelector('input[name="correo"]').value;
            const userPassword = this.querySelector('input[name="contrasena"]').value;
            const username = this.querySelector('input[name="user"]').value;  // Añadido el username

            if (userId && userName && userLastName && userEmail && username) {
                editUser(userId, userName, userLastName, userEmail, userPassword, username);
            } else {
                alert('Faltan datos para editar el usuario');
            }
        });
    }
});
