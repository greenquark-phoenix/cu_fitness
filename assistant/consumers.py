import json
import uuid
from pathlib import Path

from channels.generic.websocket import WebsocketConsumer
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from assistant.assistant import Agent

BASE_DIR = Path(__file__).resolve().parent.parent

_ = load_dotenv(BASE_DIR / '.env')
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key="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")
agent = Agent(llm)

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

        if "thread_id" in self.scope["session"]:
            thread_id = self.scope["session"]["thread_id"]
        else:
            thread_id = self.scope["session"]["thread_id"] = str(uuid.uuid4())

        user_message = {
            "message": {"msg": message, "source": "user"},
        }
        messages.append(user_message)
        self.send(text_data=json.dumps(user_message))

        for response in agent.stream_graph_update(message, thread_id):
            bot_message = {
                "message": {"msg": response, "source": "bot"},
            }
            messages.append(bot_message)
            self.send(text_data=json.dumps(bot_message))

        self.scope["session"]["messages"] = messages
        self.scope["session"].save()