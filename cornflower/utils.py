import inspect
import json
import logging
from json import JSONDecodeError
from typing import Callable, Optional, Type

from kombu import Message
from pydantic import BaseModel

logger = logging.getLogger("cornflower")
logger.setLevel(logging.WARNING)


def get_pydantic_model_class(_callable: Callable) -> Optional[Type[BaseModel]]:
    parameters = inspect.signature(_callable).parameters
    pydantic_model_class = None
    if len(parameters):
        (arg, _type), *_ = parameters.items()
        pydantic_model_class = _type.annotation
        assert issubclass(
            pydantic_model_class, BaseModel
        ), f"{_callable.__name__}: Command argument to handler function must inherit from pydantic.BaseModel"

    return pydantic_model_class


def get_on_message_callback(
    _callable: Callable, routing_key: str, pydantic_model_class: Optional[Type[BaseModel]] = None
) -> Callable[[Message], None]:
    def on_message_callback(message: Message) -> None:
        if pydantic_model_class is None:
            _callable()
            return

        try:
            pydantic_instance = pydantic_model_class(**json.loads(message.decode()))
            _callable(pydantic_instance)
        except JSONDecodeError as decode_error:
            logger.error(
                f"[{routing_key}] Error while parsing JSON for {pydantic_model_class.__name__}: {decode_error}"
            )
        except ValueError as pydantic_exception:
            logging.error(f"[{routing_key}] Error while parsing {pydantic_model_class.__name__}: {pydantic_exception}")

        message.ack()

    return on_message_callback
