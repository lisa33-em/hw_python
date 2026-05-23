from typing import Iterator, Dict, List, Any, Union
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk, ChatCompletion


class OllamaBot:
    def __init__(self, config: Any) -> None:
        self.config: Any = config
        self.client: OpenAI = OpenAI(api_key=config.api_key, base_url=config.api_host)
        self.model: str = config.model
        self.history: List[Dict[str, str]] = []

    def send_message_streaming(self, message: str) -> Iterator[str]:
        self._check_limits()

        if len(message) > self.config.chars_limit:
            message = message[: self.config.chars_limit]

        self.history.append({'role': 'user', 'content': message})

        messages: List[Dict[str, str]] = [
            {'role': 'system', 'content': self.config.system_message}
        ] + self.history

        response: Any = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=self.config.temperature,
            stream=True,
        )

        full_response: str = ''
        for chunk in response:
            if isinstance(chunk, ChatCompletionChunk):
                if chunk.choices and chunk.choices[0].delta.content:
                    content: str = chunk.choices[0].delta.content
                    full_response += content
                    yield content

        self.history.append({'role': 'assistant', 'content': full_response})

    def send_message_sync(self, message: str) -> str:
        self._check_limits()

        if len(message) > self.config.chars_limit:
            message = message[: self.config.chars_limit]

        self.history.append({'role': 'user', 'content': message})

        messages: List[Dict[str, str]] = [
            {'role': 'system', 'content': self.config.system_message}
        ] + self.history

        response: Union[ChatCompletion, Any] = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=self.config.temperature,
            stream=False,
        )

        if isinstance(response, ChatCompletion):
            assistant_response: str = response.choices[0].message.content or ''
        else:
            assistant_response = ''

        self.history.append({'role': 'assistant', 'content': assistant_response})
        return assistant_response

    def _check_limits(self) -> None:
        while len(self.history) > self.config.messages_limit:
            self.history.pop(0)

        current_chars: int = sum(len(message['content']) for message in self.history)
        while current_chars > self.config.chars_limit and len(self.history) > 1:
            removed: Dict[str, str] = self.history.pop(0)
            current_chars -= len(removed['content'])

        if self.history and len(self.history[0]['content']) > self.config.chars_limit:
            self.history[0]['content'] = self.history[0]['content'][: self.config.chars_limit]

    def reset(self) -> None:
        self.history = []
