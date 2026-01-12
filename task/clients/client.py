from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.config import DIAL_ENDPOINT
from task.config import API_KEY
from task.config import API_VERSION
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    _dial_client: Dial
    _async_dial_client: AsyncDial
    
    def __init__(self, deployment_name: str, debug: bool = False):
        super().__init__(deployment_name)
        self._dial_client = Dial(api_key=API_KEY, base_url=DIAL_ENDPOINT)
        self._async_dial_client = AsyncDial(
            api_key=API_KEY, base_url=DIAL_ENDPOINT
        )

    def get_completion(self, messages: list[Message]) -> Message:
        response = self._dial_client.chat.completions.create(
            messages=[msg.to_dict() for msg in messages],
            deployment_name=self._deployment_name,
            stream=False,
            api_version=API_VERSION
        )
        if not response.choices:
            raise Exception("No choices in response found")

        print(response.choices[0].message.content)
        return Message(role=Role.AI, content=response.choices[0].message.content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        completion  = await self._async_dial_client.chat.completions.create(
            messages=[msg.to_dict() for msg in messages],
            deployment_name=self._deployment_name,
            stream=True,
            api_version=API_VERSION
        )

        contents = []
        async for chunk in completion:
            if chunk.choices:
                if chunk.choices[0].delta.content is not None:
                    contents.append(chunk.choices[0].delta.content)
                    print(chunk.choices[0].delta.content, end="", flush=True)

        print()
        return Message(role=Role.AI, content=''.join(contents))
