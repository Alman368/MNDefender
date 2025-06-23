class RandomMessageService:
    def __init__(self):
        self.messages = [
            "¡Hola, mundo!",
            "¿Cómo puedo asistirte hoy?",
            "¡Que tengas un gran día!",
            "¡Sigue sonriendo!",
            "¡Lo estás haciendo genial!"
        ]

    def get_response(self, input_text):
        import random
        return random.choice(self.messages)

class GreetingMessageService:
    def __init__(self):
        self.responses = {
            # Saludos
            'saludos': [
                "¡Hola! Soy SVAIA, tu asistente de ciberseguridad. ¿En qué puedo ayudarte hoy?",
                "¡Buenos días! Estoy aquí para ayudarte con temas de seguridad informática.",
                "¡Hola! ¿Tienes alguna pregunta sobre vulnerabilidades o seguridad?",
            ],
            # Vulnerabilidades
            'vulnerabilidades': [
                "Las vulnerabilidades más comunes incluyen: XSS (Cross-Site Scripting), SQL Injection, CSRF, y vulnerabilidades de autenticación.",
                "Para identificar vulnerabilidades, te recomiendo usar herramientas como OWASP ZAP, Burp Suite, o realizar auditorías de código.",
                "Es importante mantener un inventario de vulnerabilidades y clasificarlas por criticidad (baja, media, alta, crítica).",
            ],
            # Seguridad web
            'seguridad': [
                "Para mejorar la seguridad de tu aplicación web, implementa: validación de entrada, escape de salida, autenticación robusta y autorización adecuada.",
                "Recuerda seguir las mejores prácticas de OWASP Top 10 para prevenir las vulnerabilidades más críticas.",
                "La seguridad debe implementarse en capas: red, aplicación, datos y usuarios.",
            ],
            # Respuestas generales
            'general': [
                "Como asistente de ciberseguridad, puedo ayudarte con análisis de vulnerabilidades, mejores prácticas de seguridad y protección contra ataques.",
                "¿Te interesa algún tema específico de seguridad? Puedo ayudarte con XSS, SQL injection, CSRF, autenticación, o configuración segura.",
                "La ciberseguridad es fundamental. ¿Hay algún aspecto específico de tu proyecto que te preocupe desde el punto de vista de seguridad?",
            ]
        }

    def get_response(self, input_text):
        import random
        
        # Convertir a minúsculas para análisis
        text_lower = input_text.lower()
        
        # Detectar tipo de consulta
        if any(word in text_lower for word in ['hola', 'buenos', 'buenas', 'saludos', 'hi']):
            return random.choice(self.responses['saludos'])
        elif any(word in text_lower for word in ['vulnerabilidad', 'vuln', 'exploit', 'cve', 'fallo']):
            return random.choice(self.responses['vulnerabilidades'])
        elif any(word in text_lower for word in ['seguridad', 'proteger', 'ataque', 'hack', 'xss', 'sql', 'csrf']):
            return random.choice(self.responses['seguridad'])
        else:
            return random.choice(self.responses['general'])

