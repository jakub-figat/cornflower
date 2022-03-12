from enum import Enum
from typing import Any, Union

from pydantic import BaseModel


class MessageDeliveryMode(int, Enum):
    TRANSIENT = 1
    PERSISTENT = 2


class OutputMessage(BaseModel):
    body: Union[list[Any], dict[str, Any]]
    routing_key: str
    delivery_mode: MessageDeliveryMode = MessageDeliveryMode.PERSISTENT

    class Config:
        allow_arbitrary_Types = True
