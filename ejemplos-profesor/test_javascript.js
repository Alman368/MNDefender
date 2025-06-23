// Archivo JavaScript con vulnerabilidades para pruebas

// Vulnerabilidad 1: Cross-Site Scripting (XSS)
function mostrarContenido(userInput) {
    document.getElementById('content').innerHTML = userInput;
}

// Vulnerabilidad 2: Code Injection
function ejecutarCodigo(userCode) {
    eval(userCode);
}

// Vulnerabilidad 3: Prototype Pollution
function combinarObjetos(userObj) {
    return Object.assign({}, userObj);
}

// Vulnerabilidad 4: Open Redirect
function redirigir(userURL) {
    window.location = userURL;
}
