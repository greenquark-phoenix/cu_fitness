import json
import uuid
from pathlib import Path

from channels.generic.websocket import WebsocketConsumer
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from assistant.assistant import Agent

BASE_DIR = Path(__file__).resolve().parent.parent
_ = load_dotenv(BASE_DIR / '.env')

class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.agent = None

    def connect(self):
        self.accept()
        messages = self.scope["session"].get("messages", [])
        for message in messages:
            self.send(text_data=json.dumps(message))

        username = self.scope["user"].username
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro-exp-03-25")
        self.agent = Agent(llm, username)

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        messages = self.scope["session"].get("messages", [])

        if "thread_id" in self.scope["session"]:
            thread_id = self.scope["session"]["thread_id"]
        else:
            thread_id = self.scope["session"]["thread_id"] = str(uuid.uuid4())

        user_message = {
            "message": {"msg": message, "source": "user"},
        }
        messages.append(user_message)
        self.send(text_data=json.dumps(user_message))

        for response in self.agent.stream_graph_update(message, thread_id):
            bot_message = {
                "message": {"msg": response, "source": "bot"},
            }
            messages.append(bot_message)
            self.send(text_data=json.dumps(bot_message))

        self.scope["session"]["messages"] = messages
        self.scope["session"].save()