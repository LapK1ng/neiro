import time
from typing import Iterable

from openai import OpenAI
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError


class OpenAIService:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def moderate(self, text: str) -> bool:
        response = self._client.moderations.create(
            model="omni-moderation-latest",
            input=text,
        )
        return response.results[0].flagged

    def generate(self, messages: Iterable[dict[str, str]], max_retries: int = 3) -> str:
        for attempt in range(1, max_retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=list(messages),
                    temperature=0.6,
                )
                return response.choices[0].message.content.strip()
            except (APITimeoutError, APIConnectionError, RateLimitError, APIStatusError):
                if attempt == max_retries:
                    raise
                time.sleep(2**attempt)
        raise RuntimeError("OpenAI request failed after retries")
