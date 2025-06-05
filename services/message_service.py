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
        self.facts = [
            "Muy bien, pero sabes que los gatos tienen 32 músculos en cada oreja.",
            "No me importa porque yo sé que los osos polares son zurdos.",
            "A qué tú no sabías que las abejas tienen 5 ojos.",
            "¿Sabías que los elefantes son los únicos animales que no pueden saltar?",
            "A mí me gusta saber que las jirafas tienen la lengua de color azul oscuro.",
            "Te va a parecer increible pero ¿sabías que los pingüinos tienen rodillas?",
            "¿Sabías que los cocodrilos no pueden sacar la lengua?",
            "Hoy no tengo ganas de trabajar pero te diré que los flamencos son rosados por comer camarones.",
            "No sé de qué me hablas pero yo sé que los perros son capaces de oír sonidos a 225 metros de distancia.",
            "Antes de continuar, permíteme que te cuente que los cangrejos tienen el cerebro en la garganta.",
            "Qué pereza, pero te diré que los ratones no pueden vomitar.",
            "Cuéntame algo que no sepa, como que las mariposas saborean con sus patas.",
            "Los martes no trabajo, pero hoy te puedo decir que el colibrí es el único pájaro que puede volar hacia atrás.",
            "Los jabalíes pueden correr a una velocidad de 50 km/h sin despeinarse.",
            "En mi siguiente reencarnación quiero ser un pulpo, porque tienen 3 corazones.",
        ]

    def get_response(self, input_text):
        import random
        return random.choice(self.facts)
