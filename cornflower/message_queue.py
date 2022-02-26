import inspect
import logging
from typing import Callable, TypeVar

from kombu import Message, Queue
from kombu.mixins import ConsumerProducerMixin

C = TypeVar(name="C")


class MessageQueue(ConsumerProducerMixin):
    def __init__(self, url: str, *args, **kwargs) -> None:
        self._url = url
        self._routing_keys = []
        self._queue_by_routing_key: dict[str, Queue] = {}
        self._on_message_callback_by_routing_key: dict[str, Callable[[Message], None]] = {}

    def get_consumers(self, consumer_cls: C, channel) -> list[C]:
        return [
            consumer_cls(
                queues=[self._queue_by_routing_key[routing_key]],
                on_message=self._on_message_callback_by_routing_key[routing_key],
            )
            for routing_key in self._routing_keys
        ]

    def listen(self, routing_key: str):
        """
        Decorator accepts callable with zero or one argument typed with pydantic.BaseModel.
        Creates on_message callback for kombu.Consumer.
        Callback automatically parses message JSON data and validates it against given pydantic schema
        and its validators.
        :param routing_key:
        :return:
        """

        def decorator(_callable):
            parameters = inspect.signature(_callable).parameters
            pydantic_model = None
            if len(parameters):
                (arg, pydantic_model), *_ = parameters.items()

            def on_message_callback(message: Message) -> None:
                if pydantic_model is not None:
                    try:
                        pydantic_instance = pydantic_model(**message.decode())
                        _callable(pydantic_instance)
                    except ValueError as pydantic_exception:
                        logging.error(
                            f"{routing_key}: Error while parsing {pydantic_model.__name__}: {pydantic_exception}"
                        )

                _callable()

            return _callable

    def _register_queue(self, routing_key: str) -> None:
        self._queue_by_routing_key[routing_key] = Queue(name=f"{routing_key}_queue", routing_key=routing_key)

    def _register_on_message_callback(self, routing_key: str, callback: Callable[[Message], None]) -> None:
        self._on_message_callback_by_routing_key[routing_key] = callback


# TODO: investigate queue name
