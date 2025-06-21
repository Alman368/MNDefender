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
        # IMPORTANTE: Esta clave API no es válida. Necesitas obtener una clave real de OpenRouter.ai
        # Visita https://openrouter.ai/ para obtener tu clave API
        self.api_key = "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"  # Reemplaza con tu clave real
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        # Mensaje de error cuando la API no está configurada correctamente
        self.api_error_message = """❌ **Error de configuración de IA**

La clave API de OpenRouter no está configurada correctamente.

**Para solucionarlo:**
1. Ve a https://openrouter.ai/
2. Crea una cuenta y obtén tu clave API
3. Reemplaza "TU_CLAVE_API_AQUI" en services/message_service.py con tu clave real
4. Reinicia el servidor

Mientras tanto, la IA no estará disponible."""

    def get_response(self, input_text):
        import requests
        import json

        # Verificar si la API está configurada
        if self.api_key == "TU_CLAVE_API_AQUI":
            return self.api_error_message

        try:
            # Preparar el prompt para que se comporte como un asistente de ciberseguridad
            system_prompt = """Eres SVAIA (Sistema de Soporte para Vulnerabilidades y Amenazas basado en Inteligencia Artificial), un asistente experto en ciberseguridad.

INSTRUCCIONES IMPORTANTES:
- Responde SIEMPRE en español
- Usa un tono profesional pero amigable
- NO generes código Python a menos que sea específicamente solicitado
- Proporciona respuestas conversacionales claras y útiles

Tu especialidad es ayudar con:
• Análisis de vulnerabilidades de seguridad
• Mejores prácticas de ciberseguridad
• Protección contra ataques (XSS, SQLi, CSRF, etc.)
• Seguridad en frameworks web (Flask, Django, etc.)
• Configuración segura de sistemas
• Análisis de código fuente para detectar problemas de seguridad

Ejemplos de respuestas apropiadas:
- "Para proteger contra XSS en Flask, te recomiendo usar escape automático..."
- "Las principales vulnerabilidades en aplicaciones web incluyen..."
- "Para mejorar la seguridad de tu base de datos MySQL, deberías..."

Si el usuario hace preguntas no relacionadas con seguridad, conecta amablemente la respuesta con aspectos de seguridad relevantes."""

            response = requests.post(
                url=self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://svaia.local",
                    "X-Title": "SVAIA - Sistema de Vulnerabilidades y Amenazas IA",
                },
                data=json.dumps({
                    "model": "deepseek/deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": input_text
                        }
                    ],
                }),
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    return "❌ La IA no pudo generar una respuesta adecuada en este momento."
            elif response.status_code == 401:
                print(f"Error de autenticación API: {response.status_code}")
                return "❌ **Error de autenticación con la IA**\n\nLa clave API no es válida o ha expirado. Por favor, verifica tu clave API en OpenRouter.ai"
            else:
                print(f"Error API: {response.status_code} - {response.text}")
                return f"❌ **Error de la IA** (Código: {response.status_code})\n\nHubo un problema al conectar con el servicio de inteligencia artificial."

        except requests.exceptions.Timeout:
            print("Timeout en la conexión con OpenRouter API")
            return "⏱️ **Timeout de la IA**\n\nLa consulta está tardando más de lo esperado. Por favor, inténtalo de nuevo."

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            return "🌐 **Error de conexión**\n\nNo se pudo conectar con el servicio de IA. Verifica tu conexión a internet."

        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {e}")
            return "❌ **Error de formato**\n\nHubo un problema procesando la respuesta de la IA."

        except Exception as e:
            print(f"Error inesperado: {e}")
            return f"❌ **Error inesperado**\n\nOcurrió un error no previsto: {str(e)}"
