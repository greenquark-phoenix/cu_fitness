import json

from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        messages = self.scope["session"].get("messages", [])
        for message in messages:
            self.send(text_data=json.dumps(message))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        messages = self.scope["session"].get("messages", [])

        user_message = {
            "message": {"msg": message, "source": "user"},
        }
        messages.append(user_message)
        self.send(text_data=json.dumps(user_message))

        bot_message = {
            "message": {"msg": f"You said: {message}", "source": "bot"},
        }
        messages.append(bot_message)
        self.send(text_data=json.dumps(bot_message))

        self.scope["session"]["messages"] = messages
        self.scope["session"].save()