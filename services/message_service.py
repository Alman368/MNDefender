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
        self.greetings = [
            "¡Hola!",
            "¡Buenos días!",
            "¡Buenas tardes!",
            "¡Buenas noches!",
            "¡Hola! ¿En qué puedo ayudarte?"
        ]

    def get_response(self, input_text):
        import random
        return random.choice(self.greetings)

class AnimalFactsService:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        # Fallback messages en caso de error de API
        self.fallback_facts = [
            "Lo siento, no puedo conectar con la IA en este momento. Pero te diré que los gatos tienen 32 músculos en cada oreja.",
            "Hay problemas con la conexión, pero ¿sabías que los osos polares son zurdos?",
            "La IA no está disponible ahora, pero puedo decirte que las abejas tienen 5 ojos."
        ]

    def get_response(self, input_text):
        import requests
        import json
        import random

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
                    return "Lo siento, no pude generar una respuesta adecuada en este momento."
            else:
                print(f"Error API: {response.status_code} - {response.text}")
                return random.choice(self.fallback_facts)

        except requests.exceptions.Timeout:
            print("Timeout en la conexión con OpenRouter API")
            return "La consulta está tardando más de lo esperado. ¿Sabías que es importante implementar timeouts en las APIs para evitar vulnerabilidades de denegación de servicio?"

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            return random.choice(self.fallback_facts)

        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {e}")
            return "Hubo un problema procesando la respuesta. Como consejo de seguridad: siempre valida y sanitiza las respuestas de APIs externas."

        except Exception as e:
            print(f"Error inesperado: {e}")
            return random.choice(self.fallback_facts)
