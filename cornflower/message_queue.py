import inspect
import json
import logging
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Callable, TypeVar

from kombu import Connection, Message, Queue
from kombu.mixins import ConsumerProducerMixin
from pydantic import BaseModel

from .utils import get_on_message_callback, get_pydantic_model_class

C = TypeVar(name="C")
V = TypeVar(name="V")


logger = logging.getLogger("cornflower")
logger.setLevel(logging.WARNING)


@dataclass
class ConsumerEntry:
    queue: Queue
    on_message_callback: Callable[[Message], None]


class MessageQueue(ConsumerProducerMixin):
    def __init__(self, url: str, *args, **kwargs) -> None:
        self.connection = Connection(url)
        self._url = url
        self._consumer_registry: list[ConsumerEntry] = []
        self._queue_by_routing_key: dict[str, Queue] = {}
        self._on_message_callback_by_routing_key: dict[str, Callable[[Message], None]] = {}

    def listen(self, routing_key: str) -> Callable[[V], V]:
        """
        Decorator accepts callable with zero or one argument typed with pydantic.BaseModel.
        Creates on_message callback for kombu.Consumer.
        Callback automatically parses message JSON data and validates it against given pydantic schema
        and its validators.
        :param routing_key:
        :return:
        """

        def decorator(_callable: V) -> V:
            pydantic_model_class = get_pydantic_model_class(_callable=_callable)
            self._register_consumer(
                routing_key=routing_key,
                callback=get_on_message_callback(
                    _callable=_callable, routing_key=routing_key, pydantic_model_class=pydantic_model_class
                ),
            )
            return _callable

        return decorator

    def dispatch(self, message) -> None:
        raise NotImplementedError

    def get_consumers(self, consumer_class: C, channel) -> list[C]:
        return [
            consumer_class(queues=[entry.queue], on_message=entry.on_message_callback)
            for entry in self._consumer_registry
        ]

    def _register_consumer(self, routing_key: str, callback: Callable[[Message], None]) -> None:
        queue = Queue(name=routing_key, routing_key=routing_key, durable=True)

        self._consumer_registry.append(
            ConsumerEntry(
                on_message_callback=callback,
                queue=queue,
            )
        )
