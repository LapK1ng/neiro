import time
from typing import Iterable

from openai import OpenAI
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError


class InsufficientBalanceError(RuntimeError):
    pass


class DeepSeekService:
    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    @staticmethod
    def _backoff_sleep(attempt: int) -> None:
        time.sleep(2**attempt)

    def _with_retries(self, operation, max_retries: int) -> object:
        for attempt in range(1, max_retries + 1):
            try:
                return operation()
            except APIStatusError as exc:
                if exc.status_code == 402:
                    raise InsufficientBalanceError("DeepSeek balance is insufficient") from exc
                if attempt == max_retries:
                    raise
                self._backoff_sleep(attempt)
            except (APITimeoutError, APIConnectionError, RateLimitError):
                if attempt == max_retries:
                    raise
                self._backoff_sleep(attempt)
        raise RuntimeError("DeepSeek request failed after retries")

    def generate(self, messages: Iterable[dict[str, str]], max_retries: int = 3) -> str:
        response = self._with_retries(
            lambda: self._client.chat.completions.create(
                model=self._model,
                messages=list(messages),
                temperature=0.6,
            ),
            max_retries=max_retries,
        )
        return response.choices[0].message.content.strip()
