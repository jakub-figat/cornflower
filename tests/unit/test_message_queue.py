from typing import Callable

import pytest

from cornflower import MessageQueue


@pytest.fixture
def message_queue() -> MessageQueue:
    return MessageQueue(url="amqp://test:test@test:5672")


@pytest.fixture
def handler_with_no_args() -> Callable[[], None]:
    def handler() -> None:
        pass

    return handler


def test_message_queue_register_handler(message_queue: MessageQueue, handler_with_no_args: Callable[[], None]) -> None:
    routing_keys = ["routing1", "routing2", "routing3"]

    for key in routing_keys:
        message_queue.listen(key)(handler_with_no_args)

    expected_keys = [entry.queue.routing_key for entry in message_queue._consumer_registry]

    assert len(message_queue._consumer_registry) == 3
    assert expected_keys == routing_keys
