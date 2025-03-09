import json

from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        user_message = {
            "message": {"msg": message, "source": "user"},
        }
        self.send(text_data=json.dumps(user_message))

        bot_message = {
            "message": {"msg": f"You said: {message}", "source": "bot"},
        }
        self.send(text_data=json.dumps(bot_message))