class AnimalFactsService:
    def __init__(self):
        """Servicio que consume la API de Google Gemini para generar respuestas.

        La clase conserva el nombre `AnimalFactsService` para evitar cambios en el resto del
        código, pero la implementación usa Gemini (google-generativeai).
        """

        import os
        from dotenv import load_dotenv
        
        # Cargar variables de entorno desde config.env
        load_dotenv('config.env')

        # Leer clave API desde archivo de configuración
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        # Validar que la clave API existe
        if not self.api_key:
            print("❌ Error: GEMINI_API_KEY no encontrada en config.env")
            self.api_key = None

        # Permitir que el modelo sea configurable mediante variable de entorno
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        # Mensaje de error cuando la API no está configurada correctamente
        self.api_error_message = (
            "❌ **Error de configuración de IA**\n\n"
            "La clave API de Gemini no está configurada en `config.env`.\n\n"
            "**Para solucionarlo:**\n"
            "1. Edita el archivo `config.env` en la raíz del proyecto\n"
            "2. Añade tu clave API: `GEMINI_API_KEY=tu_clave_aqui`\n"
            "3. Obtén una clave válida en https://ai.google.dev\n"
            "3. Reinicia el servidor"
        )

        # Intentar inicializar la librería
        if not self.api_key:
            print("API key no disponible, servicio deshabilitado")
            self.model = None
            return
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            # Normalizar nombre: si no empieza con "models/" lo añadimos para la llamada inicial
            candidate_name = self.model_name
            if not candidate_name.startswith("models/"):
                candidate_name_with_prefix = f"models/{candidate_name}"
            else:
                candidate_name_with_prefix = candidate_name

            try:
                # Intento principal con identificador completo
                self.model = genai.GenerativeModel(candidate_name_with_prefix)
                print(f"✅ Gemini configurado correctamente con modelo: {self.model_name}")
            except ValueError:
                # Fallback con el nombre tal cual (algunas versiones aceptan el nombre corto)
                self.model = genai.GenerativeModel(candidate_name)
                print(f"✅ Gemini configurado con modelo fallback: {candidate_name}")
        except Exception as e:
            print(f"Error inicializando Gemini: {e}")
            self.model = None

    def _build_prompt(self, user_text: str) -> str:
        """Crea un prompt conciso que garantice respuestas en español y Markdown."""

        system_instructions = (
            "Eres **SVAIA**, asistente experto en ciberseguridad.\n\n"
            "INSTRUCCIONES:\n"
            "- Responde SIEMPRE en español.\n"
            "- Usa formato **Markdown** rico: listas, tablas, cabeceras cuando sea útil.\n"
            "- Mantén un tono profesional y amigable.\n"
            "- NO incluyas código salvo que el usuario lo solicite explícitamente.\n"
            "- Conecta cualquier tema con la seguridad informática siempre que sea posible."
        )

        # Comprimimos el prompt: sistema + pregunta del usuario, separados por \n\n
        return f"{system_instructions}\n\nUsuario: {user_text}"

    def get_response(self, input_text):
        """Genera una respuesta usando Gemini. Devuelve Markdown listo para la UI."""

        # Validar que la librería y el modelo están listos
        if self.model is None:
            return self.api_error_message

        try:
            prompt = self._build_prompt(input_text)

            response = self.model.generate_content(prompt, generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1024,
            })

            # La librería devuelve un objeto; extraemos el texto
            markdown_text = response.text.strip() if hasattr(response, "text") else str(response)

            # Convertimos Markdown a HTML para que el front-end lo muestre con formato
            try:
                import markdown2
                # Convertir Markdown a HTML con todas las características
                html = markdown2.markdown(
                    markdown_text, 
                    extras=[
                        "tables",           # Soporte para tablas
                        "fenced-code-blocks", # Bloques de código
                        "strike",           # Texto tachado
                        "task_list",        # Listas de tareas
                        "break-on-newline", # Saltos de línea
                        "cuddled-lists",    # Listas sin espacios
                        "footnotes",        # Notas al pie
                        "header-ids",       # IDs en encabezados
                        "smarty-pants",     # Comillas inteligentes
                        "spoiler"           # Texto oculto
                    ]
                )
                print(f"Markdown original: {markdown_text[:200]}...")
                print(f"HTML convertido: {html[:200]}...")
            except Exception as conv_err:
                print(f"Error convirtiendo Markdown a HTML: {conv_err}")
                html = markdown_text  # Fallback: devolver el Markdown crudo

            return html

        except Exception as e:
            print(f"Error generando respuesta Gemini: {e}")
            return (
                "❌ **Error de la IA**\n\n"
                "No fue posible obtener respuesta en este momento. Inténtalo de nuevo más tarde."
            )
