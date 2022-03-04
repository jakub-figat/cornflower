import logging
from typing import Callable

import pytest
from _pytest.logging import LogCaptureFixture
from pydantic import BaseModel

from cornflower.utils import get_on_message_callback
from tests.unit.test_utils.conftest import FakeMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@pytest.fixture
def fake_message() -> FakeMessage:
    return FakeMessage(content={"arg": "some_text"})


@pytest.fixture
def acked_fake_message() -> FakeMessage:
    fake_message = FakeMessage(content={"arg": "acked"})
    fake_message.ack()
    return fake_message


class PydanticModel(BaseModel):
    arg: str


@pytest.fixture
def callable_with_pydantic_model() -> Callable[[PydanticModel], None]:
    def _callable(model: PydanticModel) -> None:
        logger.info(model.arg)

    return _callable


def test_get_on_message_callback_with_callable_with_side_effect(
    callable_with_pydantic_model: Callable[[PydanticModel], None], fake_message: FakeMessage, caplog: LogCaptureFixture
) -> None:
    routing_key = "test"

    on_message_callback = get_on_message_callback(
        _callable=callable_with_pydantic_model, routing_key=routing_key, pydantic_model_class=PydanticModel
    )

    with caplog.at_level(logging.INFO):
        on_message_callback(fake_message)

    assert fake_message.content["arg"] in caplog.text
