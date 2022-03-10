import json
import logging
from json import JSONDecodeError
from typing import Callable

import pytest
from _pytest.logging import LogCaptureFixture
from kombu import Message
from pydantic import BaseModel, validator

from cornflower.utils import get_on_message_callback
from tests.unit.test_utils.conftest import FakeMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@pytest.fixture
def fake_message() -> FakeMessage:
    return FakeMessage(content={"arg": "some_text"})


@pytest.fixture
def fake_message_with_invalid_json() -> FakeMessage:
    fake_message = FakeMessage(content={"arg": "text"})
    fake_message._content = "'{'arg': invalid}'"
    return fake_message


@pytest.fixture
def fake_message_with_invalid_data() -> FakeMessage:
    return FakeMessage(content={"arg": "invalid"})


@pytest.fixture
def acked_fake_message() -> FakeMessage:
    fake_message = FakeMessage(content={"arg": "acked"})
    fake_message.ack()
    return fake_message


class PydanticModel(BaseModel):
    arg: str

    @validator("arg")
    def validate_arg(cls, value) -> str:
        if value == "invalid":
            raise ValueError("Invalid arg")

        return value


@pytest.fixture
def callable_with_pydantic_model() -> Callable[[PydanticModel], None]:
    def _callable(model: PydanticModel) -> None:
        logger.info(model.arg)

    return _callable


@pytest.fixture
def on_message_callback_with_pydantic_model(
    callable_with_pydantic_model: Callable[[PydanticModel], None]
) -> Callable[[Message], None]:
    routing_key = "test"

    return get_on_message_callback(
        _callable=callable_with_pydantic_model, routing_key=routing_key, pydantic_model_class=PydanticModel
    )


def test_get_on_message_callback_with_callable_with_side_effect(
    on_message_callback_with_pydantic_model: Callable[[Message], None],
    fake_message: FakeMessage,
    caplog: LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        on_message_callback_with_pydantic_model(fake_message)

    assert fake_message.is_ack
    assert fake_message.content["arg"] in caplog.text


def test_get_on_message_callback_logs_error_on_invalid_json(
    on_message_callback_with_pydantic_model: Callable[[Message], None],
    fake_message_with_invalid_json: FakeMessage,
    caplog: LogCaptureFixture,
) -> None:
    decode_error = None

    try:
        json.loads(fake_message_with_invalid_json._content)
    except JSONDecodeError as exc:
        decode_error = exc

    expected_log = f"Error while parsing JSON for {PydanticModel.__name__}: {decode_error}"
    with caplog.at_level(logging.ERROR):
        on_message_callback_with_pydantic_model(fake_message_with_invalid_json)

    assert fake_message_with_invalid_json.is_ack
    assert expected_log in caplog.text


def test_get_on_message_callback_logs_error_on_pydantic_validation_error(
    on_message_callback_with_pydantic_model: Callable[[Message], None],
    fake_message_with_invalid_data: FakeMessage,
    caplog: LogCaptureFixture,
) -> None:
    pydantic_exception = None
    try:
        PydanticModel(**fake_message_with_invalid_data.content)
    except ValueError as exc:
        pydantic_exception = exc

    expected_log = f"Error while parsing {PydanticModel.__name__}: {pydantic_exception}"
    with caplog.at_level(logging.ERROR):
        on_message_callback_with_pydantic_model(fake_message_with_invalid_data)

    assert fake_message_with_invalid_data.is_ack
    assert expected_log in caplog.text
