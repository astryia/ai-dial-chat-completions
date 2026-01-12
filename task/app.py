import asyncio

from task.clients.client import DialClient
from task.config import SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
from dotenv import load_dotenv

load_dotenv()

async def start(stream: bool, debug: bool = False) -> None:
    custom_client = DialClient("gpt-4o", debug)
    conversation = start_conversation()

    while True:
        user_input = input("> ")
        if user_input == "exit":
            break

        if user_input == "/new":
            conversation = start_conversation()
            print("New conversation started")
            continue

        conversation.add_message(Message(role=Role.USER, content=user_input))
        response = await custom_client.stream_completion(conversation.get_messages()) if stream else custom_client.get_completion(conversation.get_messages())
        conversation.add_message(response)

def start_conversation() -> Conversation:
    conversation = Conversation()
    conversation.add_message(Message(role=Role.SYSTEM, content=SYSTEM_PROMPT))
    return conversation

asyncio.run(
    start(True, True)
)
