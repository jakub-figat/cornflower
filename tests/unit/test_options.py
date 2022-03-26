import pytest

from cornflower.options import ConsumerOptions


def test_consumer_options_raise_validation_error_on_negative_prefetch_count() -> None:
    with pytest.raises(ValueError):
        ConsumerOptions(prefetch_count=-1)
