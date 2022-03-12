import json
from typing import Any


class FakeMessage:
    def __init__(self, content: dict[str, Any]) -> None:
        self._content = json.dumps(content)
        self.is_ack = False

    def decode(self) -> str:
        return self._content

    def ack(self) -> bool:
        self.is_ack = True
        return self.is_ack

    @property
    def content(self) -> dict[str, Any]:
        content: dict[str, Any] = json.loads(self._content)
        return content
