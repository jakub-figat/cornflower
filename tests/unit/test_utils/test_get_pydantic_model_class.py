from typing import Callable, Optional, Type

import pytest
from pydantic import BaseModel

from cornflower.utils import get_pydantic_model_class


class PydanticModel1(BaseModel):
    pass


class PydanticModel2(BaseModel):
    pass


def handler_1(arg: PydanticModel1):
    pass


def handler_2(some_arg: PydanticModel2):
    pass


def handler_3():
    pass


def handler_4(arg_1: PydanticModel1, arg_2: PydanticModel2):
    pass


@pytest.mark.parametrize(
    ["_callable", "pydantic_model_class"],
    [(handler_1, PydanticModel1), (handler_2, PydanticModel2), (handler_3, None), (handler_4, PydanticModel1)],
)
def test_get_pydantic_model_class_properly_parses_pydantic_type_from_zero_or_one_argument(
    _callable: Callable, pydantic_model_class: Optional[Type[BaseModel]]
) -> None:
    assert get_pydantic_model_class(_callable=_callable) is pydantic_model_class


def test_get_pydantic_model_class_raises_assertion_error_when_argument_lacks_typing() -> None:
    def _callable(arg):
        pass

    with pytest.raises(AssertionError):
        get_pydantic_model_class(_callable)


def test_get_pydantic_model_class_raises_assertion_error_when_argument_typing_is_not_base_model_subclass() -> None:
    class A:
        pass

    def _callable(arg: A) -> None:
        pass

    with pytest.raises(AssertionError):
        get_pydantic_model_class(_callable)
