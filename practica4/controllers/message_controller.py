from flask import request


class MessageController:
    def __init__(self, message_service):
        self.message_service = message_service

    def send_message(self):
        text = request.json['message']
        response_message = self.message_service.get_response(text)
        return {'message': response_message}
