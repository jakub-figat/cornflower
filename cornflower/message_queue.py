import logging
from typing import Any, Callable, Optional, Type, TypeVar

from amqp import Channel
from kombu import Connection, Consumer, Message, Queue
from kombu.mixins import ConsumerProducerMixin
from pydantic import BaseModel

from .options import QueueOptions
from .utils import get_on_message_callback, get_pydantic_model_class

V = TypeVar("V")


logger = logging.getLogger("cornflower")
logger.setLevel(logging.WARNING)


class ConsumerEntry(BaseModel):
    queue: Queue
    on_message_callback: Callable[[Message], None]

    class Config:
        arbitrary_types_allowed = True


class MessageQueue(ConsumerProducerMixin):
    def __init__(self, url: str, queue_options: Optional[QueueOptions] = None) -> None:
        self.connection = Connection(url)
        self._queue_options = queue_options
        self._url = url
        self._consumer_registry: list[ConsumerEntry] = []

    def listen(self, routing_key: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
        """
        Decorator accepts callable with zero or one argument typed with pydantic.BaseModel.
        Creates on_message callback for kombu.Consumer.
        Callback automatically parses message JSON data and validates it against given pydantic schema
        and its validators.
        :param routing_key:
        :return:
        """

        def decorator(_callable: Callable[..., None]) -> Callable[..., None]:
            pydantic_model_class = get_pydantic_model_class(_callable=_callable)
            self._register_consumer(
                routing_key=routing_key,
                callback=get_on_message_callback(
                    _callable=_callable, routing_key=routing_key, pydantic_model_class=pydantic_model_class
                ),
            )
            return _callable

        return decorator

    def dispatch(self, message: Any) -> None:
        raise NotImplementedError

    def get_consumers(self, consumer_class: Type[Consumer], channel: Channel) -> list[Consumer]:
        return [
            consumer_class(queues=[entry.queue], on_message=entry.on_message_callback, channel=channel)
            for entry in self._consumer_registry
        ]

    def _register_consumer(self, routing_key: str, callback: Callable[[Message], None]) -> None:
        queue_options = {} if self._queue_options is None else self._queue_options.dict()
        queue = Queue(name=routing_key, routing_key=routing_key, **queue_options)

        self._consumer_registry.append(
            ConsumerEntry(
                on_message_callback=callback,
                queue=queue,
            )
        )
