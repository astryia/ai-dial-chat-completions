from email import message
import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.config import DIAL_ENDPOINT
from task.config import API_KEY
from task.models.message import Message
from task.models.role import Role

class DialClient(BaseClient):
    _endpoint: str
    _api_key: str
    _debug: bool

    def __init__(self, deployment_name: str, debug: bool = False):
        super().__init__(deployment_name)
        self._debug = debug
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"
        self._api_key = API_KEY

    def get_completion(self, messages: list[Message]) -> Message:
        
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }

        request_data = {
            "messages": [msg.to_dict() for msg in messages]
        }

        if self._debug:
            print("Sending request to Dial API:")
            print(request_data)

        response = requests.post(self._endpoint, headers=headers, json=request_data)

        if self._debug:
            print("Response from Dial API:")
            print(response.status_code)
            print(response.json())

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        data = response.json()
        message= Message(role=Role.AI, content=data['choices'][0]['message']['content'])
        print(f"{message.content}")
        return message

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }

        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "stream": True
        }

        if self._debug:
            print("Sending request to Dial API:")
            print(request_data)

        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, headers=headers, json=request_data) as response:

                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")

                if self._debug:
                    print("Received response from Dial API:")   

                async for data in response.content:
                    
                    decoded_data = data.decode('utf-8').strip()

                    if self._debug:
                        print(decoded_data)

                    if decoded_data.startswith('data: '):
                        decoded_data = decoded_data[6:].strip()
                        if decoded_data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(decoded_data)
                            content = chunk.get('choices', [])[0].get('delta', {}).get('content', '')
                            if content:
                                if not self._debug:
                                    print(content, end="", flush=True)
                                contents.append(content)
                        except json.JSONDecodeError:
                            continue
        if not self._debug:
            print()
        else:
            print(''.join(contents))

        message = Message(role=Role.AI, content=''.join(contents))
        return message
