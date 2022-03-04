import inspect
import json
import logging
from json import JSONDecodeError
from typing import Callable, TypeVar

from kombu import Connection, Message, Queue
from kombu.mixins import ConsumerProducerMixin
from pydantic import BaseModel

# Generic consumer class provided by Kombu
C = TypeVar(name="C")


# Generic callable consumed and returned by decorator
V = TypeVar(name="V")


class MessageQueue(ConsumerProducerMixin):
    def __init__(self, url: str, *args, **kwargs) -> None:
        self.connection = Connection(url)
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
            # TODO: extract parsing logic, extract validation logic
            parameters = inspect.signature(_callable).parameters
            pydantic_model = None
            if len(parameters):
                (arg, _type), *_ = parameters.items()
                pydantic_model = _type.annotation
                assert issubclass(
                    pydantic_model, BaseModel
                ), f"{_callable.__name__}: Command argument to handler function must inherit from pydantic.BaseModel"

            def on_message_callback(message: Message) -> None:
                # TODO: extract creating callback
                if pydantic_model is None:
                    _callable()

                try:
                    pydantic_instance = pydantic_model(**json.loads(message.decode()))
                    _callable(pydantic_instance)
                    message.ack()
                except JSONDecodeError as decode_error:
                    logging.error(
                        f"[{routing_key}] Error while parsing JSON for {pydantic_model.__name__}: {decode_error}"
                    )
                except ValueError as pydantic_exception:
                    logging.error(
                        f"[{routing_key}] Error while parsing {pydantic_model.__name__}: {pydantic_exception}"
                    )

            self._register_on_message_callback(routing_key=routing_key, callback=on_message_callback)

            return _callable

        self._routing_keys.append(routing_key)
        self._register_queue(routing_key=routing_key)

        return decorator

    def _register_queue(self, routing_key: str) -> None:
        self._queue_by_routing_key[routing_key] = Queue(name=routing_key, routing_key=routing_key)

    def _register_on_message_callback(self, routing_key: str, callback: Callable[[Message], None]) -> None:
        self._on_message_callback_by_routing_key[routing_key] = callback
